#!/bin/bash
# Start the EC2 Instance

# Navigate to terraform directory
cd "$(dirname "$0")/../infra/terraform"

# Get Instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

# Wait for IP to be assigned
echo "Waiting for Public IP assignment..."
sleep 5
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

echo "Instance Started!"
echo "---------------------------------------------"
echo "NEW Public IP: $PUBLIC_IP"
echo "---------------------------------------------"
echo "1. Go to GoDaddy DNS Management"
echo "2. Update 'A' Record value to: $PUBLIC_IP"
echo "3. App URL: http://eshwarsai.xyz:3000"
echo "---------------------------------------------"
