# Insecure S3 Bucket Configuration - Multiple Security Issues
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-data-bucket-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# SECURITY ISSUE: Public read access
resource "aws_s3_bucket_public_access_block" "public_bucket" {
  bucket = aws_s3_bucket.public_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# SECURITY ISSUE: No versioning enabled
# Missing: aws_s3_bucket_versioning

# SECURITY ISSUE: No encryption at rest
# Missing: aws_s3_bucket_server_side_encryption_configuration

# SECURITY ISSUE: No logging enabled
# Missing: aws_s3_bucket_logging

# SECURITY ISSUE: Public bucket policy
resource "aws_s3_bucket_policy" "public_bucket" {
  bucket = aws_s3_bucket.public_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.public_bucket.arn}/*"
      }
    ]
  })
}

# SECURITY ISSUE: No lifecycle policy for cost optimization
# Missing: aws_s3_bucket_lifecycle_configuration

# SECURITY ISSUE: No cross-region replication
# Missing: aws_s3_bucket_replication_configuration

# SECURITY ISSUE: No object lock for compliance
# Missing: aws_s3_bucket_object_lock_configuration