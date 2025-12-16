"""Tests for log processing functionality"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from securon.interfaces.core_types import LogSource, CloudLog
from securon.log_processor.normalizer import LogNormalizer
from securon.log_processor.validator import LogValidator, ValidationError
from securon.log_processor.batch_processor import BatchProcessor


class TestLogNormalizer:
    """Test log normalization functionality"""
    
    def setup_method(self):
        self.normalizer = LogNormalizer()
    
    def test_normalize_vpc_flow_log_structured(self):
        """Test VPC Flow Log normalization with structured format"""
        raw_logs = [{
            'srcaddr': '192.168.1.1',
            'dstaddr': '10.0.0.1',
            'dstport': 80,
            'protocol': '6',
            'action': 'ACCEPT',
            'timestamp': '2023-01-01T12:00:00Z'
        }]
        
        result = self.normalizer.normalize_logs(raw_logs, LogSource.VPC_FLOW)
        
        assert len(result) == 1
        log = result[0]
        assert log.source == LogSource.VPC_FLOW
        assert log.normalized_data.source_ip == '192.168.1.1'
        assert log.normalized_data.destination_ip == '10.0.0.1'
        assert log.normalized_data.port == 80
        assert log.normalized_data.protocol == 'TCP'
        assert log.normalized_data.action == 'ACCEPT'
    
    def test_normalize_vpc_flow_log_message_format(self):
        """Test VPC Flow Log normalization with message format"""
        raw_logs = [{
            'message': '2 123456789012 eni-1235b8ca 192.168.1.1 10.0.0.1 49152 80 6 20 4249 1418530010 1418530070 ACCEPT OK'
        }]
        
        result = self.normalizer.normalize_logs(raw_logs, LogSource.VPC_FLOW)
        
        assert len(result) == 1
        log = result[0]
        assert log.normalized_data.source_ip == '192.168.1.1'
        assert log.normalized_data.destination_ip == '10.0.0.1'
        assert log.normalized_data.port == 80
        assert log.normalized_data.protocol == 'TCP'
        assert log.normalized_data.action == 'ACCEPT'
    
    def test_normalize_cloudtrail_log(self):
        """Test CloudTrail log normalization"""
        raw_logs = [{
            'eventTime': '2023-01-01T12:00:00Z',
            'eventName': 'CreateUser',
            'sourceIPAddress': '203.0.113.1',
            'userIdentity': {
                'type': 'IAMUser',
                'userName': 'testuser'
            },
            'resources': [{
                'ARN': 'arn:aws:iam::123456789012:user/testuser'
            }]
        }]
        
        result = self.normalizer.normalize_logs(raw_logs, LogSource.CLOUDTRAIL)
        
        assert len(result) == 1
        log = result[0]
        assert log.source == LogSource.CLOUDTRAIL
        assert log.normalized_data.source_ip == '203.0.113.1'
        assert log.normalized_data.action == 'CreateUser'
        assert log.normalized_data.user == 'testuser'
        assert log.normalized_data.api_call == 'CreateUser'
    
    def test_normalize_iam_log(self):
        """Test IAM log normalization"""
        raw_logs = [{
            'timestamp': '2023-01-01T12:00:00Z',
            'eventName': 'AssumeRole',
            'sourceIPAddress': '192.168.1.100',
            'userName': 'service-account',
            'resource': 'arn:aws:iam::123456789012:role/ServiceRole'
        }]
        
        result = self.normalizer.normalize_logs(raw_logs, LogSource.IAM)
        
        assert len(result) == 1
        log = result[0]
        assert log.source == LogSource.IAM
        assert log.normalized_data.source_ip == '192.168.1.100'
        assert log.normalized_data.action == 'AssumeRole'
        assert log.normalized_data.user == 'service-account'
        assert log.normalized_data.resource == 'arn:aws:iam::123456789012:role/ServiceRole'
    
    def test_protocol_number_conversion(self):
        """Test protocol number to name conversion"""
        assert self.normalizer._protocol_number_to_name('6') == 'TCP'
        assert self.normalizer._protocol_number_to_name('17') == 'UDP'
        assert self.normalizer._protocol_number_to_name('1') == 'ICMP'
        assert self.normalizer._protocol_number_to_name('-') is None
        assert self.normalizer._protocol_number_to_name(None) is None
    
    def test_timestamp_parsing(self):
        """Test various timestamp format parsing"""
        # ISO format
        ts1 = self.normalizer._parse_timestamp('2023-01-01T12:00:00Z')
        assert isinstance(ts1, datetime)
        
        # Unix timestamp
        ts2 = self.normalizer._parse_timestamp(1672574400)
        assert isinstance(ts2, datetime)
        
        # Already datetime
        now = datetime.now()
        ts3 = self.normalizer._parse_timestamp(now)
        assert ts3 == now


class TestLogValidator:
    """Test log validation functionality"""
    
    def setup_method(self):
        self.validator = LogValidator()
    
    def test_validate_vpc_flow_log_valid(self):
        """Test validation of valid VPC Flow Log"""
        valid_log = {
            'srcaddr': '192.168.1.1',
            'action': 'ACCEPT',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        # Should not raise exception
        self.validator._validate_vpc_flow_log(valid_log)
    
    def test_validate_vpc_flow_log_invalid(self):
        """Test validation of invalid VPC Flow Log"""
        invalid_log = {}  # Missing required fields
        
        with pytest.raises(ValidationError):
            self.validator._validate_vpc_flow_log(invalid_log)
    
    def test_validate_cloudtrail_log_valid(self):
        """Test validation of valid CloudTrail log"""
        valid_log = {
            'eventName': 'CreateUser',
            'eventTime': '2023-01-01T12:00:00Z'
        }
        
        # Should not raise exception
        self.validator._validate_cloudtrail_log(valid_log)
    
    def test_validate_cloudtrail_log_invalid(self):
        """Test validation of invalid CloudTrail log"""
        invalid_log = {}  # Missing required fields
        
        with pytest.raises(ValidationError):
            self.validator._validate_cloudtrail_log(invalid_log)
    
    def test_validate_iam_log_valid(self):
        """Test validation of valid IAM log"""
        valid_log = {
            'eventName': 'AssumeRole',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        # Should not raise exception
        self.validator._validate_iam_log(valid_log)
    
    def test_validate_iam_log_invalid(self):
        """Test validation of invalid IAM log"""
        invalid_log = {}  # Missing required fields
        
        with pytest.raises(ValidationError):
            self.validator._validate_iam_log(invalid_log)
    
    def test_ip_validation(self):
        """Test IP address validation"""
        assert self.validator._is_valid_ip('192.168.1.1') == True
        assert self.validator._is_valid_ip('10.0.0.1') == True
        assert self.validator._is_valid_ip('256.1.1.1') == False
        assert self.validator._is_valid_ip('invalid') == False
        assert self.validator._is_valid_ip('') == False
        assert self.validator._is_valid_ip('-') == False
    
    def test_validation_summary(self):
        """Test validation summary generation"""
        errors = ['Error 1', 'Error 2']
        summary = self.validator.get_validation_summary(100, 98, errors)
        
        assert summary['total_logs'] == 100
        assert summary['valid_logs'] == 98
        assert summary['invalid_logs'] == 2
        assert summary['success_rate'] == 98.0
        assert summary['error_count'] == 2


class TestBatchProcessor:
    """Test batch processing functionality"""
    
    def setup_method(self):
        self.processor = BatchProcessor(batch_size=2)  # Small batch for testing
    
    @pytest.mark.asyncio
    async def test_process_logs_from_data(self):
        """Test processing logs from in-memory data"""
        logs = [
            {
                'srcaddr': '192.168.1.1',
                'dstaddr': '10.0.0.1',
                'action': 'ACCEPT',
                'timestamp': '2023-01-01T12:00:00Z'
            },
            {
                'srcaddr': '192.168.1.2',
                'dstaddr': '10.0.0.2',
                'action': 'REJECT',
                'timestamp': '2023-01-01T12:01:00Z'
            }
        ]
        
        processed_batches = []
        async for batch in self.processor.process_logs_from_data(logs, LogSource.VPC_FLOW):
            processed_batches.append(batch)
        
        assert len(processed_batches) == 1  # Should fit in one batch
        assert len(processed_batches[0]) == 2
        assert all(isinstance(log, CloudLog) for log in processed_batches[0])
    
    @pytest.mark.asyncio
    async def test_process_all_logs(self):
        """Test processing all logs at once"""
        logs = [
            {
                'eventName': 'CreateUser',
                'eventTime': '2023-01-01T12:00:00Z',
                'sourceIPAddress': '203.0.113.1'
            }
        ]
        
        result = await self.processor.process_all_logs(logs, LogSource.CLOUDTRAIL)
        
        assert len(result) == 1
        assert isinstance(result[0], CloudLog)
        assert result[0].source == LogSource.CLOUDTRAIL
    
    def test_processing_stats(self):
        """Test processing statistics"""
        stats = self.processor.get_processing_stats()
        
        assert 'batch_size' in stats
        assert 'max_workers' in stats
        assert stats['batch_size'] == 2