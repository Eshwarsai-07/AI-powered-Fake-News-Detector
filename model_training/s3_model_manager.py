#!/usr/bin/env python3
"""
Utility script to manage model uploads and S3 operations
Complements the bash upload script with Python utilities
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ boto3 not installed. Install with: pip install boto3")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class S3ModelManager:
    """Manages model uploads and downloads from S3"""
    
    def __init__(self, bucket_name: str, aws_region: str = None):
        """
        Initialize S3 manager
        
        Args:
            bucket_name: S3 bucket name
            aws_region: AWS region (optional, uses default if not specified)
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.s3_resource = boto3.resource('s3', region_name=aws_region)
    
    def bucket_exists(self) -> bool:
        """Check if bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ Bucket exists: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ Bucket not found: {self.bucket_name}")
            elif error_code == '403':
                logger.error(f"❌ Access denied to bucket: {self.bucket_name}")
            else:
                logger.error(f"❌ Error checking bucket: {e}")
            return False
    
    def upload_directory(self, local_dir: str, s3_prefix: str) -> Tuple[int, List[str]]:
        """
        Upload entire directory to S3
        
        Args:
            local_dir: Local directory path
            s3_prefix: S3 key prefix (e.g., 'models/bert-v1')
            
        Returns:
            Tuple of (files_uploaded, failed_files)
        """
        local_path = Path(local_dir)
        
        if not local_path.is_dir():
            logger.error(f"❌ Directory not found: {local_dir}")
            return 0, []
        
        files_uploaded = 0
        failed_files = []
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(local_path)
                s3_key = f"{s3_prefix}/{rel_path}".replace('\\', '/')
                
                try:
                    logger.info(f"  Uploading {rel_path}...")
                    self.s3_client.upload_file(
                        str(file_path),
                        self.bucket_name,
                        s3_key
                    )
                    files_uploaded += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed to upload {rel_path}: {e}")
                    failed_files.append(str(rel_path))
        
        return files_uploaded, failed_files
    
    def list_models(self, prefix: str = 'models/') -> Dict[str, List[str]]:
        """
        List all models in bucket
        
        Args:
            prefix: S3 prefix to search under
            
        Returns:
            Dict mapping version tags to file lists
        """
        models = {}
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    # Extract version from path: models/bert-v1/file.txt
                    parts = key.split('/')
                    if len(parts) >= 2:
                        version = parts[1]
                        if version not in models:
                            models[version] = []
                        models[version].append(key)
        
        except ClientError as e:
            logger.error(f"❌ Error listing models: {e}")
        
        return models
    
    def get_bucket_size(self, prefix: str = '') -> Tuple[int, int]:
        """
        Get total size of files in bucket/prefix
        
        Args:
            prefix: S3 prefix to measure
            
        Returns:
            Tuple of (total_bytes, file_count)
        """
        total_size = 0
        file_count = 0
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    total_size += obj['Size']
                    file_count += 1
        
        except ClientError as e:
            logger.error(f"❌ Error calculating bucket size: {e}")
        
        return total_size, file_count
    
    def download_model(self, s3_prefix: str, local_dir: str) -> Tuple[int, List[str]]:
        """
        Download model from S3
        
        Args:
            s3_prefix: S3 key prefix (e.g., 'models/bert-v1')
            local_dir: Local directory to download to
            
        Returns:
            Tuple of (files_downloaded, failed_files)
        """
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        
        files_downloaded = 0
        failed_files = []
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=s3_prefix
            )
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    s3_key = obj['Key']
                    # Preserve directory structure
                    rel_path = s3_key[len(s3_prefix):].lstrip('/')
                    local_file = local_path / rel_path
                    
                    # Create parent directories
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        logger.info(f"  Downloading {rel_path}...")
                        self.s3_client.download_file(
                            self.bucket_name,
                            s3_key,
                            str(local_file)
                        )
                        files_downloaded += 1
                    except Exception as e:
                        logger.error(f"  ❌ Failed to download {rel_path}: {e}")
                        failed_files.append(rel_path)
        
        except ClientError as e:
            logger.error(f"❌ Error downloading model: {e}")
        
        return files_downloaded, failed_files
    
    def generate_config(self, version_tag: str) -> Dict:
        """
        Generate configuration for backend to load model from S3
        
        Args:
            version_tag: Model version tag
            
        Returns:
            Configuration dictionary
        """
        return {
            'S3_BUCKET': self.bucket_name,
            'S3_MODEL_KEY': f'models/{version_tag}',
            'MODEL_VERSION': version_tag,
            'AWS_REGION': self.s3_client.meta.region_name or 'us-east-1'
        }


def main():
    parser = argparse.ArgumentParser(
        description='S3 Model Manager - Upload/Download/List models'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload model to S3')
    upload_parser.add_argument('--bucket', required=True, help='S3 bucket name')
    upload_parser.add_argument('--model-dir', required=True, help='Local model directory')
    upload_parser.add_argument('--version', required=True, help='Version tag (e.g., bert-v1)')
    upload_parser.add_argument('--region', help='AWS region')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download model from S3')
    download_parser.add_argument('--bucket', required=True, help='S3 bucket name')
    download_parser.add_argument('--version', required=True, help='Version tag to download')
    download_parser.add_argument('--output', default='./downloaded_model', help='Output directory')
    download_parser.add_argument('--region', help='AWS region')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List models in S3 bucket')
    list_parser.add_argument('--bucket', required=True, help='S3 bucket name')
    list_parser.add_argument('--region', help='AWS region')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Generate backend configuration')
    config_parser.add_argument('--bucket', required=True, help='S3 bucket name')
    config_parser.add_argument('--version', required=True, help='Version tag')
    config_parser.add_argument('--region', help='AWS region')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = S3ModelManager(args.bucket, args.region)
    
    if not manager.bucket_exists():
        logger.error("Cannot proceed without valid bucket access")
        sys.exit(1)
    
    if args.command == 'upload':
        logger.info(f"🚀 Uploading model from {args.model_dir}")
        uploaded, failed = manager.upload_directory(
            args.model_dir,
            f"models/{args.version}"
        )
        logger.info(f"✅ Uploaded {uploaded} files")
        if failed:
            logger.warning(f"⚠️  Failed to upload {len(failed)} files")
            for f in failed:
                logger.warning(f"  - {f}")
    
    elif args.command == 'download':
        logger.info(f"⬇️  Downloading model version {args.version}")
        downloaded, failed = manager.download_model(
            f"models/{args.version}",
            args.output
        )
        logger.info(f"✅ Downloaded {downloaded} files to {args.output}")
        if failed:
            logger.warning(f"⚠️  Failed to download {len(failed)} files")
    
    elif args.command == 'list':
        models = manager.list_models()
        logger.info(f"📦 Models in {args.bucket}:")
        for version, files in models.items():
            logger.info(f"  {version}: {len(files)} files")
    
    elif args.command == 'config':
        config = manager.generate_config(args.version)
        logger.info("📋 Generated configuration:")
        print(json.dumps(config, indent=2))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
