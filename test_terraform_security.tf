# Test Terraform file with various security issues for demonstration

# S3 Bucket with public access (Critical/High severity)
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket-example"
  
  tags = {
    Name = "Public Bucket Example"
  }
}

resource "aws_s3_bucket_acl" "public_bucket_acl" {
  bucket = aws_s3_bucket.public_bucket.id
  acl    = "public-read"  # Security issue: public access
}

# Security Group with unrestricted access (Critical severity)
resource "aws_security_group" "unrestricted_sg" {
  name_prefix = "unrestricted-"
  description = "Security group with unrestricted access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Security issue: SSH open to world
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Security issue: RDP open to world
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Security issue: All ports open
  }

  tags = {
    Name = "Unrestricted Security Group"
  }
}

# EC2 Instance with security issues (Medium severity)
resource "aws_instance" "insecure_instance" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.micro"
  
  associate_public_ip_address = true  # Security issue: public IP
  
  vpc_security_group_ids = [aws_security_group.unrestricted_sg.id]

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = false  # Security issue: unencrypted storage
  }

  metadata_options {
    http_tokens = "optional"  # Security issue: allows IMDSv1
  }

  tags = {
    Name = "Insecure Instance"
  }
}

# RDS Instance with security issues (High severity)
resource "aws_db_instance" "insecure_db" {
  identifier = "insecure-database"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage = 20
  storage_type      = "gp2"
  storage_encrypted = false  # Security issue: unencrypted storage
  
  db_name  = "testdb"
  username = "admin"
  password = "password123"  # Security issue: hardcoded password
  
  publicly_accessible = true  # Security issue: public access
  
  backup_retention_period = 0  # Security issue: no backups
  
  skip_final_snapshot = true

  tags = {
    Name = "Insecure Database"
  }
}

# IAM Policy with wildcard permissions (High severity)
resource "aws_iam_policy" "overprivileged_policy" {
  name        = "OverprivilegedPolicy"
  description = "Policy with excessive permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # Security issue: wildcard actions
        Resource = "*"  # Security issue: wildcard resources
      }
    ]
  })
}

# IAM Role with cross-account trust (High severity)
resource "aws_iam_role" "cross_account_role" {
  name = "CrossAccountRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::123456789012:root"  # Security issue: cross-account without conditions
        }
      }
    ]
  })
}