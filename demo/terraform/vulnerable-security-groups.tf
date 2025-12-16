# Vulnerable Security Group Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

# CRITICAL SECURITY ISSUE: Overly permissive security group
resource "aws_security_group" "web_server" {
  name_prefix = "web-server-sg"
  vpc_id      = aws_vpc.main.id

  # CRITICAL: SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access from anywhere - SECURITY RISK"
  }

  # HIGH RISK: RDP access from anywhere
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "RDP access from anywhere - SECURITY RISK"
  }

  # MEDIUM RISK: FTP access
  ingress {
    from_port   = 21
    to_port     = 21
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "FTP access - Use SFTP instead"
  }

  # HIGH RISK: Telnet access
  ingress {
    from_port   = 23
    to_port     = 23
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Telnet access - Use SSH instead"
  }

  # MEDIUM RISK: SNMP access from internet
  ingress {
    from_port   = 161
    to_port     = 161
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SNMP access from internet"
  }

  # Acceptable: HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # Acceptable: HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # CRITICAL: All outbound traffic allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "web-server-sg"
  }
}

# SECURITY ISSUE: Database security group with broad access
resource "aws_security_group" "database" {
  name_prefix = "database-sg"
  vpc_id      = aws_vpc.main.id

  # CRITICAL: Database access from anywhere
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MySQL access from anywhere - CRITICAL RISK"
  }

  # CRITICAL: PostgreSQL access from anywhere
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "PostgreSQL access from anywhere - CRITICAL RISK"
  }

  # CRITICAL: MongoDB access from anywhere
  ingress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MongoDB access from anywhere - CRITICAL RISK"
  }

  tags = {
    Name = "database-sg"
  }
}