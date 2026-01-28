#!/bin/bash

# Setup Script for Terraform AWS Infrastructure & Ansible Configuration
# This script handles the entire lifecycle: Setup -> Provision -> Configure

echo "=================================="
echo "Infrastructure & Configuration Setup"
echo "=================================="
echo ""

# Helper to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check Terraform
if ! command_exists terraform; then
    echo "❌ Terraform is not installed!"
    echo "Install it from: https://www.terraform.io/downloads"
    exit 1
fi
echo "✅ Terraform is installed"

# 2. Check Ansible
if command_exists ansible-playbook; then
    ANSIBLE_VERSION=$(ansible-playbook --version | head -n 1 | cut -d' ' -f2-3)
    echo "✅ Ansible installed: $ANSIBLE_VERSION"
else
    echo "⚠️  Ansible not found! Automatic configuration will be skipped."
    echo "   Install with: brew install ansible"
fi
echo ""

# 3. Prompt for credentials
echo "Please enter your AWS credentials:"
echo ""
read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -sp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""
read -p "Git Repository URL: " GIT_REPO_URL
echo ""
echo ""

# Export credentials
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export TF_VAR_repo_url="$GIT_REPO_URL"

echo "✅ AWS credentials set"
echo ""

# Navigate to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Current directory: $SCRIPT_DIR"
echo ""

# 4. Initialize Terraform
if [ ! -d ".terraform" ]; then
    echo "🔧 Initializing Terraform..."
    terraform init
    if [ $? -ne 0 ]; then
        echo "❌ Terraform init failed!"
        exit 1
    fi
    echo "✅ Terraform initialized"
    echo ""
fi

# 5. Run Plan
echo "📋 Running Terraform plan..."
echo ""
terraform plan

if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed!"
    exit 1
fi

echo ""
echo "=================================="
echo "Ready to apply?"
echo "=================================="
echo ""
read -p "Do you want to create the infrastructure? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    echo ""
    echo "🚀 Creating infrastructure..."
    echo "⏱️  This may take 5-15 minutes. Please be patient..."
    echo ""
    
    # 6. Apply Terraform
    terraform apply -auto-approve
    STATUS=$?
    
    if [ $STATUS -eq 0 ]; then
        echo ""
        echo "=================================="
        echo "✅ Infrastructure Created Successfully!"
        echo "=================================="
        echo ""
        
        # 7. Ansible Integration
        if command_exists ansible-playbook; then
            echo "🔄 Starting Ansible Configuration..."
            
            INVENTORY_FILE="../ansible/inventory.ini"
            PLAYBOOK_FILE="../ansible/playbook.yml"
            
            if [ -f "$INVENTORY_FILE" ]; then
                echo "📄 Found Inventory: $INVENTORY_FILE"
                
                # Extract IP from Terraform output
                SERVER_IP=$(terraform output -raw instance_public_ip)
                
                echo "⏳ Waiting for SSH to be available on $SERVER_IP..."
                echo "   (This can take 1-2 minutes for the instance to boot)"
                
                # Wait for SSH port 22
                if command_exists nc; then
                    count=0
                    while [ $count -lt 30 ]; do
                        nc -z -w 5 "$SERVER_IP" 22 2>/dev/null
                        if [ $? -eq 0 ]; then
                            echo "   ✅ SSH is reachable!"
                            break
                        fi
                        echo "   ... waiting for SSH ($count/30)..."
                        sleep 10
                        count=$((count + 1))
                    done
                else
                    echo "   ⚠️  'nc' command not found. Waiting 60s blindly..."
                    sleep 60
                fi

                echo "▶️  Running Ansible Playbook..."
                echo ""
                # Disable host key checking just for this run to avoid prompts
                export ANSIBLE_HOST_KEY_CHECKING=False
                
                ansible-playbook -i "$INVENTORY_FILE" "$PLAYBOOK_FILE"
                ANSIBLE_STATUS=$?
                
                if [ $ANSIBLE_STATUS -eq 0 ]; then
                     echo ""
                     echo "✅ Ansible Configuration Complete!"
                else
                     echo ""
                     echo "❌ Ansible Configuration Failed!"
                     echo "You can retry manually: ansible-playbook -i $INVENTORY_FILE $PLAYBOOK_FILE"
                fi
            else
                echo "⚠️  Inventory file not found at $INVENTORY_FILE"
                echo "Check if inventory.tf created it correctly."
            fi
        else
            echo "ℹ️  Skipping Ansible (not installed)"
        fi
        
        echo "📊 Infrastructure Details:"
        terraform output
        echo ""
        echo "🔑 SSH Key saved to: ai-fake-news-detector-key.pem"
        echo ""
        echo "🧠 IMPORTANT: MODEL UPLOAD"
        echo "--------------------------"
        echo "Since the AI model is stored in S3 for production, you must upload it:"
        echo ""
        echo "1. Configure your LOCAL AWS credentials (or use existing ones)."
        echo "2. Run this command from your LAPTOP terminal:"
        echo "   python ../../model_training/upload_s3.py --model-dir ../../model_training/saved_model/fake-news-bert --bucket \$(terraform output -raw model_bucket_name) --version v1"
        echo ""
        echo "The server will automatically download the model from S3 using its IAM Role."
        echo ""
        echo "To connect to your instance:"
        echo "  chmod 400 ai-fake-news-detector-key.pem"
        echo "  ssh -i ai-fake-news-detector-key.pem ubuntu@\$(terraform output -raw instance_public_ip)"
        echo ""
    else
        echo ""
        echo "❌ Infrastructure creation failed!"
        echo "Check the error messages above for details."
        exit 1
    fi
else
    echo ""
    echo "Cancelled. No changes made."
    echo ""
    echo "You can run 'terraform apply' manually when ready."
fi
