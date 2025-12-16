"""Tests for Rule Engine component"""

import pytest
import asyncio
import tempfile
import os
from datetime import datetime

from src.securon.rule_engine import ConcreteRuleEngine, RuleEngineError
from src.securon.interfaces.iac_scanner import SecurityRule
from src.securon.interfaces.core_types import Severity, RuleSource, RuleStatus


@pytest.fixture
def temp_storage_path():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield os.path.join(temp_dir, "test_rules")
    # Cleanup is handled by tempfile


@pytest.fixture
def rule_engine(temp_storage_path):
    """Create a rule engine instance for testing"""
    return ConcreteRuleEngine(storage_path=temp_storage_path)


@pytest.fixture
def sample_rule():
    """Create a sample security rule for testing"""
    return SecurityRule(
        id="test-rule-001",
        name="Test Security Rule",
        description="This is a test security rule for validation",
        severity=Severity.HIGH,
        pattern=r"resource\s+\"aws_s3_bucket\"",
        remediation="Ensure S3 bucket has proper security configuration",
        source=RuleSource.STATIC,
        status=RuleStatus.CANDIDATE,
        created_at=datetime.now()
    )


@pytest.mark.asyncio
async def test_add_rule(rule_engine, sample_rule):
    """Test adding a new rule"""
    await rule_engine.add_rule(sample_rule)
    
    # Verify rule was added
    retrieved_rule = await rule_engine.get_rule_by_id(sample_rule.id)
    assert retrieved_rule is not None
    assert retrieved_rule.id == sample_rule.id
    assert retrieved_rule.name == sample_rule.name


@pytest.mark.asyncio
async def test_approve_candidate_rule(rule_engine, sample_rule):
    """Test approving a candidate rule"""
    # Add rule as candidate
    await rule_engine.add_rule(sample_rule)
    
    # Approve the rule
    await rule_engine.approve_candidate_rule(sample_rule.id)
    
    # Verify rule is now active
    active_rules = await rule_engine.get_active_rules()
    assert len(active_rules) == 1
    assert active_rules[0].id == sample_rule.id
    assert active_rules[0].status == RuleStatus.ACTIVE


@pytest.mark.asyncio
async def test_reject_candidate_rule(rule_engine, sample_rule):
    """Test rejecting a candidate rule"""
    # Add rule as candidate
    await rule_engine.add_rule(sample_rule)
    
    # Reject the rule
    await rule_engine.reject_candidate_rule(sample_rule.id)
    
    # Verify rule is now rejected
    rejected_rules = await rule_engine.get_rejected_rules()
    assert len(rejected_rules) == 1
    assert rejected_rules[0].id == sample_rule.id
    assert rejected_rules[0].status == RuleStatus.REJECTED


@pytest.mark.asyncio
async def test_remove_rule(rule_engine, sample_rule):
    """Test removing a rule"""
    # Add rule
    await rule_engine.add_rule(sample_rule)
    
    # Verify rule exists
    retrieved_rule = await rule_engine.get_rule_by_id(sample_rule.id)
    assert retrieved_rule is not None
    
    # Remove rule
    await rule_engine.remove_rule(sample_rule.id)
    
    # Verify rule is gone
    retrieved_rule = await rule_engine.get_rule_by_id(sample_rule.id)
    assert retrieved_rule is None


@pytest.mark.asyncio
async def test_invalid_rule_validation(rule_engine):
    """Test that invalid rules are rejected"""
    invalid_rule = SecurityRule(
        id="",  # Invalid empty ID
        name="",  # Invalid empty name
        description="",  # Invalid empty description
        severity=Severity.HIGH,
        pattern="[invalid regex",  # Invalid regex pattern
        remediation="",  # Invalid empty remediation
        source=RuleSource.STATIC,
        status=RuleStatus.CANDIDATE,
        created_at=datetime.now()
    )
    
    with pytest.raises(RuleEngineError):
        await rule_engine.add_rule(invalid_rule)


@pytest.mark.asyncio
async def test_get_candidate_rules(rule_engine, sample_rule):
    """Test getting candidate rules"""
    # Add rule as candidate
    await rule_engine.add_rule(sample_rule)
    
    # Get candidate rules
    candidate_rules = await rule_engine.get_candidate_rules()
    assert len(candidate_rules) == 1
    assert candidate_rules[0].id == sample_rule.id
    assert candidate_rules[0].status == RuleStatus.CANDIDATE


if __name__ == "__main__":
    pytest.main([__file__])