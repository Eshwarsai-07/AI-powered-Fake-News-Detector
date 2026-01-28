# 🚀 Quick Start Guide

## What's Been Fixed

Your Terraform configuration had **timeout issues** when creating EC2 instances. Here's what was fixed:

### ✅ Problems Solved

1. **Extended Timeouts** - Increased from default 10min to 15min
2. **Root Volume Config** - Added proper EBS volume configuration (20GB gp3)
3. **User Data Script** - Ensures instance initializes correctly
4. **Dynamic AZ Selection** - No more hardcoded availability zones
5. **Proper Dependencies** - Ensures networking is ready before EC2 creation
6. **Metadata Options** - Configured IMDSv2 for better compatibility

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ AWS Account with active credentials
- ✅ Terraform installed (`brew install terraform` on Mac)
- ✅ Your AWS Access Key ID
- ✅ Your AWS Secret Access Key

---

## 🎯 Three Ways to Deploy

### Option 1: Automated Setup (Easiest) ⭐

```bash
cd /Users/eshwarsai/Desktop/AI\ Fake\ News\ Detector/terraform
./setup.sh
```

The script will:
- Prompt for your AWS credentials
- Initialize Terraform
- Show you what will be created
- Create the infrastructure
- Display connection information

### Option 2: Manual Steps

```bash
# 1. Set AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# 2. Navigate to terraform directory
cd /Users/eshwarsai/Desktop/AI\ Fake\ News\ Detector/terraform

# 3. Initialize Terraform
terraform init

# 4. Preview changes
terraform plan

# 5. Create infrastructure
terraform apply
```

Type `yes` when prompted.

### Option 3: Troubleshoot First

If you're having issues, run the troubleshooting script first:

```bash
cd /Users/eshwarsai/Desktop/AI\ Fake\ News\ Detector/terraform
./troubleshoot.sh
```

This will check:
- Terraform installation
- AWS credentials
- Configuration validity
- Current state
- And more...

---

## ⏱️ Expected Timeline

- **Initialization**: 30 seconds - 1 minute
- **Planning**: 10-30 seconds
- **Creation**: 3-8 minutes (timeout set to 15 minutes for safety)

**Don't panic if it takes a few minutes!** The extended timeout prevents the errors you experienced before.

---

## 📊 After Successful Creation

You'll see output like this:

```
connection_info = <<EOT

╔════════════════════════════════════════════════════════════╗
║           EC2 Instance Connection Information              ║
╚════════════════════════════════════════════════════════════╝

Public IP:    13.232.XXX.XXX
Instance ID:  i-0123456789abcdef0
Region:       ap-south-1
AZ:           ap-south-1a

SSH Command:
chmod 400 ai-fake-news-detector-key.pem
ssh -i ai-fake-news-detector-key.pem ubuntu@13.232.XXX.XXX

Security Group Ports Open:
- SSH:   22
- HTTP:  80
- HTTPS: 443

EOT
```

---

## 🔐 Connect to Your Instance

```bash
# Make sure key has correct permissions
chmod 400 ai-fake-news-detector-key.pem

# Connect via SSH
ssh -i ai-fake-news-detector-key.pem ubuntu@<YOUR_PUBLIC_IP>
```

Replace `<YOUR_PUBLIC_IP>` with the IP from the output.

---

## 🗑️ Clean Up (When Done)

### Automated Cleanup

```bash
./cleanup.sh
```

### Manual Cleanup

```bash
terraform destroy
```

Type `yes` to confirm.

---

## 🆘 Troubleshooting

### Still Getting Timeouts?

1. **Check AWS Service Status**: https://status.aws.amazon.com/
2. **Verify Credentials**: Make sure your AWS keys are valid
3. **Try Different Region**: Edit `variables.tf` and change `aws_region`
4. **Check Quotas**: You might have hit EC2 limits in your account

### Run Diagnostics

```bash
./troubleshoot.sh
```

### Enable Debug Logging

```bash
export TF_LOG=DEBUG
terraform apply
```

### Clean Slate

```bash
# Destroy everything
terraform destroy

# Remove all local files
rm -rf .terraform terraform.tfstate* ai-fake-news-detector-key.pem

# Start fresh
terraform init
terraform apply
```

---

## 📁 Files Created

After running Terraform, you'll have:

- `ai-fake-news-detector-key.pem` - SSH private key (keep secure!)
- `terraform.tfstate` - State file (don't delete!)
- `.terraform/` - Terraform plugins

---

## 💰 Cost Estimate

- **EC2 t2.micro**: FREE (750 hours/month for 12 months)
- **EBS 20GB gp3**: ~$1.60/month
- **Data Transfer**: First 1GB free, then $0.09/GB

**Total**: ~$1.60/month (or FREE if within free tier)

---

## 🔒 Security Notes

⚠️ **IMPORTANT**:

1. **Never commit** `ai-fake-news-detector-key.pem` to git
2. **Never share** your AWS credentials
3. **Restrict SSH access** in production (currently open to 0.0.0.0/0)
4. The `.gitignore` file protects sensitive files automatically

---

## 📚 Available Scripts

| Script | Purpose |
|--------|---------|
| `setup.sh` | Automated setup and deployment |
| `cleanup.sh` | Automated cleanup and destroy |
| `troubleshoot.sh` | Diagnose issues |

---

## 🎓 Next Steps

After your EC2 instance is running:

1. **SSH into the instance**
2. **Install Docker**: 
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   ```
3. **Install Docker Compose**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```
4. **Deploy your application**
5. **Configure domain** (if you have one)
6. **Set up SSL/HTTPS**

---

## 📞 Need Help?

1. Run `./troubleshoot.sh` for diagnostics
2. Check the detailed `README.md` for more information
3. Review Terraform logs with `TF_LOG=DEBUG`

---

## ✨ Summary

**You're ready to deploy!** The timeout issues have been fixed with:
- Extended timeouts (15 minutes)
- Proper volume configuration
- Dynamic availability zone selection
- Better error handling

Just run `./setup.sh` and provide your AWS credentials when prompted. 🚀
