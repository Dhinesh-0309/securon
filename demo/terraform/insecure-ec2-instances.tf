# Insecure EC2 Instance Configuration
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# SECURITY ISSUE: EC2 instance with multiple vulnerabilities
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  
  # SECURITY ISSUE: Using default VPC (if no subnet specified)
  subnet_id = aws_subnet.public.id
  
  # CRITICAL: No IAM role attached - likely using access keys
  # Missing: iam_instance_profile
  
  # SECURITY ISSUE: Public IP assigned
  associate_public_ip_address = true
  
  # SECURITY ISSUE: Overly permissive security group
  vpc_security_group_ids = [aws_security_group.web_server.id]
  
  # SECURITY ISSUE: No detailed monitoring
  monitoring = false
  
  # SECURITY ISSUE: Unencrypted root volume
  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = false  # Should be true
    
    # SECURITY ISSUE: No KMS key specified for encryption
    # Missing: kms_key_id
  }
  
  # SECURITY ISSUE: Additional unencrypted EBS volume
  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = 100
    encrypted   = false  # Should be true
  }
  
  # SECURITY ISSUE: Sensitive data in user_data (base64 encoded but visible)
  user_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y apache2
              
              # SECURITY ISSUE: Hardcoded credentials
              export DB_PASSWORD="super_secret_password_123"
              export API_KEY="ak_live_1234567890abcdef"
              
              # SECURITY ISSUE: Downloading and executing script from internet
              curl -sSL https://get.docker.com/ | sh
              
              # SECURITY ISSUE: Running services as root
              systemctl start apache2
              systemctl enable apache2
              EOF
  )
  
  # SECURITY ISSUE: No termination protection
  disable_api_termination = false
  
  # SECURITY ISSUE: Instance metadata service v1 enabled (less secure)
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"  # Should be "required" for IMDSv2
    http_put_response_hop_limit = 1
  }

  tags = {
    Name = "web-server"
    # SECURITY ISSUE: No proper tagging for compliance/governance
  }
}

# Supporting infrastructure
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true  # SECURITY ISSUE: Auto-assign public IPs

  tags = {
    Name = "public-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# SECURITY ISSUE: Database instance with vulnerabilities
resource "aws_instance" "database" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.large"
  
  subnet_id = aws_subnet.public.id  # CRITICAL: Database in public subnet
  
  # CRITICAL: Database accessible from internet
  associate_public_ip_address = true
  
  vpc_security_group_ids = [aws_security_group.database.id]
  
  # SECURITY ISSUE: No backup strategy
  # SECURITY ISSUE: No encryption
  # SECURITY ISSUE: No monitoring
  monitoring = false
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
    encrypted   = false  # Database storage unencrypted
  }
  
  user_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y mysql-server
              
              # SECURITY ISSUE: Weak MySQL configuration
              mysql -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'password123';"
              mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';"
              mysql -e "FLUSH PRIVILEGES;"
              
              # SECURITY ISSUE: Bind to all interfaces
              sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
              systemctl restart mysql
              EOF
  )

  tags = {
    Name = "database-server"
  }
}