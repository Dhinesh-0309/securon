"""Output formatters for CLI interface"""

import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

from ..interfaces.iac_scanner import ScanResult, SecurityRule
from ..interfaces.core_types import Severity, RuleStatus


class OutputFormatter(ABC):
    """Abstract base class for output formatters"""
    
    @abstractmethod
    def format_scan_results(self, results: List[ScanResult], target_path: str) -> str:
        """Format scan results for display"""
        pass
    
    @abstractmethod
    def format_rules(self, rules: List[SecurityRule]) -> str:
        """Format rules list for display"""
        pass
    
    @abstractmethod
    def format_rule_details(self, rule: SecurityRule) -> str:
        """Format detailed rule information for display"""
        pass


class JSONFormatter(OutputFormatter):
    """JSON output formatter"""
    
    def format_scan_results(self, results: List[ScanResult], target_path: str) -> str:
        """Format scan results as JSON"""
        output = {
            "target": target_path,
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(results),
            "issues": []
        }
        
        for result in results:
            output["issues"].append({
                "severity": result.severity.value,
                "rule_id": result.rule_id,
                "description": result.description,
                "file_path": result.file_path,
                "line_number": result.line_number,
                "remediation": result.remediation
            })
        
        return json.dumps(output, indent=2)
    
    def format_rules(self, rules: List[SecurityRule]) -> str:
        """Format rules list as JSON"""
        output = {
            "total_rules": len(rules),
            "rules": []
        }
        
        for rule in rules:
            output["rules"].append({
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity.value,
                "status": rule.status.value,
                "source": rule.source.value,
                "created_at": rule.created_at.isoformat()
            })
        
        return json.dumps(output, indent=2)
    
    def format_rule_details(self, rule: SecurityRule) -> str:
        """Format detailed rule information as JSON"""
        output = {
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "severity": rule.severity.value,
            "pattern": rule.pattern,
            "remediation": rule.remediation,
            "source": rule.source.value,
            "status": rule.status.value,
            "created_at": rule.created_at.isoformat()
        }
        
        return json.dumps(output, indent=2)


class TableFormatter(OutputFormatter):
    """Table output formatter"""
    
    def format_scan_results(self, results: List[ScanResult], target_path: str) -> str:
        """Format scan results as a table"""
        if not results:
            return f"✅ No security issues found in {target_path}"
        
        # Group results by severity for better organization
        severity_groups = {}
        for result in results:
            if result.severity not in severity_groups:
                severity_groups[result.severity] = []
            severity_groups[result.severity].append(result)
        
        output_lines = []
        output_lines.append(f"🔍 {target_path}")
        
        # Show summary first
        total = len(results)
        critical = len(severity_groups.get(Severity.CRITICAL, []))
        high = len(severity_groups.get(Severity.HIGH, []))
        medium = len(severity_groups.get(Severity.MEDIUM, []))
        low = len(severity_groups.get(Severity.LOW, []))
        
        summary_parts = []
        if critical > 0: summary_parts.append(f"🔴 {critical} Critical")
        if high > 0: summary_parts.append(f"🟠 {high} High")
        if medium > 0: summary_parts.append(f"🟡 {medium} Medium")
        if low > 0: summary_parts.append(f"🟢 {low} Low")
        
        output_lines.append(f"   {total} issues found: {', '.join(summary_parts)}")
        output_lines.append("")
        
        # Display results grouped by severity (highest first)
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        
        for severity in severity_order:
            if severity not in severity_groups:
                continue
            
            severity_results = severity_groups[severity]
            severity_icon = self._get_severity_icon(severity)
            
            output_lines.append(f"{severity_icon}{severity.value} Issues:")
            
            for i, result in enumerate(severity_results, 1):
                output_lines.append(f"  {result.file_path}:{result.line_number} - {result.description}")
                output_lines.append(f"    💡 {result.remediation}")
                if i < len(severity_results):  # Add spacing between issues except the last one
                    output_lines.append("")
        
        return "\n".join(output_lines)
    
    def format_rules(self, rules: List[SecurityRule]) -> str:
        """Format rules list as a table"""
        if not rules:
            return "No rules found"
        
        output_lines = []
        output_lines.append(f"📋 Security Rules ({len(rules)} total)")
        output_lines.append("=" * 100)
        
        # Table header
        header = f"{'ID':<20} {'Name':<30} {'Severity':<10} {'Status':<12} {'Source':<12}"
        output_lines.append(header)
        output_lines.append("-" * 100)
        
        # Sort rules by status and severity
        sorted_rules = sorted(rules, key=lambda r: (r.status.value, r.severity.value))
        
        for rule in sorted_rules:
            status_icon = self._get_status_icon(rule.status)
            severity_icon = self._get_severity_icon(rule.severity)
            
            row = (f"{rule.id[:18]:<20} {rule.name[:28]:<30} "
                  f"{severity_icon}{rule.severity.value:<9} "
                  f"{status_icon}{rule.status.value:<11} {rule.source.value:<12}")
            output_lines.append(row)
        
        return "\n".join(output_lines)
    
    def format_rule_details(self, rule: SecurityRule) -> str:
        """Format detailed rule information as a table"""
        output_lines = []
        output_lines.append(f"📄 Rule Details: {rule.name}")
        output_lines.append("=" * 80)
        output_lines.append(f"ID:          {rule.id}")
        output_lines.append(f"Name:        {rule.name}")
        output_lines.append(f"Status:      {self._get_status_icon(rule.status)}{rule.status.value}")
        output_lines.append(f"Severity:    {self._get_severity_icon(rule.severity)}{rule.severity.value}")
        output_lines.append(f"Source:      {rule.source.value}")
        output_lines.append(f"Created:     {rule.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("")
        output_lines.append("Description:")
        output_lines.append(f"  {rule.description}")
        output_lines.append("")
        output_lines.append("Pattern:")
        output_lines.append(f"  {rule.pattern}")
        output_lines.append("")
        output_lines.append("Remediation:")
        output_lines.append(f"  {rule.remediation}")
        
        return "\n".join(output_lines)
    
    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level"""
        icons = {
            Severity.CRITICAL: "🔴 ",
            Severity.HIGH: "🟠 ",
            Severity.MEDIUM: "🟡 ",
            Severity.LOW: "🟢 "
        }
        return icons.get(severity, "⚪ ")
    
    def _get_status_icon(self, status: RuleStatus) -> str:
        """Get icon for rule status"""
        icons = {
            RuleStatus.ACTIVE: "✅ ",
            RuleStatus.CANDIDATE: "⏳ ",
            RuleStatus.REJECTED: "❌ "
        }
        return icons.get(status, "⚪ ")


class SummaryFormatter(OutputFormatter):
    """Summary output formatter"""
    
    def format_scan_results(self, results: List[ScanResult], target_path: str) -> str:
        """Format scan results as a summary"""
        if not results:
            return f"✅ {target_path} - No issues found"
        
        # Count issues by severity
        severity_counts = {}
        for result in results:
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
        
        # Build compact summary line
        summary_parts = []
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                icon = self._get_severity_icon(severity)
                summary_parts.append(f"{icon}{count}")
        
        total = len(results)
        summary = " ".join(summary_parts) if summary_parts else "No issues"
        
        return f"🔍 {target_path} - {total} issues ({summary})"
    
    def format_rules(self, rules: List[SecurityRule]) -> str:
        """Format rules list as a summary"""
        if not rules:
            return "No rules found"
        
        # Count rules by status
        status_counts = {}
        for rule in rules:
            status_counts[rule.status] = status_counts.get(rule.status, 0) + 1
        
        output_lines = []
        output_lines.append(f"📋 Security Rules Summary")
        output_lines.append(f"   Total Rules: {len(rules)}")
        
        for status in [RuleStatus.ACTIVE, RuleStatus.CANDIDATE, RuleStatus.REJECTED]:
            count = status_counts.get(status, 0)
            if count > 0:
                icon = self._get_status_icon(status)
                output_lines.append(f"   {icon}{status.value}: {count}")
        
        return "\n".join(output_lines)
    
    def format_rule_details(self, rule: SecurityRule) -> str:
        """Format detailed rule information as a summary"""
        status_icon = self._get_status_icon(rule.status)
        severity_icon = self._get_severity_icon(rule.severity)
        
        output_lines = []
        output_lines.append(f"📄 {rule.name}")
        output_lines.append(f"   ID: {rule.id}")
        output_lines.append(f"   Status: {status_icon}{rule.status.value}")
        output_lines.append(f"   Severity: {severity_icon}{rule.severity.value}")
        output_lines.append(f"   Source: {rule.source.value}")
        output_lines.append(f"   Description: {rule.description}")
        
        return "\n".join(output_lines)
    
    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level"""
        icons = {
            Severity.CRITICAL: "🔴 ",
            Severity.HIGH: "🟠 ",
            Severity.MEDIUM: "🟡 ",
            Severity.LOW: "🟢 "
        }
        return icons.get(severity, "⚪ ")
    
    def _get_status_icon(self, status: RuleStatus) -> str:
        """Get icon for rule status"""
        icons = {
            RuleStatus.ACTIVE: "✅ ",
            RuleStatus.CANDIDATE: "⏳ ",
            RuleStatus.REJECTED: "❌ "
        }
        return icons.get(status, "⚪ ")