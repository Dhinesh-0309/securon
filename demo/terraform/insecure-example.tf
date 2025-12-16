# Insecure Terraform Configuration - Multiple Security Issues

# 1. S3 Bucket with public read access (CRITICAL)
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket-demo"
}

resource "aws_s3_bucket_public_access_block" "public_bucket_pab" {
  bucket = aws_s3_bucket.public_bucket.id

  block_public_acls       = false  # INSECURE: Allows public ACLs
  block_public_policy     = false  # INSECURE: Allows public bucket policies
  ignore_public_acls      = false  # INSECURE: Doesn't ignore public ACLs
  restrict_public_buckets = false  # INSECURE: Doesn't restrict public buckets
}

resource "aws_s3_bucket_acl" "public_bucket_acl" {
  bucket = aws_s3_bucket.public_bucket.id
  acl    = "public-read"  # INSECURE: Public read access
}

# 2. Security Group with overly permissive rules (HIGH)
resource "aws_security_group" "insecure_sg" {
  name_prefix = "insecure-sg"
  description = "Insecure security group with wide open access"

  # INSECURE: SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # CRITICAL: SSH open to the world
  }

  # INSECURE: All traffic allowed outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # HIGH: All outbound traffic allowed
  }

  # INSECURE: Database port open to world
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # CRITICAL: MySQL open to the world
  }
}

# 3. RDS Instance without encryption (HIGH)
resource "aws_db_instance" "insecure_db" {
  identifier = "insecure-database"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage = 20
  storage_encrypted = false  # INSECURE: No encryption at rest
  
  db_name  = "testdb"
  username = "admin"
  password = "password123"  # INSECURE: Hardcoded password
  
  vpc_security_group_ids = [aws_security_group.insecure_sg.id]
  
  publicly_accessible = true   # INSECURE: Database publicly accessible
  skip_final_snapshot = true
  
  backup_retention_period = 0  # INSECURE: No backups
}

# 4. IAM Policy with overly broad permissions (CRITICAL)
resource "aws_iam_policy" "overly_permissive" {
  name        = "OverlyPermissivePolicy"
  description = "Policy with excessive permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # CRITICAL: Allows all actions
        Resource = "*"  # CRITICAL: On all resources
      }
    ]
  })
}

# 5. EC2 Instance with insecure configuration (MEDIUM)
resource "aws_instance" "insecure_instance" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.insecure_sg.id]
  
  # INSECURE: No encryption for EBS volumes
  root_block_device {
    encrypted = false
  }
  
  # INSECURE: Instance metadata service v1 (allows SSRF attacks)
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"  # INSECURE: Should be "required"
  }
  
  tags = {
    Name = "InsecureInstance"
  }
}

# 6. CloudTrail without encryption (MEDIUM)
resource "aws_cloudtrail" "insecure_trail" {
  name           = "insecure-trail"
  s3_bucket_name = aws_s3_bucket.public_bucket.bucket
  
  enable_logging = true
  
  # INSECURE: No KMS encryption
  # kms_key_id = aws_kms_key.cloudtrail_key.arn  # Missing encryption
  
  # INSECURE: No log file validation
  enable_log_file_validation = false
}