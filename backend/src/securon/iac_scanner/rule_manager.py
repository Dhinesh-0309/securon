"""Rule management utilities for loading and managing security rules"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..interfaces.iac_scanner import SecurityRule
from ..interfaces.core_types import Severity, RuleSource, RuleStatus


class RuleManager:
    """Manages loading and organizing security rules"""
    
    def __init__(self, rules_directory: Optional[str] = None):
        if rules_directory:
            self.rules_directory = Path(rules_directory)
        else:
            # Default to data/rules directory relative to project root
            self.rules_directory = Path(__file__).parent.parent.parent.parent / "data" / "rules"
        
        self.rules_cache: Dict[str, List[SecurityRule]] = {}
    
    def load_comprehensive_rules(self) -> List[SecurityRule]:
        """Load all comprehensive security rules"""
        rules_file = self.rules_directory / "comprehensive_rules.json"
        
        if not rules_file.exists():
            raise FileNotFoundError(f"Comprehensive rules file not found: {rules_file}")
        
        try:
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
            
            rules = []
            severity_map = {
                "LOW": Severity.LOW,
                "MEDIUM": Severity.MEDIUM,
                "HIGH": Severity.HIGH,
                "CRITICAL": Severity.CRITICAL
            }
            
            for rule_data in rules_data.get("rules", []):
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
            
            self.rules_cache["comprehensive"] = rules
            return rules
            
        except Exception as e:
            raise RuntimeError(f"Failed to load comprehensive rules: {e}")
    
    def get_rules_by_category(self, category: str) -> List[SecurityRule]:
        """Get rules filtered by category (e.g., 'S3', 'EC2', 'IAM')"""
        if "comprehensive" not in self.rules_cache:
            self.load_comprehensive_rules()
        
        # Load category mapping from rules file
        rules_file = self.rules_directory / "comprehensive_rules.json"
        with open(rules_file, 'r') as f:
            rules_data = json.load(f)
        
        category_rules = []
        for rule_data in rules_data.get("rules", []):
            if rule_data.get("category", "").upper() == category.upper():
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
                category_rules.append(rule)
        
        return category_rules
    
    def get_rules_by_severity(self, min_severity: Severity) -> List[SecurityRule]:
        """Get rules filtered by minimum severity level"""
        if "comprehensive" not in self.rules_cache:
            self.load_comprehensive_rules()
        
        severity_order = {
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4
        }
        
        min_level = severity_order[min_severity]
        filtered_rules = []
        
        for rule in self.rules_cache["comprehensive"]:
            if severity_order[rule.severity] >= min_level:
                filtered_rules.append(rule)
        
        return filtered_rules
    
    def get_rules_by_compliance(self, compliance_framework: str) -> List[SecurityRule]:
        """Get rules that apply to a specific compliance framework"""
        rules_file = self.rules_directory / "comprehensive_rules.json"
        
        if not rules_file.exists():
            return []
        
        try:
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
            
            compliance_rules = []
            severity_map = {
                "LOW": Severity.LOW,
                "MEDIUM": Severity.MEDIUM,
                "HIGH": Severity.HIGH,
                "CRITICAL": Severity.CRITICAL
            }
            
            for rule_data in rules_data.get("rules", []):
                compliance_list = rule_data.get("compliance", [])
                if compliance_framework.upper() in [c.upper() for c in compliance_list]:
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
                    compliance_rules.append(rule)
            
            return compliance_rules
            
        except Exception as e:
            print(f"Warning: Could not filter rules by compliance: {e}")
            return []
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded rules"""
        if "comprehensive" not in self.rules_cache:
            self.load_comprehensive_rules()
        
        rules = self.rules_cache["comprehensive"]
        
        # Count by severity
        severity_counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }
        
        for rule in rules:
            severity_counts[rule.severity.value] += 1
        
        # Count by category
        rules_file = self.rules_directory / "comprehensive_rules.json"
        category_counts = {}
        
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
            
            for rule_data in rules_data.get("rules", []):
                category = rule_data.get("category", "Unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_rules": len(rules),
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "categories": list(category_counts.keys())
        }
    
    def validate_rules(self) -> List[str]:
        """Validate all rules and return any issues found"""
        issues = []
        
        try:
            rules = self.load_comprehensive_rules()
            
            # Check for duplicate IDs
            rule_ids = [rule.id for rule in rules]
            duplicates = set([x for x in rule_ids if rule_ids.count(x) > 1])
            if duplicates:
                issues.append(f"Duplicate rule IDs found: {duplicates}")
            
            # Check for empty patterns
            empty_patterns = [rule.id for rule in rules if not rule.pattern.strip()]
            if empty_patterns:
                issues.append(f"Rules with empty patterns: {empty_patterns}")
            
            # Check for missing remediation
            no_remediation = [rule.id for rule in rules if not rule.remediation.strip()]
            if no_remediation:
                issues.append(f"Rules without remediation: {no_remediation}")
            
        except Exception as e:
            issues.append(f"Failed to validate rules: {e}")
        
        return issues
    
    def export_rules_summary(self, output_file: Optional[str] = None) -> str:
        """Export a summary of all rules to a markdown file"""
        if "comprehensive" not in self.rules_cache:
            self.load_comprehensive_rules()
        
        rules = self.rules_cache["comprehensive"]
        stats = self.get_rule_statistics()
        
        # Generate markdown content
        content = []
        content.append("# Securon Security Rules Summary")
        content.append("")
        content.append(f"**Total Rules:** {stats['total_rules']}")
        content.append("")
        
        # Severity distribution
        content.append("## Severity Distribution")
        content.append("")
        for severity, count in stats['severity_distribution'].items():
            content.append(f"- **{severity}:** {count} rules")
        content.append("")
        
        # Category distribution
        content.append("## Category Distribution")
        content.append("")
        for category, count in stats['category_distribution'].items():
            content.append(f"- **{category}:** {count} rules")
        content.append("")
        
        # Rules by category
        content.append("## Rules by Category")
        content.append("")
        
        for category in stats['categories']:
            category_rules = self.get_rules_by_category(category)
            if category_rules:
                content.append(f"### {category}")
                content.append("")
                for rule in category_rules:
                    content.append(f"- **{rule.id}** ({rule.severity.value}): {rule.name}")
                    content.append(f"  - {rule.description}")
                    content.append(f"  - *Remediation:* {rule.remediation}")
                content.append("")
        
        markdown_content = "\n".join(content)
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(markdown_content)
        
        return markdown_content


# Global rule manager instance
rule_manager = RuleManager()