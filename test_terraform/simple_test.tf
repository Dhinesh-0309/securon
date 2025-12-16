resource "aws_s3_bucket" "test_bucket" {
  bucket = "my-test-bucket"
  
  # This will trigger security warnings
  acl = "public-read"
}

resource "aws_security_group" "test_sg" {
  name_prefix = "test-sg"
  
  # This will trigger critical security warnings
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "test_instance" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  # Missing security configurations
  associate_public_ip_address = true
}