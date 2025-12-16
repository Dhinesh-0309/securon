"""Rule Engine storage mechanisms"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from threading import Lock

from ..interfaces.iac_scanner import SecurityRule
from ..interfaces.core_types import RuleStatus
from .models import RuleVersion, RuleConflict, RuleMetrics, SecurityRuleValidator
# Delayed import to avoid circular dependency


class RuleStorageError(Exception):
    """Exception raised for rule storage operations"""
    pass


class EnhancedRuleStorage:
    """Enhanced rule storage with database persistence and fallback to JSON files"""
    
    def __init__(self, storage_path: str = "data/rules", use_database: bool = True):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.use_database = use_database
        
        # Initialize database access if enabled
        if self.use_database:
            try:
                from ..platform.data_access import SecuronDataAccess
                self.data_access = SecuronDataAccess()
            except Exception as e:
                print(f"Database initialization failed, falling back to JSON: {e}")
                self.use_database = False
        
        # Fallback in-memory storage for JSON mode
        if not self.use_database:
            self._rules: Dict[str, SecurityRule] = {}
            self._rule_versions: Dict[str, List[RuleVersion]] = {}
            self._rule_metrics: Dict[str, RuleMetrics] = {}
            self._conflicts: List[RuleConflict] = []
            
            # Thread safety
            self._lock = Lock()
            
            # Load existing data
            self._load_from_disk()


class InMemoryRuleStorage(EnhancedRuleStorage):
    """Legacy in-memory storage for backward compatibility"""
    
    def __init__(self, storage_path: str = "data/rules"):
        super().__init__(storage_path, use_database=False)
    
    def _get_rules_file(self) -> Path:
        return self.storage_path / "rules.json"
    
    def _get_versions_file(self) -> Path:
        return self.storage_path / "versions.json"
    
    def _get_metrics_file(self) -> Path:
        return self.storage_path / "metrics.json"
    
    def _get_conflicts_file(self) -> Path:
        return self.storage_path / "conflicts.json"
    
    def _load_from_disk(self):
        """Load rules and metadata from disk"""
        try:
            # Load rules
            rules_file = self._get_rules_file()
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    for rule_id, rule_dict in rules_data.items():
                        rule_dict['created_at'] = datetime.fromisoformat(rule_dict['created_at'])
                        self._rules[rule_id] = SecurityRule(**rule_dict)
            
            # Load versions
            versions_file = self._get_versions_file()
            if versions_file.exists():
                with open(versions_file, 'r') as f:
                    versions_data = json.load(f)
                    for rule_id, versions_list in versions_data.items():
                        self._rule_versions[rule_id] = []
                        for version_dict in versions_list:
                            version_dict['modified_at'] = datetime.fromisoformat(version_dict['modified_at'])
                            version_dict['rule']['created_at'] = datetime.fromisoformat(version_dict['rule']['created_at'])
                            rule_version = RuleVersion(
                                version=version_dict['version'],
                                rule=SecurityRule(**version_dict['rule']),
                                modified_at=version_dict['modified_at'],
                                modified_by=version_dict.get('modified_by'),
                                change_reason=version_dict.get('change_reason')
                            )
                            self._rule_versions[rule_id].append(rule_version)
            
            # Load metrics
            metrics_file = self._get_metrics_file()
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    for rule_id, metrics_dict in metrics_data.items():
                        if metrics_dict.get('last_triggered'):
                            metrics_dict['last_triggered'] = datetime.fromisoformat(metrics_dict['last_triggered'])
                        self._rule_metrics[rule_id] = RuleMetrics(**metrics_dict)
            
            # Load conflicts
            conflicts_file = self._get_conflicts_file()
            if conflicts_file.exists():
                with open(conflicts_file, 'r') as f:
                    conflicts_data = json.load(f)
                    self._conflicts = [RuleConflict(**conflict) for conflict in conflicts_data]
                    
        except Exception as e:
            raise RuleStorageError(f"Failed to load rules from disk: {str(e)}")
    
    def _save_to_disk(self):
        """Save rules and metadata to disk"""
        try:
            # Save rules
            rules_data = {}
            for rule_id, rule in self._rules.items():
                rule_dict = rule.model_dump()
                rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                rules_data[rule_id] = rule_dict
            
            with open(self._get_rules_file(), 'w') as f:
                json.dump(rules_data, f, indent=2)
            
            # Save versions
            versions_data = {}
            for rule_id, versions in self._rule_versions.items():
                versions_data[rule_id] = []
                for version in versions:
                    version_dict = {
                        'version': version.version,
                        'rule': version.rule.model_dump(),
                        'modified_at': version.modified_at.isoformat(),
                        'modified_by': version.modified_by,
                        'change_reason': version.change_reason
                    }
                    version_dict['rule']['created_at'] = version_dict['rule']['created_at'].isoformat() if isinstance(version_dict['rule']['created_at'], datetime) else version_dict['rule']['created_at']
                    versions_data[rule_id].append(version_dict)
            
            with open(self._get_versions_file(), 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            # Save metrics
            metrics_data = {}
            for rule_id, metrics in self._rule_metrics.items():
                metrics_dict = metrics.model_dump()
                if metrics_dict.get('last_triggered'):
                    metrics_dict['last_triggered'] = metrics_dict['last_triggered'].isoformat()
                metrics_data[rule_id] = metrics_dict
            
            with open(self._get_metrics_file(), 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Save conflicts
            conflicts_data = [conflict.model_dump() for conflict in self._conflicts]
            with open(self._get_conflicts_file(), 'w') as f:
                json.dump(conflicts_data, f, indent=2)
                
        except Exception as e:
            raise RuleStorageError(f"Failed to save rules to disk: {str(e)}")
    
    async def store_rule(self, rule: SecurityRule) -> None:
        """Store a security rule"""
        if self.use_database:
            try:
                await self.data_access.store_security_rule(rule)
                return
            except Exception as e:
                from ..platform.data_access import DataAccessError
                if isinstance(e, DataAccessError):
                    raise RuleStorageError(f"Database storage failed: {str(e)}")
                else:
                    raise
        
        # Fallback to JSON storage
        with self._lock:
            # Validate rule
            validation_errors = SecurityRuleValidator.validate_security_rule(rule)
            if validation_errors:
                raise RuleStorageError(f"Rule validation failed: {', '.join(validation_errors)}")
            
            # Check for existing rule
            if rule.id in self._rules:
                # Create new version
                existing_rule = self._rules[rule.id]
                if rule.id not in self._rule_versions:
                    self._rule_versions[rule.id] = []
                
                version_number = len(self._rule_versions[rule.id]) + 1
                new_version = RuleVersion(
                    version=version_number,
                    rule=rule,
                    modified_at=datetime.now(),
                    change_reason="Rule updated"
                )
                self._rule_versions[rule.id].append(new_version)
            else:
                # Initialize metrics for new rule
                self._rule_metrics[rule.id] = RuleMetrics(rule_id=rule.id)
            
            # Store the rule
            self._rules[rule.id] = rule
            self._save_to_disk()
    
    async def get_rule(self, rule_id: str) -> Optional[SecurityRule]:
        """Get a security rule by ID"""
        if self.use_database:
            try:
                return await self.data_access.get_security_rule(rule_id)
            except Exception as e:
                from ..platform.data_access import DataAccessError
                if isinstance(e, DataAccessError):
                    raise RuleStorageError(f"Database access failed: {str(e)}")
                else:
                    raise
        
        # Fallback to JSON storage
        with self._lock:
            return self._rules.get(rule_id)
    
    async def get_rules_by_status(self, status: RuleStatus) -> List[SecurityRule]:
        """Get all rules with a specific status"""
        if self.use_database:
            try:
                return await self.data_access.get_rules_by_status(status)
            except Exception as e:
                from ..platform.data_access import DataAccessError
                if isinstance(e, DataAccessError):
                    raise RuleStorageError(f"Database access failed: {str(e)}")
                else:
                    raise
        
        # Fallback to JSON storage
        with self._lock:
            return [rule for rule in self._rules.values() if rule.status == status]
    
    async def get_all_rules(self) -> List[SecurityRule]:
        """Get all rules"""
        with self._lock:
            return list(self._rules.values())
    
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID"""
        if self.use_database:
            try:
                return await self.data_access.delete_security_rule(rule_id)
            except Exception as e:
                from ..platform.data_access import DataAccessError
                if isinstance(e, DataAccessError):
                    raise RuleStorageError(f"Database access failed: {str(e)}")
                else:
                    raise
        
        # Fallback to JSON storage
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                # Clean up related data
                if rule_id in self._rule_versions:
                    del self._rule_versions[rule_id]
                if rule_id in self._rule_metrics:
                    del self._rule_metrics[rule_id]
                self._save_to_disk()
                return True
            return False
    
    async def get_rule_versions(self, rule_id: str) -> List[RuleVersion]:
        """Get all versions of a rule"""
        with self._lock:
            return self._rule_versions.get(rule_id, [])
    
    async def get_rule_metrics(self, rule_id: str) -> Optional[RuleMetrics]:
        """Get metrics for a rule"""
        with self._lock:
            return self._rule_metrics.get(rule_id)
    
    async def update_rule_metrics(self, rule_id: str, metrics: RuleMetrics) -> None:
        """Update metrics for a rule"""
        with self._lock:
            self._rule_metrics[rule_id] = metrics
            self._save_to_disk()
    
    async def get_conflicts(self) -> List[RuleConflict]:
        """Get all rule conflicts"""
        with self._lock:
            return self._conflicts.copy()
    
    async def add_conflict(self, conflict: RuleConflict) -> None:
        """Add a rule conflict"""
        with self._lock:
            self._conflicts.append(conflict)
            self._save_to_disk()
    
    async def resolve_conflict(self, rule_id: str, conflicting_rule_id: str) -> None:
        """Resolve a rule conflict"""
        with self._lock:
            self._conflicts = [
                c for c in self._conflicts 
                if not (c.rule_id == rule_id and c.conflicting_rule_id == conflicting_rule_id)
            ]
            self._save_to_disk()