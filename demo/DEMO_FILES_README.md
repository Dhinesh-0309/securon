# Securon Platform - Demonstration Files

This directory contains comprehensive demonstration files showcasing the security analysis capabilities of the Securon Platform. These files are designed to trigger various security alerts and demonstrate the platform's ability to detect threats and misconfigurations.

## 📊 Log Files for ML Analysis

### 1. VPC Flow Logs - Suspicious Activity (`logs/vpc-flow-suspicious-activity.json`)
**Demonstrates:** Port scanning and reconnaissance attempts
- **Threat Type:** Network reconnaissance
- **Pattern:** Single IP scanning multiple targets on SSH port
- **Expected Detections:** 
  - Suspicious IP behavior
  - Port scanning activity
  - Potential brute force attempts

### 2. CloudTrail Logs - Brute Force Attack (`logs/cloudtrail-brute-force-attempt.json`)
**Demonstrates:** Authentication brute force attempts
- **Threat Type:** Credential attacks
- **Pattern:** Multiple failed login attempts from same IP
- **Expected Detections:**
  - Brute force attack patterns
  - Suspicious authentication behavior
  - Account enumeration attempts

### 3. WAF Logs - DDoS and Injection Attacks (`logs/waf-ddos-attack.json`)
**Demonstrates:** Web application attacks
- **Threat Type:** Application layer attacks
- **Pattern:** Rate limiting triggers and SQL injection attempts
- **Expected Detections:**
  - DDoS attack patterns
  - SQL injection attempts
  - Malicious user agents

### 4. ALB Access Logs - Web Reconnaissance (`logs/alb-access-anomalies.json`)
**Demonstrates:** Web application reconnaissance
- **Threat Type:** Information gathering
- **Pattern:** Scanning for common vulnerabilities and admin panels
- **Expected Detections:**
  - Directory traversal attempts
  - Admin panel discovery
  - Automated scanning behavior

## 🏗️ Terraform Files for IaC Security Scanning

### 1. Insecure S3 Bucket (`terraform/insecure-s3-bucket.tf`)
**Security Issues Demonstrated:**
- ❌ Public read access enabled
- ❌ No versioning configured
- ❌ No encryption at rest
- ❌ No access logging
- ❌ Public bucket policy
- ❌ No lifecycle policy
- ❌ No cross-region replication
- ❌ No object lock for compliance

**Expected Violations:** 8+ security rule violations

### 2. Vulnerable Security Groups (`terraform/vulnerable-security-groups.tf`)
**Security Issues Demonstrated:**
- 🔴 **CRITICAL:** SSH (22) open to 0.0.0.0/0
- 🔴 **CRITICAL:** RDP (3389) open to 0.0.0.0/0
- 🔴 **CRITICAL:** Database ports (3306, 5432, 27017) open to internet
- 🟠 **HIGH:** FTP (21) and Telnet (23) enabled
- 🟡 **MEDIUM:** SNMP (161) accessible from internet

**Expected Violations:** 10+ security rule violations

### 3. Insecure EC2 Instances (`terraform/insecure-ec2-instances.tf`)
**Security Issues Demonstrated:**
- ❌ No IAM role attached (likely using access keys)
- ❌ Public IP assignment
- ❌ Unencrypted EBS volumes
- ❌ No detailed monitoring
- ❌ Hardcoded credentials in user data
- ❌ IMDSv1 enabled (less secure)
- ❌ Database in public subnet
- ❌ No termination protection

**Expected Violations:** 12+ security rule violations

### 4. Vulnerable IAM Policies (`terraform/vulnerable-iam-policies.tf`)
**Security Issues Demonstrated:**
- 🔴 **CRITICAL:** Overly permissive policies (Admin access)
- 🔴 **CRITICAL:** IAM users with programmatic access
- 🔴 **CRITICAL:** Public access in S3 policies
- 🔴 **CRITICAL:** Cross-account trust without conditions
- ❌ Weak password policy
- ❌ Excessive Lambda permissions
- ❌ PowerUser access for EC2 roles

**Expected Violations:** 15+ security rule violations

### 5. Insecure RDS Database (`terraform/insecure-rds-database.tf`)
**Security Issues Demonstrated:**
- 🔴 **CRITICAL:** Publicly accessible database
- 🔴 **CRITICAL:** No encryption at rest
- 🔴 **CRITICAL:** Weak credentials in plain text
- ❌ No backup retention
- ❌ Older database engine version
- ❌ No audit logging
- ❌ SSL not enforced
- ❌ No deletion protection
- ❌ Database in public subnet

**Expected Violations:** 20+ security rule violations

## 🎯 How to Use These Files

### For Log Analysis:
1. Navigate to the **AI Log Analyzer** section
2. Upload any of the log files from the `logs/` directory
3. Watch the ML processing pipeline analyze the data
4. Review detected anomalies and generated security rules

### For IaC Scanning:
1. Navigate to the **IaC Scanner** section
2. Upload any of the Terraform files from the `terraform/` directory
3. Review the security violations detected
4. Examine the severity levels and remediation suggestions

## 📈 Expected Results Summary

| File Type | Expected Anomalies | Expected Violations | Severity Levels |
|-----------|-------------------|-------------------|-----------------|
| VPC Flow Logs | 1-2 | N/A | Medium-High |
| CloudTrail Logs | 1-2 | N/A | High |
| WAF Logs | 2-3 | N/A | High-Critical |
| ALB Logs | 1-2 | N/A | Medium |
| S3 Terraform | N/A | 8+ | Low-Medium |
| Security Groups | N/A | 10+ | Medium-Critical |
| EC2 Instances | N/A | 12+ | Medium-High |
| IAM Policies | N/A | 15+ | High-Critical |
| RDS Database | N/A | 20+ | High-Critical |

## 🔍 Key Features Demonstrated

### ML-Powered Log Analysis:
- **Pattern Recognition:** Identifies suspicious behavior patterns
- **Anomaly Detection:** Detects deviations from normal baselines
- **Threat Classification:** Categorizes threats by type and severity
- **Rule Generation:** Automatically generates security rules

### IaC Security Scanning:
- **150+ Security Rules:** Comprehensive rule coverage
- **Multi-Cloud Support:** AWS, Azure, GCP configurations
- **Compliance Frameworks:** CIS, NIST, SOC 2 alignment
- **Remediation Guidance:** Actionable fix recommendations

## 🚀 Demo Workflow

1. **Start with Log Analysis:**
   - Upload `vpc-flow-suspicious-activity.json`
   - Demonstrate ML processing pipeline
   - Show anomaly detection results

2. **Progress to IaC Scanning:**
   - Upload `vulnerable-security-groups.tf`
   - Highlight critical security violations
   - Explain remediation recommendations

3. **Advanced Scenarios:**
   - Combine multiple log files for complex analysis
   - Upload complete infrastructure configurations
   - Demonstrate rule management and approval workflow

## 📝 Notes for Reviewers

- All files contain **intentional security vulnerabilities** for demonstration purposes
- **Never use these configurations in production environments**
- Files are designed to trigger maximum security alerts for comprehensive testing
- Each file focuses on specific security domains for targeted demonstration
- Real-world scenarios would typically have fewer concentrated vulnerabilities

## 🔧 Customization

To create additional demonstration files:
1. Follow the JSON structure for log files with `timestamp` and `raw_data` fields
2. Use standard Terraform syntax for infrastructure files
3. Include comments explaining security issues for educational purposes
4. Test files with the platform to verify expected detection rates