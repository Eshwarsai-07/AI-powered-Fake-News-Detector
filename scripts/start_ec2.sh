#!/bin/bash
# Start the EC2 Instance

# Navigate to terraform directory
cd "$(dirname "$0")/../infra/terraform"

# Get Instance ID
INSTANCE_ID=$(terraform output -raw instance_id)
echo "Instance ID: $INSTANCE_ID"

# Start the instance
echo "Starting instance..."
aws ec2 start-instances --instance-ids "$INSTANCE_ID" > /dev/null

# Wait for it to be running
echo "Waiting for instance to be in 'running' state..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

# Get Public IP
echo "Fetching Public IP..."
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

echo "---------------------------------------------"
echo "Instance Started Successfully!"
echo "---------------------------------------------"
echo "NEW Public IP: $PUBLIC_IP"
echo "---------------------------------------------"
echo "1. Go to GoDaddy DNS Management"
echo "2. Update 'A' Record value to: $PUBLIC_IP"
echo "3. App URL: http://eshwarsai.xyz"
echo "---------------------------------------------"
