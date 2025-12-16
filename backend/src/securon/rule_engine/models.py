"""Rule Engine data models and validation"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
import re

from ..interfaces.iac_scanner import SecurityRule
from ..interfaces.core_types import Severity, RuleSource, RuleStatus


class RuleVersion(BaseModel):
    """Represents a version of a security rule"""
    version: int
    rule: SecurityRule
    modified_at: datetime
    modified_by: Optional[str] = None
    change_reason: Optional[str] = None


class RuleConflict(BaseModel):
    """Represents a conflict between rules"""
    rule_id: str
    conflicting_rule_id: str
    conflict_type: str
    description: str
    severity: Severity


class SecurityRuleValidator:
    """Validates security rules for correctness and consistency"""
    
    @staticmethod
    def validate_rule_pattern(pattern: str) -> bool:
        """Validate that a rule pattern is syntactically correct"""
        if not pattern or not isinstance(pattern, str):
            return False
        
        # Basic validation - pattern should not be empty and should be valid regex
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
    
    @staticmethod
    def validate_rule_id(rule_id: str) -> bool:
        """Validate rule ID format"""
        if not rule_id or not isinstance(rule_id, str):
            return False
        
        # Rule ID should be alphanumeric with hyphens/underscores, 3-50 chars
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return bool(re.match(pattern, rule_id))
    
    @staticmethod
    def validate_security_rule(rule: SecurityRule) -> List[str]:
        """Validate a complete security rule and return list of validation errors"""
        errors = []
        
        if not SecurityRuleValidator.validate_rule_id(rule.id):
            errors.append("Invalid rule ID format")
        
        if not rule.name or len(rule.name.strip()) < 3:
            errors.append("Rule name must be at least 3 characters")
        
        if not rule.description or len(rule.description.strip()) < 10:
            errors.append("Rule description must be at least 10 characters")
        
        if not SecurityRuleValidator.validate_rule_pattern(rule.pattern):
            errors.append("Invalid rule pattern")
        
        if not rule.remediation or len(rule.remediation.strip()) < 10:
            errors.append("Rule remediation must be at least 10 characters")
        
        return errors


class RuleMetrics(BaseModel):
    """Metrics for rule performance and usage"""
    rule_id: str
    times_triggered: int = 0
    false_positives: int = 0
    true_positives: int = 0
    last_triggered: Optional[datetime] = None
    effectiveness_score: float = 0.0
    
    def calculate_effectiveness(self) -> float:
        """Calculate rule effectiveness based on true/false positives"""
        total_triggers = self.true_positives + self.false_positives
        if total_triggers == 0:
            return 0.0
        return self.true_positives / total_triggers