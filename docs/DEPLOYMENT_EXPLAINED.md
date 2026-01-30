# 🚀 End-to-End Deployment Guide: How It Works

This document explains the "Magic" behind your deployment. It covers how we go from **zero** to a fully running **Kubernetes Cluster** on AWS.

---

## 🧩 The 3-Layer Architecture

Your deployment consists of three distinct layers, each handled by a specific tool:

### 1. Infrastructure Layer (Terraform) 🏗️
**Role:** "The Builder"
-   **What it does:** Talks to AWS and rents the physical server (EC2 instance), sets up the network (VPC), attaches the permanent IP (Elastic IP), and opens the firewall ports (Security Groups).
-   **Key Files:** `infra/terraform/*.tf`
-   **Output:** A running Ubuntu server with an IP address (e.g., `3.7.117.77`).

### 2. Configuration Layer (Ansible) ⚙️
**Role:** "The Mechanic"
-   **What it does:** Logs into the empty Ubuntu server and installs necessary software.
-   **Software Installed:**
    -   `Docker`: To run containers.
    -   `Kind`: To create a Kubernetes cluster *inside* Docker.
    -   `Kubectl`: To talk to the Kubernetes cluster.
    -   `Helm`: Package manager for Kubernetes (optional for future).
-   **Key Files:** `infra/ansible/playbook.yml`

### 3. Application Layer (Kubernetes/Kind) ☸️
**Role:** "The Conductor"
-   **What it does:** Orchestrates your application containers.
-   **Components:**
    -   **Kind Cluster:** A local Kubernetes cluster running as a Docker container.
    -   **Pods:** Small units running your code (Frontend, Backend).
    -   **Services:** Networking that allows Pods to talk to each other.
    -   **NodePort:** Exposes your app to the outside world (Ports `3000`, `8000`, etc).

---

## 🔄 How to Redeploy From Scratch (Disaster Recovery)

If you want to delete everything and start over on a fresh EC2 instance, follow these steps:

### Step 1: Destroy Existing Infrastructure 💥
This deletes the server and stops billing (except for the Elastic IP if kept).
```bash
cd infra/terraform
terraform destroy -auto-approve
```

### Step 2: Create New Infrastructure 🏗️
This creates a fresh EC2 instance.
```bash
terraform apply -auto-approve
```
*Wait for it to finish. It will output the new IP (or reuse the Elastic IP).*

### Step 3: Configure the Server (Ansible) ⚙️
This installs Docker, Kind, and sets up the environment.
```bash
cd ../ansible
ansible-playbook -i inventory.ini playbook.yml
```

### Step 4: Deploy the App (Kubernetes) 🚀
This creates the cluster and runs your app.
*(Note: These steps are usually automated by Ansible, but here is the manual breakdown)*

1.  **SSH into the server:**
    ```bash
    ssh -i ../terraform/ai-fake-news-detector-key.pem ubuntu@3.7.117.77
    ```

2.  **Create the Kind Cluster:**
    ```bash
    kind create cluster --config kind-config.yaml
    ```
    *This reads `kind-config.yaml` to open ports 3000, 8000, 3001, 9090.*

3.  **Apply Kubernetes Manifests:**
    ```bash
    kubectl apply -R -f k8s/
    ```
    *This tells Kubernetes to start the Pods defined in your YAML files.*

---

## 🧠 How "Kind" Works (Kubernetes in Docker)

Normally, Kubernetes requires 3+ servers. **Kind** cheats by running Kubernetes *inside* a Docker container.

1.  **The "Node":** Your EC2 instance runs a Docker container called `kind-control-plane`.
2.  **Port Mapping:**
    -   User hits EC2 Port `3000` -> Docker sends to Kind Container Port `30080` -> Kubernetes sends to Frontend Pod Port `80`.
    -   This map is defined in `kind-config.yaml`.

## 🔄 CI/CD Automation
Use `git push` to `main` branch:
1.  **GitHub Actions** builds new Docker images.
2.  It uses **SSH** to log into your EC2.
3.  It runs `kubectl rollout restart` to download the new images and update the app.
