#!/usr/bin/env python3
"""Demo script showing IaC Scanner integration with Rule Engine"""

import asyncio
import sys
import os
import tempfile
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from securon.iac_scanner import IaCScannerFactory, ConcreteIaCScanner
from securon.rule_engine import ConcreteRuleEngine
from securon.interfaces.iac_scanner import SecurityRule
from securon.interfaces.core_types import Severity, RuleSource, RuleStatus


async def demo_iac_scanner_with_rule_engine():
    """Demonstrate IaC Scanner integration with Rule Engine"""
    
    print("=== Securon IaC Scanner Demo ===")
    print()
    
    # Create a Rule Engine instance
    rule_engine = ConcreteRuleEngine()
    
    # Add a custom rule to the Rule Engine
    custom_rule = SecurityRule(
        id="custom-s3-versioning",
        name="S3 Bucket Versioning Required",
        description="S3 buckets should have versioning enabled for data protection",
        severity=Severity.MEDIUM,
        pattern="config:versioning.enabled=false",
        remediation="Enable versioning on S3 bucket by setting versioning.enabled = true",
        source=RuleSource.ML_GENERATED,
        status=RuleStatus.ACTIVE,
        created_at=datetime.now()
    )
    
    await rule_engine.add_rule(custom_rule)
    print(f"Added custom rule: {custom_rule.name}")
    
    # Create IaC Scanner with Rule Engine integration
    scanner = await IaCScannerFactory.create_scanner_async(rule_engine)
    
    # Create a sample Terraform file with various security issues
    terraform_content = '''
# Vulnerable Terraform configuration for demonstration

resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-company-data-bucket"
  acl    = "public-read"  # VULNERABILITY: Public read access
  
  versioning {
    enabled = false  # VULNERABILITY: No versioning
  }
}

resource "aws_security_group" "web_sg" {
  name_prefix = "web-"
  description = "Security group for web servers"
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # VULNERABILITY: Open to internet
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # VULNERABILITY: Open to internet
  }
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # VULNERABILITY: SSH open to internet
  }
}

resource "aws_iam_policy" "admin_access" {
  name        = "AdminAccess"
  description = "Full admin access policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"          # VULNERABILITY: Wildcard permissions
        Resource = "*"
      }
    ]
  })
}

resource "aws_db_instance" "main_db" {
  identifier = "main-database"
  engine     = "mysql"
  
  publicly_accessible = true  # VULNERABILITY: Database exposed to internet
  
  backup_retention_period = 0  # Poor practice: No backups
}

resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  associate_public_ip_address = true
  
  security_groups = [aws_security_group.web_sg.name]
}
'''
    
    # Write the Terraform content to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(terraform_content)
        temp_file = f.name
    
    try:
        print(f"\nScanning Terraform file: {temp_file}")
        print("=" * 60)
        
        # Scan the file for security issues
        results = await scanner.scan_file(temp_file)
        
        print(f"Found {len(results)} security issues:")
        print()
        
        # Group results by severity
        by_severity = {}
        for result in results:
            if result.severity not in by_severity:
                by_severity[result.severity] = []
            by_severity[result.severity].append(result)
        
        # Display results grouped by severity
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        
        for severity in severity_order:
            if severity in by_severity:
                print(f"🔴 {severity} Issues ({len(by_severity[severity])}):")
                for result in by_severity[severity]:
                    print(f"  • {result.description}")
                    print(f"    Rule: {result.rule_id}")
                    print(f"    Line: {result.line_number}")
                    print(f"    Fix: {result.remediation}")
                    print()
        
        # Show applied rules
        applied_rules = scanner.get_applied_rules()
        print(f"Applied Security Rules ({len(applied_rules)}):")
        for rule in applied_rules:
            status_icon = "✅" if rule.status == RuleStatus.ACTIVE else "⏳"
            print(f"  {status_icon} {rule.name} ({rule.severity})")
        
        print()
        print("Demo completed successfully!")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


async def demo_directory_scanning():
    """Demonstrate directory scanning capabilities"""
    
    print("\n=== Directory Scanning Demo ===")
    
    # Create a temporary directory with multiple Terraform files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")
        
        # Create main.tf
        main_tf = os.path.join(temp_dir, "main.tf")
        with open(main_tf, 'w') as f:
            f.write('''
resource "aws_s3_bucket" "app_bucket" {
  bucket = "my-app-bucket"
  acl    = "public-read"
}
''')
        
        # Create security.tf
        security_tf = os.path.join(temp_dir, "security.tf")
        with open(security_tf, 'w') as f:
            f.write('''
resource "aws_security_group" "app_sg" {
  name = "app-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
''')
        
        # Create database.tf
        database_tf = os.path.join(temp_dir, "database.tf")
        with open(database_tf, 'w') as f:
            f.write('''
resource "aws_db_instance" "app_db" {
  identifier = "app-database"
  publicly_accessible = true
}
''')
        
        # Scan the entire directory
        scanner = ConcreteIaCScanner()
        results = await scanner.scan_directory(temp_dir)
        
        print(f"\nScanned directory with {len(os.listdir(temp_dir))} Terraform files")
        print(f"Found {len(results)} total security issues:")
        
        # Group by file
        by_file = {}
        for result in results:
            filename = os.path.basename(result.file_path)
            if filename not in by_file:
                by_file[filename] = []
            by_file[filename].append(result)
        
        for filename, file_results in by_file.items():
            print(f"\n📄 {filename} ({len(file_results)} issues):")
            for result in file_results:
                print(f"  • {result.severity}: {result.description}")


if __name__ == "__main__":
    asyncio.run(demo_iac_scanner_with_rule_engine())
    asyncio.run(demo_directory_scanning())