resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_acl" "secure_bucket_acl" {
  bucket = aws_s3_bucket.secure_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_security_group" "secure_sg" {
  name = "secure-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}

resource "aws_db_instance" "secure_db" {
  identifier = "secure-db"
  publicly_accessible = false
  storage_encrypted = true
  backup_retention_period = 7
}