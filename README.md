# AI Fake News Detector 🔍

A production-ready ML platform for detecting fake news using a fine-tuned BERT model. This project demonstrates a full-stack AI application integrated with professional DevOps practices: **Infrastructure as Code (Terraform)**, **Configuration Automation (Ansible)**, and **GitOps (Argo CD)**.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Green)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-purple)
![Ansible](https://img.shields.io/badge/Ansible-Ready-red)
![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange)

---

## 🏗️ Cloud Architecture

The platform is designed to be fully automated and secure on AWS:

1.  **Infrastructure (Terraform)**: Provisions VPC, S3 (for models), and an EC2 instance with an **IAM Instance Profile** (No long-lived AWS keys in the app!).
2.  **Configuration (Ansible)**: Bootstraps the EC2 host with Docker, Kubernetes (Kind), and Argo CD.
3.  **ML Lifecycle**: Models are trained offline and uploaded to S3. At startup, the Backend Pod downloads the model directly from S3 using IAM credentials.
4.  **GitOps (Argo CD)**: Syncs Kubernetes manifests from the `main` branch to the cluster automatically.

---

## 📁 Project Structure

```bash
.
├── infra/                  # Infrastructure as Code
│   ├── terraform/          # AWS Provisioning (VPC, EC2, S3, IAM)
│   └── ansible/            # Host Configuration (Docker, K8s, Argo CD)
├── k8s/                    # Kubernetes Manifests (GitOps Source)
├── backend/                # FastAPI ML Inference Service
├── frontend/               # React User Interface
├── model_training/         # Local training scripts & S3 uploader
└── README.md
```

---

## 🚀 Deployment Guide

### 1. Provision & Bootstrap
Deploy the entire cloud stack with one command:
```bash
cd infra/terraform
./setup.sh
```

### 2. Upload ML Model
Once the infrastructure is ready, upload your fine-tuned BERT model:
```bash
python model_training/upload_s3.py \
  --model-dir model_training/saved_model/fake-news-bert \
  --bucket <YOUR_TF_OUTPUT_BUCKET> \
  --version v1
```

### 3. Access the Stack
All services are exposed via your **EC2 Public IP**:
- **Application**: `http://<EC2_IP>:30080`
- **Argo CD**: `http://<EC2_IP>:8080`
- **Dashboards**: Grafana (`:3000`) & Prometheus (`:9090`)

---

## 🛡️ Security & Reliability

- **IAM Instance Profile**: Applications authenticate to AWS services via temporary metadata tokens, not hardcoded secrets.
- **NodePort Exposure**: Tools are secured via AWS Security Groups, allowing access only to specific management ports.
- **Fail-Fast Logic**: The backend validates external dependencies (S3, MongoDB Atlas) at startup and logs detailed health metrics.
- **MongoDB Atlas**: Fully integrated for persistent prediction history.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Model** | BERT (Hugging Face Transformers) |
| **Backend** | FastAPI, Python 3.10, PyTorch |
| **Frontend** | React 18, Vite |
| **Database** | MongoDB Atlas |
| **Infrastructure** | Terraform, AWS (VPC, EC2, S3, IAM) |
| **Orchestration** | Kubernetes (Kind), Ansible |
| **Observability** | Prometheus, Grafana |
| **CI/CD** | GitHub Actions, Argo CD |

---

**Built for scalability and security. Ready for production demo.**
