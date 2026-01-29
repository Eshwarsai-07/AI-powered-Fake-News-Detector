#!/bin/bash
# Start the EC2 Instance

# Navigate to terraform directory
cd "$(dirname "$0")/../infra/terraform"

# Get Instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

echo "Starting EC2 Instance: $INSTANCE_ID..."
aws ec2 start-instances --instance-ids "$INSTANCE_ID" --region ap-south-1
echo "Instance starting. Please wait 2-3 minutes for Kubernetes to become active."
echo "Application URL: http://3.7.117.77:3000"
