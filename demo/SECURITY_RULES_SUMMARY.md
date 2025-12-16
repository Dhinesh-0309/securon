# Securon Security Rules Summary

**Total Rules:** 63

## Severity Distribution

- **LOW:** 15 rules
- **MEDIUM:** 30 rules
- **HIGH:** 13 rules
- **CRITICAL:** 5 rules

## Category Distribution

- **S3:** 7 rules
- **EC2:** 5 rules
- **Security Groups:** 5 rules
- **IAM:** 6 rules
- **RDS:** 5 rules
- **VPC:** 3 rules
- **CloudTrail:** 3 rules
- **KMS:** 2 rules
- **Lambda:** 3 rules
- **ELB:** 3 rules
- **CloudFront:** 2 rules
- **Route53:** 1 rules
- **SNS:** 2 rules
- **SQS:** 2 rules
- **ElastiCache:** 2 rules
- **EKS:** 2 rules
- **ECS:** 2 rules
- **API Gateway:** 2 rules
- **CloudWatch:** 2 rules
- **Config:** 1 rules
- **GuardDuty:** 1 rules
- **Secrets Manager:** 2 rules

## Rules by Category

### S3

- **s3-001** (HIGH): S3 Bucket Public Read Access
  - S3 bucket should not have public-read ACL
  - *Remediation:* Remove public-read ACL and use bucket policies for controlled access
- **s3-002** (CRITICAL): S3 Bucket Public Write Access
  - S3 bucket should not have public-write ACL
  - *Remediation:* Remove public-write ACL to prevent unauthorized data modification
- **s3-003** (MEDIUM): S3 Bucket Encryption Disabled
  - S3 bucket should have server-side encryption enabled
  - *Remediation:* Enable server-side encryption using AES256 or KMS
- **s3-004** (LOW): S3 Bucket Versioning Disabled
  - S3 bucket should have versioning enabled
  - *Remediation:* Enable versioning to protect against accidental deletion
- **s3-005** (LOW): S3 Bucket Logging Disabled
  - S3 bucket should have access logging enabled
  - *Remediation:* Enable access logging for audit and compliance
- **s3-006** (MEDIUM): S3 Bucket MFA Delete Disabled
  - S3 bucket should have MFA delete enabled for critical data
  - *Remediation:* Enable MFA delete for additional protection
- **s3-007** (HIGH): S3 Bucket Public Access Block Disabled
  - S3 bucket should have public access block enabled
  - *Remediation:* Enable all public access block settings

### EC2

- **ec2-001** (MEDIUM): EC2 Instance Public IP
  - EC2 instance should not have public IP unless required
  - *Remediation:* Use private subnets and NAT gateway for outbound access
- **ec2-002** (MEDIUM): EC2 Instance Unencrypted EBS
  - EC2 instance should have encrypted EBS volumes
  - *Remediation:* Enable EBS encryption for data at rest protection
- **ec2-003** (MEDIUM): EC2 Instance IMDSv1 Enabled
  - EC2 instance should use IMDSv2 only
  - *Remediation:* Set http_tokens to 'required' to enforce IMDSv2
- **ec2-004** (LOW): EC2 Instance Monitoring Disabled
  - EC2 instance should have detailed monitoring enabled
  - *Remediation:* Enable detailed monitoring for better observability
- **ec2-005** (MEDIUM): EC2 Instance No Key Pair
  - EC2 instance should have a key pair for secure access
  - *Remediation:* Specify a key pair for secure SSH access

### Security Groups

- **sg-001** (CRITICAL): Security Group SSH Open to World
  - Security group should not allow SSH (port 22) from 0.0.0.0/0
  - *Remediation:* Restrict SSH access to specific IP ranges or use bastion hosts
- **sg-002** (CRITICAL): Security Group RDP Open to World
  - Security group should not allow RDP (port 3389) from 0.0.0.0/0
  - *Remediation:* Restrict RDP access to specific IP ranges
- **sg-003** (CRITICAL): Security Group Database Port Open
  - Security group should not allow database ports from 0.0.0.0/0
  - *Remediation:* Restrict database access to application security groups only
- **sg-004** (MEDIUM): Security Group All Traffic Outbound
  - Security group should not allow all outbound traffic
  - *Remediation:* Define specific outbound rules based on requirements
- **sg-005** (LOW): Security Group No Description
  - Security group rules should have descriptions
  - *Remediation:* Add descriptions to all security group rules for documentation

### IAM

- **iam-001** (HIGH): IAM Policy Wildcard Actions
  - IAM policy should not use wildcard (*) actions
  - *Remediation:* Use specific actions following principle of least privilege
- **iam-002** (HIGH): IAM Policy Wildcard Resources
  - IAM policy should not use wildcard (*) resources
  - *Remediation:* Specify exact resource ARNs instead of wildcards
- **iam-003** (MEDIUM): IAM User Without MFA
  - IAM users should have MFA enabled
  - *Remediation:* Enable MFA for all IAM users
- **iam-004** (CRITICAL): IAM Root Access Keys
  - Root account should not have access keys
  - *Remediation:* Delete root access keys and use IAM users instead
- **iam-005** (MEDIUM): IAM Password Policy Weak
  - IAM password policy should enforce strong passwords
  - *Remediation:* Set minimum length, complexity, and rotation requirements
- **iam-006** (HIGH): IAM Role Cross-Account Trust
  - IAM role should not allow cross-account access without conditions
  - *Remediation:* Add conditions to cross-account trust relationships

### RDS

- **rds-001** (HIGH): RDS Instance Public Access
  - RDS instance should not be publicly accessible
  - *Remediation:* Set publicly_accessible to false
- **rds-002** (HIGH): RDS Instance Unencrypted
  - RDS instance should have encryption at rest enabled
  - *Remediation:* Enable storage encryption using KMS
- **rds-003** (MEDIUM): RDS Instance No Backup
  - RDS instance should have automated backups enabled
  - *Remediation:* Set backup retention period to at least 7 days
- **rds-004** (MEDIUM): RDS Instance Multi-AZ Disabled
  - RDS instance should have Multi-AZ enabled for production
  - *Remediation:* Enable Multi-AZ for high availability
- **rds-005** (MEDIUM): RDS Instance Deletion Protection Disabled
  - RDS instance should have deletion protection enabled
  - *Remediation:* Enable deletion protection for production databases

### VPC

- **vpc-001** (HIGH): VPC Default Security Group Open
  - Default VPC security group should not have open rules
  - *Remediation:* Remove all rules from default security group
- **vpc-002** (MEDIUM): VPC Flow Logs Disabled
  - VPC should have flow logs enabled
  - *Remediation:* Enable VPC flow logs for network monitoring
- **vpc-003** (LOW): VPC DNS Resolution Disabled
  - VPC should have DNS resolution enabled
  - *Remediation:* Enable DNS support for proper name resolution

### CloudTrail

- **cloudtrail-001** (MEDIUM): CloudTrail Encryption Disabled
  - CloudTrail should have KMS encryption enabled
  - *Remediation:* Enable KMS encryption for CloudTrail logs
- **cloudtrail-002** (MEDIUM): CloudTrail Log Validation Disabled
  - CloudTrail should have log file validation enabled
  - *Remediation:* Enable log file validation to detect tampering
- **cloudtrail-003** (LOW): CloudTrail Single Region
  - CloudTrail should be multi-region for global coverage
  - *Remediation:* Enable multi-region trail for comprehensive logging

### KMS

- **kms-001** (MEDIUM): KMS Key Rotation Disabled
  - KMS key should have automatic rotation enabled
  - *Remediation:* Enable automatic key rotation for better security
- **kms-002** (LOW): KMS Key No Deletion Window
  - KMS key should have appropriate deletion window
  - *Remediation:* Set deletion window to at least 7 days

### Lambda

- **lambda-001** (HIGH): Lambda Function Public Access
  - Lambda function should not allow public access
  - *Remediation:* Restrict function access to specific principals
- **lambda-002** (LOW): Lambda Function No Dead Letter Queue
  - Lambda function should have dead letter queue configured
  - *Remediation:* Configure dead letter queue for error handling
- **lambda-003** (MEDIUM): Lambda Function No VPC
  - Lambda function should run in VPC when accessing private resources
  - *Remediation:* Configure VPC settings for functions accessing private resources

### ELB

- **elb-001** (HIGH): ELB No SSL Certificate
  - Load balancer should use SSL/TLS certificates
  - *Remediation:* Configure SSL certificate for HTTPS listeners
- **elb-002** (LOW): ELB Access Logs Disabled
  - Load balancer should have access logs enabled
  - *Remediation:* Enable access logs for audit and troubleshooting
- **elb-003** (LOW): ELB Deletion Protection Disabled
  - Load balancer should have deletion protection enabled
  - *Remediation:* Enable deletion protection for production load balancers

### CloudFront

- **cloudfront-001** (MEDIUM): CloudFront No HTTPS Redirect
  - CloudFront distribution should redirect HTTP to HTTPS
  - *Remediation:* Set viewer protocol policy to redirect-to-https
- **cloudfront-002** (MEDIUM): CloudFront No WAF
  - CloudFront distribution should have WAF enabled
  - *Remediation:* Associate WAF web ACL with CloudFront distribution

### Route53

- **route53-001** (LOW): Route53 Query Logging Disabled
  - Route53 hosted zone should have query logging enabled
  - *Remediation:* Enable query logging for DNS monitoring

### SNS

- **sns-001** (MEDIUM): SNS Topic Not Encrypted
  - SNS topic should have encryption enabled
  - *Remediation:* Enable KMS encryption for SNS topic
- **sns-002** (HIGH): SNS Topic Public Access
  - SNS topic should not allow public access
  - *Remediation:* Restrict topic access to specific principals

### SQS

- **sqs-001** (MEDIUM): SQS Queue Not Encrypted
  - SQS queue should have encryption enabled
  - *Remediation:* Enable KMS encryption for SQS queue
- **sqs-002** (HIGH): SQS Queue Public Access
  - SQS queue should not allow public access
  - *Remediation:* Restrict queue access to specific principals

### ElastiCache

- **elasticache-001** (MEDIUM): ElastiCache Cluster Not Encrypted
  - ElastiCache cluster should have encryption enabled
  - *Remediation:* Enable encryption at rest and in transit
- **elasticache-002** (MEDIUM): ElastiCache No Auth Token
  - ElastiCache Redis cluster should use auth token
  - *Remediation:* Configure auth token for Redis authentication

### EKS

- **eks-001** (MEDIUM): EKS Cluster Public Endpoint
  - EKS cluster should not have public API endpoint
  - *Remediation:* Disable public access or restrict CIDR blocks
- **eks-002** (LOW): EKS Cluster No Logging
  - EKS cluster should have control plane logging enabled
  - *Remediation:* Enable control plane logging for audit and troubleshooting

### ECS

- **ecs-001** (HIGH): ECS Task Definition Privileged
  - ECS task definition should not run in privileged mode
  - *Remediation:* Remove privileged mode and use specific capabilities
- **ecs-002** (MEDIUM): ECS Task Definition Root User
  - ECS task definition should not run as root user
  - *Remediation:* Specify non-root user in container definition

### API Gateway

- **apigateway-001** (MEDIUM): API Gateway No WAF
  - API Gateway should have WAF enabled
  - *Remediation:* Associate WAF web ACL with API Gateway
- **apigateway-002** (LOW): API Gateway No Logging
  - API Gateway should have access logging enabled
  - *Remediation:* Enable access logging for API Gateway stage

### CloudWatch

- **cloudwatch-001** (MEDIUM): CloudWatch Log Group Not Encrypted
  - CloudWatch log group should have encryption enabled
  - *Remediation:* Enable KMS encryption for log group
- **cloudwatch-002** (LOW): CloudWatch Log Group No Retention
  - CloudWatch log group should have retention policy
  - *Remediation:* Set appropriate log retention period

### Config

- **config-001** (MEDIUM): Config Service Disabled
  - AWS Config should be enabled for compliance monitoring
  - *Remediation:* Enable AWS Config for resource compliance monitoring

### GuardDuty

- **guardduty-001** (MEDIUM): GuardDuty Disabled
  - GuardDuty should be enabled for threat detection
  - *Remediation:* Enable GuardDuty for threat detection and monitoring

### Secrets Manager

- **secretsmanager-001** (MEDIUM): Secrets Manager No Rotation
  - Secrets Manager secret should have automatic rotation
  - *Remediation:* Enable automatic rotation for secrets
- **secretsmanager-002** (LOW): Secrets Manager No KMS
  - Secrets Manager secret should use customer managed KMS key
  - *Remediation:* Use customer managed KMS key for encryption
