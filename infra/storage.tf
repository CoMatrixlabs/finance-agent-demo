# Bucket the reconciliation partner reads exported client records from.
resource "aws_s3_bucket" "analytics_exports" {
  bucket = "finance-agent-analytics-exports"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "analytics_exports" {
  bucket                  = aws_s3_bucket.analytics_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
