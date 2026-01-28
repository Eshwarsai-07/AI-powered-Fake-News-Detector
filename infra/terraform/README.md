# AWS Infrastructure with Terraform & Ansible

This directory contains the automation necessary to provision and configure the cloud infrastructure for the AI Fake News Detector.

## 🏗️ What is Provisioned?

- **VPC & Networking**: A secure, isolated network with public subnets.
- **S3 Bucket**: Private storage for ML model artifacts (with versioning).
- **IAM Role**: An instance profile that allows the EC2 server to read from S3 securely.
- **EC2 Instance**: A `t3.medium` Ubuntu server sized for BERT inference and Kubernetes (Kind).
- **Security Group**: Firewall rules for SSH, HTTP, HTTPS, and management ports (3000, 8080, 9090).

---

## 🚀 Quick Start (Automated)

The easiest way to deploy is using the provided setup script:

```bash
cd infra/terraform
./setup.sh
```

**The script will:**
1. Initialize Terraform.
2. Provision all AWS resources.
3. Automatically generate an `inventory.ini` for Ansible.
4. Trigger the Ansible playbook to bootstrap Docker, Kubernetes, and Argo CD.

---

## 🛠️ Manual Workflow (Advanced)

If you prefer to run steps manually:

1. **Initialize**: `terraform init`
2. **Apply**: `terraform apply`
3. **Bootstrap**: Navigate to `../ansible` and run the playbook using the generated inventory.

---

## 🔐 Security Notes

- **Identity-Based Access**: The backend application uses **IAM Roles**, not long-lived Access Keys, to access S3.
- **Private Keys**: Your SSH key (`ai-fake-news-detector-key.pem`) is generated locally and ignored by Git. **Do not share it.**
- **Region**: Defaults to `ap-south-1`. This can be changed in `variables.tf`.

---

## 🧹 Cleanup

To avoid AWS charges when done:
```bash
./cleanup.sh
# OR
terraform destroy
```
