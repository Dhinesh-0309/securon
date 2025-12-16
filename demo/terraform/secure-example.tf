# Secure Terraform Configuration - Following Security Best Practices

# 1. S3 Bucket with proper security configuration (SECURE)
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket-demo"
}

resource "aws_s3_bucket_public_access_block" "secure_bucket_pab" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true  # SECURE: Blocks public ACLs
  block_public_policy     = true  # SECURE: Blocks public bucket policies
  ignore_public_acls      = true  # SECURE: Ignores public ACLs
  restrict_public_buckets = true  # SECURE: Restricts public buckets
}

resource "aws_s3_bucket_encryption_configuration" "secure_bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  # SECURE: Server-side encryption enabled
    }
  }
}

resource "aws_s3_bucket_versioning" "secure_bucket_versioning" {
  bucket = aws_s3_bucket.secure_bucket.id
  versioning_configuration {
    status = "Enabled"  # SECURE: Versioning enabled
  }
}

# 2. Security Group with restrictive rules (SECURE)
resource "aws_security_group" "secure_sg" {
  name_prefix = "secure-sg"
  description = "Secure security group with restricted access"

  # SECURE: SSH access only from specific IP range
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # SECURE: Limited to private network
    description = "SSH access from private network only"
  }

  # SECURE: HTTPS access from anywhere (acceptable for web services)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # SECURE: Specific outbound rules
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP outbound for updates"
  }

  tags = {
    Name = "SecureSecurityGroup"
  }
}

# 3. KMS Key for encryption
resource "aws_kms_key" "secure_key" {
  description             = "KMS key for secure resources"
  deletion_window_in_days = 7
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_kms_alias" "secure_key_alias" {
  name          = "alias/secure-demo-key"
  target_key_id = aws_kms_key.secure_key.key_id
}

# 4. RDS Instance with proper security configuration (SECURE)
resource "aws_db_instance" "secure_db" {
  identifier = "secure-database"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage = 20
  storage_encrypted = true  # SECURE: Encryption at rest enabled
  kms_key_id       = aws_kms_key.secure_key.arn  # SECURE: Customer managed key
  
  db_name  = "securedb"
  username = "admin"
  manage_master_user_password = true  # SECURE: AWS manages password
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  
  publicly_accessible = false  # SECURE: Not publicly accessible
  skip_final_snapshot = false
  final_snapshot_identifier = "secure-db-final-snapshot"
  
  backup_retention_period = 7  # SECURE: 7 days backup retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["error", "general", "slow_query"]  # SECURE: Logging enabled
  
  tags = {
    Name = "SecureDatabase"
  }
}

# 5. Dedicated security group for database (SECURE)
resource "aws_security_group" "db_sg" {
  name_prefix = "secure-db-sg"
  description = "Security group for secure database"

  # SECURE: Database access only from application security group
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.secure_sg.id]  # SECURE: Only from app SG
    description     = "MySQL access from application tier"
  }

  tags = {
    Name = "SecureDatabaseSG"
  }
}

# 6. IAM Policy with least privilege principle (SECURE)
resource "aws_iam_policy" "least_privilege" {
  name        = "LeastPrivilegePolicy"
  description = "Policy following least privilege principle"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.secure_bucket.arn}/*"  # SECURE: Specific resource
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.secure_bucket.arn  # SECURE: Specific bucket
      }
    ]
  })
}

# 7. EC2 Instance with secure configuration (SECURE)
resource "aws_instance" "secure_instance" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.secure_sg.id]
  
  # SECURE: Encrypted EBS volumes
  root_block_device {
    encrypted   = true
    kms_key_id  = aws_kms_key.secure_key.arn
    volume_type = "gp3"
  }
  
  # SECURE: Instance metadata service v2 (prevents SSRF attacks)
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"  # SECURE: Requires IMDSv2
    http_put_response_hop_limit = 1
  }
  
  # SECURE: Monitoring enabled
  monitoring = true
  
  tags = {
    Name = "SecureInstance"
  }
}

# 8. CloudTrail with proper security configuration (SECURE)
resource "aws_cloudtrail" "secure_trail" {
  name           = "secure-trail"
  s3_bucket_name = aws_s3_bucket.secure_bucket.bucket
  
  enable_logging = true
  
  # SECURE: KMS encryption enabled
  kms_key_id = aws_kms_key.secure_key.arn
  
  # SECURE: Log file validation enabled
  enable_log_file_validation = true
  
  # SECURE: Multi-region trail
  is_multi_region_trail = true
  
  # SECURE: Include global service events
  include_global_service_events = true
  
  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.secure_bucket.arn}/*"]
    }
  }
  
  tags = {
    Name = "SecureCloudTrail"
  }
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}