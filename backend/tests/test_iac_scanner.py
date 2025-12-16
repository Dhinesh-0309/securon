"""Tests for IaC Scanner component"""

import pytest
import tempfile
import os
from pathlib import Path

from src.securon.iac_scanner import (
    ConcreteIaCScanner, 
    IaCScannerError,
    TerraformParser,
    TerraformParseError,
    DefaultSecurityRules,
    IaCScannerFactory
)
from src.securon.interfaces.iac_scanner import SecurityRule, ScanResult
from src.securon.interfaces.core_types import Severity, RuleSource, RuleStatus
from datetime import datetime


class TestTerraformParser:
    """Test Terraform file parsing functionality"""
    
    @pytest.fixture
    def parser(self):
        return TerraformParser()
    
    @pytest.fixture
    def sample_terraform_content(self):
        return '''
resource "aws_s3_bucket" "test_bucket" {
  bucket = "my-test-bucket"
  acl    = "private"
}

resource "aws_security_group" "test_sg" {
  name = "test-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
'''
    
    @pytest.mark.asyncio
    async def test_parse_hcl_file(self, parser, sample_terraform_content):
        """Test parsing of HCL Terraform files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write(sample_terraform_content)
            f.flush()
            
            try:
                resources = await parser.parse_file(f.name)
                
                assert len(resources) == 2
                
                # Check S3 bucket resource
                s3_resource = next(r for r in resources if r.type == "aws_s3_bucket")
                assert s3_resource.name == "test_bucket"
                assert s3_resource.configuration["bucket"] == "my-test-bucket"
                assert s3_resource.configuration["acl"] == "private"
                
                # Check Security Group resource
                sg_resource = next(r for r in resources if r.type == "aws_security_group")
                assert sg_resource.name == "test_sg"
                assert sg_resource.configuration["name"] == "test-sg"
                
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_parse_json_file(self, parser):
        """Test parsing of JSON Terraform files"""
        json_content = '''
{
  "resource": {
    "aws_instance": {
      "web": {
        "ami": "ami-12345678",
        "instance_type": "t2.micro"
      }
    }
  }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf.json', delete=False) as f:
            f.write(json_content)
            f.flush()
            
            try:
                resources = await parser.parse_file(f.name)
                
                assert len(resources) == 1
                instance_resource = resources[0]
                assert instance_resource.type == "aws_instance"
                assert instance_resource.name == "web"
                assert instance_resource.configuration["ami"] == "ami-12345678"
                
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_parse_invalid_file(self, parser):
        """Test parsing of invalid Terraform files"""
        invalid_content = '''
resource "aws_s3_bucket" "test" {
  bucket = "test"
  # Missing closing brace
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write(invalid_content)
            f.flush()
            
            try:
                with pytest.raises(TerraformParseError):
                    await parser.parse_file(f.name)
            finally:
                os.unlink(f.name)


class TestIaCScanner:
    """Test IaC Scanner functionality"""
    
    @pytest.fixture
    def scanner(self):
        return ConcreteIaCScanner()
    
    @pytest.fixture
    def vulnerable_terraform_content(self):
        return '''
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}

resource "aws_security_group" "open_sg" {
  name = "open-sg"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "public_db" {
  identifier = "public-db"
  publicly_accessible = true
}
'''
    
    @pytest.mark.asyncio
    async def test_scan_file_with_vulnerabilities(self, scanner, vulnerable_terraform_content):
        """Test scanning a file with security vulnerabilities"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write(vulnerable_terraform_content)
            f.flush()
            
            try:
                results = await scanner.scan_file(f.name)
                
                # Should detect multiple vulnerabilities
                assert len(results) >= 3
                
                # Check for S3 public-read vulnerability
                s3_violations = [r for r in results if r.rule_id == "s3-001"]
                assert len(s3_violations) >= 1
                assert s3_violations[0].severity == Severity.HIGH
                
                # Check for security group unrestricted ingress (SSH, RDP, or database ports)
                sg_violations = [r for r in results if r.rule_id in ["sg-001", "sg-002", "sg-003"]]
                assert len(sg_violations) >= 1
                assert sg_violations[0].severity == Severity.CRITICAL
                
                # Check for RDS public access
                rds_violations = [r for r in results if r.rule_id == "rds-001"]
                assert len(rds_violations) >= 1
                assert rds_violations[0].severity == Severity.HIGH
                
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_scan_secure_file(self, scanner):
        """Test scanning a file with no security vulnerabilities"""
        secure_content = '''
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"
}

resource "aws_security_group" "secure_sg" {
  name = "secure-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write(secure_content)
            f.flush()
            
            try:
                results = await scanner.scan_file(f.name)
                
                # Should have no critical vulnerabilities for these specific rules
                critical_violations = [r for r in results if r.severity == Severity.CRITICAL]
                assert len(critical_violations) == 0
                
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_scan_directory(self, scanner, vulnerable_terraform_content):
        """Test scanning a directory of Terraform files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple Terraform files
            file1_path = os.path.join(temp_dir, "main.tf")
            file2_path = os.path.join(temp_dir, "security.tf")
            
            with open(file1_path, 'w') as f:
                f.write(vulnerable_terraform_content)
            
            with open(file2_path, 'w') as f:
                f.write('''
resource "aws_s3_bucket" "another_bucket" {
  bucket = "another-public-bucket"
  acl    = "public-read"
}
''')
            
            results = await scanner.scan_directory(temp_dir)
            
            # Should find vulnerabilities from both files
            assert len(results) >= 2
            
            # Check that results come from different files
            file_paths = {r.file_path for r in results}
            assert len(file_paths) >= 2
    
    @pytest.mark.asyncio
    async def test_scan_nonexistent_file(self, scanner):
        """Test scanning a file that doesn't exist"""
        with pytest.raises(IaCScannerError, match="File not found"):
            await scanner.scan_file("/nonexistent/file.tf")
    
    @pytest.mark.asyncio
    async def test_scan_invalid_extension(self, scanner):
        """Test scanning a file with invalid extension"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some content")
            f.flush()
            
            try:
                with pytest.raises(IaCScannerError, match="Invalid Terraform file extension"):
                    await scanner.scan_file(f.name)
            finally:
                os.unlink(f.name)
    
    def test_apply_rules(self, scanner):
        """Test applying custom security rules"""
        custom_rule = SecurityRule(
            id="custom-rule",
            name="Custom Rule",
            description="Custom security rule",
            severity=Severity.MEDIUM,
            pattern="resource_type:aws_instance",
            remediation="Custom remediation",
            source=RuleSource.STATIC,
            status=RuleStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        initial_count = len(scanner.get_applied_rules())
        scanner.apply_rules([custom_rule])
        
        # Should have the custom rule plus default rules
        applied_rules = scanner.get_applied_rules()
        assert len(applied_rules) >= 1
        
        # Check that custom rule is present
        custom_rules = [r for r in applied_rules if r.id == "custom-rule"]
        assert len(custom_rules) == 1
        assert custom_rules[0].name == "Custom Rule"
    
    def test_get_supported_resource_types(self, scanner):
        """Test getting supported resource types"""
        supported_types = scanner.get_supported_resource_types()
        
        assert isinstance(supported_types, set)
        assert len(supported_types) > 0
        assert "aws_s3_bucket" in supported_types
        assert "aws_security_group" in supported_types
        assert "aws_iam_policy" in supported_types


class TestDefaultSecurityRules:
    """Test default security rules"""
    
    def test_get_default_rules(self):
        """Test getting default security rules"""
        rules = DefaultSecurityRules.get_default_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        
        # Check that all rules have required fields
        for rule in rules:
            assert rule.id
            assert rule.name
            assert rule.description
            assert rule.severity in [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
            assert rule.pattern
            assert rule.remediation
            assert rule.source == RuleSource.STATIC
            assert rule.status == RuleStatus.ACTIVE
        
        # Check for specific important rules
        rule_ids = {rule.id for rule in rules}
        assert "s3-001" in rule_ids  # S3 Bucket Public Read Access
        assert "sg-001" in rule_ids  # Security Group SSH Open to World
        assert "iam-001" in rule_ids  # IAM Policy Wildcard Actions


class TestIaCScannerFactory:
    """Test IaC Scanner factory"""
    
    def test_create_scanner_without_rule_engine(self):
        """Test creating scanner without rule engine"""
        scanner = IaCScannerFactory.create_scanner()
        
        assert isinstance(scanner, ConcreteIaCScanner)
        
        # Should have default rules applied
        applied_rules = scanner.get_applied_rules()
        assert len(applied_rules) > 0
    
    @pytest.mark.asyncio
    async def test_create_scanner_async_without_rule_engine(self):
        """Test creating scanner asynchronously without rule engine"""
        scanner = await IaCScannerFactory.create_scanner_async()
        
        assert isinstance(scanner, ConcreteIaCScanner)
        
        # Should have default rules applied
        applied_rules = scanner.get_applied_rules()
        assert len(applied_rules) > 0