resource "aws_s3_bucket" "example" {
  bucket = "my-test-bucket"
}

resource "aws_security_group" "web" {
  name_prefix = "web-sg"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # This will trigger security warnings
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  
  vpc_security_group_ids = [aws_security_group.web.id]
  
  # Missing encryption and monitoring - will trigger warnings
}