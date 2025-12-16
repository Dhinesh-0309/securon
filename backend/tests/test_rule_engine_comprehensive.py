"""Comprehensive tests for Rule Engine component covering all requirements"""

import pytest
import asyncio
import tempfile
import os
from datetime import datetime

from src.securon.rule_engine import ConcreteRuleEngine, RuleEngineError, create_test_rule_engine
from src.securon.interfaces.iac_scanner import SecurityRule
from src.securon.interfaces.core_types import Severity, RuleSource, RuleStatus


class TestRuleEngineRequirements:
    """Test Rule Engine against specific requirements"""
    
    @pytest.fixture
    def rule_engine(self):
        """Create a test rule engine instance"""
        return create_test_rule_engine()
    
    @pytest.fixture
    def ml_generated_rule(self):
        """Create an ML-generated candidate rule"""
        return SecurityRule(
            id="ml-rule-001",
            name="ML Detected Anomaly Rule",
            description="Rule generated from ML anomaly detection for suspicious API calls",
            severity=Severity.HIGH,
            pattern=r"aws_iam_policy.*\"Effect\":\s*\"Allow\".*\"Action\":\s*\"\*\"",
            remediation="Restrict IAM policy actions to specific services and operations",
            source=RuleSource.ML_GENERATED,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_requirement_5_1_generate_candidate_rules(self, rule_engine, ml_generated_rule):
        """Test Requirement 5.1: Generate candidate Security_Rules based on ML findings"""
        # Add ML-generated candidate rule
        await rule_engine.add_rule(ml_generated_rule)
        
        # Verify rule is in candidate status
        candidate_rules = await rule_engine.get_candidate_rules()
        assert len(candidate_rules) == 1
        assert candidate_rules[0].id == ml_generated_rule.id
        assert candidate_rules[0].source == RuleSource.ML_GENERATED
        assert candidate_rules[0].status == RuleStatus.CANDIDATE
    
    @pytest.mark.asyncio
    async def test_requirement_5_2_provide_clear_descriptions(self, rule_engine, ml_generated_rule):
        """Test Requirement 5.2: Provide clear descriptions of what each rule will enforce"""
        await rule_engine.add_rule(ml_generated_rule)
        
        retrieved_rule = await rule_engine.get_rule_by_id(ml_generated_rule.id)
        assert retrieved_rule is not None
        assert len(retrieved_rule.description) >= 10  # Meaningful description
        assert len(retrieved_rule.remediation) >= 10  # Clear remediation steps
        assert retrieved_rule.pattern is not None  # Clear enforcement pattern
    
    @pytest.mark.asyncio
    async def test_requirement_5_3_approve_candidate_rule(self, rule_engine, ml_generated_rule):
        """Test Requirement 5.3: Approve candidate rule and add to Rule_Engine"""
        # Add candidate rule
        await rule_engine.add_rule(ml_generated_rule)
        
        # Approve the rule
        await rule_engine.approve_candidate_rule(ml_generated_rule.id)
        
        # Verify rule is now active
        active_rules = await rule_engine.get_active_rules()
        assert len(active_rules) == 1
        assert active_rules[0].id == ml_generated_rule.id
        assert active_rules[0].status == RuleStatus.ACTIVE
        
        # Verify rule is no longer in candidates
        candidate_rules = await rule_engine.get_candidate_rules()
        assert len(candidate_rules) == 0
    
    @pytest.mark.asyncio
    async def test_requirement_5_4_reject_candidate_rule(self, rule_engine, ml_generated_rule):
        """Test Requirement 5.4: Reject candidate rule and maintain current Rule_Engine state"""
        # Add candidate rule
        await rule_engine.add_rule(ml_generated_rule)
        
        # Get initial state
        initial_active_rules = await rule_engine.get_active_rules()
        initial_active_count = len(initial_active_rules)
        
        # Reject the rule
        await rule_engine.reject_candidate_rule(ml_generated_rule.id)
        
        # Verify rule is now rejected
        rejected_rules = await rule_engine.get_rejected_rules()
        assert len(rejected_rules) == 1
        assert rejected_rules[0].id == ml_generated_rule.id
        assert rejected_rules[0].status == RuleStatus.REJECTED
        
        # Verify active rules unchanged
        current_active_rules = await rule_engine.get_active_rules()
        assert len(current_active_rules) == initial_active_count
    
    @pytest.mark.asyncio
    async def test_requirement_5_5_maintain_reviewable_state(self, rule_engine, ml_generated_rule):
        """Test Requirement 5.5: Maintain candidate rules in reviewable state"""
        # Add candidate rule
        await rule_engine.add_rule(ml_generated_rule)
        
        # Verify rule remains in candidate state until action is taken
        candidate_rules = await rule_engine.get_candidate_rules()
        assert len(candidate_rules) == 1
        
        # Rule should be retrievable and reviewable
        rule = await rule_engine.get_rule_by_id(ml_generated_rule.id)
        assert rule is not None
        assert rule.status == RuleStatus.CANDIDATE
        
        # All rule information should be accessible for review
        assert rule.name is not None
        assert rule.description is not None
        assert rule.severity is not None
        assert rule.pattern is not None
        assert rule.remediation is not None
    
    @pytest.mark.asyncio
    async def test_requirement_6_5_immediate_rule_availability(self, rule_engine, ml_generated_rule):
        """Test Requirement 6.5: New rules immediately included in subsequent scans"""
        # Add and approve rule
        await rule_engine.add_rule(ml_generated_rule)
        await rule_engine.approve_candidate_rule(ml_generated_rule.id)
        
        # Verify rule is immediately available for enforcement
        active_rules = await rule_engine.get_active_rules()
        rule_ids = [rule.id for rule in active_rules]
        assert ml_generated_rule.id in rule_ids
        
        # Add another rule and verify it's also immediately available
        second_rule = SecurityRule(
            id="immediate-rule-002",
            name="Immediate Availability Test",
            description="Testing immediate rule availability after approval",
            severity=Severity.MEDIUM,
            pattern=r"test_pattern",
            remediation="Test remediation",
            source=RuleSource.STATIC,
            status=RuleStatus.CANDIDATE,
            created_at=datetime.now()
        )
        
        await rule_engine.add_rule(second_rule)
        await rule_engine.approve_candidate_rule(second_rule.id)
        
        # Both rules should be immediately available
        updated_active_rules = await rule_engine.get_active_rules()
        updated_rule_ids = [rule.id for rule in updated_active_rules]
        assert ml_generated_rule.id in updated_rule_ids
        assert second_rule.id in updated_rule_ids
        assert len(updated_active_rules) == 2
    
    @pytest.mark.asyncio
    async def test_rule_versioning_and_conflict_resolution(self, rule_engine):
        """Test rule versioning and conflict resolution capabilities"""
        # Create initial rule
        original_rule = SecurityRule(
            id="versioned-rule-001",
            name="Versioned Security Rule",
            description="Original version of the rule",
            severity=Severity.HIGH,
            pattern=r"original_pattern",
            remediation="Original remediation",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await rule_engine.add_rule(original_rule)
        
        # Update the rule (should create new version)
        updated_rule = SecurityRule(
            id="versioned-rule-001",  # Same ID
            name="Versioned Security Rule",
            description="Updated version of the rule with better detection",
            severity=Severity.CRITICAL,  # Changed severity
            pattern=r"updated_pattern",  # Changed pattern
            remediation="Updated remediation with more details",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        await rule_engine.add_rule(updated_rule)
        
        # Verify the rule was updated
        current_rule = await rule_engine.get_rule_by_id("versioned-rule-001")
        assert current_rule is not None
        assert current_rule.severity == Severity.CRITICAL
        assert current_rule.pattern == r"updated_pattern"
    
    @pytest.mark.asyncio
    async def test_rule_validation_comprehensive(self, rule_engine):
        """Test comprehensive rule validation"""
        # Test various invalid rule scenarios
        invalid_rules = [
            # Empty ID
            SecurityRule(
                id="",
                name="Valid Name",
                description="Valid description that is long enough",
                severity=Severity.HIGH,
                pattern=r"valid_pattern",
                remediation="Valid remediation that is long enough",
                source=RuleSource.STATIC,
                status=RuleStatus.CANDIDATE,
                created_at=datetime.now()
            ),
            # Short name
            SecurityRule(
                id="valid-id",
                name="AB",  # Too short
                description="Valid description that is long enough",
                severity=Severity.HIGH,
                pattern=r"valid_pattern",
                remediation="Valid remediation that is long enough",
                source=RuleSource.STATIC,
                status=RuleStatus.CANDIDATE,
                created_at=datetime.now()
            ),
            # Invalid regex pattern
            SecurityRule(
                id="valid-id-2",
                name="Valid Name",
                description="Valid description that is long enough",
                severity=Severity.HIGH,
                pattern="[invalid regex",  # Invalid regex
                remediation="Valid remediation that is long enough",
                source=RuleSource.STATIC,
                status=RuleStatus.CANDIDATE,
                created_at=datetime.now()
            )
        ]
        
        # All invalid rules should be rejected
        for invalid_rule in invalid_rules:
            with pytest.raises(RuleEngineError):
                await rule_engine.add_rule(invalid_rule)


if __name__ == "__main__":
    pytest.main([__file__])