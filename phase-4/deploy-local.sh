#!/bin/bash
# Phase 4: Local Minikube Deployment Script
# Following cloud-native-k8s-blueprint and operating-k8s-local skills

set -e

echo "🚀 Evolution Todo - Phase 4 Local Kubernetes Deployment"
echo "========================================================"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v minikube &> /dev/null; then
        echo "❌ Minikube not installed. Install from: https://minikube.sigs.k8s.io/"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not installed. Install from: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        echo "❌ Helm not installed. Install from: https://helm.sh/docs/intro/install/"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not installed. Install from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    echo "✅ All prerequisites installed"
}

# Start Minikube
start_minikube() {
    echo ""
    echo "🔧 Starting Minikube cluster..."
    
    if minikube status | grep -q "Running"; then
        echo "✅ Minikube already running"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
        echo "✅ Minikube started"
    fi
    
    # Enable addons
    echo "📦 Enabling addons..."
    minikube addons enable ingress
    minikube addons enable metrics-server
}

# Build Docker images
build_images() {
    echo ""
    echo "🐳 Building Docker images..."
    
    # Point to Minikube's Docker daemon
    eval $(minikube docker-env)
    
    # Build backend
    echo "Building backend image..."
    cd "$(dirname "$0")"
    
    # Copy phase-3 backend files temporarily
    rm -rf backend-build
    mkdir -p backend-build
    cp -r ../phase-3/backend/* backend-build/
    rm -rf backend-build/.venv backend-build/__pycache__ backend-build/.env backend-build/.git
    
    # Copy our Dockerfile
    cp backend/Dockerfile backend-build/
    
    docker build -t todo-backend:latest backend-build/
    rm -rf backend-build
    
    # Build frontend
    echo "Building frontend image..."
    rm -rf frontend-build
    mkdir -p frontend-build
    cp -r ../phase-3/frontend/* frontend-build/
    rm -rf frontend-build/node_modules frontend-build/.next frontend-build/.env frontend-build/.git
    
    # Update next.config.ts for standalone output
    cat > frontend-build/next.config.ts << 'NEXTCONFIG'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
NEXTCONFIG
    
    # Copy our Dockerfile
    cp frontend/Dockerfile frontend-build/
    
    docker build \
        --build-arg NEXT_PUBLIC_API_URL=http://todo-app-backend:8000 \
        -t todo-frontend:latest frontend-build/
    rm -rf frontend-build
    
    echo "✅ Docker images built successfully"
    docker images | grep todo
}

# Deploy with Helm
deploy_helm() {
    echo ""
    echo "⎈ Deploying with Helm..."
    
    # Check for required secrets
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ DATABASE_URL environment variable not set"
        echo "   Export it: export DATABASE_URL='your-neon-db-url'"
        exit 1
    fi
    
    if [ -z "$BETTER_AUTH_SECRET" ] && [ -z "$JWT_SECRET" ]; then
        echo "❌ JWT_SECRET or BETTER_AUTH_SECRET environment variable not set"
        echo "   Export it: export JWT_SECRET='your-secret'"
        exit 1
    fi
    
    JWT_SECRET="${JWT_SECRET:-$BETTER_AUTH_SECRET}"
    
    cd "$(dirname "$0")/helm/todo-app"
    
    helm upgrade --install todo-app . \
        -f values-local.yaml \
        --set "secrets.databaseUrl=$DATABASE_URL" \
        --set "secrets.jwtSecret=$JWT_SECRET" \
        --set "secrets.groqApiKey=${GROQ_API_KEY:-}" \
        --set "secrets.openaiApiKey=${OPENAI_API_KEY:-}"
    
    echo "✅ Helm deployment complete"
}

# Wait for pods
wait_for_pods() {
    echo ""
    echo "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=todo-app-backend --timeout=120s || true
    kubectl wait --for=condition=ready pod -l app=todo-app-frontend --timeout=120s || true
    
    echo ""
    echo "📊 Pod Status:"
    kubectl get pods
}

# Get access URLs
show_access() {
    echo ""
    echo "🌐 Access URLs:"
    echo "Backend:  $(minikube service todo-app-backend --url 2>/dev/null || echo 'Use: kubectl port-forward svc/todo-app-backend 8000:8000')"
    echo "Frontend: $(minikube service todo-app-frontend --url 2>/dev/null || echo 'Use: kubectl port-forward svc/todo-app-frontend 3000:3000')"
    
    echo ""
    echo "💡 Or run port-forward commands:"
    echo "   kubectl port-forward svc/todo-app-backend 8000:8000 &"
    echo "   kubectl port-forward svc/todo-app-frontend 3000:3000 &"
}

# Main
main() {
    check_prerequisites
    start_minikube
    build_images
    deploy_helm
    wait_for_pods
    show_access
    
    echo ""
    echo "✅ Deployment complete! 🎉"
}

main "$@"
