"""Main CLI interface for Securon platform"""

import argparse
import asyncio
import json
import sys
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..platform import PlatformOrchestrator, PlatformConfig
from ..platform.orchestrator import ComponentError
from ..interfaces.iac_scanner import ScanResult, SecurityRule
from ..interfaces.core_types import Severity, RuleStatus
from .formatters import OutputFormatter, JSONFormatter, TableFormatter, SummaryFormatter


class SecuronCLI:
    """Main CLI class for Securon platform operations"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.platform: Optional[PlatformOrchestrator] = None
        self.config_path = config_path or "config/platform.json"
        self.formatters = {
            'json': JSONFormatter(),
            'table': TableFormatter(),
            'summary': SummaryFormatter()
        }
    
    async def initialize(self) -> None:
        """Initialize the platform"""
        try:
            # Suppress logging for clean CLI output
            logging.getLogger('securon').setLevel(logging.CRITICAL)
            logging.getLogger('root').setLevel(logging.CRITICAL)
            
            # Load configuration
            if os.path.exists(self.config_path):
                config = PlatformConfig.from_file(self.config_path)
            else:
                config = PlatformConfig.from_environment()
            
            # Initialize platform
            self.platform = PlatformOrchestrator(config)
            await self.platform.initialize()
            
        except Exception as e:
            print(f"Error: Failed to initialize security platform", file=sys.stderr)
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the platform"""
        if self.platform:
            await self.platform.shutdown()
    
    async def scan_file(self, file_path: str, output_format: str = 'table', 
                       severity_filter: Optional[str] = None) -> int:
        """Scan a single Terraform file"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            # Perform the scan using platform workflow
            results = await self.platform.scan_iac_workflow(file_path)
            
            # Filter by severity if specified
            if severity_filter:
                severity_enum = Severity(severity_filter.upper())
                results = [r for r in results if r.severity == severity_enum]
            
            # Format and display results
            formatter = self.formatters[output_format]
            output = formatter.format_scan_results(results, file_path)
            print(output)
            
            # Return exit code based on findings
            return self._get_exit_code(results)
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def scan_directory(self, directory_path: str, output_format: str = 'table',
                           severity_filter: Optional[str] = None) -> int:
        """Scan a directory of Terraform files"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            # Get IaC scanner from platform
            iac_scanner = self.platform.get_iac_scanner()
            
            # Perform the scan
            results = await iac_scanner.scan_directory(directory_path)
            
            # Filter by severity if specified
            if severity_filter:
                severity_enum = Severity(severity_filter.upper())
                results = [r for r in results if r.severity == severity_enum]
            
            # Format and display results
            formatter = self.formatters[output_format]
            output = formatter.format_scan_results(results, directory_path)
            print(output)
            
            # Return exit code based on findings
            return self._get_exit_code(results)
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def list_rules(self, status_filter: Optional[str] = None, 
                        output_format: str = 'table') -> int:
        """List security rules"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            rule_engine = self.platform.get_rule_engine()
            
            if status_filter:
                status_enum = RuleStatus(status_filter.upper())
                if status_enum == RuleStatus.ACTIVE:
                    rules = await rule_engine.get_active_rules()
                elif status_enum == RuleStatus.CANDIDATE:
                    rules = await rule_engine.get_candidate_rules()
                elif status_enum == RuleStatus.REJECTED:
                    rules = await rule_engine.get_rejected_rules()
                else:
                    rules = []
            else:
                rules = await rule_engine.get_all_rules()
            
            # Format and display rules
            formatter = self.formatters[output_format]
            output = formatter.format_rules(rules)
            print(output)
            
            return 0
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def approve_rule(self, rule_id: str) -> int:
        """Approve a candidate rule"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            rule_engine = self.platform.get_rule_engine()
            await rule_engine.approve_candidate_rule(rule_id)
            print(f"Rule '{rule_id}' approved successfully")
            return 0
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def reject_rule(self, rule_id: str) -> int:
        """Reject a candidate rule"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            rule_engine = self.platform.get_rule_engine()
            await rule_engine.reject_candidate_rule(rule_id)
            print(f"Rule '{rule_id}' rejected successfully")
            return 0
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def show_rule_details(self, rule_id: str, output_format: str = 'table') -> int:
        """Show detailed information about a specific rule"""
        if not self.platform:
            print("Error: Platform not initialized", file=sys.stderr)
            return 1
        
        try:
            rule_engine = self.platform.get_rule_engine()
            rule = await rule_engine.get_rule_by_id(rule_id)
            if not rule:
                print(f"Rule '{rule_id}' not found", file=sys.stderr)
                return 1
            
            formatter = self.formatters[output_format]
            output = formatter.format_rule_details(rule)
            print(output)
            
            return 0
            
        except ComponentError as e:
            print(f"Platform error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    async def show_rule_statistics(self, output_format: str = 'table') -> int:
        """Show statistics about loaded security rules"""
        try:
            from ..iac_scanner.rule_manager import rule_manager
            
            stats = rule_manager.get_rule_statistics()
            
            if output_format == 'json':
                print(json.dumps(stats, indent=2))
            else:
                print("Security Rules Statistics")
                print("=" * 30)
                print(f"Total Rules: {stats['total_rules']}")
                print()
                
                print("Severity Distribution:")
                for severity, count in stats['severity_distribution'].items():
                    print(f"  {severity}: {count} rules")
                print()
                
                print("Category Distribution:")
                for category, count in stats['category_distribution'].items():
                    print(f"  {category}: {count} rules")
            
            return 0
            
        except Exception as e:
            print(f"Error getting rule statistics: {e}", file=sys.stderr)
            return 1
    
    async def export_rules_summary(self, output_file: str) -> int:
        """Export rules summary to markdown file"""
        try:
            from ..iac_scanner.rule_manager import rule_manager
            
            summary = rule_manager.export_rules_summary(output_file)
            print(f"Rules summary exported to: {output_file}")
            
            return 0
            
        except Exception as e:
            print(f"Error exporting rules summary: {e}", file=sys.stderr)
            return 1
    
    def _get_exit_code(self, results: List[ScanResult]) -> int:
        """Determine exit code based on scan results"""
        if not results:
            return 0  # No issues found
        
        # Check for critical or high severity issues
        for result in results:
            if result.severity in [Severity.CRITICAL, Severity.HIGH]:
                return 2  # Critical/high severity issues found
        
        return 1  # Medium/low severity issues found


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog='securon',
        description='Securon Platform CLI - Cloud security scanning and rule management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  securon scan file terraform/main.tf
  securon scan directory terraform/ --format json
  securon scan file main.tf --severity high --format summary
  securon rules list --status active
  securon rules approve rule-123
  securon rules show rule-123 --format json
        """
    )
    
    # Global options
    parser.add_argument('--version', action='version', version='Securon CLI 1.0.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan Terraform files for security issues')
    scan_subparsers = scan_parser.add_subparsers(dest='scan_type', help='Scan type')
    
    # Scan file subcommand
    scan_file_parser = scan_subparsers.add_parser('file', help='Scan a single Terraform file')
    scan_file_parser.add_argument('path', help='Path to Terraform file')
    scan_file_parser.add_argument('--format', choices=['json', 'table', 'summary'], 
                                 default='table', help='Output format')
    scan_file_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'],
                                 help='Filter results by severity level')
    
    # Scan directory subcommand
    scan_dir_parser = scan_subparsers.add_parser('directory', help='Scan a directory of Terraform files')
    scan_dir_parser.add_argument('path', help='Path to directory containing Terraform files')
    scan_dir_parser.add_argument('--format', choices=['json', 'table', 'summary'], 
                                default='table', help='Output format')
    scan_dir_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'],
                                help='Filter results by severity level')
    
    # Rules command
    rules_parser = subparsers.add_parser('rules', help='Manage security rules')
    rules_subparsers = rules_parser.add_subparsers(dest='rules_action', help='Rules action')
    
    # List rules subcommand
    list_rules_parser = rules_subparsers.add_parser('list', help='List security rules')
    list_rules_parser.add_argument('--status', choices=['active', 'candidate', 'rejected'],
                                  help='Filter rules by status')
    list_rules_parser.add_argument('--format', choices=['json', 'table', 'summary'],
                                  default='table', help='Output format')
    
    # Approve rule subcommand
    approve_parser = rules_subparsers.add_parser('approve', help='Approve a candidate rule')
    approve_parser.add_argument('rule_id', help='ID of the rule to approve')
    
    # Reject rule subcommand
    reject_parser = rules_subparsers.add_parser('reject', help='Reject a candidate rule')
    reject_parser.add_argument('rule_id', help='ID of the rule to reject')
    
    # Show rule details subcommand
    show_parser = rules_subparsers.add_parser('show', help='Show detailed information about a rule')
    show_parser.add_argument('rule_id', help='ID of the rule to show')
    show_parser.add_argument('--format', choices=['json', 'table', 'summary'],
                            default='table', help='Output format')
    
    # Rule statistics subcommand
    stats_parser = rules_subparsers.add_parser('stats', help='Show security rules statistics')
    stats_parser.add_argument('--format', choices=['json', 'table'],
                             default='table', help='Output format')
    
    # Export rules summary subcommand
    export_parser = rules_subparsers.add_parser('export', help='Export rules summary to markdown')
    export_parser.add_argument('output_file', help='Output markdown file path')
    
    return parser


async def main() -> int:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = SecuronCLI()
    
    try:
        # Initialize platform
        await cli.initialize()
        
        if args.command == 'scan':
            if args.scan_type == 'file':
                return await cli.scan_file(args.path, args.format, args.severity)
            elif args.scan_type == 'directory':
                return await cli.scan_directory(args.path, args.format, args.severity)
            else:
                print("Error: Must specify 'file' or 'directory' for scan command", file=sys.stderr)
                return 1
        
        elif args.command == 'rules':
            if args.rules_action == 'list':
                return await cli.list_rules(args.status, args.format)
            elif args.rules_action == 'approve':
                return await cli.approve_rule(args.rule_id)
            elif args.rules_action == 'reject':
                return await cli.reject_rule(args.rule_id)
            elif args.rules_action == 'show':
                return await cli.show_rule_details(args.rule_id, args.format)
            elif args.rules_action == 'stats':
                return await cli.show_rule_statistics(args.format)
            elif args.rules_action == 'export':
                return await cli.export_rules_summary(args.output_file)
            else:
                print("Error: Invalid rules action", file=sys.stderr)
                return 1
        
        else:
            print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
    finally:
        # Ensure platform is shutdown
        await cli.shutdown()


def cli_main():
    """Synchronous entry point for CLI"""
    return asyncio.run(main())


if __name__ == '__main__':
    sys.exit(cli_main())