#!/bin/bash
# Stop the EC2 Instance to save costs

# Navigate to terraform directory
cd "$(dirname "$0")/../infra/terraform"

# Get Instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

echo "Stopping EC2 Instance: $INSTANCE_ID..."
aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region ap-south-1
echo "Instance stopping. It may take a minute to fully stop."
