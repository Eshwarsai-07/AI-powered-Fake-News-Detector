# Terraform AWS Infrastructure Setup

This Terraform configuration creates an EC2 instance with VPC, security groups, and networking for the AI Fake News Detector project.

## What Was Fixed

The previous timeout errors when creating EC2 instances have been resolved by:

1. **Added explicit timeouts** - Extended create timeout to 15 minutes
2. **Root block device configuration** - Properly configured EBS volume (20GB gp3)
3. **User data script** - Ensures instance initializes correctly
4. **Dynamic availability zones** - Automatically selects available AZ instead of hardcoded zone
5. **Proper dependencies** - Ensures networking is ready before EC2 creation
6. **Metadata options** - Configured IMDSv2 for better instance metadata handling

## Prerequisites

1. **AWS Account** - You need an active AWS account
2. **Terraform Installed** - Version 1.0 or higher
3. **AWS Credentials** - Access Key and Secret Access Key

## Setup Instructions

### Step 1: Configure AWS Credentials

You have two options:

#### Option A: Environment Variables (Recommended)
```bash
export AWS_ACCESS_KEY_ID="your-access-key-here"
export AWS_SECRET_ACCESS_KEY="your-secret-key-here"
```

#### Option B: AWS Credentials File
Create/edit `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your-access-key-here
aws_secret_access_key = your-secret-key-here
```

### Step 2: Initialize Terraform

Navigate to the terraform directory and initialize:
```bash
cd /Users/eshwarsai/Desktop/AI\ Fake\ News\ Detector/terraform
terraform init
```

### Step 3: Review the Plan

See what Terraform will create:
```bash
terraform plan
```

### Step 4: Apply the Configuration

Create the infrastructure:
```bash
terraform apply
```

Type `yes` when prompted to confirm.

**Note:** The EC2 instance creation now has a 15-minute timeout, so be patient. It typically takes 2-5 minutes.

### Step 5: Get the Public IP

After successful creation, Terraform will output the public IP:
```bash
terraform output
```

Or specifically:
```bash
terraform output instance_public_ip
```

## What Gets Created

1. **VPC** - Virtual Private Cloud (10.0.0.0/16)
2. **Internet Gateway** - For internet access
3. **Public Subnet** - Subnet for the EC2 instance (10.0.1.0/24)
4. **Route Table** - Routes traffic to internet gateway
5. **Security Group** - Allows SSH (22), HTTP (80), HTTPS (443)
6. **Key Pair** - SSH key for accessing the instance
7. **EC2 Instance** - Ubuntu 22.04 t2.micro instance with 20GB storage

## Files Generated

- `ai-fake-news-detector-key.pem` - Private SSH key (keep this secure!)
- `terraform.tfstate` - Terraform state file (DO NOT delete)
- `.terraform/` - Terraform plugins and modules

## Connecting to Your Instance

Once created, connect via SSH:
```bash
chmod 400 ai-fake-news-detector-key.pem
ssh -i ai-fake-news-detector-key.pem ubuntu@<PUBLIC_IP>
```

Replace `<PUBLIC_IP>` with the IP from terraform output.

## Troubleshooting

### If you still get timeout errors:

1. **Check AWS Service Health**: Visit https://status.aws.amazon.com/
2. **Verify Credentials**: Ensure your AWS credentials are valid
3. **Check Quotas**: Verify you haven't hit EC2 instance limits
4. **Try Different Region**: Edit `main.tf` and change region if needed

### Clean up and retry:

```bash
# Destroy existing resources
terraform destroy

# Clean state
rm -rf .terraform terraform.tfstate*

# Reinitialize and apply
terraform init
terraform apply
```

### Check Terraform logs:

```bash
# Enable detailed logging
export TF_LOG=DEBUG
terraform apply
```

## Destroying Infrastructure

When you're done, clean up to avoid charges:
```bash
terraform destroy
```

Type `yes` to confirm deletion of all resources.

## Cost Estimate

- **t2.micro EC2**: Free tier eligible (750 hours/month free for 12 months)
- **EBS Storage**: ~$2/month for 20GB gp3
- **Data Transfer**: First 1GB free, then $0.09/GB

## Security Notes

1. **SSH Key**: The `.pem` file is stored locally - keep it secure!
2. **Security Group**: Currently allows SSH from anywhere (0.0.0.0/0) - restrict this in production
3. **No Encryption**: Root volume is unencrypted for simplicity - enable in production

## Next Steps

After the EC2 instance is created:
1. SSH into the instance
2. Install Docker and Docker Compose
3. Deploy your AI Fake News Detector application
4. Configure domain and SSL certificates

## Support

If you encounter issues:
- Check the Terraform logs with `TF_LOG=DEBUG`
- Verify AWS credentials are correct
- Ensure you have the necessary AWS permissions
- Check AWS service quotas and limits
