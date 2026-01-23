#!/bin/bash

# Script to load Docker images into the kind cluster
# kind clusters can't access your local Docker images by default

set -e  # Exit on any error

echo "📦 Loading Docker images into kind cluster..."

# Check if kind cluster exists
if ! kind get clusters | grep -q "^fake-news$"; then
    echo "❌ kind cluster 'fake-news' not found. Please run setup-kind.sh first."
    exit 1
fi

# Check if Docker images exist
echo "🔍 Checking for Docker images..."

if ! docker images | grep -q "fake-news-backend"; then
    echo "❌ Docker image 'fake-news-backend:latest' not found."
    echo "   Please build it first: docker-compose build backend"
    exit 1
fi

if ! docker images | grep -q "fake-news-frontend"; then
    echo "❌ Docker image 'fake-news-frontend:latest' not found."
    echo "   Please build it first: docker-compose build frontend"
    exit 1
fi

# Load backend image into kind
echo "📥 Loading backend image into kind cluster..."
kind load docker-image fake-news-backend:latest --name fake-news

# Load frontend image into kind
echo "📥 Loading frontend image into kind cluster..."
kind load docker-image fake-news-frontend:latest --name fake-news

echo "✅ Docker images loaded successfully!"
echo ""
echo "Next step:"
echo "Deploy the app: ./scripts/deploy-k8s.sh"
