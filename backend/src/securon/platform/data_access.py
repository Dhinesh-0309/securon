"""Enhanced data access layer with comprehensive error handling and validation"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from .database import DatabaseManager, DatabaseError
from ..interfaces.core_types import (
    Severity, RuleSource, RuleStatus, LogSource, AnomalyType,
    CloudLog, NormalizedLogEntry, TimeRange, AnomalyPattern, Explanation
)
from ..interfaces.iac_scanner import SecurityRule, ScanResult
from ..rule_engine.models import RuleVersion, RuleConflict, RuleMetrics
from ..ml_engine.interfaces import AnomalyResult


logger = logging.getLogger(__name__)


class DataAccessError(Exception):
    """Exception raised for data access operations"""
    pass


class DataValidator:
    """Validates data before storage operations"""
    
    @staticmethod
    def validate_security_rule(rule: SecurityRule) -> List[str]:
        """Validate security rule data"""
        errors = []
        
        if not rule.id or len(rule.id.strip()) < 3:
            errors.append("Rule ID must be at least 3 characters")
        
        if not rule.name or len(rule.name.strip()) < 3:
            errors.append("Rule name must be at least 3 characters")
        
        if not rule.description or len(rule.description.strip()) < 10:
            errors.append("Rule description must be at least 10 characters")
        
        if not rule.pattern or len(rule.pattern.strip()) < 1:
            errors.append("Rule pattern cannot be empty")
        
        if not rule.remediation or len(rule.remediation.strip()) < 10:
            errors.append("Rule remediation must be at least 10 characters")
        
        return errors
    
    @staticmethod
    def validate_cloud_log(log: CloudLog) -> List[str]:
        """Validate cloud log data"""
        errors = []
        
        if not log.timestamp:
            errors.append("Log timestamp is required")
        
        if not log.source:
            errors.append("Log source is required")
        
        if not log.raw_data:
            errors.append("Log raw data cannot be empty")
        
        if not log.normalized_data:
            errors.append("Log normalized data is required")
        
        # Validate normalized data
        if not log.normalized_data.source_ip:
            errors.append("Normalized log must have source IP")
        
        if not log.normalized_data.action:
            errors.append("Normalized log must have action")
        
        return errors
    
    @staticmethod
    def validate_anomaly_result(anomaly: AnomalyResult) -> List[str]:
        """Validate anomaly result data"""
        errors = []
        
        if not anomaly.id:
            errors.append("Anomaly ID is required")
        
        if not anomaly.type:
            errors.append("Anomaly type is required")
        
        if anomaly.severity < 0 or anomaly.severity > 1:
            errors.append("Anomaly severity must be between 0 and 1")
        
        if anomaly.confidence < 0 or anomaly.confidence > 1:
            errors.append("Anomaly confidence must be between 0 and 1")
        
        if not anomaly.affected_resources:
            errors.append("Anomaly must have affected resources")
        
        if not anomaly.time_window:
            errors.append("Anomaly must have time window")
        
        return errors


class SecuronDataAccess:
    """Enhanced data access layer for Securon platform"""
    
    def __init__(self, db_path: str = "data/securon.db", backup_enabled: bool = True):
        self.db_manager = DatabaseManager(db_path, backup_enabled)
        self.validator = DataValidator()
        
        # Performance monitoring
        self._operation_counts = {}
        self._error_counts = {}
        
        logger.info("SecuronDataAccess initialized")
    
    def _record_operation(self, operation: str, success: bool = True):
        """Record operation for monitoring"""
        if operation not in self._operation_counts:
            self._operation_counts[operation] = {'success': 0, 'error': 0}
        
        if success:
            self._operation_counts[operation]['success'] += 1
        else:
            self._operation_counts[operation]['error'] += 1
            
            if operation not in self._error_counts:
                self._error_counts[operation] = 0
            self._error_counts[operation] += 1
    
    # Security Rules Operations
    async def store_security_rule(self, rule: SecurityRule) -> None:
        """Store security rule with validation"""
        try:
            # Validate rule
            validation_errors = self.validator.validate_security_rule(rule)
            if validation_errors:
                raise DataAccessError(f"Rule validation failed: {', '.join(validation_errors)}")
            
            await self.db_manager.store_security_rule(rule)
            self._record_operation('store_security_rule', True)
            
        except Exception as e:
            self._record_operation('store_security_rule', False)
            logger.error(f"Failed to store security rule {rule.id}: {str(e)}")
            raise DataAccessError(f"Failed to store security rule: {str(e)}")
    
    async def get_security_rule(self, rule_id: str) -> Optional[SecurityRule]:
        """Get security rule by ID"""
        try:
            rule = await self.db_manager.get_security_rule(rule_id)
            self._record_operation('get_security_rule', True)
            return rule
            
        except Exception as e:
            self._record_operation('get_security_rule', False)
            logger.error(f"Failed to get security rule {rule_id}: {str(e)}")
            raise DataAccessError(f"Failed to get security rule: {str(e)}")
    
    async def get_rules_by_status(self, status: RuleStatus) -> List[SecurityRule]:
        """Get all rules with specific status"""
        try:
            rules = await self.db_manager.get_rules_by_status(status)
            self._record_operation('get_rules_by_status', True)
            return rules
            
        except Exception as e:
            self._record_operation('get_rules_by_status', False)
            logger.error(f"Failed to get rules by status {status}: {str(e)}")
            raise DataAccessError(f"Failed to get rules by status: {str(e)}")
    
    async def get_all_active_rules(self) -> List[SecurityRule]:
        """Get all active security rules"""
        return await self.get_rules_by_status(RuleStatus.ACTIVE)
    
    async def get_candidate_rules(self) -> List[SecurityRule]:
        """Get all candidate security rules"""
        return await self.get_rules_by_status(RuleStatus.CANDIDATE)
    
    async def approve_rule(self, rule_id: str) -> bool:
        """Approve a candidate rule"""
        try:
            rule = await self.get_security_rule(rule_id)
            if not rule:
                return False
            
            if rule.status != RuleStatus.CANDIDATE:
                raise DataAccessError(f"Rule {rule_id} is not a candidate rule")
            
            rule.status = RuleStatus.ACTIVE
            await self.store_security_rule(rule)
            
            logger.info(f"Approved rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve rule {rule_id}: {str(e)}")
            raise DataAccessError(f"Failed to approve rule: {str(e)}")
    
    async def reject_rule(self, rule_id: str) -> bool:
        """Reject a candidate rule"""
        try:
            rule = await self.get_security_rule(rule_id)
            if not rule:
                return False
            
            if rule.status != RuleStatus.CANDIDATE:
                raise DataAccessError(f"Rule {rule_id} is not a candidate rule")
            
            rule.status = RuleStatus.REJECTED
            await self.store_security_rule(rule)
            
            logger.info(f"Rejected rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject rule {rule_id}: {str(e)}")
            raise DataAccessError(f"Failed to reject rule: {str(e)}")
    
    async def delete_security_rule(self, rule_id: str) -> bool:
        """Delete security rule"""
        try:
            result = await self.db_manager.delete_security_rule(rule_id)
            self._record_operation('delete_security_rule', True)
            return result
            
        except Exception as e:
            self._record_operation('delete_security_rule', False)
            logger.error(f"Failed to delete security rule {rule_id}: {str(e)}")
            raise DataAccessError(f"Failed to delete security rule: {str(e)}")
    
    # Cloud Logs Operations
    async def store_cloud_logs(self, logs: List[CloudLog], batch_id: Optional[str] = None) -> None:
        """Store cloud logs with validation"""
        try:
            if not batch_id:
                batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            async with self.db_manager.get_connection() as conn:
                for log in logs:
                    # Validate log
                    validation_errors = self.validator.validate_cloud_log(log)
                    if validation_errors:
                        logger.warning(f"Skipping invalid log: {', '.join(validation_errors)}")
                        continue
                    
                    # Serialize data
                    raw_data_json = json.dumps(log.raw_data)
                    normalized_data_json = json.dumps(log.normalized_data.model_dump(), default=str)
                    checksum = self.db_manager._calculate_checksum(log.model_dump())
                    
                    conn.execute("""
                        INSERT INTO cloud_logs 
                        (timestamp, source, raw_data, normalized_data, batch_id, checksum)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        log.timestamp, log.source.value, raw_data_json,
                        normalized_data_json, batch_id, checksum
                    ))
                
                conn.commit()
            
            self._record_operation('store_cloud_logs', True)
            logger.info(f"Stored {len(logs)} cloud logs with batch ID: {batch_id}")
            
        except Exception as e:
            self._record_operation('store_cloud_logs', False)
            logger.error(f"Failed to store cloud logs: {str(e)}")
            raise DataAccessError(f"Failed to store cloud logs: {str(e)}")
    
    async def get_cloud_logs(self, 
                           source: Optional[LogSource] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: int = 1000) -> List[CloudLog]:
        """Get cloud logs with filtering"""
        try:
            query = "SELECT * FROM cloud_logs WHERE 1=1"
            params = []
            
            if source:
                query += " AND source = ?"
                params.append(source.value)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            async with self.db_manager.get_connection() as conn:
                rows = conn.execute(query, params).fetchall()
                
                logs = []
                for row in rows:
                    try:
                        raw_data = json.loads(row['raw_data'])
                        normalized_data_dict = json.loads(row['normalized_data'])
                        
                        # Convert timestamp strings back to datetime
                        if isinstance(normalized_data_dict['timestamp'], str):
                            normalized_data_dict['timestamp'] = datetime.fromisoformat(normalized_data_dict['timestamp'])
                        
                        normalized_data = NormalizedLogEntry(**normalized_data_dict)
                        
                        log = CloudLog(
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            source=LogSource(row['source']),
                            raw_data=raw_data,
                            normalized_data=normalized_data
                        )
                        
                        # Validate integrity
                        if self.db_manager._validate_data_integrity(row['checksum'], log.model_dump()):
                            logs.append(log)
                        else:
                            logger.warning(f"Skipping log with integrity check failure")
                            
                    except Exception as e:
                        logger.warning(f"Failed to deserialize log: {str(e)}")
                        continue
                
                self._record_operation('get_cloud_logs', True)
                return logs
                
        except Exception as e:
            self._record_operation('get_cloud_logs', False)
            logger.error(f"Failed to get cloud logs: {str(e)}")
            raise DataAccessError(f"Failed to get cloud logs: {str(e)}")
    
    # ML Findings Operations
    async def store_ml_finding(self, anomaly: AnomalyResult, explanation: Explanation) -> None:
        """Store ML finding/anomaly with explanation"""
        try:
            # Validate anomaly
            validation_errors = self.validator.validate_anomaly_result(anomaly)
            if validation_errors:
                raise DataAccessError(f"Anomaly validation failed: {', '.join(validation_errors)}")
            
            async with self.db_manager.get_connection() as conn:
                # Serialize complex data
                affected_resources_json = json.dumps(anomaly.affected_resources)
                patterns_json = json.dumps([p.model_dump() for p in anomaly.patterns])
                explanation_json = json.dumps(explanation.model_dump())
                
                checksum = self.db_manager._calculate_checksum({
                    'id': anomaly.id,
                    'type': anomaly.type.value,
                    'severity': anomaly.severity,
                    'confidence': anomaly.confidence
                })
                
                conn.execute("""
                    INSERT INTO ml_findings 
                    (id, anomaly_type, severity, confidence, affected_resources, 
                     time_window_start, time_window_end, patterns, explanation, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    anomaly.id, anomaly.type.value, anomaly.severity, anomaly.confidence,
                    affected_resources_json, anomaly.time_window.start, anomaly.time_window.end,
                    patterns_json, explanation_json, checksum
                ))
                
                conn.commit()
            
            self._record_operation('store_ml_finding', True)
            logger.info(f"Stored ML finding: {anomaly.id}")
            
        except Exception as e:
            self._record_operation('store_ml_finding', False)
            logger.error(f"Failed to store ML finding {anomaly.id}: {str(e)}")
            raise DataAccessError(f"Failed to store ML finding: {str(e)}")
    
    async def get_ml_findings(self, 
                            anomaly_type: Optional[AnomalyType] = None,
                            processed: Optional[bool] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get ML findings with filtering"""
        try:
            query = "SELECT * FROM ml_findings WHERE 1=1"
            params = []
            
            if anomaly_type:
                query += " AND anomaly_type = ?"
                params.append(anomaly_type.value)
            
            if processed is not None:
                query += " AND processed = ?"
                params.append(processed)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            async with self.db_manager.get_connection() as conn:
                rows = conn.execute(query, params).fetchall()
                
                findings = []
                for row in rows:
                    try:
                        finding = {
                            'id': row['id'],
                            'anomaly_type': AnomalyType(row['anomaly_type']),
                            'severity': row['severity'],
                            'confidence': row['confidence'],
                            'affected_resources': json.loads(row['affected_resources']),
                            'time_window': TimeRange(
                                start=datetime.fromisoformat(row['time_window_start']),
                                end=datetime.fromisoformat(row['time_window_end'])
                            ),
                            'patterns': [AnomalyPattern(**p) for p in json.loads(row['patterns'])],
                            'explanation': Explanation(**json.loads(row['explanation'])),
                            'created_at': datetime.fromisoformat(row['created_at']),
                            'processed': bool(row['processed'])
                        }
                        findings.append(finding)
                        
                    except Exception as e:
                        logger.warning(f"Failed to deserialize ML finding: {str(e)}")
                        continue
                
                self._record_operation('get_ml_findings', True)
                return findings
                
        except Exception as e:
            self._record_operation('get_ml_findings', False)
            logger.error(f"Failed to get ML findings: {str(e)}")
            raise DataAccessError(f"Failed to get ML findings: {str(e)}")
    
    # Backup and Recovery Operations
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create database backup"""
        try:
            backup_path = await self.db_manager.create_backup(backup_name)
            self._record_operation('create_backup', True)
            return backup_path
            
        except Exception as e:
            self._record_operation('create_backup', False)
            logger.error(f"Failed to create backup: {str(e)}")
            raise DataAccessError(f"Failed to create backup: {str(e)}")
    
    async def restore_backup(self, backup_path: str) -> None:
        """Restore database from backup"""
        try:
            await self.db_manager.restore_backup(backup_path)
            self._record_operation('restore_backup', True)
            
        except Exception as e:
            self._record_operation('restore_backup', False)
            logger.error(f"Failed to restore backup: {str(e)}")
            raise DataAccessError(f"Failed to restore backup: {str(e)}")
    
    async def cleanup_old_backups(self, keep_days: int = 30) -> None:
        """Clean up old backup files"""
        try:
            await self.db_manager.cleanup_old_backups(keep_days)
            self._record_operation('cleanup_old_backups', True)
            
        except Exception as e:
            self._record_operation('cleanup_old_backups', False)
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            # Don't raise error for cleanup failures
    
    # System Health and Monitoring
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information"""
        try:
            health = {}
            
            # Database statistics
            db_stats = await self.db_manager.get_database_stats()
            health['database'] = db_stats
            
            # Operation statistics
            health['operations'] = self._operation_counts.copy()
            health['error_counts'] = self._error_counts.copy()
            
            # Calculate error rates
            error_rates = {}
            for operation, counts in self._operation_counts.items():
                total = counts['success'] + counts['error']
                if total > 0:
                    error_rates[operation] = counts['error'] / total
            health['error_rates'] = error_rates
            
            # System status
            health['status'] = 'healthy' if all(rate < 0.1 for rate in error_rates.values()) else 'degraded'
            health['timestamp'] = datetime.now().isoformat()
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def reset_statistics(self) -> None:
        """Reset operation statistics"""
        self._operation_counts.clear()
        self._error_counts.clear()
        logger.info("Operation statistics reset")