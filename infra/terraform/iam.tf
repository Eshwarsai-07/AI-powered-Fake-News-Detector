# 1. IAM Role for EC2
resource "aws_iam_role" "ec2_s3_role" {
  name = "ai-fake-news-detector-s3-role"

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

# 2. IAM Policy for S3 access
resource "aws_iam_role_policy" "s3_access_policy" {
  name = "ai-fake-news-detector-s3-policy"
  role = aws_iam_role.ec2_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.model_bucket.arn,
          "${aws_s3_bucket.model_bucket.arn}/*"
        ]
      }
    ]
  })
}

# 3. IAM Instance Profile
resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ai-fake-news-detector-s3-profile"
  role = aws_iam_role.ec2_s3_role.name
}
