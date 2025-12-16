# Securon Platform 🛡️

A lightweight, product-focused cloud security platform that demonstrates adaptive DevSecOps security without requiring live cloud access. The system integrates static Infrastructure-as-Code (IaC) scanning with machine-learning-based runtime behavior analysis in a closed-loop workflow.

## ✨ Features

- **🔍 Static IaC Analysis**: 132+ comprehensive security rules covering 35+ AWS services
- **🤖 ML-Based Anomaly Detection**: Unsupervised learning using Isolation Forest algorithm
- **🔄 Adaptive Rule Engine**: ML findings automatically generate new security rules
- **📊 Multiple Interfaces**: CLI, Web UI, and API access
- **📋 Compliance Ready**: PCI-DSS, SOC2, HIPAA, GDPR support
- **🚀 CI/CD Integration**: Exit codes for automated pipeline integration

## 🚀 Quick Start

### Installation

Choose your preferred installation method:

#### Option 1: Automatic Installation (Recommended)

**Linux/macOS:**
```bash
./install.sh
```

**Windows:**
```cmd
install.bat
```

#### Option 2: Manual Installation

```bash
cd backend
pip install -e .
```

#### Option 3: Python Installation Script

```bash
cd backend
python install.py
```

### Verify Installation

```bash
securon --version
```

## 📋 CLI Commands

### Rule Management

```bash
# Show rule statistics
securon rules stats
securon rules stats --format json

# List security rules
securon rules list
securon rules list --status active
securon rules list --status candidate

# Show rule details
securon rules show <rule-id>

# Export rules summary
securon rules export rules-summary.md

# Approve/reject candidate rules
securon rules approve <rule-id>
securon rules reject <rule-id>
```

### Infrastructure Scanning

```bash
# Scan a single Terraform file
securon scan file terraform/main.tf
securon scan file terraform/main.tf --format json
securon scan file terraform/main.tf --format summary

# Scan a directory
securon scan directory terraform/
securon scan directory terraform/ --format table

# Filter by severity
securon scan file main.tf --severity critical
securon scan file main.tf --severity high
```

### Output Formats

- **`table`** (default): Detailed tabular output
- **`json`**: Machine-readable JSON format
- **`summary`**: Quick overview with counts

## 🔍 Demo & Testing

### Demo Files

The platform includes demonstration Terraform files with **clean, developer-focused output**:

```bash
# Quick summary (perfect for CI/CD)
securon scan file demo/terraform/insecure-example.tf --format summary
# Output: 🔍 demo/terraform/insecure-example.tf - 26 issues (🔴 3 🟠 7 🟡 12 🟢 4)

# Detailed analysis for developers
securon scan file demo/terraform/insecure-example.tf --format table
# Shows: File:line locations, descriptions, and fix instructions

# Focus on critical issues only
securon scan file demo/terraform/insecure-example.tf --severity critical
# Shows: Only blocking security issues

# Scan entire directory
securon scan directory demo/terraform/ --format summary
# Output: 🔍 demo/terraform/ - 91 issues (🔴 15 🟠 23 🟡 36 🟢 17)
```

### Expected Results

- **Insecure file**: 26 security issues - `🔴 3 🟠 7 🟡 12 🟢 4`
- **Secure file**: 34 issues (shows comprehensive coverage) - `🔴 6 🟠 9 🟡 13 🟢 6`
- **Mixed file**: Combination of secure and insecure patterns
- **Clean output**: No logging noise, only essential security information

## 📊 Security Rules Coverage

### 132 Comprehensive Rules Across 35+ AWS Services

| Service | Rules | Key Areas |
|---------|-------|-----------|
| **S3** | 10 | Public access, encryption, versioning, lifecycle |
| **IAM** | 9 | Permissions, MFA, access keys, cross-account trust |
| **EC2** | 8 | Public IPs, encryption, IMDS, monitoring |
| **Security Groups** | 8 | SSH/RDP access, database ports, protocols |
| **RDS** | 8 | Public access, encryption, backups, monitoring |
| **Lambda** | 6 | Public access, VPC, tracing, concurrency |
| **ELB** | 6 | SSL/TLS, logging, health checks |
| **VPC** | 5 | Flow logs, DNS, default security groups |
| **CloudFront** | 5 | HTTPS redirect, WAF, OAI |
| **And 26 more...** | 67 | Comprehensive AWS coverage |

### Severity Distribution

- **CRITICAL**: 5 rules (3.8%) - Immediate security risks
- **HIGH**: 25 rules (18.9%) - Significant security concerns  
- **MEDIUM**: 66 rules (50.0%) - Important security improvements
- **LOW**: 36 rules (27.3%) - Best practice recommendations

### Compliance Frameworks

- **PCI-DSS**: Payment Card Industry Data Security Standard
- **SOC2**: Service Organization Control 2
- **HIPAA**: Health Insurance Portability and Accountability Act
- **GDPR**: General Data Protection Regulation

## 🔧 CI/CD Integration

The CLI returns different exit codes for pipeline integration:

- `0`: No issues found ✅
- `1`: Low/Medium severity issues found ⚠️
- `2`: High/Critical severity issues found ❌

### Example CI/CD Usage

```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    securon scan directory terraform/
    if [ $? -eq 2 ]; then
      echo "Critical security issues found!"
      exit 1
    fi
```

```bash
# Jenkins/Shell example
securon scan file main.tf --severity critical
if [ $? -ne 0 ]; then
    echo "Critical security issues found - failing build"
    exit 1
fi
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │   Web Interface │    │  API Interface  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Core Platform  │
                    └─────────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
    │IaC Scanner│      │ ML Engine │      │Rule Engine│
    └───────────┘      └───────────┘      └───────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    ┌─────────▼───────┐
                    │  Data Storage   │
                    └─────────────────┘
```

## 🛠️ Development

### Project Structure

```
securon-platform/
├── backend/                 # Python backend
│   ├── src/securon/        # Main package
│   ├── data/rules/         # Security rules
│   ├── tests/              # Test suite
│   └── pyproject.toml      # Package configuration
├── frontend/               # React frontend
├── demo/                   # Demo Terraform files
├── install.sh             # Linux/macOS installer
├── install.bat            # Windows installer
└── README.md              # This file
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Adding New Rules

1. Edit `backend/data/rules/comprehensive_rules.json`
2. Add rule definition with pattern and remediation
3. Test with demo files
4. Update documentation

## 📚 Documentation

- **[Security Rules Summary](demo/SECURITY_RULES_SUMMARY.md)**: Complete rule documentation
- **[Comprehensive Rules Guide](demo/COMPREHENSIVE_SECURITY_RULES.md)**: Detailed coverage information
- **[API Documentation](backend/src/securon/api/)**: REST API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the `/demo` directory for examples
- **CLI Help**: Run `securon --help` for command reference

---

**🎯 Mission**: Ensure no security vulnerability passes into deployment with comprehensive static analysis and adaptive machine learning.

**✨ Happy Scanning!**