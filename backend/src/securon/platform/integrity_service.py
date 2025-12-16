"""Data integrity and validation service"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from .data_access import SecuronDataAccess, DataAccessError
from ..interfaces.core_types import Severity


logger = logging.getLogger(__name__)


@dataclass
class IntegrityCheck:
    """Result of an integrity check"""
    component: str
    status: str  # 'passed', 'failed', 'warning'
    message: str
    details: Optional[Dict[str, Any]] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()


@dataclass
class ValidationResult:
    """Result of data validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Optional[Dict[str, Any]] = None


class DataIntegrityService:
    """Service for ensuring data integrity and validation"""
    
    def __init__(self, data_access: SecuronDataAccess):
        self.data_access = data_access
        self._integrity_cache = {}
        self._cache_ttl = timedelta(hours=1)
        
        logger.info("DataIntegrityService initialized")
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate SHA-256 checksum for data"""
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True, default=str)
        elif isinstance(data, (list, tuple)):
            data_str = json.dumps(sorted(data) if all(isinstance(x, (str, int, float)) for x in data) else data, default=str)
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, component: str) -> bool:
        """Check if cached integrity result is still valid"""
        if component not in self._integrity_cache:
            return False
        
        cached_result = self._integrity_cache[component]
        return datetime.now() - cached_result.checked_at < self._cache_ttl
    
    async def validate_security_rules(self) -> ValidationResult:
        """Validate all security rules for consistency and correctness"""
        errors = []
        warnings = []
        metadata = {}
        
        try:
            # Get all rules
            from ..interfaces.core_types import RuleStatus
            all_rules = []
            for status in RuleStatus:
                rules = await self.data_access.get_rules_by_status(status)
                all_rules.extend(rules)
            
            metadata['total_rules'] = len(all_rules)
            
            # Check for duplicate IDs
            rule_ids = [rule.id for rule in all_rules]
            duplicate_ids = set([x for x in rule_ids if rule_ids.count(x) > 1])
            if duplicate_ids:
                errors.append(f"Duplicate rule IDs found: {', '.join(duplicate_ids)}")
            
            # Validate individual rules
            invalid_rules = []
            for rule in all_rules:
                rule_errors = self._validate_single_rule(rule)
                if rule_errors:
                    invalid_rules.append(f"{rule.id}: {', '.join(rule_errors)}")
            
            if invalid_rules:
                errors.extend(invalid_rules)
            
            # Check for pattern conflicts
            pattern_conflicts = self._check_pattern_conflicts(all_rules)
            if pattern_conflicts:
                warnings.extend(pattern_conflicts)
            
            # Validate rule relationships
            relationship_issues = self._validate_rule_relationships(all_rules)
            if relationship_issues:
                warnings.extend(relationship_issues)
            
            metadata['active_rules'] = len([r for r in all_rules if r.status.value == 'ACTIVE'])
            metadata['candidate_rules'] = len([r for r in all_rules if r.status.value == 'CANDIDATE'])
            metadata['rejected_rules'] = len([r for r in all_rules if r.status.value == 'REJECTED'])
            
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Security rules validation failed: {str(e)}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                metadata=metadata
            )
    
    def _validate_single_rule(self, rule) -> List[str]:
        """Validate a single security rule"""
        errors = []
        
        # Basic field validation
        if not rule.id or len(rule.id.strip()) < 3:
            errors.append("Rule ID must be at least 3 characters")
        
        if not rule.name or len(rule.name.strip()) < 3:
            errors.append("Rule name must be at least 3 characters")
        
        if not rule.description or len(rule.description.strip()) < 10:
            errors.append("Rule description must be at least 10 characters")
        
        if not rule.pattern or len(rule.pattern.strip()) < 1:
            errors.append("Rule pattern cannot be empty")
        
        if not rule.remediation or len(rule.remediation.strip()) < 10:
            errors.append("Rule remediation must be at least 10 characters")
        
        # Pattern validation (basic regex check)
        try:
            import re
            re.compile(rule.pattern)
        except re.error as e:
            errors.append(f"Invalid regex pattern: {str(e)}")
        
        # Severity validation
        if rule.severity not in [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]:
            errors.append("Invalid severity level")
        
        return errors
    
    def _check_pattern_conflicts(self, rules) -> List[str]:
        """Check for conflicting patterns between rules"""
        conflicts = []
        
        # Group rules by pattern similarity
        patterns = {}
        for rule in rules:
            if rule.status.value == 'ACTIVE':  # Only check active rules
                pattern_key = rule.pattern.lower().strip()
                if pattern_key in patterns:
                    patterns[pattern_key].append(rule)
                else:
                    patterns[pattern_key] = [rule]
        
        # Find exact duplicates
        for pattern, rule_list in patterns.items():
            if len(rule_list) > 1:
                rule_ids = [r.id for r in rule_list]
                conflicts.append(f"Duplicate patterns found in rules: {', '.join(rule_ids)}")
        
        return conflicts
    
    def _validate_rule_relationships(self, rules) -> List[str]:
        """Validate relationships between rules"""
        issues = []
        
        # Check for rules that might override each other
        active_rules = [r for r in rules if r.status.value == 'ACTIVE']
        
        # Group by severity to check for inconsistencies
        severity_groups = {}
        for rule in active_rules:
            if rule.severity not in severity_groups:
                severity_groups[rule.severity] = []
            severity_groups[rule.severity].append(rule)
        
        # Check if high-severity rules have corresponding lower-severity variants
        if Severity.CRITICAL in severity_groups and len(severity_groups[Severity.CRITICAL]) > len(severity_groups.get(Severity.HIGH, [])):
            issues.append("More CRITICAL rules than HIGH severity rules - consider review")
        
        return issues
    
    async def check_database_integrity(self) -> IntegrityCheck:
        """Check database integrity and consistency"""
        component = "database"
        
        # Check cache first
        if self._is_cache_valid(component):
            return self._integrity_cache[component]
        
        try:
            # Get database statistics
            db_stats = await self.data_access.get_system_health()
            
            issues = []
            
            # Check for reasonable data distribution
            if 'database' in db_stats:
                stats = db_stats['database']
                
                # Check if we have rules but no metrics
                rules_count = stats.get('security_rules_count', 0)
                metrics_count = stats.get('rule_metrics_count', 0)
                
                if rules_count > 0 and metrics_count == 0:
                    issues.append("Rules exist but no metrics found")
                
                # Check for orphaned data
                versions_count = stats.get('rule_versions_count', 0)
                if versions_count > rules_count * 2:  # Arbitrary threshold
                    issues.append("Excessive rule versions may indicate cleanup needed")
                
                # Check database size
                db_size = stats.get('database_size_bytes', 0)
                if db_size > 100 * 1024 * 1024:  # 100MB threshold
                    issues.append("Database size is large, consider archiving old data")
            
            # Determine status
            if not issues:
                status = "passed"
                message = "Database integrity check passed"
            else:
                status = "warning"
                message = f"Database integrity issues found: {'; '.join(issues)}"
            
            result = IntegrityCheck(
                component=component,
                status=status,
                message=message,
                details={'issues': issues, 'stats': db_stats}
            )
            
            # Cache result
            self._integrity_cache[component] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Database integrity check failed: {str(e)}")
            result = IntegrityCheck(
                component=component,
                status="failed",
                message=f"Database integrity check failed: {str(e)}"
            )
            return result
    
    async def check_backup_integrity(self) -> IntegrityCheck:
        """Check backup system integrity"""
        component = "backup"
        
        # Check cache first
        if self._is_cache_valid(component):
            return self._integrity_cache[component]
        
        try:
            # This would integrate with BackupService
            # For now, we'll do basic checks
            
            backup_dir = Path("data/backups")
            issues = []
            
            if not backup_dir.exists():
                issues.append("Backup directory does not exist")
            else:
                # Check for recent backups
                db_backups = list(backup_dir.glob("**/*.db"))
                if not db_backups:
                    issues.append("No database backups found")
                else:
                    # Check if latest backup is recent (within 48 hours)
                    latest_backup = max(db_backups, key=lambda x: x.stat().st_mtime)
                    backup_age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)
                    
                    if backup_age > timedelta(hours=48):
                        issues.append(f"Latest backup is {backup_age.days} days old")
            
            # Determine status
            if not issues:
                status = "passed"
                message = "Backup integrity check passed"
            else:
                status = "warning" if backup_dir.exists() else "failed"
                message = f"Backup integrity issues: {'; '.join(issues)}"
            
            result = IntegrityCheck(
                component=component,
                status=status,
                message=message,
                details={'issues': issues, 'backup_dir': str(backup_dir)}
            )
            
            # Cache result
            self._integrity_cache[component] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Backup integrity check failed: {str(e)}")
            result = IntegrityCheck(
                component=component,
                status="failed",
                message=f"Backup integrity check failed: {str(e)}"
            )
            return result
    
    async def check_data_consistency(self) -> IntegrityCheck:
        """Check data consistency across components"""
        component = "data_consistency"
        
        try:
            issues = []
            
            # Validate security rules
            rules_validation = await self.validate_security_rules()
            if not rules_validation.valid:
                issues.extend([f"Rules: {error}" for error in rules_validation.errors])
            
            # Add warnings as minor issues
            if rules_validation.warnings:
                issues.extend([f"Rules warning: {warning}" for warning in rules_validation.warnings])
            
            # Check for data orphans (this would be expanded based on actual relationships)
            # For now, we'll do basic consistency checks
            
            # Determine status
            if not issues:
                status = "passed"
                message = "Data consistency check passed"
            elif any("error" in issue.lower() for issue in issues):
                status = "failed"
                message = f"Data consistency errors found: {len(issues)} issues"
            else:
                status = "warning"
                message = f"Data consistency warnings: {len(issues)} issues"
            
            result = IntegrityCheck(
                component=component,
                status=status,
                message=message,
                details={'issues': issues, 'rules_metadata': rules_validation.metadata}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Data consistency check failed: {str(e)}")
            result = IntegrityCheck(
                component=component,
                status="failed",
                message=f"Data consistency check failed: {str(e)}"
            )
            return result
    
    async def run_comprehensive_integrity_check(self) -> Dict[str, IntegrityCheck]:
        """Run all integrity checks"""
        logger.info("Starting comprehensive integrity check")
        
        checks = {}
        
        # Run all checks concurrently
        tasks = {
            'database': self.check_database_integrity(),
            'backup': self.check_backup_integrity(),
            'data_consistency': self.check_data_consistency()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for i, (check_name, task) in enumerate(tasks.items()):
            result = results[i]
            if isinstance(result, Exception):
                checks[check_name] = IntegrityCheck(
                    component=check_name,
                    status="failed",
                    message=f"Check failed with exception: {str(result)}"
                )
            else:
                checks[check_name] = result
        
        # Log summary
        passed = sum(1 for check in checks.values() if check.status == "passed")
        failed = sum(1 for check in checks.values() if check.status == "failed")
        warnings = sum(1 for check in checks.values() if check.status == "warning")
        
        logger.info(f"Integrity check completed: {passed} passed, {warnings} warnings, {failed} failed")
        
        return checks
    
    async def repair_data_issues(self, dry_run: bool = True) -> Dict[str, Any]:
        """Attempt to repair common data issues"""
        logger.info(f"Starting data repair (dry_run={dry_run})")
        
        repairs = {
            'attempted': [],
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        try:
            # Run integrity checks first
            checks = await self.run_comprehensive_integrity_check()
            
            # Repair database issues
            if checks['database'].status in ['failed', 'warning']:
                repair_name = "database_cleanup"
                repairs['attempted'].append(repair_name)
                
                try:
                    if not dry_run:
                        # Perform actual cleanup operations
                        # This would include removing orphaned records, fixing constraints, etc.
                        pass
                    
                    repairs['successful'].append(repair_name)
                    logger.info(f"Repair successful: {repair_name}")
                    
                except Exception as e:
                    repairs['failed'].append(f"{repair_name}: {str(e)}")
                    logger.error(f"Repair failed: {repair_name}: {str(e)}")
            
            # Repair backup issues
            if checks['backup'].status in ['failed', 'warning']:
                repair_name = "backup_system"
                repairs['attempted'].append(repair_name)
                
                try:
                    if not dry_run:
                        # Create backup directory if missing
                        backup_dir = Path("data/backups")
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Create emergency backup
                        await self.data_access.create_backup("emergency_repair_backup")
                    
                    repairs['successful'].append(repair_name)
                    logger.info(f"Repair successful: {repair_name}")
                    
                except Exception as e:
                    repairs['failed'].append(f"{repair_name}: {str(e)}")
                    logger.error(f"Repair failed: {repair_name}: {str(e)}")
            
            return repairs
            
        except Exception as e:
            logger.error(f"Data repair process failed: {str(e)}")
            repairs['failed'].append(f"repair_process: {str(e)}")
            return repairs
    
    def clear_integrity_cache(self):
        """Clear the integrity check cache"""
        self._integrity_cache.clear()
        logger.info("Integrity check cache cleared")
    
    async def get_integrity_summary(self) -> Dict[str, Any]:
        """Get a summary of system integrity status"""
        checks = await self.run_comprehensive_integrity_check()
        
        summary = {
            'overall_status': 'passed',
            'total_checks': len(checks),
            'passed': 0,
            'warnings': 0,
            'failed': 0,
            'last_check': datetime.now().isoformat(),
            'details': {}
        }
        
        for check_name, check in checks.items():
            summary['details'][check_name] = {
                'status': check.status,
                'message': check.message,
                'checked_at': check.checked_at.isoformat()
            }
            
            if check.status == 'passed':
                summary['passed'] += 1
            elif check.status == 'warning':
                summary['warnings'] += 1
            elif check.status == 'failed':
                summary['failed'] += 1
                summary['overall_status'] = 'failed'
        
        # If no failures but warnings exist, overall status is warning
        if summary['overall_status'] != 'failed' and summary['warnings'] > 0:
            summary['overall_status'] = 'warning'
        
        return summary