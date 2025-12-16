"""Tests for platform integration"""

import pytest
import tempfile
import os
from pathlib import Path

from src.securon.platform import PlatformOrchestrator, PlatformConfig
from src.securon.platform.orchestrator import ComponentError
from src.securon.interfaces.core_types import CloudLog, LogSource, NormalizedLogEntry
from datetime import datetime


class TestPlatformIntegration:
    """Test platform integration and orchestration"""
    
    @pytest.fixture
    async def platform(self):
        """Create a test platform instance"""
        # Create temporary config
        config = PlatformConfig()
        config.logging.level = "ERROR"  # Reduce log noise in tests
        config.monitoring.enabled = False  # Disable monitoring for tests
        
        # Use temporary directory for rule storage
        with tempfile.TemporaryDirectory() as temp_dir:
            config.rule_engine.storage_path = os.path.join(temp_dir, "rules")
            
            platform = PlatformOrchestrator(config)
            await platform.initialize()
            
            yield platform
            
            await platform.shutdown()
    
    @pytest.mark.asyncio
    async def test_platform_initialization(self, platform):
        """Test that platform initializes correctly"""
        assert platform.initialized
        assert platform.running
        
        # Check that all components are available
        assert platform.get_iac_scanner() is not None
        assert platform.get_ml_engine() is not None
        assert platform.get_rule_engine() is not None
        assert platform.get_log_processor() is not None
        assert platform.get_monitor() is not None
    
    @pytest.mark.asyncio
    async def test_platform_status(self, platform):
        """Test platform status reporting"""
        status = await platform.get_platform_status()
        
        assert status['status'] == 'running'
        assert 'components' in status
        assert 'uptime_seconds' in status
        assert status['uptime_seconds'] >= 0
        
        # Check component status
        components = status['components']
        expected_components = ['monitoring', 'rule_engine', 'ml_engine', 'iac_scanner', 'log_processor']
        
        for component in expected_components:
            assert component in components
            assert components[component]['initialized'] is True
    
    @pytest.mark.asyncio
    async def test_process_logs_workflow(self, platform):
        """Test the complete log processing workflow"""
        # Create test logs
        test_logs = [
            CloudLog(
                timestamp=datetime.now(),
                source=LogSource.VPC_FLOW,
                raw_data={
                    "srcaddr": "192.168.1.100",
                    "dstaddr": "10.0.0.1",
                    "srcport": 12345,
                    "dstport": 22,
                    "protocol": 6,
                    "action": "ACCEPT"
                },
                normalized_data=NormalizedLogEntry(
                    timestamp=datetime.now(),
                    source_ip="192.168.1.100",
                    destination_ip="10.0.0.1",
                    port=22,
                    protocol="TCP",
                    action="ACCEPT"
                )
            )
        ]
        
        # Process logs through workflow
        result = await platform.process_logs_workflow(test_logs)
        
        assert 'logs_processed' in result
        assert 'anomalies_detected' in result
        assert 'candidate_rules_generated' in result
        assert 'anomalies' in result
        
        assert result['logs_processed'] == 1
        assert result['anomalies_detected'] >= 0
        assert result['candidate_rules_generated'] >= 0
    
    @pytest.mark.asyncio
    async def test_scan_iac_workflow(self, platform):
        """Test the IaC scanning workflow"""
        # Create a temporary Terraform file
        terraform_content = '''
resource "aws_s3_bucket" "test" {
  bucket = "test-bucket"
}

resource "aws_security_group" "test" {
  name = "test-sg"
  
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name
        
        try:
            # Scan the file
            results = await platform.scan_iac_workflow(temp_file)
            
            # Should return a list of scan results (may be empty if no rules match)
            assert isinstance(results, list)
            
            # The workflow should complete successfully regardless of findings
            # This tests the integration, not specific security rule detection
            
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_component_restart(self, platform):
        """Test component restart functionality"""
        # Test restarting rule engine
        result = await platform.restart_component('rule_engine')
        assert result is True
        
        # Verify component is still functional
        rule_engine = platform.get_rule_engine()
        rules = await rule_engine.get_active_rules()
        assert isinstance(rules, list)
    
    @pytest.mark.asyncio
    async def test_component_error_handling(self, platform):
        """Test error handling for invalid component operations"""
        # Test invalid component name
        result = await platform.restart_component('invalid_component')
        assert result is False
    
    @pytest.mark.asyncio
    async def test_platform_without_initialization(self):
        """Test platform behavior when not initialized"""
        config = PlatformConfig()
        platform = PlatformOrchestrator(config)
        
        # Should raise ComponentError when accessing components
        with pytest.raises(ComponentError):
            platform.get_iac_scanner()
        
        with pytest.raises(ComponentError):
            platform.get_ml_engine()
        
        with pytest.raises(ComponentError):
            platform.get_rule_engine()
        
        with pytest.raises(ComponentError):
            platform.get_log_processor()
        
        with pytest.raises(ComponentError):
            platform.get_monitor()


class TestPlatformConfig:
    """Test platform configuration management"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = PlatformConfig()
        
        assert config.environment == "development"
        assert config.debug is False
        assert config.api_host == "0.0.0.0"
        assert config.api_port == 8000
        
        # Check nested configs are created
        assert config.database is not None
        assert config.ml_engine is not None
        assert config.rule_engine is not None
        assert config.iac_scanner is not None
        assert config.logging is not None
        assert config.monitoring is not None
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = PlatformConfig()
        
        # Valid config should not raise
        config.validate()
        
        # Invalid ML contamination should raise
        config.ml_engine.contamination = 1.5
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_from_environment(self):
        """Test loading configuration from environment variables"""
        # Set some environment variables
        os.environ['SECURON_ENVIRONMENT'] = 'test'
        os.environ['SECURON_DEBUG'] = 'true'
        os.environ['SECURON_API_PORT'] = '9000'
        
        try:
            config = PlatformConfig.from_environment()
            
            assert config.environment == 'test'
            assert config.debug is True
            assert config.api_port == 9000
            
        finally:
            # Clean up environment variables
            for key in ['SECURON_ENVIRONMENT', 'SECURON_DEBUG', 'SECURON_API_PORT']:
                if key in os.environ:
                    del os.environ[key]
    
    def test_config_file_operations(self):
        """Test saving and loading configuration from file"""
        config = PlatformConfig()
        config.environment = "test"
        config.debug = True
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            # Save config
            config.save_to_file(config_file)
            
            # Load config
            loaded_config = PlatformConfig.from_file(config_file)
            
            assert loaded_config.environment == "test"
            assert loaded_config.debug is True
            
        finally:
            os.unlink(config_file)