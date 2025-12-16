# Mixed Terraform Configuration - Some Secure, Some Insecure

# 1. SECURE: Properly configured VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "MainVPC"
  }
}

# 2. SECURE: Private subnet
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "PrivateSubnet"
  }
}

# 3. INSECURE: Public subnet with auto-assign public IP (MEDIUM risk)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-west-2b"
  map_public_ip_on_launch = true  # INSECURE: Auto-assigns public IPs

  tags = {
    Name = "PublicSubnet"
  }
}

# 4. SECURE: Internet Gateway (acceptable for public subnet)
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "MainIGW"
  }
}

# 5. INSECURE: Route table allowing all traffic to IGW
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"  # MEDIUM: All traffic routed to internet
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "PublicRouteTable"
  }
}

# 6. SECURE: Load balancer with proper configuration
resource "aws_lb" "secure_alb" {
  name               = "secure-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public.id, aws_subnet.private.id]

  enable_deletion_protection = true  # SECURE: Deletion protection enabled

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.bucket
    prefix  = "alb-logs"
    enabled = true  # SECURE: Access logging enabled
  }

  tags = {
    Name = "SecureALB"
  }
}

# 7. SECURE: ALB Security Group
resource "aws_security_group" "alb_sg" {
  name_prefix = "alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]  # SECURE: Only to VPC
    description = "Outbound to VPC"
  }

  tags = {
    Name = "ALBSG"
  }
}

# 8. INSECURE: Lambda function with overly permissive role
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",  # INSECURE: Too broad - should be specific actions
          "dynamodb:*",  # INSECURE: Too broad
          "logs:*"  # INSECURE: Too broad
        ]
        Resource = "*"  # INSECURE: Should be specific resources
      }
    ]
  })
}

# 9. SECURE: S3 bucket for load balancer logs
resource "aws_s3_bucket" "lb_logs" {
  bucket = "secure-lb-logs-demo-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "lb_logs_pab" {
  bucket = aws_s3_bucket.lb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lb_logs_encryption" {
  bucket = aws_s3_bucket.lb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 10. INSECURE: SNS Topic without encryption
resource "aws_sns_topic" "notifications" {
  name = "app-notifications"
  
  # INSECURE: No KMS encryption specified
  # kms_master_key_id = aws_kms_key.sns_key.arn  # Missing encryption
}

# 11. SECURE: Random ID for unique naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 12. INSECURE: ElastiCache cluster without encryption
resource "aws_elasticache_subnet_group" "cache_subnet_group" {
  name       = "cache-subnet-group"
  subnet_ids = [aws_subnet.private.id]
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "app-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.cache_subnet_group.name
  security_group_ids   = [aws_security_group.cache_sg.id]
  
  # INSECURE: No encryption at rest
  # at_rest_encryption_enabled = true  # Missing
  
  # INSECURE: No encryption in transit
  # transit_encryption_enabled = true  # Missing
}

# 13. INSECURE: Cache security group with broad access
resource "aws_security_group" "cache_sg" {
  name_prefix = "cache-sg"
  description = "Security group for ElastiCache"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]  # MEDIUM: Could be more restrictive
    description = "Redis access from VPC"
  }

  tags = {
    Name = "CacheSG"
  }
}