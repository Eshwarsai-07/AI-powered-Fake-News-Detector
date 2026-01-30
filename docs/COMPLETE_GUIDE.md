# AI Fake News Detector - Complete Operations Guide

## 1. System Architecture: How It Works

This project is a full-stack AI application running on a modern "Cloud Native" stack. Here is the flow:

1.  **Code & CI/CD:**
    *   You push code to **GitHub**.
    *   **GitHub Actions** automatically builds Docker images for Backend (FastAPI + BERT) and Frontend (React).
    *   Images are pushed to **GitHub Container Registry (GHCR)**.

2.  **Infrastructure (AWS EC2):**
    *   An AWS EC2 `t2.large` instance hosts the application.
    *   **Terraform** sets up this server automatically.

3.  **Orchestration (Kubernetes/Kind):**
    *   Inside the EC2 instance, we run **Kind** (Kubernetes in Docker).
    *   **ArgoCD** runs inside the cluster. It watches your Git repository.
    *   When you change Kubernetes files (`k8s/`), ArgoCD automatically updates the running app.

4.  **Monitoring:**
    *   **Prometheus** collects metrics (CPU/Memory) from your pods.
    *   **Grafana** visualizes these metrics in dashboards.

---

## 2. Beginner's Start Guide

### Prerequisites (What you need installed)
*   **Git**: To push code.
*   **AWS CLI**: To talk to AWS.
*   **Terraform**: To create the server.
*   **Kubectl**: To control Kubernetes.
*   **Docker**: To see what's happening locally.

### Step 1: Create the Server (Infrastructure)
1.  Navigate to the infrastructure folder:
    ```bash
    cd infra/terraform
    ```
2.  Initialize and Apply Terraform:
    ```bash
    terraform init
    terraform apply -auto-approve
    ```
    *This creates the EC2 instance, VPC, and Security Groups.*

### Step 2: Start the Application Stack
We have a master script that connects to the new server and installs everything (Docker, Kind, Kubernetes Pods, ArgoCD).

1.  Run the start script from the root of the project:
    ```bash
    ./scripts/start_ec2.sh
    ```
    *   It will output your **Public IP**.
    *   Go to GoDaddy/Namecheap and update your Domain's `A` Record to this IP.

2.  **Wait 5-10 minutes** for the server to install everything.

### Step 3: Deployment (CI/CD)
You don't need to manually copy code to the server!
1.  Make changes to your code locally.
2.  Push to GitHub:
    ```bash
    git push origin main
    ```
3.  **GitHub Actions** builds the new image.
4.  **ArgoCD** (on the server) pulls the new image and updates the app.

---

## 3. Accessing the System

| Component | URL (Local Access via Tunnel) | Port Forward Command (Run on Laptop) | Login |
|---|---|---|---|
| **Web App** | [http://eshwarsai.xyz:3000](http://eshwarsai.xyz:3000) | *None (Public Access)* | - |
| **ArgoCD** | [https://localhost:8080](https://localhost:8080) | `ssh -i infra/terraform/ai-fake-news-detector-key.pem -L 8080:localhost:8080 ubuntu@<IP>` | `admin` / *(Get from Secret)* |
| **Grafana** | [http://localhost:3002](http://localhost:3002) | `ssh -i infra/terraform/ai-fake-news-detector-key.pem -L 3002:localhost:3002 ubuntu@<IP>` | `admin` / `admin` |

### How to Get the ArgoCD Password
SSH into the server and run:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

---

## 4. Useful Commands

**Pull latest code on Server:**
```bash
ssh -i infra/terraform/ai-fake-news-detector-key.pem ubuntu@<IP>
cd ai-fake-news-detector
git pull origin main
```

**Force restart App:**
```bash
kubectl rollout restart deployment/backend -n fake-news-app
kubectl rollout restart deployment/frontend -n fake-news-app
```

**Check Pod Status:**
```bash
kubectl get pods -A
```
