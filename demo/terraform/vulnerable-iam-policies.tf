# Vulnerable IAM Configuration with Multiple Security Issues

# CRITICAL SECURITY ISSUE: Overly permissive IAM policy
resource "aws_iam_policy" "admin_policy" {
  name        = "AdminPolicy"
  description = "Administrative access policy - TOO PERMISSIVE"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # CRITICAL: Full administrative access
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# SECURITY ISSUE: IAM user with programmatic access (should use roles)
resource "aws_iam_user" "service_user" {
  name = "service-user"
  path = "/"

  tags = {
    Department = "Engineering"
  }
}

# CRITICAL: Attaching admin policy to user
resource "aws_iam_user_policy_attachment" "service_user_admin" {
  user       = aws_iam_user.service_user.name
  policy_arn = aws_iam_policy.admin_policy.arn
}

# SECURITY ISSUE: Creating access keys (should use temporary credentials)
resource "aws_iam_access_key" "service_user_key" {
  user = aws_iam_user.service_user.name
}

# SECURITY ISSUE: S3 policy allowing public access
resource "aws_iam_policy" "s3_public_policy" {
  name        = "S3PublicPolicy"
  description = "S3 policy with public access - SECURITY RISK"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "*"
        Principal = "*"  # CRITICAL: Public access
      }
    ]
  })
}

# SECURITY ISSUE: EC2 role with excessive permissions
resource "aws_iam_role" "ec2_role" {
  name = "EC2Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# CRITICAL: Attaching AWS managed PowerUser policy (too broad)
resource "aws_iam_role_policy_attachment" "ec2_poweruser" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

# SECURITY ISSUE: Custom policy with dangerous permissions
resource "aws_iam_policy" "dangerous_policy" {
  name        = "DangerousPolicy"
  description = "Policy with dangerous permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # CRITICAL: Can modify IAM policies and users
        Effect = "Allow"
        Action = [
          "iam:*",
          "sts:AssumeRole"
        ]
        Resource = "*"
      },
      {
        # CRITICAL: Can access all secrets
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "*"
      },
      {
        # CRITICAL: Can modify security groups
        Effect = "Allow"
        Action = [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupEgress"
        ]
        Resource = "*"
      }
    ]
  })
}

# SECURITY ISSUE: Lambda role with excessive permissions
resource "aws_iam_role" "lambda_role" {
  name = "LambdaRole"

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

# CRITICAL: Lambda with admin access
resource "aws_iam_role_policy_attachment" "lambda_admin" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# SECURITY ISSUE: Cross-account trust policy that's too permissive
resource "aws_iam_role" "cross_account_role" {
  name = "CrossAccountRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          # CRITICAL: Allows any AWS account to assume this role
          AWS = "*"
        }
        Action = "sts:AssumeRole"
        # Missing: Condition blocks for additional security
      }
    ]
  })
}

# SECURITY ISSUE: Instance profile without proper restrictions
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# SECURITY ISSUE: Group with administrative privileges
resource "aws_iam_group" "admin_group" {
  name = "administrators"
}

resource "aws_iam_group_policy_attachment" "admin_group_policy" {
  group      = aws_iam_group.admin_group.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# SECURITY ISSUE: Password policy that's too weak
resource "aws_iam_account_password_policy" "weak_policy" {
  minimum_password_length        = 6   # Should be at least 12
  require_lowercase_characters   = false
  require_numbers               = false
  require_uppercase_characters   = false
  require_symbols               = false
  allow_users_to_change_password = true
  max_password_age              = 0    # No expiration
  password_reuse_prevention     = 0    # No reuse prevention
}