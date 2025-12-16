"""Tests for data persistence and storage functionality"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from src.securon.platform.database import DatabaseManager, DatabaseError
from src.securon.platform.data_access import SecuronDataAccess, DataAccessError
from src.securon.platform.backup_service import BackupService
from src.securon.platform.integrity_service import DataIntegrityService
from src.securon.interfaces.iac_scanner import SecurityRule
from src.securon.interfaces.core_types import (
    Severity, RuleSource, RuleStatus, LogSource, AnomalyType,
    CloudLog, NormalizedLogEntry, TimeRange
)


class TestDatabaseManager:
    """Test database management functionality"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_securon.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Create database manager instance"""
        return DatabaseManager(temp_db_path, backup_enabled=False)
    
    def test_database_initialization(self, db_manager):
        """Test database initialization creates all tables"""
        # Database should be initialized without errors
        assert db_manager.db_path.exists()
        
        # Check that database file has content (SQLite files are binary)
        assert db_manager.db_path.stat().st_size > 0
    
    @pytest.mark.asyncio
    async def test_security_rule_storage(self, db_manager):
        """Test storing and retrieving security rules"""
        # Create test rule
        rule = SecurityRule(
            id="test-rule-1",
            name="Test Rule",
            description="This is a test security rule for validation",
            severity=Severity.HIGH,
            pattern="test-pattern-.*",
            remediation="Fix the test issue by following these steps",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        # Store rule
        await db_manager.store_security_rule(rule)
        
        # Retrieve rule
        retrieved_rule = await db_manager.get_security_rule("test-rule-1")
        
        assert retrieved_rule is not None
        assert retrieved_rule.id == rule.id
        assert retrieved_rule.name == rule.name
        assert retrieved_rule.severity == rule.severity
        assert retrieved_rule.status == rule.status
    
    @pytest.mark.asyncio
    async def test_rule_versioning(self, db_manager):
        """Test rule versioning functionality"""
        # Create initial rule
        rule = SecurityRule(
            id="versioned-rule",
            name="Versioned Rule",
            description="This rule will be updated to test versioning",
            severity=Severity.MEDIUM,
            pattern="initial-pattern",
            remediation="Initial remediation steps",
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
        
        # Store initial version
        await db_manager.store_security_rule(rule)
        
        # Update rule
        rule.description = "Updated description for version testing"
        rule.pattern = "updated-pattern"
        rule.status = RuleStatus.ACTIVE
        
        # Store updated version
        await db_manager.store_security_rule(rule)
        
        # Verify updated rule
        retrieved_rule = await db_manager.get_security_rule("versioned-rule")
        assert retrieved_rule.description == "Updated description for version testing"
        assert retrieved_rule.pattern == "updated-pattern"
        assert retrieved_rule.status == RuleStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_rules_by_status(self, db_manager):
        """Test filtering rules by status"""
        # Create rules with different statuses
        rules = [
            SecurityRule(
                id=f"rule-{i}",
                name=f"Rule {i}",
                description=f"Test rule {i} with specific status",
                severity=Severity.LOW,
                pattern=f"pattern-{i}",
                remediation=f"Remediation for rule {i}",
                source=RuleSource.STATIC,
                status=status,
                created_at=datetime.now()
            )
            for i, status in enumerate([RuleStatus.ACTIVE, RuleStatus.CANDIDATE, RuleStatus.REJECTED])
        ]
        
        # Store all rules
        for rule in rules:
            await db_manager.store_security_rule(rule)
        
        # Test filtering
        active_rules = await db_manager.get_rules_by_status(RuleStatus.ACTIVE)
        candidate_rules = await db_manager.get_rules_by_status(RuleStatus.CANDIDATE)
        rejected_rules = await db_manager.get_rules_by_status(RuleStatus.REJECTED)
        
        assert len(active_rules) == 1
        assert len(candidate_rules) == 1
        assert len(rejected_rules) == 1
        
        assert active_rules[0].status == RuleStatus.ACTIVE
        assert candidate_rules[0].status == RuleStatus.CANDIDATE
        assert rejected_rules[0].status == RuleStatus.REJECTED
    
    @pytest.mark.asyncio
    async def test_rule_deletion(self, db_manager):
        """Test rule deletion"""
        # Create and store rule
        rule = SecurityRule(
            id="delete-test-rule",
            name="Delete Test Rule",
            description="This rule will be deleted for testing",
            severity=Severity.CRITICAL,
            pattern="delete-test-pattern",
            remediation="This rule should be deleted",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await db_manager.store_security_rule(rule)
        
        # Verify rule exists
        retrieved_rule = await db_manager.get_security_rule("delete-test-rule")
        assert retrieved_rule is not None
        
        # Delete rule
        deleted = await db_manager.delete_security_rule("delete-test-rule")
        assert deleted is True
        
        # Verify rule is gone
        retrieved_rule = await db_manager.get_security_rule("delete-test-rule")
        assert retrieved_rule is None
        
        # Try to delete non-existent rule
        deleted = await db_manager.delete_security_rule("non-existent-rule")
        assert deleted is False


class TestDataAccess:
    """Test data access layer functionality"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_data_access.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def data_access(self, temp_db_path):
        """Create data access instance"""
        return SecuronDataAccess(temp_db_path, backup_enabled=False)
    
    @pytest.mark.asyncio
    async def test_rule_approval_workflow(self, data_access):
        """Test rule approval workflow"""
        # Create candidate rule
        rule = SecurityRule(
            id="approval-test-rule",
            name="Approval Test Rule",
            description="This rule will test the approval workflow",
            severity=Severity.HIGH,
            pattern="approval-test-pattern",
            remediation="Follow approval test remediation",
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
        
        # Store candidate rule
        await data_access.store_security_rule(rule)
        
        # Verify it's in candidate status
        candidate_rules = await data_access.get_candidate_rules()
        assert len(candidate_rules) == 1
        assert candidate_rules[0].id == "approval-test-rule"
        
        # Approve rule
        approved = await data_access.approve_rule("approval-test-rule")
        assert approved is True
        
        # Verify it's now active
        active_rules = await data_access.get_all_active_rules()
        assert len(active_rules) == 1
        assert active_rules[0].id == "approval-test-rule"
        assert active_rules[0].status == RuleStatus.ACTIVE
        
        # Verify it's no longer in candidates
        candidate_rules = await data_access.get_candidate_rules()
        assert len(candidate_rules) == 0
    
    @pytest.mark.asyncio
    async def test_rule_rejection_workflow(self, data_access):
        """Test rule rejection workflow"""
        # Create candidate rule
        rule = SecurityRule(
            id="rejection-test-rule",
            name="Rejection Test Rule",
            description="This rule will test the rejection workflow",
            severity=Severity.MEDIUM,
            pattern="rejection-test-pattern",
            remediation="Follow rejection test remediation",
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
        
        # Store candidate rule
        await data_access.store_security_rule(rule)
        
        # Reject rule
        rejected = await data_access.reject_rule("rejection-test-rule")
        assert rejected is True
        
        # Verify it's now rejected
        retrieved_rule = await data_access.get_security_rule("rejection-test-rule")
        assert retrieved_rule.status == RuleStatus.REJECTED
        
        # Verify it's no longer in candidates
        candidate_rules = await data_access.get_candidate_rules()
        assert len(candidate_rules) == 0
    
    @pytest.mark.asyncio
    async def test_cloud_logs_storage(self, data_access):
        """Test cloud logs storage and retrieval"""
        # Create test logs
        logs = []
        for i in range(5):
            normalized_data = NormalizedLogEntry(
                timestamp=datetime.now() - timedelta(hours=i),
                source_ip=f"192.168.1.{i+1}",
                destination_ip=f"10.0.0.{i+1}",
                port=80 + i,
                protocol="TCP",
                action="ALLOW",
                user=f"user{i}",
                resource=f"resource{i}",
                api_call=f"api_call_{i}"
            )
            
            log = CloudLog(
                timestamp=datetime.now() - timedelta(hours=i),
                source=LogSource.VPC_FLOW,
                raw_data={"test": f"data_{i}", "value": i},
                normalized_data=normalized_data
            )
            logs.append(log)
        
        # Store logs
        await data_access.store_cloud_logs(logs, "test-batch-1")
        
        # Retrieve all logs
        retrieved_logs = await data_access.get_cloud_logs(limit=10)
        assert len(retrieved_logs) == 5
        
        # Test filtering by source
        vpc_logs = await data_access.get_cloud_logs(source=LogSource.VPC_FLOW)
        assert len(vpc_logs) == 5
        
        cloudtrail_logs = await data_access.get_cloud_logs(source=LogSource.CLOUDTRAIL)
        assert len(cloudtrail_logs) == 0
        
        # Test time-based filtering
        recent_logs = await data_access.get_cloud_logs(
            start_time=datetime.now() - timedelta(hours=2)
        )
        assert len(recent_logs) >= 2  # Should include logs from last 2 hours
    
    @pytest.mark.asyncio
    async def test_data_validation(self, data_access):
        """Test data validation functionality"""
        # Test invalid rule
        invalid_rule = SecurityRule(
            id="x",  # Too short
            name="",  # Empty
            description="short",  # Too short
            severity=Severity.HIGH,
            pattern="",  # Empty
            remediation="short",  # Too short
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        # Should raise validation error
        with pytest.raises(DataAccessError):
            await data_access.store_security_rule(invalid_rule)
    
    @pytest.mark.asyncio
    async def test_system_health(self, data_access):
        """Test system health monitoring"""
        # Add some test data
        rule = SecurityRule(
            id="health-test-rule",
            name="Health Test Rule",
            description="This rule is for testing system health",
            severity=Severity.LOW,
            pattern="health-test-pattern",
            remediation="Health test remediation steps",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await data_access.store_security_rule(rule)
        
        # Get system health
        health = await data_access.get_system_health()
        
        assert 'database' in health
        assert 'operations' in health
        assert 'status' in health
        assert health['status'] in ['healthy', 'degraded', 'error']


class TestBackupService:
    """Test backup and recovery functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def data_access(self, temp_dir):
        """Create data access with temporary database"""
        db_path = Path(temp_dir) / "backup_test.db"
        return SecuronDataAccess(str(db_path), backup_enabled=False)
    
    @pytest.fixture
    def backup_service(self, temp_dir):
        """Create backup service"""
        # Create data access with backup enabled
        db_path = Path(temp_dir) / "backup_test.db"
        data_access = SecuronDataAccess(str(db_path), backup_enabled=True)
        
        # Mock config
        class MockConfig:
            def get(self, key, default=None):
                config_map = {
                    'rule_engine.backup_enabled': True,
                    'rule_engine.backup_interval_hours': 1,
                    'rule_engine.backup_retention_days': 7,
                    'rule_engine.max_backups': 10,
                    'rule_engine.backup_path': str(Path(temp_dir) / 'backups')
                }
                return config_map.get(key, default)
        
        return BackupService(data_access, MockConfig())
    
    @pytest.mark.asyncio
    async def test_database_backup_creation(self, backup_service):
        """Test database backup creation"""
        # Add some test data
        rule = SecurityRule(
            id="backup-test-rule",
            name="Backup Test Rule",
            description="This rule is for testing backup functionality",
            severity=Severity.MEDIUM,
            pattern="backup-test-pattern",
            remediation="Backup test remediation steps",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await backup_service.data_access.store_security_rule(rule)
        
        # Create backup
        backup_info = await backup_service.create_database_backup()
        
        assert backup_info.name.endswith('.db')
        assert Path(backup_info.path).exists()
        assert backup_info.size_bytes > 0
        assert backup_info.backup_type == 'database'
    
    @pytest.mark.asyncio
    async def test_full_backup_creation(self, backup_service):
        """Test full backup creation"""
        # Add test data
        rule = SecurityRule(
            id="full-backup-test-rule",
            name="Full Backup Test Rule",
            description="This rule is for testing full backup functionality",
            severity=Severity.HIGH,
            pattern="full-backup-test-pattern",
            remediation="Full backup test remediation steps",
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
        
        await backup_service.data_access.store_security_rule(rule)
        
        # Create full backup
        backups = await backup_service.create_full_backup(
            backup_type='test',
            description='Test full backup'
        )
        
        assert 'database' in backups
        assert 'configuration' in backups
        
        # Verify backup files exist
        for backup_info in backups.values():
            assert Path(backup_info.path).exists()
            assert backup_info.size_bytes > 0
    
    @pytest.mark.asyncio
    async def test_backup_listing(self, backup_service):
        """Test backup listing functionality"""
        # Create a few backups
        await backup_service.create_database_backup("test_backup_1.db")
        await backup_service.create_database_backup("test_backup_2.db")
        
        # List backups
        backups = await backup_service.list_backups()
        
        assert len(backups) >= 2
        
        # Test filtering by type
        db_backups = await backup_service.list_backups(backup_type='database')
        assert len(db_backups) >= 2
        
        config_backups = await backup_service.list_backups(backup_type='configuration')
        # May be 0 if no config backups were created in this test
    
    @pytest.mark.asyncio
    async def test_backup_status(self, backup_service):
        """Test backup status reporting"""
        # Create a backup first
        await backup_service.create_database_backup()
        
        # Get status
        status = await backup_service.get_backup_status()
        
        assert status['enabled'] is True
        assert status['total_backups'] >= 1
        assert status['total_size_bytes'] > 0
        assert 'latest_backup' in status
        assert status['latest_backup'] is not None


class TestIntegrityService:
    """Test data integrity service functionality"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "integrity_test.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def data_access(self, temp_db_path):
        """Create data access instance"""
        return SecuronDataAccess(temp_db_path, backup_enabled=False)
    
    @pytest.fixture
    def integrity_service(self, data_access):
        """Create integrity service"""
        return DataIntegrityService(data_access)
    
    @pytest.mark.asyncio
    async def test_security_rules_validation(self, integrity_service, data_access):
        """Test security rules validation"""
        # Add valid rules
        valid_rule = SecurityRule(
            id="valid-integrity-rule",
            name="Valid Integrity Rule",
            description="This is a valid rule for integrity testing",
            severity=Severity.MEDIUM,
            pattern="valid-pattern-.*",
            remediation="Follow these valid remediation steps",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await data_access.store_security_rule(valid_rule)
        
        # Validate rules
        validation_result = await integrity_service.validate_security_rules()
        
        assert validation_result.valid is True
        assert len(validation_result.errors) == 0
        assert validation_result.metadata['total_rules'] >= 1
        assert validation_result.metadata['active_rules'] >= 1
    
    @pytest.mark.asyncio
    async def test_database_integrity_check(self, integrity_service, data_access):
        """Test database integrity checking"""
        # Add some test data
        rule = SecurityRule(
            id="db-integrity-rule",
            name="DB Integrity Rule",
            description="This rule is for testing database integrity",
            severity=Severity.LOW,
            pattern="db-integrity-pattern",
            remediation="Database integrity remediation steps",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await data_access.store_security_rule(rule)
        
        # Check database integrity
        integrity_check = await integrity_service.check_database_integrity()
        
        assert integrity_check.component == "database"
        assert integrity_check.status in ["passed", "warning", "failed"]
        assert integrity_check.message is not None
        assert integrity_check.checked_at is not None
    
    @pytest.mark.asyncio
    async def test_comprehensive_integrity_check(self, integrity_service):
        """Test comprehensive integrity checking"""
        # Run all integrity checks
        checks = await integrity_service.run_comprehensive_integrity_check()
        
        assert 'database' in checks
        assert 'backup' in checks
        assert 'data_consistency' in checks
        
        # All checks should have valid results
        for check_name, check in checks.items():
            assert check.component == check_name
            assert check.status in ["passed", "warning", "failed"]
            assert check.message is not None
    
    @pytest.mark.asyncio
    async def test_integrity_summary(self, integrity_service):
        """Test integrity summary generation"""
        summary = await integrity_service.get_integrity_summary()
        
        assert 'overall_status' in summary
        assert summary['overall_status'] in ['passed', 'warning', 'failed']
        assert 'total_checks' in summary
        assert summary['total_checks'] > 0
        assert 'details' in summary
        assert len(summary['details']) == summary['total_checks']


# Integration test
class TestDataPersistenceIntegration:
    """Integration tests for complete data persistence system"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for integration tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, temp_dir):
        """Test complete data persistence workflow"""
        # Initialize components
        db_path = Path(temp_dir) / "integration_test.db"
        data_access = SecuronDataAccess(str(db_path), backup_enabled=True)
        
        # Mock config for backup service
        class MockConfig:
            def get(self, key, default=None):
                return {
                    'rule_engine.backup_enabled': True,
                    'rule_engine.backup_path': str(Path(temp_dir) / 'backups')
                }.get(key, default)
        
        backup_service = BackupService(data_access, MockConfig())
        integrity_service = DataIntegrityService(data_access)
        
        # 1. Create and store rules
        rules = []
        for i in range(3):
            rule = SecurityRule(
                id=f"integration-rule-{i}",
                name=f"Integration Rule {i}",
                description=f"This is integration test rule number {i}",
                severity=[Severity.LOW, Severity.MEDIUM, Severity.HIGH][i],
                pattern=f"integration-pattern-{i}",
                remediation=f"Integration remediation steps for rule {i}",
                source=RuleSource.STATIC,
                status=[RuleStatus.ACTIVE, RuleStatus.CANDIDATE, RuleStatus.REJECTED][i],
                created_at=datetime.now()
            )
            rules.append(rule)
            await data_access.store_security_rule(rule)
        
        # 2. Test rule operations
        active_rules = await data_access.get_all_active_rules()
        assert len(active_rules) == 1
        
        candidate_rules = await data_access.get_candidate_rules()
        assert len(candidate_rules) == 1
        
        # Approve candidate rule
        approved = await data_access.approve_rule("integration-rule-1")
        assert approved is True
        
        # Verify approval
        active_rules = await data_access.get_all_active_rules()
        assert len(active_rules) == 2
        
        # 3. Create backup
        backup_info = await backup_service.create_database_backup()
        assert Path(backup_info.path).exists()
        
        # Ensure backup directory exists for integrity check
        # The integrity service checks for "data/backups" hardcoded path
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. Run integrity checks
        integrity_summary = await integrity_service.get_integrity_summary()
        assert integrity_summary['overall_status'] in ['passed', 'warning']
        
        # 5. Test system health
        health = await data_access.get_system_health()
        assert health['status'] in ['healthy', 'degraded']
        
        # 6. Cleanup
        backup_service.stop_scheduler()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])