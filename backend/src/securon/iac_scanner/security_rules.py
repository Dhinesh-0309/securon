"""Security rules for Terraform resource analysis"""

import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from ..interfaces.iac_scanner import SecurityRule, ScanResult
from ..interfaces.core_types import Severity, RuleSource, RuleStatus, TerraformResource


@dataclass
class RuleCheck:
    """Represents a security rule check function"""
    rule_id: str
    check_function: Callable[[TerraformResource], List[ScanResult]]


class SecurityRuleEngine:
    """Engine for applying security rules to Terraform resources"""
    
    def __init__(self):
        self.rule_checks: Dict[str, RuleCheck] = {}
        self._register_default_checks()
    
    async def check_rule(self, rule: SecurityRule, resource: TerraformResource) -> List[ScanResult]:
        """Apply a security rule to a Terraform resource"""
        # Use pattern-based matching for custom rules
        if rule.id in self.rule_checks:
            # Use registered check function
            check = self.rule_checks[rule.id]
            return check.check_function(resource)
        else:
            # Use pattern-based matching for dynamic rules
            return self._check_pattern_rule(rule, resource)
    
    def _check_pattern_rule(self, rule: SecurityRule, resource: TerraformResource) -> List[ScanResult]:
        """Check a rule using pattern matching"""
        violations = []
        
        # Simple pattern matching - can be extended for more complex patterns
        if self._matches_pattern(rule.pattern, resource):
            violation = ScanResult(
                severity=rule.severity,
                rule_id=rule.id,
                description=rule.description,
                file_path=resource.file_path,
                line_number=resource.line_number,
                remediation=rule.remediation
            )
            violations.append(violation)
        
        return violations
    
    def _matches_pattern(self, pattern: str, resource: TerraformResource) -> bool:
        """Check if a resource matches a rule pattern"""
        # Convert pattern to regex and check against resource configuration
        try:
            # Simple pattern matching - resource type and configuration checks
            if pattern.startswith("resource_type:"):
                expected_type = pattern.split(":", 1)[1].strip()
                return resource.type == expected_type
            
            # Configuration-based patterns
            if pattern.startswith("config:"):
                config_pattern = pattern.split(":", 1)[1].strip()
                return self._check_config_pattern(config_pattern, resource.configuration)
            
            # Default: treat as regex pattern against resource type
            return bool(re.search(pattern, resource.type))
            
        except Exception:
            return False
    
    def _check_config_pattern(self, pattern: str, config: Dict[str, Any]) -> bool:
        """Check if configuration matches a pattern"""
        # Simple key-value pattern matching
        if "=" in pattern:
            key, expected_value = pattern.split("=", 1)
            key = key.strip()
            expected_value = expected_value.strip().strip('"\'')
            
            # Navigate nested configuration
            current = config
            for part in key.split("."):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            
            return str(current) == expected_value
        
        # Check if key exists
        key = pattern.strip()
        current = config
        for part in key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return True
    
    def _register_default_checks(self) -> None:
        """Register default security check functions"""
        
        # Enhanced S3 security checks
        def check_s3_security(resource: TerraformResource) -> List[ScanResult]:
            if resource.type not in ["aws_s3_bucket", "aws_s3_bucket_acl", "aws_s3_bucket_public_access_block"]:
                return []
            
            violations = []
            config = resource.configuration
            
            # S3 bucket public read/write ACL checks
            if resource.type in ["aws_s3_bucket", "aws_s3_bucket_acl"]:
                acl = config.get("acl", "")
                if acl in ["public-read", "public-read-write"]:
                    severity = Severity.CRITICAL if "write" in acl else Severity.HIGH
                    violations.append(ScanResult(
                        severity=severity,
                        rule_id="s3-001" if "read" in acl else "s3-002",
                        description=f"S3 bucket has {acl} ACL which allows public access",
                        file_path=resource.file_path,
                        line_number=resource.line_number,
                        remediation="Remove public ACL and use bucket policies for controlled access"
                    ))
            
            # S3 public access block checks
            if resource.type == "aws_s3_bucket_public_access_block":
                pab_settings = ["block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets"]
                for setting in pab_settings:
                    if config.get(setting) is False:
                        violations.append(ScanResult(
                            severity=Severity.HIGH,
                            rule_id="s3-007",
                            description=f"S3 bucket public access block has {setting} disabled",
                            file_path=resource.file_path,
                            line_number=resource.line_number,
                            remediation="Enable all public access block settings"
                        ))
            
            return violations
        
        # Enhanced Security Group checks
        def check_security_group(resource: TerraformResource) -> List[ScanResult]:
            if resource.type != "aws_security_group":
                return []
            
            violations = []
            config = resource.configuration
            
            # Check ingress rules for dangerous ports
            ingress_rules = config.get("ingress", [])
            if not isinstance(ingress_rules, list):
                ingress_rules = [ingress_rules]
            
            dangerous_ports = {
                22: ("SSH", "sg-001"),
                3389: ("RDP", "sg-002"),
                3306: ("MySQL", "sg-003"),
                5432: ("PostgreSQL", "sg-003"),
                1433: ("MSSQL", "sg-003"),
                27017: ("MongoDB", "sg-003")
            }
            
            for rule in ingress_rules:
                if isinstance(rule, dict):
                    cidr_blocks = rule.get("cidr_blocks", [])
                    from_port = rule.get("from_port")
                    to_port = rule.get("to_port")
                    
                    if "0.0.0.0/0" in cidr_blocks:
                        # Check for specific dangerous ports
                        for port, (service, rule_id) in dangerous_ports.items():
                            if (from_port == port or to_port == port or 
                                (from_port <= port <= to_port if from_port and to_port else False)):
                                violations.append(ScanResult(
                                    severity=Severity.CRITICAL,
                                    rule_id=rule_id,
                                    description=f"Security group allows {service} (port {port}) from 0.0.0.0/0",
                                    file_path=resource.file_path,
                                    line_number=resource.line_number,
                                    remediation=f"Restrict {service} access to specific IP ranges"
                                ))
                        
                        # General unrestricted access check
                        if from_port == 0 and to_port == 65535:
                            violations.append(ScanResult(
                                severity=Severity.CRITICAL,
                                rule_id="sg-004",
                                description="Security group allows all traffic from 0.0.0.0/0",
                                file_path=resource.file_path,
                                line_number=resource.line_number,
                                remediation="Define specific port ranges and protocols"
                            ))
            
            return violations
        
        # Enhanced EC2 security checks
        def check_ec2_security(resource: TerraformResource) -> List[ScanResult]:
            if resource.type != "aws_instance":
                return []
            
            violations = []
            config = resource.configuration
            
            # Check for public IP assignment
            if config.get("associate_public_ip_address") is True:
                violations.append(ScanResult(
                    severity=Severity.MEDIUM,
                    rule_id="ec2-001",
                    description="EC2 instance has public IP assigned",
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    remediation="Use private subnets and NAT gateway for outbound access"
                ))
            
            # Check EBS encryption
            root_block_device = config.get("root_block_device", {})
            if isinstance(root_block_device, dict) and root_block_device.get("encrypted") is False:
                violations.append(ScanResult(
                    severity=Severity.MEDIUM,
                    rule_id="ec2-002",
                    description="EC2 instance has unencrypted root EBS volume",
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    remediation="Enable EBS encryption for data at rest protection"
                ))
            
            # Check IMDS configuration
            metadata_options = config.get("metadata_options", {})
            if isinstance(metadata_options, dict):
                if metadata_options.get("http_tokens") == "optional":
                    violations.append(ScanResult(
                        severity=Severity.MEDIUM,
                        rule_id="ec2-003",
                        description="EC2 instance allows IMDSv1 which is vulnerable to SSRF",
                        file_path=resource.file_path,
                        line_number=resource.line_number,
                        remediation="Set http_tokens to 'required' to enforce IMDSv2"
                    ))
            
            return violations
        
        # Enhanced RDS security checks
        def check_rds_security(resource: TerraformResource) -> List[ScanResult]:
            if resource.type not in ["aws_db_instance", "aws_rds_cluster"]:
                return []
            
            violations = []
            config = resource.configuration
            
            # Public access check
            if config.get("publicly_accessible") is True:
                violations.append(ScanResult(
                    severity=Severity.HIGH,
                    rule_id="rds-001",
                    description="RDS instance is publicly accessible",
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    remediation="Set publicly_accessible to false"
                ))
            
            # Encryption check
            if config.get("storage_encrypted") is False:
                violations.append(ScanResult(
                    severity=Severity.HIGH,
                    rule_id="rds-002",
                    description="RDS instance does not have encryption at rest enabled",
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    remediation="Enable storage encryption using KMS"
                ))
            
            # Backup check
            if config.get("backup_retention_period", 0) == 0:
                violations.append(ScanResult(
                    severity=Severity.MEDIUM,
                    rule_id="rds-003",
                    description="RDS instance has automated backups disabled",
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    remediation="Set backup retention period to at least 7 days"
                ))
            
            return violations
        
        # Enhanced IAM security checks
        def check_iam_security(resource: TerraformResource) -> List[ScanResult]:
            if resource.type not in ["aws_iam_policy", "aws_iam_role_policy", "aws_iam_role"]:
                return []
            
            violations = []
            config = resource.configuration
            
            # IAM policy wildcard checks
            if resource.type in ["aws_iam_policy", "aws_iam_role_policy"]:
                policy = config.get("policy")
                if self._check_iam_wildcards(policy):
                    violations.append(ScanResult(
                        severity=Severity.HIGH,
                        rule_id="iam-001",
                        description="IAM policy contains wildcard actions or resources",
                        file_path=resource.file_path,
                        line_number=resource.line_number,
                        remediation="Use specific actions and resources following least privilege"
                    ))
            
            # IAM role cross-account trust check
            if resource.type == "aws_iam_role":
                assume_role_policy = config.get("assume_role_policy")
                if self._check_cross_account_trust(assume_role_policy):
                    violations.append(ScanResult(
                        severity=Severity.HIGH,
                        rule_id="iam-006",
                        description="IAM role allows cross-account access without conditions",
                        file_path=resource.file_path,
                        line_number=resource.line_number,
                        remediation="Add conditions to cross-account trust relationships"
                    ))
            
            return violations
        
        # Register enhanced checks
        self.rule_checks["s3-security"] = RuleCheck("s3-security", check_s3_security)
        self.rule_checks["sg-security"] = RuleCheck("sg-security", check_security_group)
        self.rule_checks["ec2-security"] = RuleCheck("ec2-security", check_ec2_security)
        self.rule_checks["rds-security"] = RuleCheck("rds-security", check_rds_security)
        self.rule_checks["iam-security"] = RuleCheck("iam-security", check_iam_security)
        
        # Register comprehensive rule IDs to use the same check functions
        # S3 rules
        for rule_id in ["s3-001", "s3-002", "s3-003", "s3-004", "s3-005", "s3-006", "s3-007"]:
            self.rule_checks[rule_id] = RuleCheck(rule_id, check_s3_security)
        
        # Security Group rules
        for rule_id in ["sg-001", "sg-002", "sg-003", "sg-004", "sg-005"]:
            self.rule_checks[rule_id] = RuleCheck(rule_id, check_security_group)
        
        # EC2 rules
        for rule_id in ["ec2-001", "ec2-002", "ec2-003", "ec2-004", "ec2-005"]:
            self.rule_checks[rule_id] = RuleCheck(rule_id, check_ec2_security)
        
        # RDS rules
        for rule_id in ["rds-001", "rds-002", "rds-003", "rds-004", "rds-005"]:
            self.rule_checks[rule_id] = RuleCheck(rule_id, check_rds_security)
        
        # IAM rules
        for rule_id in ["iam-001", "iam-002", "iam-003", "iam-004", "iam-005", "iam-006"]:
            self.rule_checks[rule_id] = RuleCheck(rule_id, check_iam_security)
    
    def _check_iam_wildcards(self, policy: Any) -> bool:
        """Check if IAM policy contains wildcards"""
        if isinstance(policy, str):
            return "*" in policy and ("Action" in policy or "Resource" in policy)
        elif isinstance(policy, dict):
            return self._has_wildcard_actions(policy) or self._has_wildcard_resources(policy)
        return False
    
    def _has_wildcard_resources(self, policy_doc: Dict[str, Any]) -> bool:
        """Check if IAM policy document has wildcard resources"""
        statements = policy_doc.get("Statement", [])
        if not isinstance(statements, list):
            statements = [statements]
        
        for statement in statements:
            if isinstance(statement, dict):
                resources = statement.get("Resource", [])
                if isinstance(resources, str):
                    resources = [resources]
                
                for resource in resources:
                    if resource == "*":
                        return True
        return False
    
    def _check_cross_account_trust(self, assume_role_policy: Any) -> bool:
        """Check if assume role policy allows cross-account access without conditions"""
        if isinstance(assume_role_policy, str):
            return "arn:aws:iam::" in assume_role_policy and "Condition" not in assume_role_policy
        elif isinstance(assume_role_policy, dict):
            statements = assume_role_policy.get("Statement", [])
            if not isinstance(statements, list):
                statements = [statements]
            
            for statement in statements:
                if isinstance(statement, dict):
                    principal = statement.get("Principal", {})
                    if isinstance(principal, dict):
                        aws_principals = principal.get("AWS", [])
                        if isinstance(aws_principals, str):
                            aws_principals = [aws_principals]
                        
                        for aws_principal in aws_principals:
                            if "arn:aws:iam::" in aws_principal and statement.get("Condition") is None:
                                return True
        return False
    
    def _has_wildcard_actions(self, policy_doc: Dict[str, Any]) -> bool:
        """Check if IAM policy document has wildcard actions"""
        statements = policy_doc.get("Statement", [])
        if not isinstance(statements, list):
            statements = [statements]
        
        for statement in statements:
            if isinstance(statement, dict):
                actions = statement.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                
                for action in actions:
                    if action == "*" or action.endswith(":*"):
                        return True
        
        return False


class DefaultSecurityRules:
    """Default security rules for common Terraform misconfigurations"""
    
    @staticmethod
    def get_default_rules() -> List[SecurityRule]:
        """Get the default set of security rules"""
        import json
        import os
        from pathlib import Path
        
        # Load comprehensive rules from JSON file
        rules_file = Path(__file__).parent.parent.parent.parent / "data" / "rules" / "comprehensive_rules.json"
        
        if not rules_file.exists():
            # Fallback to basic rules if comprehensive rules file doesn't exist
            return DefaultSecurityRules._get_basic_rules()
        
        try:
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
            
            rules = []
            for rule_data in rules_data.get("rules", []):
                # Map severity string to enum
                severity_map = {
                    "LOW": Severity.LOW,
                    "MEDIUM": Severity.MEDIUM,
                    "HIGH": Severity.HIGH,
                    "CRITICAL": Severity.CRITICAL
                }
                
                rule = SecurityRule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    severity=severity_map.get(rule_data["severity"], Severity.MEDIUM),
                    pattern=rule_data["pattern"],
                    remediation=rule_data["remediation"],
                    source=RuleSource.STATIC,
                    status=RuleStatus.ACTIVE,
                    created_at=datetime.now()
                )
                rules.append(rule)
            
            return rules
            
        except Exception as e:
            print(f"Warning: Could not load comprehensive rules: {e}")
            return DefaultSecurityRules._get_basic_rules()
    
    @staticmethod
    def _get_basic_rules() -> List[SecurityRule]:
        """Get basic fallback rules if comprehensive rules can't be loaded"""
        return [
            SecurityRule(
                id="s3-public-read",
                name="S3 Bucket Public Read",
                description="S3 bucket should not have public-read ACL",
                severity=Severity.HIGH,
                pattern="resource_type:aws_s3_bucket",
                remediation="Remove public-read ACL or use bucket policies for controlled access",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            ),
            SecurityRule(
                id="sg-unrestricted-ingress",
                name="Security Group Unrestricted Ingress",
                description="Security group should not allow unrestricted ingress",
                severity=Severity.CRITICAL,
                pattern="resource_type:aws_security_group",
                remediation="Restrict CIDR blocks to specific IP ranges",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            ),
            SecurityRule(
                id="iam-wildcard-actions",
                name="IAM Wildcard Actions",
                description="IAM policies should not use wildcard actions",
                severity=Severity.HIGH,
                pattern="resource_type:aws_iam_policy",
                remediation="Use specific actions instead of wildcards",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            ),
            SecurityRule(
                id="s3-encryption-disabled",
                name="S3 Bucket Encryption Disabled",
                description="S3 bucket should have encryption enabled",
                severity=Severity.MEDIUM,
                pattern="config:server_side_encryption_configuration",
                remediation="Enable server-side encryption for S3 bucket",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            ),
            SecurityRule(
                id="rds-public-access",
                name="RDS Instance Public Access",
                description="RDS instance should not be publicly accessible",
                severity=Severity.HIGH,
                pattern="config:publicly_accessible=true",
                remediation="Set publicly_accessible to false for RDS instances",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            ),
            SecurityRule(
                id="cloudtrail-encryption-disabled",
                name="CloudTrail Encryption Disabled",
                description="CloudTrail should have encryption enabled",
                severity=Severity.MEDIUM,
                pattern="resource_type:aws_cloudtrail",
                remediation="Enable KMS encryption for CloudTrail logs",
                source=RuleSource.STATIC,
                status=RuleStatus.ACTIVE,
                created_at=datetime.now()
            )
        ]