#!/bin/bash
# Setup ArgoCD on Kind Cluster

echo "----------------------------------------------------"
echo "Installing ArgoCD..."
echo "----------------------------------------------------"

# 1. Create Namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# 2. Install ArgoCD (Stable)
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Wait for ArgoCD server
echo "Waiting for ArgoCD server to be ready..."
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

echo "----------------------------------------------------"
echo "Configuring Projects and Apps..."
echo "----------------------------------------------------"

# Resolve script directory to allow running from anywhere
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# 4. Apply Project
kubectl apply -f "$REPO_ROOT/k8s/argocd/project.yaml"

# 5. Apply App of Apps
kubectl apply -f "$REPO_ROOT/k8s/argocd/applications.yaml"

echo "----------------------------------------------------"
echo "ArgoCD Setup Complete!"
echo "----------------------------------------------------"
echo "Access ArgoCD UI:"
echo "1. Port Forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "2. Open: https://localhost:8080"
echo "3. Default User: admin"
echo "4. Get Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d"
