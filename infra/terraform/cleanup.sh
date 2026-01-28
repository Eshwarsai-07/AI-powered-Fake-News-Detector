#!/bin/bash

# Cleanup and Destroy Script for Terraform Infrastructure
# This script safely destroys all AWS resources created by Terraform

echo "=================================="
echo "AWS Infrastructure Cleanup"
echo "=================================="
echo ""

# Navigate to terraform directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Current directory: $SCRIPT_DIR"
echo ""

# Check if terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo "⚠️  No terraform.tfstate found. Nothing to destroy."
    exit 0
fi

# Show what will be destroyed
echo "📋 Resources that will be DESTROYED:"
echo ""
terraform show
echo ""

# Confirm destruction
echo "=================================="
echo "⚠️  WARNING: This will DELETE all resources!"
echo "=================================="
echo ""
echo "This includes:"
echo "  - EC2 Instance"
echo "  - VPC and Networking"
echo "  - Security Groups"
echo "  - SSH Key Pair"
echo ""
read -p "Are you ABSOLUTELY SURE you want to destroy everything? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    echo ""
    echo "🗑️  Destroying infrastructure..."
    echo ""
    
    terraform destroy -auto-approve
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=================================="
        echo "✅ All resources destroyed successfully!"
        echo "=================================="
        echo ""
        
        # Ask about cleaning up local files
        read -p "Do you want to remove local Terraform files? (yes/no): " CLEAN_LOCAL
        
        if [ "$CLEAN_LOCAL" = "yes" ]; then
            echo ""
            echo "🧹 Cleaning up local files..."
            
            # Remove terraform state files
            rm -f terraform.tfstate*
            
            # Remove .terraform directory
            rm -rf .terraform
            
            # Remove lock file
            rm -f .terraform.lock.hcl
            
            # Remove generated SSH key
            rm -f ai-fake-news-detector-key.pem
            
            echo "✅ Local files cleaned up"
            echo ""
            echo "You can run 'terraform init' to start fresh."
        else
            echo ""
            echo "Local files kept. State files remain."
        fi
        
        echo ""
        echo "✅ Cleanup complete!"
    else
        echo ""
        echo "❌ Destroy failed!"
        echo "Check the error messages above."
        echo ""
        echo "You may need to manually clean up resources in AWS Console."
        exit 1
    fi
else
    echo ""
    echo "Cancelled. No resources were destroyed."
fi
