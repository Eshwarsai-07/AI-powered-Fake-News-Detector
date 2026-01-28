# 1. Create S3 Bucket for ML models
resource "aws_s3_bucket" "model_bucket" {
  bucket_prefix = "fake-news-models-" # Random suffix for uniqueness
  force_destroy = true # Allows terraform to delete the bucket even if it's not empty

  tags = {
    Name        = "fake-news-models"
    Environment = "Dev"
  }
}

# 2. Enable versioning for model artifacts
resource "aws_s3_bucket_versioning" "model_bucket_versioning" {
  bucket = aws_s3_bucket.model_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3. Block public access (Security Best Practice)
resource "aws_s3_bucket_public_access_block" "model_bucket_public_access" {
  bucket = aws_s3_bucket.model_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
