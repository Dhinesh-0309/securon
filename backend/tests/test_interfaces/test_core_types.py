"""Test core types with property-based testing"""

import pytest
from hypothesis import given, strategies as st

from src.securon.interfaces.core_types import CloudLog
from src.securon.interfaces.iac_scanner import SecurityRule
from tests.test_utils.generators import cloud_log_strategy, security_rule_strategy


class TestCoreTypes:
    @given(cloud_log_strategy)
    def test_cloud_log_generation(self, log: CloudLog):
        """Test that generated CloudLog objects are valid"""
        assert log.timestamp is not None
        assert log.source in ["VPC_FLOW", "CLOUDTRAIL", "IAM"]
        assert log.normalized_data.source_ip is not None
        # IP address format validation
        ip_parts = log.normalized_data.source_ip.split(".")
        assert len(ip_parts) == 4
        for part in ip_parts:
            assert 0 <= int(part) <= 255

    @given(security_rule_strategy)
    def test_security_rule_generation(self, rule: SecurityRule):
        """Test that generated SecurityRule objects are valid"""
        assert rule.id is not None
        assert len(rule.name) > 0
        assert rule.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert rule.source in ["STATIC", "ML_GENERATED"]
        assert rule.status in ["ACTIVE", "CANDIDATE", "REJECTED"]
        assert rule.created_at is not None

    @given(st.lists(cloud_log_strategy, min_size=1, max_size=100))
    def test_cloud_log_list_processing(self, logs: list[CloudLog]):
        """Test processing lists of cloud logs"""
        assert len(logs) > 0
        for log in logs:
            assert isinstance(log, CloudLog)
            assert log.source in ["VPC_FLOW", "CLOUDTRAIL", "IAM"]