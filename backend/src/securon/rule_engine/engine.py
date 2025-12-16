"""Rule Engine implementation with approval/rejection workflow and conflict resolution"""

from datetime import datetime
from typing import List, Optional, Set
import uuid
import asyncio

from ..interfaces.rule_engine import RuleEngine
from ..interfaces.iac_scanner import SecurityRule
from ..interfaces.core_types import RuleStatus, Severity
from .storage import InMemoryRuleStorage, RuleStorageError
from .models import RuleConflict, RuleMetrics, SecurityRuleValidator


class RuleEngineError(Exception):
    """Exception raised for rule engine operations"""
    pass


class ConcreteRuleEngine(RuleEngine):
    """Concrete implementation of the Rule Engine"""
    
    def __init__(self, storage_path: str = "data/rules"):
        self.storage = InMemoryRuleStorage(storage_path)
        self._conflict_detector = RuleConflictDetector()
    
    async def add_rule(self, rule: SecurityRule) -> None:
        """Add a new security rule to the engine"""
        try:
            # Validate the rule
            validation_errors = SecurityRuleValidator.validate_security_rule(rule)
            if validation_errors:
                raise RuleEngineError(f"Rule validation failed: {', '.join(validation_errors)}")
            
            # Check for conflicts with existing rules
            existing_rules = await self.storage.get_all_rules()
            conflicts = await self._conflict_detector.detect_conflicts(rule, existing_rules)
            
            if conflicts:
                # Store conflicts for review
                for conflict in conflicts:
                    await self.storage.add_conflict(conflict)
                
                # Set rule status to candidate if there are conflicts
                rule.status = RuleStatus.CANDIDATE
            
            # Store the rule
            await self.storage.store_rule(rule)
            
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to add rule: {str(e)}")
    
    async def remove_rule(self, rule_id: str) -> None:
        """Remove a security rule from the engine"""
        try:
            success = await self.storage.delete_rule(rule_id)
            if not success:
                raise RuleEngineError(f"Rule with ID '{rule_id}' not found")
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to remove rule: {str(e)}")
    
    async def get_active_rules(self) -> List[SecurityRule]:
        """Get all active security rules"""
        try:
            return await self.storage.get_rules_by_status(RuleStatus.ACTIVE)
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get active rules: {str(e)}")
    
    async def get_candidate_rules(self) -> List[SecurityRule]:
        """Get all candidate security rules awaiting approval"""
        try:
            return await self.storage.get_rules_by_status(RuleStatus.CANDIDATE)
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get candidate rules: {str(e)}")
    
    async def get_rejected_rules(self) -> List[SecurityRule]:
        """Get all rejected security rules"""
        try:
            return await self.storage.get_rules_by_status(RuleStatus.REJECTED)
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get rejected rules: {str(e)}")
    
    async def approve_candidate_rule(self, rule_id: str) -> None:
        """Approve a candidate rule and make it active"""
        try:
            rule = await self.storage.get_rule(rule_id)
            if not rule:
                raise RuleEngineError(f"Rule with ID '{rule_id}' not found")
            
            if rule.status != RuleStatus.CANDIDATE:
                raise RuleEngineError(f"Rule '{rule_id}' is not a candidate rule")
            
            # Check if approving this rule would create new conflicts
            active_rules = await self.get_active_rules()
            conflicts = await self._conflict_detector.detect_conflicts(rule, active_rules)
            
            if conflicts:
                # Resolve conflicts by setting conflicting rules to candidate status
                for conflict in conflicts:
                    conflicting_rule = await self.storage.get_rule(conflict.conflicting_rule_id)
                    if conflicting_rule and conflicting_rule.status == RuleStatus.ACTIVE:
                        conflicting_rule.status = RuleStatus.CANDIDATE
                        await self.storage.store_rule(conflicting_rule)
            
            # Approve the rule
            rule.status = RuleStatus.ACTIVE
            await self.storage.store_rule(rule)
            
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to approve candidate rule: {str(e)}")
    
    async def reject_candidate_rule(self, rule_id: str) -> None:
        """Reject a candidate rule"""
        try:
            rule = await self.storage.get_rule(rule_id)
            if not rule:
                raise RuleEngineError(f"Rule with ID '{rule_id}' not found")
            
            if rule.status != RuleStatus.CANDIDATE:
                raise RuleEngineError(f"Rule '{rule_id}' is not a candidate rule")
            
            # Reject the rule
            rule.status = RuleStatus.REJECTED
            await self.storage.store_rule(rule)
            
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to reject candidate rule: {str(e)}")
    
    async def get_rule_by_id(self, rule_id: str) -> Optional[SecurityRule]:
        """Get a specific rule by ID"""
        try:
            return await self.storage.get_rule(rule_id)
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get rule: {str(e)}")
    
    async def get_all_rules(self) -> List[SecurityRule]:
        """Get all rules regardless of status"""
        try:
            return await self.storage.get_all_rules()
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get all rules: {str(e)}")
    
    async def get_conflicts(self) -> List[RuleConflict]:
        """Get all rule conflicts"""
        try:
            return await self.storage.get_conflicts()
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to get conflicts: {str(e)}")
    
    async def resolve_conflict(self, rule_id: str, conflicting_rule_id: str, resolution: str) -> None:
        """Resolve a conflict between two rules"""
        try:
            if resolution == "keep_first":
                # Keep the first rule, reject the second
                conflicting_rule = await self.storage.get_rule(conflicting_rule_id)
                if conflicting_rule:
                    conflicting_rule.status = RuleStatus.REJECTED
                    await self.storage.store_rule(conflicting_rule)
            elif resolution == "keep_second":
                # Keep the second rule, reject the first
                rule = await self.storage.get_rule(rule_id)
                if rule:
                    rule.status = RuleStatus.REJECTED
                    await self.storage.store_rule(rule)
            elif resolution == "merge":
                # This would require more complex logic for merging rules
                # For now, we'll just mark both as candidates for manual review
                pass
            
            # Remove the conflict record
            await self.storage.resolve_conflict(rule_id, conflicting_rule_id)
            
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to resolve conflict: {str(e)}")
    
    async def update_rule_metrics(self, rule_id: str, triggered: bool, is_true_positive: bool) -> None:
        """Update metrics for a rule based on its usage"""
        try:
            metrics = await self.storage.get_rule_metrics(rule_id)
            if not metrics:
                metrics = RuleMetrics(rule_id=rule_id)
            
            if triggered:
                metrics.times_triggered += 1
                metrics.last_triggered = datetime.now()
                
                if is_true_positive:
                    metrics.true_positives += 1
                else:
                    metrics.false_positives += 1
                
                metrics.effectiveness_score = metrics.calculate_effectiveness()
            
            await self.storage.update_rule_metrics(rule_id, metrics)
            
        except RuleStorageError as e:
            raise RuleEngineError(f"Failed to update rule metrics: {str(e)}")


class RuleConflictDetector:
    """Detects conflicts between security rules"""
    
    async def detect_conflicts(self, new_rule: SecurityRule, existing_rules: List[SecurityRule]) -> List[RuleConflict]:
        """Detect conflicts between a new rule and existing rules"""
        conflicts = []
        
        for existing_rule in existing_rules:
            if existing_rule.id == new_rule.id:
                continue
            
            # Check for pattern conflicts
            pattern_conflict = self._check_pattern_conflict(new_rule, existing_rule)
            if pattern_conflict:
                conflicts.append(pattern_conflict)
            
            # Check for duplicate names
            name_conflict = self._check_name_conflict(new_rule, existing_rule)
            if name_conflict:
                conflicts.append(name_conflict)
        
        return conflicts
    
    def _check_pattern_conflict(self, rule1: SecurityRule, rule2: SecurityRule) -> Optional[RuleConflict]:
        """Check if two rules have conflicting patterns"""
        # Simple conflict detection - rules with identical patterns
        if rule1.pattern == rule2.pattern and rule1.severity != rule2.severity:
            return RuleConflict(
                rule_id=rule1.id,
                conflicting_rule_id=rule2.id,
                conflict_type="pattern_severity_mismatch",
                description=f"Rules have identical patterns but different severities: {rule1.severity} vs {rule2.severity}",
                severity=Severity.MEDIUM
            )
        
        return None
    
    def _check_name_conflict(self, rule1: SecurityRule, rule2: SecurityRule) -> Optional[RuleConflict]:
        """Check if two rules have conflicting names"""
        if rule1.name.lower() == rule2.name.lower():
            return RuleConflict(
                rule_id=rule1.id,
                conflicting_rule_id=rule2.id,
                conflict_type="duplicate_name",
                description=f"Rules have identical names: {rule1.name}",
                severity=Severity.LOW
            )
        
        return None