"""Demo script showing Rule Engine functionality"""

import asyncio
from datetime import datetime
import tempfile
import os

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from securon.rule_engine import ConcreteRuleEngine
from securon.interfaces.iac_scanner import SecurityRule
from securon.interfaces.core_types import Severity, RuleSource, RuleStatus


async def demo_rule_engine():
    """Demonstrate Rule Engine capabilities"""
    
    # Create a temporary rule engine for demo
    temp_dir = tempfile.mkdtemp()
    storage_path = os.path.join(temp_dir, "demo_rules")
    rule_engine = ConcreteRuleEngine(storage_path=storage_path)
    
    print("=== Securon Rule Engine Demo ===\n")
    
    # Create sample rules
    rule1 = SecurityRule(
        id="s3-public-read",
        name="S3 Bucket Public Read Access",
        description="Detects S3 buckets with public read access which may expose sensitive data",
        severity=Severity.HIGH,
        pattern=r'resource\s+"aws_s3_bucket_acl".*"public-read"',
        remediation="Remove public-read ACL and use bucket policies for controlled access",
        source=RuleSource.STATIC,
        status=RuleStatus.CANDIDATE,
        created_at=datetime.now()
    )
    
    rule2 = SecurityRule(
        id="ec2-unrestricted-ssh",
        name="EC2 Unrestricted SSH Access",
        description="Detects EC2 security groups allowing SSH access from anywhere (0.0.0.0/0)",
        severity=Severity.CRITICAL,
        pattern=r'resource\s+"aws_security_group_rule".*"0\.0\.0\.0/0".*"22"',
        remediation="Restrict SSH access to specific IP ranges or use bastion hosts",
        source=RuleSource.ML_GENERATED,
        status=RuleStatus.CANDIDATE,
        created_at=datetime.now()
    )
    
    # Add rules to engine
    print("1. Adding candidate rules...")
    await rule_engine.add_rule(rule1)
    await rule_engine.add_rule(rule2)
    
    # Show candidate rules
    candidate_rules = await rule_engine.get_candidate_rules()
    print(f"   Added {len(candidate_rules)} candidate rules")
    for rule in candidate_rules:
        print(f"   - {rule.name} ({rule.severity})")
    
    print("\n2. Approving S3 rule...")
    await rule_engine.approve_candidate_rule(rule1.id)
    
    print("3. Rejecting SSH rule...")
    await rule_engine.reject_candidate_rule(rule2.id)
    
    # Show active rules
    active_rules = await rule_engine.get_active_rules()
    print(f"\n4. Active rules: {len(active_rules)}")
    for rule in active_rules:
        print(f"   - {rule.name} (Status: {rule.status})")
    
    # Show rejected rules
    rejected_rules = await rule_engine.get_rejected_rules()
    print(f"\n5. Rejected rules: {len(rejected_rules)}")
    for rule in rejected_rules:
        print(f"   - {rule.name} (Status: {rule.status})")
    
    # Demonstrate rule metrics
    print("\n6. Updating rule metrics...")
    await rule_engine.update_rule_metrics(rule1.id, triggered=True, is_true_positive=True)
    await rule_engine.update_rule_metrics(rule1.id, triggered=True, is_true_positive=False)
    
    # Create a conflicting rule to demonstrate conflict detection
    conflicting_rule = SecurityRule(
        id="s3-public-read-v2",
        name="S3 Bucket Public Read Access",  # Same name as rule1
        description="Alternative detection for S3 public read access",
        severity=Severity.MEDIUM,  # Different severity
        pattern=r'resource\s+"aws_s3_bucket_acl".*"public-read"',  # Same pattern
        remediation="Use private ACLs and CloudFront for public content",
        source=RuleSource.ML_GENERATED,
        status=RuleStatus.CANDIDATE,
        created_at=datetime.now()
    )
    
    print("\n7. Adding conflicting rule...")
    await rule_engine.add_rule(conflicting_rule)
    
    # Show conflicts
    conflicts = await rule_engine.get_conflicts()
    print(f"   Detected {len(conflicts)} conflicts:")
    for conflict in conflicts:
        print(f"   - {conflict.conflict_type}: {conflict.description}")
    
    print("\n8. Rule Engine Demo Complete!")
    print(f"   Storage location: {storage_path}")
    
    return rule_engine


if __name__ == "__main__":
    asyncio.run(demo_rule_engine())