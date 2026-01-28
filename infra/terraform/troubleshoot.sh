#!/bin/bash

# Troubleshooting Script for Terraform AWS Infrastructure
# This script helps diagnose common issues

echo "=================================="
echo "Terraform Troubleshooting Tool"
echo "=================================="
echo ""

# Navigate to terraform directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check 1: Terraform Installation
echo "1️⃣  Checking Terraform installation..."
if command_exists terraform; then
    TERRAFORM_VERSION=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)
    echo "   ✅ Terraform installed: v$TERRAFORM_VERSION"
else
    echo "   ❌ Terraform not found!"
    echo "   Install from: https://www.terraform.io/downloads"
    exit 1
fi
echo ""

# Check 2: AWS CLI (optional but helpful)
echo "2️⃣  Checking AWS CLI..."
if command_exists aws; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
    echo "   ✅ AWS CLI installed: $AWS_VERSION"
else
    echo "   ⚠️  AWS CLI not installed (optional)"
    echo "   Install from: https://aws.amazon.com/cli/"
fi
echo ""

# Check 3: AWS Credentials
echo "3️⃣  Checking AWS credentials..."
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "   ✅ AWS credentials found in environment variables"
elif [ -f "$HOME/.aws/credentials" ]; then
    echo "   ✅ AWS credentials file exists at ~/.aws/credentials"
else
    echo "   ❌ No AWS credentials found!"
    echo "   Set environment variables:"
    echo "     export AWS_ACCESS_KEY_ID='your-key'"
    echo "     export AWS_SECRET_ACCESS_KEY='your-secret'"
    exit 1
fi
echo ""

# Check 4: Terraform Initialization
echo "4️⃣  Checking Terraform initialization..."
if [ -d ".terraform" ]; then
    echo "   ✅ Terraform initialized (.terraform directory exists)"
else
    echo "   ⚠️  Terraform not initialized"
    echo "   Run: terraform init"
    read -p "   Initialize now? (yes/no): " INIT_NOW
    if [ "$INIT_NOW" = "yes" ]; then
        terraform init
        if [ $? -eq 0 ]; then
            echo "   ✅ Initialization successful"
        else
            echo "   ❌ Initialization failed"
            exit 1
        fi
    fi
fi
echo ""

# Check 5: Terraform State
echo "5️⃣  Checking Terraform state..."
if [ -f "terraform.tfstate" ]; then
    STATE_SIZE=$(wc -c < terraform.tfstate)
    if [ "$STATE_SIZE" -gt 200 ]; then
        echo "   ✅ State file exists and has content ($STATE_SIZE bytes)"
        
        # Try to get resource count
        RESOURCE_COUNT=$(terraform state list 2>/dev/null | wc -l)
        if [ "$RESOURCE_COUNT" -gt 0 ]; then
            echo "   📊 Resources in state: $RESOURCE_COUNT"
        fi
    else
        echo "   ⚠️  State file exists but appears empty"
    fi
else
    echo "   ℹ️  No state file (no resources created yet)"
fi
echo ""

# Check 6: Validate Configuration
echo "6️⃣  Validating Terraform configuration..."
terraform validate > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Configuration is valid"
else
    echo "   ❌ Configuration has errors:"
    terraform validate
    exit 1
fi
echo ""

# Check 7: AWS Connectivity
echo "7️⃣  Testing AWS connectivity..."
if command_exists aws && [ -n "$AWS_ACCESS_KEY_ID" ]; then
    AWS_IDENTITY=$(aws sts get-caller-identity 2>&1)
    if [ $? -eq 0 ]; then
        echo "   ✅ Successfully connected to AWS"
        ACCOUNT_ID=$(echo "$AWS_IDENTITY" | grep -o '"Account": "[^"]*' | cut -d'"' -f4)
        echo "   📋 Account ID: $ACCOUNT_ID"
    else
        echo "   ❌ Cannot connect to AWS"
        echo "   Error: $AWS_IDENTITY"
    fi
else
    echo "   ⚠️  Skipping (AWS CLI not available or credentials not in env)"
fi
echo ""

# Check 8: File Permissions
echo "8️⃣  Checking file permissions..."
if [ -f "ai-fake-news-detector-key.pem" ]; then
    PERMS=$(stat -f "%OLp" ai-fake-news-detector-key.pem 2>/dev/null || stat -c "%a" ai-fake-news-detector-key.pem 2>/dev/null)
    if [ "$PERMS" = "400" ]; then
        echo "   ✅ SSH key has correct permissions (400)"
    else
        echo "   ⚠️  SSH key permissions: $PERMS (should be 400)"
        echo "   Fix with: chmod 400 ai-fake-news-detector-key.pem"
    fi
else
    echo "   ℹ️  No SSH key file yet (will be created on apply)"
fi
echo ""

# Summary
echo "=================================="
echo "Summary"
echo "=================================="
echo ""

if [ -f "terraform.tfstate" ]; then
    STATE_SIZE=$(wc -c < terraform.tfstate)
    if [ "$STATE_SIZE" -gt 200 ]; then
        echo "📊 Current Infrastructure Status:"
        echo ""
        terraform show -no-color | head -n 50
        echo ""
        echo "💡 To see full details: terraform show"
        echo "💡 To see outputs: terraform output"
    fi
else
    echo "ℹ️  No infrastructure deployed yet"
    echo ""
    echo "Next steps:"
    echo "  1. Set AWS credentials (if not done)"
    echo "  2. Run: terraform plan"
    echo "  3. Run: terraform apply"
fi

echo ""
echo "=================================="
echo "Common Commands"
echo "=================================="
echo ""
echo "  terraform plan          - Preview changes"
echo "  terraform apply         - Create/update infrastructure"
echo "  terraform destroy       - Delete all resources"
echo "  terraform output        - Show output values"
echo "  terraform state list    - List all resources"
echo "  terraform show          - Show current state"
echo ""
echo "Or use the helper scripts:"
echo "  ./setup.sh             - Guided setup and apply"
echo "  ./cleanup.sh           - Guided cleanup and destroy"
echo ""
