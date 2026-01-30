# Kubernetes Architecture

## Overview
The infrastructure runs on a single-node Kubernetes cluster orchestrated by **Kind** (Kubernetes in Docker) on an AWS EC2 instance. This architecture simulates a production-grade environment while maintaining cost-efficiency for demonstration purposes.

![Architecture](../images/Architecture.png)

## Infrastructure Layers

### 1. Physical Layer (AWS)
*   **Instance Type**: `t3.medium` (2 vCPU, 4GB RAM) provided balances cost and performance for this workload.
*   **OS**: Ubuntu 22.04 LTS.

### 2. Orchestration Layer (Kind)
*   **Control Plane**: Runs as a Docker container, hosting the API Server, Controller Manager, and Scheduler.
*   **Data Plane**: The same node acts as the worker, executing application pods.

### 3. Networking
*   **Ingress Controller**: Nginx acts as the entry point, routing HTTP traffic from port 80 to internal services.
*   **Service Mesh**: Standard Kube-Proxy iptables mode for service-to-service communication.

## Namespace Isolation
*   `fake-news-app`: Contains business logic (Frontend/Backend).
*   `argocd`: Hosts the continuous delivery control plane.
*   `monitoring`: Dedicated namespace for Prometheus and Grafana.
