"""IaC Scanner implementation for Terraform security analysis"""

import os
import re
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from ..interfaces.iac_scanner import IaCScanner, SecurityRule, ScanResult
from ..interfaces.core_types import Severity, TerraformResource
from .terraform_parser import TerraformParser, TerraformParseError
from .security_rules import DefaultSecurityRules, SecurityRuleEngine
from .rule_manager import rule_manager


class IaCScannerError(Exception):
    """Exception raised for IaC scanner operations"""
    pass


class ConcreteIaCScanner(IaCScanner):
    """Concrete implementation of the IaC Scanner"""
    
    def __init__(self):
        self.terraform_parser = TerraformParser()
        self.security_rule_engine = SecurityRuleEngine()
        self.applied_rules: List[SecurityRule] = []
        
        # Load default security rules
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default security rules"""
        try:
            # Try to load comprehensive rules first
            comprehensive_rules = rule_manager.load_comprehensive_rules()
            self.applied_rules.extend(comprehensive_rules)
            # Removed print statement for clean CLI output
        except Exception as e:
            # Fallback to basic rules (silently)
            default_rules = DefaultSecurityRules.get_default_rules()
            self.applied_rules.extend(default_rules)
    
    async def scan_file(self, file_path: str) -> List[ScanResult]:
        """Scan a single Terraform file for security misconfigurations"""
        if not os.path.exists(file_path):
            raise IaCScannerError(f"File not found: {file_path}")
        
        if not file_path.endswith(('.tf', '.tf.json')):
            raise IaCScannerError(f"Invalid Terraform file extension: {file_path}")
        
        try:
            # Parse the Terraform file
            resources = await self.terraform_parser.parse_file(file_path)
            
            # Apply security rules to find misconfigurations
            scan_results = []
            for resource in resources:
                results = await self._apply_rules_to_resource(resource)
                scan_results.extend(results)
            
            return scan_results
            
        except TerraformParseError as e:
            raise IaCScannerError(f"Failed to parse Terraform file {file_path}: {str(e)}")
        except Exception as e:
            raise IaCScannerError(f"Unexpected error scanning file {file_path}: {str(e)}")
    
    async def scan_directory(self, directory_path: str) -> List[ScanResult]:
        """Scan a directory of Terraform files for security misconfigurations"""
        if not os.path.exists(directory_path):
            raise IaCScannerError(f"Directory not found: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise IaCScannerError(f"Path is not a directory: {directory_path}")
        
        # Find all Terraform files in the directory recursively
        terraform_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.tf', '.tf.json')):
                    terraform_files.append(os.path.join(root, file))
        
        if not terraform_files:
            return []  # No Terraform files found
        
        # Scan all files concurrently
        scan_tasks = [self.scan_file(file_path) for file_path in terraform_files]
        results_lists = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        all_results = []
        for i, results in enumerate(results_lists):
            if isinstance(results, Exception):
                # Log the error but continue with other files
                print(f"Error scanning {terraform_files[i]}: {str(results)}")
                continue
            all_results.extend(results)
        
        return all_results
    
    def apply_rules(self, rules: List[SecurityRule]) -> None:
        """Apply security rules to the scanner"""
        # Replace existing applied rules with new ones
        self.applied_rules = rules.copy()
        
        # Always include default rules for baseline security
        default_rules = DefaultSecurityRules.get_default_rules()
        
        # Add default rules that aren't already present
        existing_rule_ids = {rule.id for rule in self.applied_rules}
        for default_rule in default_rules:
            if default_rule.id not in existing_rule_ids:
                self.applied_rules.append(default_rule)
    
    async def _apply_rules_to_resource(self, resource: TerraformResource) -> List[ScanResult]:
        """Apply all security rules to a single Terraform resource"""
        results = []
        seen_violations = set()
        
        for rule in self.applied_rules:
            violations = await self.security_rule_engine.check_rule(rule, resource)
            
            # Deduplicate violations based on rule_id, file_path, and line_number
            for violation in violations:
                violation_key = (violation.rule_id, violation.file_path, violation.line_number, violation.description)
                if violation_key not in seen_violations:
                    seen_violations.add(violation_key)
                    results.append(violation)
        
        return results
    
    def get_applied_rules(self) -> List[SecurityRule]:
        """Get the currently applied security rules"""
        return self.applied_rules.copy()
    
    def get_supported_resource_types(self) -> Set[str]:
        """Get the set of supported Terraform resource types"""
        return {
            'aws_s3_bucket',
            'aws_security_group',
            'aws_iam_role',
            'aws_iam_policy',
            'aws_instance',
            'aws_db_instance',
            'aws_elasticsearch_domain',
            'aws_cloudtrail',
            'aws_kms_key',
            'aws_lambda_function',
            'aws_api_gateway_rest_api',
            'aws_cloudfront_distribution',
            'aws_elb',
            'aws_alb',
            'aws_rds_cluster',
            'aws_redshift_cluster'
        }