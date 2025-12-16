# Securon CLI Quick Reference 🚀

## Installation

```bash
# Automatic installation
./install.sh                    # Linux/macOS
install.bat                     # Windows

# Manual installation
cd backend && pip install -e .

# Verify
securon --version
```

## Essential Commands

### 🔍 Scanning

```bash
# Basic scanning
securon scan file main.tf
securon scan directory terraform/

# With output formats
securon scan file main.tf --format json
securon scan file main.tf --format summary
securon scan directory terraform/ --format table

# Filter by severity
securon scan file main.tf --severity critical
securon scan file main.tf --severity high
```

### 📋 Rule Management

```bash
# Rule statistics
securon rules stats
securon rules stats --format json

# List rules
securon rules list
securon rules list --status active
securon rules list --status candidate

# Rule details
securon rules show <rule-id>

# Export documentation
securon rules export rules-summary.md
```

### 🎯 Demo Commands

```bash
# Test with demo files
securon scan file demo/terraform/insecure-example.tf
securon scan file demo/terraform/secure-example.tf
securon scan directory demo/terraform/

# Quick overview
securon scan directory demo/terraform/ --format summary
```

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `table` | Detailed tabular (default) | Human review |
| `json` | Machine-readable JSON | CI/CD integration |
| `summary` | Quick counts overview | Quick assessment |

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | No issues | ✅ Continue |
| `1` | Low/Medium issues | ⚠️ Review |
| `2` | High/Critical issues | ❌ Block deployment |

## Severity Levels

| Level | Count | Description |
|-------|-------|-------------|
| `CRITICAL` | 5 | Immediate security risks |
| `HIGH` | 25 | Significant concerns |
| `MEDIUM` | 66 | Important improvements |
| `LOW` | 36 | Best practices |

## Common Workflows

### 🔄 Development Workflow
```bash
# 1. Scan during development
securon scan file main.tf

# 2. Check critical issues only
securon scan file main.tf --severity critical

# 3. Full directory scan before commit
securon scan directory terraform/ --format summary
```

### 🚀 CI/CD Integration
```bash
# Fail build on critical issues
securon scan directory terraform/ --severity critical
if [ $? -ne 0 ]; then exit 1; fi

# Generate JSON report
securon scan directory terraform/ --format json > security-report.json
```

### 📊 Rule Management
```bash
# Check rule coverage
securon rules stats

# Export documentation
securon rules export security-rules.md

# Review candidate rules
securon rules list --status candidate
```

## Help & Support

```bash
# General help
securon --help

# Command-specific help
securon scan --help
securon rules --help

# Version info
securon --version
```

---

**💡 Pro Tip**: Use `--format summary` for quick overviews and `--severity critical` to focus on the most important issues first!

**🎯 Remember**: Exit code `2` means critical issues found - perfect for failing CI/CD pipelines!