#!/bin/bash

################################################################################
# Model Upload to S3 Automation Script
# Uploads BERT model to AWS S3 bucket with automatic configuration
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TERRAFORM_DIR="${PROJECT_ROOT}/infra/terraform"
MODEL_DIR="${SCRIPT_DIR}/saved_model/fake-news-bert"
ENV_FILE="${PROJECT_ROOT}/.env"
VERSION_TAG="bert-v1"
BUCKET_NAME=""  # Will be retrieved from Terraform

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if AWS CLI is installed
check_aws_cli() {
    print_info "Checking AWS CLI installation..."
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Install it with: pip install awscli"
        exit 1
    fi
    print_success "AWS CLI is installed"
}

# Check AWS credentials
check_aws_credentials() {
    print_info "Checking AWS credentials..."
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured or invalid"
        echo ""
        echo "Configure credentials with:"
        echo "  aws configure"
        echo "Or set environment variables:"
        echo "  export AWS_ACCESS_KEY_ID=your-key"
        echo "  export AWS_SECRET_ACCESS_KEY=your-secret"
        echo "  export AWS_DEFAULT_REGION=us-east-1"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS credentials valid (Account: $ACCOUNT_ID)"
}

# Get S3 bucket name from Terraform outputs
get_bucket_from_terraform() {
    print_header "Retrieving S3 Bucket from Terraform"
    
    # Check if Terraform directory exists
    if [ ! -d "$TERRAFORM_DIR" ]; then
        print_error "Terraform directory not found: $TERRAFORM_DIR"
        exit 1
    fi
    
    # Get bucket name from Terraform output
    cd "$TERRAFORM_DIR"
    
    if ! BUCKET_NAME=$(terraform output -raw model_bucket_name 2>/dev/null); then
        print_error "Failed to retrieve bucket name from Terraform"
        echo ""
        echo "Make sure:"
        echo "  1. Terraform has been initialized: terraform init"
        echo "  2. Infrastructure was created: terraform apply"
        echo "  3. Output 'model_bucket_name' exists in outputs.tf"
        exit 1
    fi
    
    cd - > /dev/null
    print_success "Retrieved bucket from Terraform: s3://${BUCKET_NAME}"
    
    # Verify bucket exists
    if aws s3 ls "s3://${BUCKET_NAME}" 2>/dev/null; then
        print_success "Bucket is accessible"
    else
        print_error "Bucket exists but is not accessible. Check AWS credentials and permissions."
        exit 1
    fi
}

# Check model directory exists
check_model_files() {
    print_header "Verifying Model Files"
    
    if [ ! -d "$MODEL_DIR" ]; then
        print_error "Model directory not found: $MODEL_DIR"
        exit 1
    fi
    
    # Count files
    FILE_COUNT=$(find "$MODEL_DIR" -type f | wc -l)
    if [ "$FILE_COUNT" -eq 0 ]; then
        print_error "No model files found in $MODEL_DIR"
        exit 1
    fi
    
    print_success "Found $FILE_COUNT model files"
    print_info "Model files:"
    find "$MODEL_DIR" -type f -exec basename {} \; | sed 's/^/  - /'
}

# Upload model to S3
upload_model() {
    print_header "Uploading Model to S3"
    
    S3_PREFIX="models/${VERSION_TAG}"
    print_info "Uploading to: s3://${BUCKET_NAME}/${S3_PREFIX}/"
    
    # Use Python script for reliable upload with logging
    python3 "${SCRIPT_DIR}/upload_s3.py" \
        --model-dir "$MODEL_DIR" \
        --bucket "$BUCKET_NAME" \
        --version "$VERSION_TAG"
    
    if [ $? -ne 0 ]; then
        print_error "Upload failed"
        exit 1
    fi
    
    print_success "Model uploaded successfully"
}

# Update .env file
update_env_file() {
    print_header "Updating .env Configuration"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found, creating one..."
        touch "$ENV_FILE"
    fi
    
    # Remove existing S3 settings if they exist
    sed -i.bak '/^S3_BUCKET=/d' "$ENV_FILE"
    sed -i.bak '/^S3_MODEL_KEY=/d' "$ENV_FILE"
    
    # Add new S3 settings
    {
        echo ""
        echo "# S3 Configuration"
        echo "S3_BUCKET=${BUCKET_NAME}"
        echo "S3_MODEL_KEY=models/${VERSION_TAG}"
    } >> "$ENV_FILE"
    
    print_success ".env updated with S3 configuration"
    print_info "S3_BUCKET=${BUCKET_NAME}"
    print_info "S3_MODEL_KEY=models/${VERSION_TAG}"
}

# Verify upload
verify_upload() {
    print_header "Verifying Upload"
    
    UPLOADED_FILES=$(aws s3 ls "s3://${BUCKET_NAME}/models/${VERSION_TAG}/" --recursive | wc -l)
    
    if [ "$UPLOADED_FILES" -gt 0 ]; then
        print_success "$UPLOADED_FILES files verified in S3"
        echo ""
        print_info "Files in S3:"
        aws s3 ls "s3://${BUCKET_NAME}/models/${VERSION_TAG}/" --recursive | awk '{print "  - " $4}'
    else
        print_error "No files found in S3 after upload"
        exit 1
    fi
}

# Generate access script
create_download_script() {
    print_header "Creating Download Script"
    
    DOWNLOAD_SCRIPT="${SCRIPT_DIR}/download_model_from_s3.sh"
    
    cat > "$DOWNLOAD_SCRIPT" << 'DOWNLOAD_EOF'
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
DOWNLOAD_EOF
    
    chmod +x "$DOWNLOAD_SCRIPT"
    print_success "Download script created: $DOWNLOAD_SCRIPT"
}

# Display summary
print_summary() {
    print_header "✅ Upload Complete!"
    
    echo ""
    echo "Configuration Summary:"
    echo "  S3 Bucket:     $BUCKET_NAME"
    echo "  Model Version: $VERSION_TAG"
    echo "  Model Path:    models/${VERSION_TAG}/"
    echo "  Files Uploaded: $UPLOADED_FILES"
    echo ""
    echo "Next steps:"
    echo "  1. Backend app will load from: s3://${BUCKET_NAME}/models/${VERSION_TAG}/"
    echo "  2. Ensure EC2 instance has S3 access via IAM role"
    echo "  3. Deploy with: ansible-playbook infra/ansible/playbook.yml"
    echo ""
    echo "To download model later:"
    echo "  ./download_model_from_s3.sh $BUCKET_NAME $VERSION_TAG"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "🚀 Model Upload to S3 - Automation Script"
    
    # Run checks
    check_aws_cli
    check_aws_credentials
    check_model_files
    
    # Get bucket from Terraform
    get_bucket_from_terraform
    upload_model
    
    # Verify and configure
    verify_upload
    update_env_file
    create_download_script
    
    # Summary
    print_summary
}

# Handle Ctrl+C
trap 'print_error "Upload cancelled by user"; exit 1' INT TERM

# Run main
main "$@"
