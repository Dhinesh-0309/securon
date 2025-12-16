# Securon CLI Documentation

The Securon CLI provides command-line access to the Securon platform's Infrastructure-as-Code (IaC) scanning and security rule management capabilities.

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Required Python packages (install via `pip install -r requirements.txt`)

### Running the CLI

You can run the CLI in several ways:

1. **Direct Python execution:**
   ```bash
   python securon_cli.py [command] [options]
   ```

2. **Using the wrapper script:**
   ```bash
   ./securon [command] [options]
   ```

## Commands

### Scanning Commands

#### Scan a Single File
```bash
python securon_cli.py scan file <path_to_terraform_file> [options]
```

**Options:**
- `--format {json,table,summary}`: Output format (default: table)
- `--severity {low,medium,high,critical}`: Filter results by severity level

**Examples:**
```bash
# Basic file scan with table output
python securon_cli.py scan file terraform/main.tf

# Scan with JSON output
python securon_cli.py scan file terraform/main.tf --format json

# Show only critical issues
python securon_cli.py scan file terraform/main.tf --severity critical

# Summary format for quick overview
python securon_cli.py scan file terraform/main.tf --format summary
```

#### Scan a Directory
```bash
python securon_cli.py scan directory <path_to_directory> [options]
```

**Options:**
- `--format {json,table,summary}`: Output format (default: table)
- `--severity {low,medium,high,critical}`: Filter results by severity level

**Examples:**
```bash
# Scan all Terraform files in a directory
python securon_cli.py scan directory terraform/

# Scan directory with JSON output
python securon_cli.py scan directory terraform/ --format json

# Show only high and critical issues
python securon_cli.py scan directory terraform/ --severity high
```

### Rule Management Commands

#### List Security Rules
```bash
python securon_cli.py rules list [options]
```

**Options:**
- `--status {active,candidate,rejected}`: Filter rules by status
- `--format {json,table,summary}`: Output format (default: table)

**Examples:**
```bash
# List all rules
python securon_cli.py rules list

# List only active rules
python securon_cli.py rules list --status active

# List candidate rules awaiting approval
python securon_cli.py rules list --status candidate

# JSON format for programmatic use
python securon_cli.py rules list --format json
```

#### Show Rule Details
```bash
python securon_cli.py rules show <rule_id> [options]
```

**Options:**
- `--format {json,table,summary}`: Output format (default: table)

**Examples:**
```bash
# Show detailed information about a rule
python securon_cli.py rules show rule-123

# Get rule details in JSON format
python securon_cli.py rules show rule-123 --format json
```

#### Approve a Candidate Rule
```bash
python securon_cli.py rules approve <rule_id>
```

**Example:**
```bash
# Approve a candidate rule to make it active
python securon_cli.py rules approve rule-123
```

#### Reject a Candidate Rule
```bash
python securon_cli.py rules reject <rule_id>
```

**Example:**
```bash
# Reject a candidate rule
python securon_cli.py rules reject rule-456
```

## Output Formats

### Table Format (Default)
Provides a human-readable table with icons and organized sections:
- Color-coded severity levels with icons (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low)
- Grouped results by severity
- Detailed information including file paths, line numbers, and remediation advice

### JSON Format
Machine-readable JSON output suitable for integration with other tools:
- Structured data with timestamps
- Complete issue details
- Easy to parse programmatically

### Summary Format
Concise overview showing:
- Total issue count
- Breakdown by severity level
- Minimal output for quick assessment

## Exit Codes

The CLI uses standard exit codes to indicate scan results:

- `0`: Success (no issues found or operation completed successfully)
- `1`: Medium or low severity issues found, or general error
- `2`: Critical or high severity issues found
- `130`: Operation cancelled by user (Ctrl+C)

## Integration with Rule Engine

The CLI automatically integrates with the Securon Rule Engine:

1. **Active Rules**: All active rules from the Rule Engine are automatically applied during scans
2. **Rule Synchronization**: Changes made through the CLI are immediately reflected in the Rule Engine
3. **Consistent Enforcement**: Rules are consistently applied across CLI and UI interfaces

## Error Handling

The CLI provides comprehensive error handling:

- **File Not Found**: Clear error messages for missing files or directories
- **Invalid Terraform**: Specific parsing errors with line numbers
- **Permission Issues**: Helpful messages for file access problems
- **Network Errors**: Graceful handling of Rule Engine connectivity issues

## Examples and Use Cases

### Development Workflow
```bash
# Quick scan during development
python securon_cli.py scan file main.tf --format summary

# Detailed scan before commit
python securon_cli.py scan directory . --format table

# CI/CD integration (fail on critical issues)
python securon_cli.py scan directory terraform/ --severity critical --format json
```

### Rule Management Workflow
```bash
# Review candidate rules generated by ML Engine
python securon_cli.py rules list --status candidate

# Approve useful rules
python securon_cli.py rules approve ml-generated-rule-001

# Check active rules
python securon_cli.py rules list --status active
```

### Security Audit
```bash
# Comprehensive scan with all details
python securon_cli.py scan directory infrastructure/ --format json > security_audit.json

# Focus on critical issues only
python securon_cli.py scan directory infrastructure/ --severity critical
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Ensure you're running from the correct directory and Python path is set up properly
2. **Permission denied**: Check file permissions and ensure the CLI script is executable
3. **No rules loaded**: Verify the Rule Engine is accessible and contains active rules
4. **Terraform parsing errors**: Check Terraform syntax and file format

### Debug Mode
For detailed error information, you can run Python with verbose output:
```bash
python -v securon_cli.py [command] [options]
```

## Integration Examples

### CI/CD Pipeline (GitHub Actions)
```yaml
- name: Security Scan
  run: |
    python securon_cli.py scan directory terraform/ --format json > scan_results.json
    if [ $? -eq 2 ]; then
      echo "Critical security issues found!"
      exit 1
    fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python securon_cli.py scan directory terraform/ --severity high --format summary
exit $?
```

### Makefile Integration
```makefile
security-scan:
	python securon_cli.py scan directory terraform/ --format table

security-check:
	python securon_cli.py scan directory terraform/ --severity critical --format summary
```