#!/bin/bash

# Download Model from S3
# Usage: ./download_model_from_s3.sh [bucket-name] [version]

BUCKET_NAME="${1:-}"
VERSION_TAG="${2:-bert-v1}"
DOWNLOAD_DIR="${3:-./downloaded_model}"

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: $0 <bucket-name> [version] [download-dir]"
    exit 1
fi

mkdir -p "$DOWNLOAD_DIR"
echo "Downloading model from s3://${BUCKET_NAME}/models/${VERSION_TAG}/"
aws s3 sync "s3://${BUCKET_NAME}/models/${VERSION_TAG}/" "$DOWNLOAD_DIR/"
echo "✅ Model downloaded to $DOWNLOAD_DIR"
