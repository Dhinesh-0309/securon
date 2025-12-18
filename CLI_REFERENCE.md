# Securon CLI - Complete Command Reference 🛡️

This guide covers all CLI commands and usage patterns for the Securon platform.

## 📋 Table of Contents

- [Basic Usage](#basic-usage)
- [Scanning Commands](#scanning-commands)
- [Rule Management](#rule-management)
- [Output Formats](#output-formats)
- [Advanced Usage](#advanced-usage)
- [CI/CD Integration](#cicd-integration)
- [Examples](#examples)

## 🚀 Basic Usage

### Installation Verification

```bash
# Check if Securon is installed
securon --version

# Show general help
securon --help

# Show help for specific commands
securon scan --help
securon rules --help
```

### Quick Start

```bash
# Scan a single file (basic)
securon scan file terraform/main.tf

# Scan a directory (basic)
securon scan directory terraform/

# Show rule statistics
securon rules stats
```

## 🔍 Scanning Commands

### File Scanning

```bash
# Basic file scan
securon scan file <path-to-terraform-file>

# Examples
securon scan file main.tf
securon scan file terraform/vpc.tf
securon scan file demo/terraform/insecure-example.tf
```

### Directory Scanning

```bash
# Basic directory scan
securon scan directory <path-to-directory>

# Examples
securon scan directory terraform/
securon scan directory demo/terraform/
securon scan directory . # Current directory
```

### Scanning with Output Formats

```bash
# Table format (default) - detailed output
securon scan file main.tf --format table
securon scan file main.tf --format detailed

# JSON format - machine readable
securon scan file main.tf --format json

# Summary format - quick overview
securon scan file main.tf --format summary
securon scan directory terraform/ --format summary
```

### Filtering by Severity

```bash
# Show only critical issues
securon scan file main.tf --severity critical

# Show high and critical issues
securon scan file main.tf --severity high

# Show medium and above
securon scan file main.tf --severity medium

# Show all issues (default)
securon scan file main.tf --severity low
```

### Combined Options

```bash
# Critical issues in JSON format
securon scan file main.tf --severity critical --format json

# Directory scan with summary format
securon scan directory terraform/ --format summary

# High severity issues in table format
securon scan directory terraform/ --severity high --format table
```

## 📊 Rule Management

### Rule Statistics

```bash
# Show rule statistics (human readable)
securon rules stats

# Show rule statistics in JSON format
securon rules stats --format json
```

### Listing Rules

```bash
# List all security rules
securon rules list

# List only active rules
securon rules list --status active

# List candidate rules (from ML)
securon rules list --status candidate

# List rules by severity
securon rules list --severity critical
securon rules list --severity high
```

### Rule Details

```bash
# Show details for a specific rule
securon rules show <rule-id>

# Examples
securon rules show S3-001
securon rules show IAM-005
securon rules show EC2-003
```

### Rule Export

```bash
# Export rules summary to markdown
securon rules export rules-summary.md

# Export to different formats
securon rules export rules.json --format json
securon rules export rules.txt --format text
```

### Rule Approval (ML Integration)

```bash
# Approve a candidate rule (from ML analysis)
securon rules approve <rule-id>

# Reject a candidate rule
securon rules reject <rule-id>

# Examples
securon rules approve ML-001
securon rules reject ML-002
```

## 📄 Output Formats

### Table Format (Default)

```bash
securon scan file main.tf --format table
```

**Output Example:**
```
┌─────────────────┬──────────┬─────────────────────────────────────┬──────────────────────────────────────┐
│ File:Line       │ Severity │ Rule ID                             │ Description                          │
├─────────────────┼──────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ main.tf:15      │ CRITICAL │ S3-001                              │ S3 bucket allows public read access │
│ main.tf:23      │ HIGH     │ IAM-003                             │ IAM policy allows wildcard actions  │
└─────────────────┴──────────┴─────────────────────────────────────┴──────────────────────────────────────┘
```

### JSON Format

```bash
securon scan file main.tf --format json
```

**Output Example:**
```json
{
  "scan_results": {
    "file": "main.tf",
    "issues": [
      {
        "line": 15,
        "severity": "CRITICAL",
        "rule_id": "S3-001",
        "description": "S3 bucket allows public read access",
        "remediation": "Set bucket ACL to private"
      }
    ],
    "summary": {
      "total_issues": 5,
      "critical": 1,
      "high": 2,
      "medium": 1,
      "low": 1
    }
  }
}
```

### Summary Format

```bash
securon scan file main.tf --format summary
```

**Output Example:**
```
🔍 main.tf - 5 issues (🔴 1 🟠 2 🟡 1 🟢 1)
```

## 🔧 Advanced Usage

### Environment Variables

```bash
# Set custom rules directory
export SECURON_RULES_DIR=/path/to/custom/rules

# Set output format default
export SECURON_DEFAULT_FORMAT=json

# Set severity filter default
export SECURON_DEFAULT_SEVERITY=high
```

### Configuration Files

Create `.securon.yml` in your project root:

```yaml
# Default scanning options
default_format: table
default_severity: medium
exclude_patterns:
  - "*.backup.tf"
  - "test_*.tf"

# Custom rule directories
custom_rules:
  - "./custom-rules/"
  - "/shared/security-rules/"

# CI/CD settings
ci_mode: true
fail_on_high: true
fail_on_critical: true
```

### Batch Operations

```bash
# Scan multiple files
for file in terraform/*.tf; do
    echo "Scanning $file"
    securon scan file "$file" --format summary
done

# Scan and save results
securon scan directory terraform/ --format json > scan-results.json

# Filter and process results
securon scan file main.tf --severity critical --format json | jq '.scan_results.issues'
```

## 🚀 CI/CD Integration

### Exit Codes

The CLI returns different exit codes for automation:

- `0`: No issues found ✅
- `1`: Low/Medium severity issues found ⚠️
- `2`: High/Critical severity issues found ❌

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Securon
        run: |
          cd backend
          pip install -e .
      
      - name: Security Scan
        run: |
          securon scan directory terraform/ --format summary
          exit_code=$?
          if [ $exit_code -eq 2 ]; then
            echo "Critical security issues found!"
            exit 1
          elif [ $exit_code -eq 1 ]; then
            echo "Security issues found - review recommended"
          fi
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                script {
                    def exitCode = sh(
                        script: 'securon scan directory terraform/ --severity critical',
                        returnStatus: true
                    )
                    
                    if (exitCode == 2) {
                        error("Critical security issues found!")
                    } else if (exitCode == 1) {
                        echo "Security issues found - review recommended"
                    }
                }
            }
        }
    }
}
```

### GitLab CI

```yaml
security_scan:
  stage: test
  script:
    - cd backend && pip install -e .
    - securon scan directory terraform/ --format json > security-report.json
    - |
      if [ $? -eq 2 ]; then
        echo "Critical security issues found!"
        exit 1
      fi
  artifacts:
    reports:
      junit: security-report.json
    when: always
```

## 📚 Examples

### Basic Scanning Examples

```bash
# Quick security check
securon scan file main.tf --format summary

# Detailed analysis
securon scan file main.tf --format table

# Focus on critical issues only
securon scan file main.tf --severity critical

# Scan entire project
securon scan directory . --format summary
```

### Rule Management Examples

```bash
# Check rule coverage
securon rules stats

# Find specific rules
securon rules list | grep S3
securon rules list --severity critical

# Export documentation
securon rules export security-rules.md
```

### CI/CD Examples

```bash
# Pre-commit hook
securon scan file terraform/main.tf --severity high
if [ $? -ne 0 ]; then
    echo "Security issues found - commit blocked"
    exit 1
fi

# Build pipeline check
securon scan directory terraform/ --format json > results.json
critical_count=$(jq '.scan_results.summary.critical' results.json)
if [ "$critical_count" -gt 0 ]; then
    echo "Critical issues found: $critical_count"
    exit 1
fi
```

### Automation Examples

```bash
# Daily security report
#!/bin/bash
DATE=$(date +%Y-%m-%d)
securon scan directory terraform/ --format json > "security-report-$DATE.json"
securon rules stats --format json > "rules-stats-$DATE.json"

# Security metrics collection
securon scan directory . --format json | \
jq '.scan_results.summary' > security-metrics.json
```

## 🎯 Common Use Cases

### Development Workflow

```bash
# Before committing
securon scan file terraform/new-feature.tf --severity high

# Code review preparation
securon scan directory terraform/ --format summary > review-notes.txt

# Security documentation
securon rules export project-security-rules.md
```

### Security Auditing

```bash
# Full security audit
securon scan directory . --format json > full-audit.json

# Critical issues only
securon scan directory . --severity critical --format table

# Rule coverage analysis
securon rules stats --format json
```

### Compliance Reporting

```bash
# Generate compliance report
securon scan directory terraform/ --format json > compliance-report.json
securon rules list --format json > rules-inventory.json

# Export rule documentation
securon rules export compliance-rules.md
```

## 🆘 Troubleshooting

### Common Issues

```bash
# Command not found
which securon
# If not found, reinstall: cd backend && pip install -e .

# Permission errors
chmod +x install.sh
sudo ./install.sh

# Module import errors
cd backend
pip install -r requirements.txt
pip install -e .
```

### Debug Mode

```bash
# Enable verbose output
securon --verbose scan file main.tf

# Debug rule loading
securon --debug rules list

# Trace execution
securon --trace scan directory terraform/
```

## 📊 Performance Tips

```bash
# Faster scanning for large directories
securon scan directory terraform/ --format summary

# Parallel scanning (custom script)
find terraform/ -name "*.tf" | xargs -P 4 -I {} securon scan file {}

# Cache results for repeated scans
securon scan directory terraform/ --cache --format json
```

---

## 🎉 Summary

The Securon CLI provides comprehensive security scanning with:

- **132+ security rules** across 35+ AWS services
- **Multiple output formats** (table, JSON, summary)
- **Severity filtering** (critical, high, medium, low)
- **CI/CD integration** with proper exit codes
- **Rule management** and ML-based adaptive rules
- **Flexible configuration** options

**Happy scanning! 🛡️✨**