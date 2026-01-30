# 🆘 AI Fake News Detector - Operations Guide

This guide explains how your deployment works, how to access it, and how to manage costs.

## 🏗 Architecture Overview

-   **Cloud Provider:** AWS (EC2 Instance)
-   **Orchestration:** Kubernetes (Kind - Kubernetes in Docker)
-   **Services:**
    -   **Frontend:** React App (Port `3000`)
    -   **Backend:** FastAPI with BERT Model (Port `8000`)
    -   **Database:** MongoDB Atlas (External)
    -   **Monitoring:** Prometheus (Port `9090`) & Grafana (Port `3001`)

---

## 🔑 How to Log In (SSH)

To access your server terminal (EC2 instance), run this command from your project folder:

```bash
# 1. Ensure your key has correct permissions
chmod 400 "infra/terraform/ai-fake-news-detector-key.pem"

# 2. SSH into the server
ssh -i "infra/terraform/ai-fake-news-detector-key.pem" ubuntu@3.7.117.77
```

---

## ☸️ Managing the Kind Cluster

Once logged in via SSH, you can use `kubectl` to manage your application.

### Check Cluster Status
```bash
# Get all pods (Frontend, Backend, Monitoring)
kubectl get pods -A

# Check services and ports
kubectl get svc -n fake-news-app
```

### View Application Logs
```bash
# Backend Logs
kubectl logs -l app=backend -n fake-news-app -f

# Frontend Logs
kubectl logs -l app=frontend -n fake-news-app -f
```

### Restarting Services
If something is stuck, you can restart the deployment:
```bash
kubectl rollout restart deployment backend -n fake-news-app
```

---

## 💰 Cost Management (Stop/Start)

**⚠️ Important:** You are charged for the EC2 instance while it is **Running**.
You are also charged a small fee for the **Elastic IP** if the instance is **Stopped**.
To verify current costs, check the [AWS Billing Dashboard](https://console.aws.amazon.com/billing/home).

### Stopping the Server (Pause Work)
Use the provided script to stop the instance and save compute costs:
```bash
./scripts/stop_ec2.sh
```

### Starting the Server (Resume Work)
```bash
./scripts/start_ec2.sh
```
**CRITICAL: After the server starts:**
1.  Copy the **NEW Public IP** output by the script.
2.  Log in to **GoDaddy**.
3.  Update your **A Record (@)** with this new IP.
4.  Wait ~5 minutes, then your app at `http://eshwarsai.xyz:3000` will work again!

---
