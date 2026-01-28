import boto3
import os
import argparse
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def upload_to_s3(local_dir, bucket_name, version_tag):
    """
    Uploads a directory of model artifacts to S3 with a version tag.
    Example: local_dir=saved_model/fake-news-bert -> s3://bucket/models/bert-v1/
    """
    s3_client = boto3.client('s3')
    
    # Verify bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        logger.error(f"❌ Error: Bucket '{bucket_name}' not found or access denied.")
        return False

    prefix = f"models/{version_tag}"
    logger.info(f"🚀 Starting upload to s3://{bucket_name}/{prefix}")

    if not os.path.isdir(local_dir):
        logger.error(f"❌ Error: Local directory '{local_dir}' does not exist.")
        return False

    files_uploaded = 0
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # Create relative path to preserve directory structure in S3
            rel_path = os.path.relpath(local_path, local_dir)
            s3_key = f"{prefix}/{rel_path}"
            
            logger.info(f"  Uploading {rel_path}...")
            try:
                s3_client.upload_file(local_path, bucket_name, s3_key)
                files_uploaded += 1
            except Exception as e:
                logger.error(f"  FAILED to upload {file}: {e}")
                return False

    logger.info(f"✅ Successfully uploaded {files_uploaded} model artifacts to S3!")
    logger.info(f"📍 Model Key: {prefix}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload trained model to S3")
    parser.add_argument("--model-dir", type=str, required=True, 
                        help="Local directory containing model files (e.g. model_training/saved_model/fake-news-bert)")
    parser.add_argument("--bucket", type=str, required=True, 
                        help="S3 bucket name (from terraform output)")
    parser.add_argument("--version", type=str, required=True, 
                        help="Version tag (e.g. bert-v1)")
    
    args = parser.parse_args()
    
    try:
        success = upload_to_s3(args.model_dir, args.bucket, args.version)
        if not success:
            exit(1)
    except KeyboardInterrupt:
        logger.info("\nCancelled by user.")
        exit(1)
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        exit(1)
