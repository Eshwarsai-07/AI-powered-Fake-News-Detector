#!/bin/bash

# Script to set up a kind (Kubernetes in Docker) cluster for the Fake News Detector app
# This creates a local Kubernetes cluster on your Mac

set -e  # Exit on any error

echo "🚀 Setting up kind cluster for Fake News Detector..."

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ kind is not installed. Please install it first:"
    echo "   brew install kind"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   brew install kubectl"
    exit 1
fi

# Delete existing cluster if it exists
if kind get clusters | grep -q "^fake-news$"; then
    echo "⚠️  Existing 'fake-news' cluster found. Deleting it..."
    kind delete cluster --name fake-news
fi

# Create kind cluster with custom configuration
echo "📦 Creating kind cluster 'fake-news'..."
cat <<EOF | kind create cluster --name fake-news --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 30080  # Frontend
    hostPort: 30080
    protocol: TCP
  - containerPort: 30090  # Prometheus
    hostPort: 30090
    protocol: TCP
  - containerPort: 30091  # Grafana
    hostPort: 30091
    protocol: TCP
  - containerPort: 80     # Ingress HTTP
    hostPort: 80
    protocol: TCP
  - containerPort: 443    # Ingress HTTPS
    hostPort: 443
    protocol: TCP
  extraMounts:
  - hostPath: $(pwd)/model_training/saved_model
    containerPath: /mnt/data/model
EOF

# Wait for cluster to be ready
echo "⏳ Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=120s

# Install NGINX Ingress Controller
echo "📥 Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
echo "⏳ Waiting for NGINX Ingress Controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

echo "✅ kind cluster 'fake-news' is ready!"
echo ""
echo "Next steps:"
echo "1. Load Docker images: ./scripts/load-images-kind.sh"
echo "2. Deploy the app: ./scripts/deploy-k8s.sh"
