#!/bin/bash

# Script to deploy the Fake News Detector app to Kubernetes
# This applies all YAML files in the correct order

set -e  # Exit on any error

echo "🚀 Deploying Fake News Detector to Kubernetes..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not connected to a cluster."
    echo "   Please run setup-kind.sh first."
    exit 1
fi

# 1. Create namespace
echo "📁 Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# 2. Create persistent volumes
echo "💾 Creating persistent volumes..."
kubectl apply -f k8s/volumes/model-pv.yaml
kubectl apply -f k8s/volumes/model-pvc.yaml

# Wait for PVC to be bound
echo "⏳ Waiting for PVC to be bound..."
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/model-pvc -n fake-news-app --timeout=60s || true

# 3. Deploy database
echo "🗄️ Deploying database..."
kubectl apply -f k8s/database/mongodb.yaml

# 4. Deploy backend
echo "🧠 Deploying backend..."
kubectl apply -f k8s/backend/configmap.yaml
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml
kubectl apply -f k8s/backend/hpa.yaml

# 4. Deploy frontend
echo "🎨 Deploying frontend..."
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml

# 5. Deploy ingress
echo "🌐 Deploying ingress..."
kubectl apply -f k8s/ingress/ingress.yaml

# 6. Deploy monitoring (optional, may fail if Prometheus Operator not installed)
echo "📊 Deploying monitoring..."
kubectl apply -f k8s/monitoring/prometheus.yaml || echo "⚠️  Prometheus deployment skipped (may need Prometheus Operator)"
kubectl apply -f k8s/monitoring/grafana.yaml || echo "⚠️  Grafana deployment skipped"
kubectl apply -f k8s/monitoring/servicemonitor.yaml || echo "⚠️  ServiceMonitor skipped (needs Prometheus Operator)"

# Wait for deployments to be ready
echo "⏳ Waiting for backend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/backend -n fake-news-app

echo "⏳ Waiting for frontend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/frontend -n fake-news-app

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Access your application:"
echo "   Frontend:   http://localhost:30080"
echo "   Prometheus: http://localhost:30090"
echo "   Grafana:    http://localhost:30091 (admin/admin123)"
echo ""
echo "🔍 Check status:"
echo "   kubectl get pods -n fake-news-app"
echo "   kubectl get svc -n fake-news-app"
echo ""
echo "📝 View logs:"
echo "   kubectl logs -f deployment/backend -n fake-news-app"
echo "   kubectl logs -f deployment/frontend -n fake-news-app"
