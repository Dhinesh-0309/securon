# Insecure RDS Database Configuration

# SECURITY ISSUE: DB subnet group in public subnets
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.public.id, aws_subnet.public_2.id]  # Should use private subnets

  tags = {
    Name = "Main DB subnet group"
  }
}

# Additional public subnet for multi-AZ requirement
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-2"
  }
}

# CRITICAL SECURITY ISSUES: RDS instance with multiple vulnerabilities
resource "aws_db_instance" "main" {
  identifier = "main-database"
  
  # Database configuration
  engine         = "mysql"
  engine_version = "5.7.44"  # SECURITY ISSUE: Older version, should use latest
  instance_class = "db.t3.micro"
  
  # SECURITY ISSUE: Weak database credentials
  db_name  = "myapp"
  username = "admin"  # SECURITY ISSUE: Predictable username
  password = "password123"  # CRITICAL: Weak password in plain text
  
  # Storage configuration
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type         = "gp2"
  storage_encrypted    = false  # CRITICAL: No encryption at rest
  # Missing: kms_key_id for encryption
  
  # Network configuration - CRITICAL ISSUES
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible    = true  # CRITICAL: Database accessible from internet
  port                   = 3306
  
  # Backup and maintenance - SECURITY ISSUES
  backup_retention_period = 0     # CRITICAL: No backups
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # SECURITY ISSUE: No automated backups
  skip_final_snapshot = true  # Should be false for production
  
  # SECURITY ISSUE: No deletion protection
  deletion_protection = false  # Should be true for production
  
  # SECURITY ISSUE: No enhanced monitoring
  monitoring_interval = 0  # Should be enabled
  
  # SECURITY ISSUE: No performance insights
  performance_insights_enabled = false
  
  # SECURITY ISSUE: Auto minor version upgrade disabled
  auto_minor_version_upgrade = false  # Should be true for security patches
  
  # SECURITY ISSUE: Multi-AZ disabled (no high availability)
  multi_az = false  # Should be true for production
  
  # SECURITY ISSUE: No parameter group for security hardening
  # Missing: parameter_group_name
  
  # SECURITY ISSUE: No option group for additional security features
  # Missing: option_group_name
  
  # Logging - SECURITY ISSUE: No audit logging
  enabled_cloudwatch_logs_exports = []  # Should include ["error", "general", "slow-query"]
  
  tags = {
    Name = "main-database"
    # SECURITY ISSUE: No proper tagging for compliance
  }
}

# SECURITY ISSUE: RDS parameter group with insecure settings
resource "aws_db_parameter_group" "insecure" {
  family = "mysql5.7"
  name   = "insecure-mysql-params"

  parameter {
    # SECURITY ISSUE: General log disabled
    name  = "general_log"
    value = "0"  # Should be "1" for audit trail
  }

  parameter {
    # SECURITY ISSUE: Slow query log disabled
    name  = "slow_query_log"
    value = "0"  # Should be "1" for performance monitoring
  }

  parameter {
    # SECURITY ISSUE: Log output to file disabled
    name  = "log_output"
    value = "NONE"  # Should be "FILE" or "TABLE"
  }

  parameter {
    # SECURITY ISSUE: SSL not enforced
    name  = "require_secure_transport"
    value = "0"  # Should be "1" to enforce SSL
  }
}

# SECURITY ISSUE: Read replica with same security issues
resource "aws_db_instance" "read_replica" {
  identifier = "main-database-replica"
  
  # Replica configuration
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = "db.t3.micro"
  
  # SECURITY ISSUE: Replica also publicly accessible
  publicly_accessible = true  # Should be false
  
  # SECURITY ISSUE: No encryption (inherits from source but source isn't encrypted)
  
  # SECURITY ISSUE: No monitoring on replica
  monitoring_interval = 0
  
  # SECURITY ISSUE: Auto minor version upgrade disabled
  auto_minor_version_upgrade = false
  
  tags = {
    Name = "main-database-replica"
  }
}

# SECURITY ISSUE: Aurora cluster with vulnerabilities (commented out to avoid conflicts)
/*
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier = "aurora-cluster"
  engine             = "aurora-mysql"
  engine_version     = "5.7.mysql_aurora.2.07.2"  # Older version
  
  # SECURITY ISSUE: Weak credentials
  database_name   = "myapp"
  master_username = "admin"
  master_password = "password123"  # Weak password
  
  # SECURITY ISSUE: No encryption
  storage_encrypted = false
  
  # SECURITY ISSUE: No backups
  backup_retention_period = 0
  
  # SECURITY ISSUE: Skip final snapshot
  skip_final_snapshot = true
  
  # SECURITY ISSUE: No deletion protection
  deletion_protection = false
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  
  tags = {
    Name = "aurora-cluster"
  }
}
*/