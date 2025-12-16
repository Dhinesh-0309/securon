"""Tests for ML Engine implementation"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.securon.ml_engine import create_ml_engine, IsolationForestMLEngine
from src.securon.interfaces.core_types import (
    CloudLog, LogSource, NormalizedLogEntry, AnomalyType, Severity
)
from src.securon.interfaces.ml_engine import AnomalyResult
from src.securon.interfaces.iac_scanner import SecurityRule, RuleSource, RuleStatus


class TestMLEngine:
    """Test ML Engine functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.ml_engine = create_ml_engine(contamination=0.2, random_state=42)
        
    def create_sample_logs(self, count: int = 10) -> List[CloudLog]:
        """Create sample cloud logs for testing"""
        logs = []
        base_time = datetime.now()
        
        for i in range(count):
            # Create normal logs
            log = CloudLog(
                timestamp=base_time + timedelta(minutes=i),
                source=LogSource.VPC_FLOW,
                raw_data={"test": f"data_{i}"},
                normalized_data=NormalizedLogEntry(
                    timestamp=base_time + timedelta(minutes=i),
                    source_ip=f"192.168.1.{i + 1}",
                    destination_ip=f"10.0.0.{i + 1}",
                    port=80 + i,
                    protocol="TCP",
                    action="ACCEPT",
                    user=f"user_{i}",
                    resource=f"resource_{i}",
                    api_call=f"api_call_{i}"
                )
            )
            logs.append(log)
            
        # Add some anomalous logs
        anomalous_logs = [
            CloudLog(
                timestamp=base_time + timedelta(hours=3),  # Unusual time
                source=LogSource.CLOUDTRAIL,
                raw_data={"anomaly": "port_scan"},
                normalized_data=NormalizedLogEntry(
                    timestamp=base_time + timedelta(hours=3),
                    source_ip="192.168.1.100",
                    destination_ip="10.0.0.100",
                    port=22,  # SSH port
                    protocol="TCP",
                    action="REJECT",
                    user="suspicious_user",
                    resource="critical_resource",
                    api_call="admin_action"
                )
            ),
            CloudLog(
                timestamp=base_time + timedelta(hours=2),
                source=LogSource.IAM,
                raw_data={"anomaly": "brute_force"},
                normalized_data=NormalizedLogEntry(
                    timestamp=base_time + timedelta(hours=2),
                    source_ip="192.168.1.200",
                    port=443,
                    protocol="HTTPS",
                    action="failed_login",
                    user="admin",
                    resource="auth_service",
                    api_call="authenticate"
                )
            )
        ]
        
        logs.extend(anomalous_logs)
        return logs
    
    @pytest.mark.asyncio
    async def test_process_logs_basic(self):
        """Test basic log processing functionality"""
        logs = self.create_sample_logs(20)
        
        anomalies = await self.ml_engine.process_logs(logs)
        
        # Should detect some anomalies
        assert len(anomalies) > 0
        assert all(isinstance(a, AnomalyResult) for a in anomalies)
        
        # Check anomaly structure
        for anomaly in anomalies:
            assert anomaly.id is not None
            assert isinstance(anomaly.type, AnomalyType)
            assert 0 <= anomaly.severity <= 1
            assert 0 <= anomaly.confidence <= 1
            assert len(anomaly.affected_resources) > 0
            assert len(anomaly.patterns) > 0
    
    @pytest.mark.asyncio
    async def test_process_empty_logs(self):
        """Test processing empty log list"""
        anomalies = await self.ml_engine.process_logs([])
        assert anomalies == []
    
    @pytest.mark.asyncio
    async def test_generate_candidate_rules(self):
        """Test candidate rule generation from anomalies"""
        logs = self.create_sample_logs(15)
        anomalies = await self.ml_engine.process_logs(logs)
        
        if anomalies:  # Only test if anomalies were detected
            rules = self.ml_engine.generate_candidate_rules(anomalies)
            
            assert len(rules) > 0
            assert all(isinstance(r, SecurityRule) for r in rules)
            
            # Check rule structure
            for rule in rules:
                assert rule.id is not None
                assert rule.name is not None
                assert rule.description is not None
                assert isinstance(rule.severity, Severity)
                assert rule.pattern is not None
                assert rule.remediation is not None
                assert rule.source == RuleSource.ML_GENERATED
                assert rule.status == RuleStatus.CANDIDATE
                assert rule.created_at is not None
    
    @pytest.mark.asyncio
    async def test_explain_anomaly(self):
        """Test anomaly explanation generation"""
        logs = self.create_sample_logs(15)
        anomalies = await self.ml_engine.process_logs(logs)
        
        if anomalies:  # Only test if anomalies were detected
            explanation = self.ml_engine.explain_anomaly(anomalies[0])
            
            assert explanation.summary is not None
            assert explanation.technical_details is not None
            assert isinstance(explanation.risk_level, Severity)
            assert len(explanation.recommended_actions) > 0
            assert all(isinstance(action, str) for action in explanation.recommended_actions)
    
    def test_anomaly_type_classification(self):
        """Test anomaly type classification logic"""
        engine = IsolationForestMLEngine()
        
        # Test port scan detection
        port_scan_log = CloudLog(
            timestamp=datetime.now(),
            source=LogSource.VPC_FLOW,
            raw_data={},
            normalized_data=NormalizedLogEntry(
                timestamp=datetime.now(),
                source_ip="192.168.1.1",
                port=22,  # SSH port (< 1024)
                protocol="TCP",
                action="CONNECT"
            )
        )
        
        anomaly_type = engine._classify_anomaly_type(port_scan_log)
        assert anomaly_type == AnomalyType.PORT_SCAN
        
        # Test brute force detection
        brute_force_log = CloudLog(
            timestamp=datetime.now(),
            source=LogSource.IAM,
            raw_data={},
            normalized_data=NormalizedLogEntry(
                timestamp=datetime.now(),
                source_ip="192.168.1.1",
                action="failed_login",
                user="admin"
            )
        )
        
        anomaly_type = engine._classify_anomaly_type(brute_force_log)
        assert anomaly_type == AnomalyType.BRUTE_FORCE
        
        # Test unusual API detection
        api_log = CloudLog(
            timestamp=datetime.now(),
            source=LogSource.CLOUDTRAIL,
            raw_data={},
            normalized_data=NormalizedLogEntry(
                timestamp=datetime.now(),
                source_ip="192.168.1.1",
                action="API_CALL",
                api_call="DeleteUser"
            )
        )
        
        anomaly_type = engine._classify_anomaly_type(api_log)
        assert anomaly_type == AnomalyType.UNUSUAL_API
    
    def test_feature_extraction(self):
        """Test feature extraction from logs"""
        engine = IsolationForestMLEngine()
        # Create only normal logs, not including anomalous ones
        logs = []
        base_time = datetime.now()
        
        for i in range(5):
            log = CloudLog(
                timestamp=base_time + timedelta(minutes=i),
                source=LogSource.VPC_FLOW,
                raw_data={"test": f"data_{i}"},
                normalized_data=NormalizedLogEntry(
                    timestamp=base_time + timedelta(minutes=i),
                    source_ip=f"192.168.1.{i + 1}",
                    destination_ip=f"10.0.0.{i + 1}",
                    port=80 + i,
                    protocol="TCP",
                    action="ACCEPT",
                    user=f"user_{i}",
                    resource=f"resource_{i}",
                    api_call=f"api_call_{i}"
                )
            )
            logs.append(log)
        
        features_df = engine._extract_features(logs)
        
        assert len(features_df) == 5
        assert 'hour_of_day' in features_df.columns
        assert 'day_of_week' in features_df.columns
        assert 'source_ip_hash' in features_df.columns
        assert 'port' in features_df.columns
        assert 'protocol_hash' in features_df.columns
        assert 'action_hash' in features_df.columns
        
        # Check that all values are numeric
        assert features_df.dtypes.apply(lambda x: x.kind in 'biufc').all()


class TestMLEngineFactory:
    """Test ML Engine factory functionality"""
    
    def test_create_ml_engine_default(self):
        """Test creating ML engine with default parameters"""
        engine = create_ml_engine()
        
        assert isinstance(engine, IsolationForestMLEngine)
        assert engine.contamination == 0.1
        assert engine.random_state == 42
    
    def test_create_ml_engine_custom(self):
        """Test creating ML engine with custom parameters"""
        engine = create_ml_engine(contamination=0.2, random_state=123)
        
        assert isinstance(engine, IsolationForestMLEngine)
        assert engine.contamination == 0.2
        assert engine.random_state == 123