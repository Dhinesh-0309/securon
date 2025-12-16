"""ML Engine implementation with Isolation Forest algorithm"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..interfaces.ml_engine import MLEngine, AnomalyResult
from ..interfaces.core_types import (
    CloudLog, AnomalyType, AnomalyPattern, Explanation, 
    TimeRange, Severity
)
from ..interfaces.iac_scanner import SecurityRule, RuleSource, RuleStatus


class IsolationForestMLEngine(MLEngine):
    """ML Engine implementation using Isolation Forest for anomaly detection"""
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the ML Engine with Isolation Forest
        
        Args:
            contamination: Expected proportion of anomalies in the data
            random_state: Random state for reproducible results
        """
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        
    async def process_logs(self, logs: List[CloudLog]) -> List[AnomalyResult]:
        """Process cloud logs and detect anomalies using Isolation Forest"""
        if not logs:
            return []
            
        # Convert logs to feature matrix
        features_df = self._extract_features(logs)
        
        if features_df.empty:
            return []
            
        # Normalize features
        features_normalized = self.scaler.fit_transform(features_df)
        
        # Detect anomalies
        anomaly_scores = self.isolation_forest.fit_predict(features_normalized)
        anomaly_scores_continuous = self.isolation_forest.decision_function(features_normalized)
        
        # Generate anomaly results
        anomalies = []
        for i, (score, continuous_score) in enumerate(zip(anomaly_scores, anomaly_scores_continuous)):
            if score == -1:  # Anomaly detected
                log = logs[i]
                anomaly = self._create_anomaly_result(
                    log, features_df.iloc[i], continuous_score, i
                )
                anomalies.append(anomaly)
                
        return anomalies
    
    def _extract_features(self, logs: List[CloudLog]) -> pd.DataFrame:
        """Extract numerical features from cloud logs for ML analysis"""
        features = []
        
        for log in logs:
            normalized = log.normalized_data
            feature_dict = {
                'hour_of_day': log.timestamp.hour,
                'day_of_week': log.timestamp.weekday(),
                'source_ip_hash': hash(normalized.source_ip) % 10000,
                'port': normalized.port or 0,
                'protocol_hash': hash(normalized.protocol or '') % 100,
                'action_hash': hash(normalized.action) % 100,
                'user_hash': hash(normalized.user or '') % 1000,
                'resource_hash': hash(normalized.resource or '') % 1000,
                'api_call_hash': hash(normalized.api_call or '') % 1000,
            }
            
            # Add destination IP if available
            if normalized.destination_ip:
                feature_dict['dest_ip_hash'] = hash(normalized.destination_ip) % 10000
            else:
                feature_dict['dest_ip_hash'] = 0
                
            features.append(feature_dict)
            
        return pd.DataFrame(features)
    
    def _create_anomaly_result(
        self, 
        log: CloudLog, 
        features: pd.Series, 
        anomaly_score: float,
        log_index: int
    ) -> AnomalyResult:
        """Create an AnomalyResult from a detected anomaly"""
        
        # Determine anomaly type based on log characteristics
        anomaly_type = self._classify_anomaly_type(log)
        
        # Calculate severity based on anomaly score (more negative = more anomalous)
        severity = abs(anomaly_score)
        confidence = min(1.0, abs(anomaly_score) * 2)  # Scale confidence
        
        # Create time window around the anomaly
        time_window = TimeRange(
            start=log.timestamp - timedelta(minutes=5),
            end=log.timestamp + timedelta(minutes=5)
        )
        
        # Generate patterns that contributed to the anomaly
        patterns = self._generate_anomaly_patterns(features, log)
        
        # Determine affected resources
        affected_resources = []
        if log.normalized_data.resource:
            affected_resources.append(log.normalized_data.resource)
        if log.normalized_data.source_ip:
            affected_resources.append(f"IP:{log.normalized_data.source_ip}")
        if log.normalized_data.destination_ip:
            affected_resources.append(f"IP:{log.normalized_data.destination_ip}")
            
        return AnomalyResult(
            id=str(uuid.uuid4()),
            type=anomaly_type,
            severity=severity,
            confidence=confidence,
            affected_resources=affected_resources,
            time_window=time_window,
            patterns=patterns
        )
    
    def _classify_anomaly_type(self, log: CloudLog) -> AnomalyType:
        """Classify the type of anomaly based on log characteristics"""
        normalized = log.normalized_data
        
        # Port scan detection: unusual port access patterns
        if normalized.port and (normalized.port < 1024 or normalized.port > 65000):
            return AnomalyType.PORT_SCAN
            
        # Brute force detection: authentication-related actions
        if normalized.action and any(keyword in normalized.action.lower() 
                                   for keyword in ['login', 'auth', 'signin', 'failed']):
            return AnomalyType.BRUTE_FORCE
            
        # Unusual API behavior: uncommon API calls
        if normalized.api_call and any(keyword in normalized.api_call.lower()
                                     for keyword in ['delete', 'modify', 'admin', 'root']):
            return AnomalyType.UNUSUAL_API
            
        # Default to suspicious IP for other cases
        return AnomalyType.SUSPICIOUS_IP
    
    def _generate_anomaly_patterns(self, features: pd.Series, log: CloudLog) -> List[AnomalyPattern]:
        """Generate patterns that contributed to the anomaly detection"""
        patterns = []
        
        # Hour of day pattern
        if features['hour_of_day'] < 6 or features['hour_of_day'] > 22:
            patterns.append(AnomalyPattern(
                feature="hour_of_day",
                expected_range=(6.0, 22.0),
                actual_value=float(features['hour_of_day']),
                deviation=abs(features['hour_of_day'] - 14.0) / 14.0
            ))
            
        # Port pattern
        if features['port'] > 0:
            if features['port'] < 1024 or features['port'] > 65000:
                patterns.append(AnomalyPattern(
                    feature="port",
                    expected_range=(1024.0, 65000.0),
                    actual_value=float(features['port']),
                    deviation=1.0 if features['port'] < 1024 else 
                             (features['port'] - 65000) / 65000
                ))
                
        # Add at least one pattern if none were generated
        if not patterns:
            patterns.append(AnomalyPattern(
                feature="general_behavior",
                expected_range=(0.0, 1.0),
                actual_value=0.0,
                deviation=1.0
            ))
            
        return patterns
    
    def generate_candidate_rules(self, anomalies: List[AnomalyResult]) -> List[SecurityRule]:
        """Generate candidate security rules from detected anomalies"""
        rules = []
        
        # Group anomalies by type to create comprehensive rules
        anomaly_groups = {}
        for anomaly in anomalies:
            if anomaly.type not in anomaly_groups:
                anomaly_groups[anomaly.type] = []
            anomaly_groups[anomaly.type].append(anomaly)
            
        # Generate rules for each anomaly type
        for anomaly_type, type_anomalies in anomaly_groups.items():
            rule = self._create_rule_for_anomaly_type(anomaly_type, type_anomalies)
            rules.append(rule)
            
        return rules
    
    def _create_rule_for_anomaly_type(
        self, 
        anomaly_type: AnomalyType, 
        anomalies: List[AnomalyResult]
    ) -> SecurityRule:
        """Create a security rule for a specific anomaly type"""
        
        # Calculate average severity
        avg_severity = sum(a.severity for a in anomalies) / len(anomalies)
        
        # Map severity to enum
        if avg_severity > 0.8:
            severity = Severity.CRITICAL
        elif avg_severity > 0.6:
            severity = Severity.HIGH
        elif avg_severity > 0.4:
            severity = Severity.MEDIUM
        else:
            severity = Severity.LOW
            
        # Generate rule based on anomaly type
        rule_configs = {
            AnomalyType.PORT_SCAN: {
                'name': 'ML-Generated Port Scan Detection',
                'description': 'Detect potential port scanning activities based on ML analysis',
                'pattern': 'port_access_pattern_unusual',
                'remediation': 'Review network access patterns and implement port access controls'
            },
            AnomalyType.BRUTE_FORCE: {
                'name': 'ML-Generated Brute Force Detection',
                'description': 'Detect potential brute force attacks based on ML analysis',
                'pattern': 'authentication_failure_pattern',
                'remediation': 'Implement account lockout policies and multi-factor authentication'
            },
            AnomalyType.SUSPICIOUS_IP: {
                'name': 'ML-Generated Suspicious IP Detection',
                'description': 'Detect suspicious IP activity based on ML analysis',
                'pattern': 'ip_behavior_anomaly',
                'remediation': 'Review IP access patterns and implement IP allowlisting'
            },
            AnomalyType.UNUSUAL_API: {
                'name': 'ML-Generated Unusual API Detection',
                'description': 'Detect unusual API behavior based on ML analysis',
                'pattern': 'api_usage_anomaly',
                'remediation': 'Review API access patterns and implement API rate limiting'
            }
        }
        
        config = rule_configs[anomaly_type]
        
        return SecurityRule(
            id=str(uuid.uuid4()),
            name=config['name'],
            description=config['description'],
            severity=severity,
            pattern=config['pattern'],
            remediation=config['remediation'],
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
    
    def explain_anomaly(self, anomaly: AnomalyResult) -> Explanation:
        """Provide detailed explanation for a detected anomaly"""
        
        # Generate summary based on anomaly type
        summaries = {
            AnomalyType.PORT_SCAN: "Potential port scanning activity detected",
            AnomalyType.BRUTE_FORCE: "Potential brute force attack detected", 
            AnomalyType.SUSPICIOUS_IP: "Suspicious IP activity detected",
            AnomalyType.UNUSUAL_API: "Unusual API behavior detected"
        }
        
        summary = summaries.get(anomaly.type, "Anomalous behavior detected")
        
        # Generate technical details
        technical_details = f"""
        Anomaly Type: {anomaly.type.value}
        Confidence Score: {anomaly.confidence:.2f}
        Severity Score: {anomaly.severity:.2f}
        Time Window: {anomaly.time_window.start} to {anomaly.time_window.end}
        Affected Resources: {', '.join(anomaly.affected_resources)}
        
        Detected Patterns:
        """
        
        for pattern in anomaly.patterns:
            technical_details += f"""
        - {pattern.feature}: Expected {pattern.expected_range}, Got {pattern.actual_value:.2f} (Deviation: {pattern.deviation:.2f})
        """
        
        # Map severity score to risk level
        if anomaly.severity > 0.8:
            risk_level = Severity.CRITICAL
        elif anomaly.severity > 0.6:
            risk_level = Severity.HIGH
        elif anomaly.severity > 0.4:
            risk_level = Severity.MEDIUM
        else:
            risk_level = Severity.LOW
            
        # Generate recommended actions based on anomaly type
        action_map = {
            AnomalyType.PORT_SCAN: [
                "Review network access logs for the affected time period",
                "Implement network segmentation to limit port access",
                "Configure intrusion detection systems",
                "Review firewall rules and access controls"
            ],
            AnomalyType.BRUTE_FORCE: [
                "Review authentication logs for failed login attempts",
                "Implement account lockout policies",
                "Enable multi-factor authentication",
                "Monitor for credential stuffing attacks"
            ],
            AnomalyType.SUSPICIOUS_IP: [
                "Investigate the source IP address",
                "Review geolocation and reputation of the IP",
                "Implement IP-based access controls",
                "Monitor for additional suspicious activity"
            ],
            AnomalyType.UNUSUAL_API: [
                "Review API access logs and usage patterns",
                "Implement API rate limiting and throttling",
                "Verify API key and authentication validity",
                "Monitor for API abuse patterns"
            ]
        }
        
        recommended_actions = action_map.get(anomaly.type, [
            "Review the detected anomaly in detail",
            "Investigate the affected resources",
            "Implement appropriate security controls"
        ])
        
        return Explanation(
            summary=summary,
            technical_details=technical_details.strip(),
            risk_level=risk_level,
            recommended_actions=recommended_actions
        )