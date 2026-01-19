#!/bin/bash
# =============================================================================
# Phase 4: Minikube Deployment Script
# Evolution Todo - Local Kubernetes Deployment
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RELEASE_NAME="todo-app"
NAMESPACE="todo-app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}=== Phase 4: Minikube Deployment ===${NC}"
echo "Project Directory: $PROJECT_DIR"

# -----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/6] Checking prerequisites...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}ERROR: $1 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
}

check_command docker
check_command minikube
check_command kubectl
check_command helm

# -----------------------------------------------------------------------------
# Step 2: Start Minikube
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/6] Starting Minikube...${NC}"

if minikube status | grep -q "Running"; then
    echo -e "${GREEN}✓ Minikube is already running${NC}"
else
    echo "Starting Minikube with 4 CPUs and 8GB memory..."
    minikube start --cpus 4 --memory 8192 --driver=docker
fi

# Verify cluster
kubectl cluster-info

# -----------------------------------------------------------------------------
# Step 3: Configure Docker Environment
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/6] Configuring Docker environment...${NC}"

eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker configured to use Minikube's daemon${NC}"

# -----------------------------------------------------------------------------
# Step 4: Build Docker Images
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/6] Building Docker images...${NC}"

echo "Building backend image..."
docker build -t todo-backend:latest "$PROJECT_DIR/backend"
echo -e "${GREEN}✓ Backend image built${NC}"

echo "Building frontend image..."
docker build -t todo-frontend:latest "$PROJECT_DIR/frontend"
echo -e "${GREEN}✓ Frontend image built${NC}"

# Verify images
echo -e "\nDocker images:"
docker images | grep todo

# -----------------------------------------------------------------------------
# Step 5: Create Namespace and Deploy with Helm
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/6] Deploying with Helm...${NC}"

# Create namespace if not exists
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace '$NAMESPACE' ready${NC}"

# Check if release exists
if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    echo "Upgrading existing release..."
    helm upgrade $RELEASE_NAME "$PROJECT_DIR/helm/todo-app" \
        -n $NAMESPACE \
        -f "$PROJECT_DIR/helm/todo-app/values.yaml" \
        --set backend.image.pullPolicy=Never \
        --set frontend.image.pullPolicy=Never
else
    echo "Installing new release..."
    helm install $RELEASE_NAME "$PROJECT_DIR/helm/todo-app" \
        -n $NAMESPACE \
        -f "$PROJECT_DIR/helm/todo-app/values.yaml" \
        --set backend.image.pullPolicy=Never \
        --set frontend.image.pullPolicy=Never
fi

echo -e "${GREEN}✓ Helm release deployed${NC}"

# -----------------------------------------------------------------------------
# Step 6: Wait for Pods and Verify
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[6/6] Waiting for pods to be ready...${NC}"

echo "Waiting for backend pod..."
kubectl wait --for=condition=ready pod -l app=todo-app-backend -n $NAMESPACE --timeout=120s || true

echo "Waiting for frontend pod..."
kubectl wait --for=condition=ready pod -l app=todo-app-frontend -n $NAMESPACE --timeout=120s || true

# Show status
echo -e "\n${BLUE}=== Deployment Status ===${NC}"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# -----------------------------------------------------------------------------
# Access Instructions
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "\nTo access the application:"
echo -e "  ${YELLOW}# Option 1: Port Forward${NC}"
echo "  kubectl port-forward svc/${RELEASE_NAME}-backend 8000:8000 -n $NAMESPACE &"
echo "  kubectl port-forward svc/${RELEASE_NAME}-frontend 3000:3000 -n $NAMESPACE &"
echo ""
echo -e "  ${YELLOW}# Option 2: Minikube Service${NC}"
echo "  minikube service ${RELEASE_NAME}-frontend -n $NAMESPACE"
echo ""
echo -e "  ${YELLOW}# Verify Health${NC}"
echo "  curl http://localhost:8000/health"
echo ""
echo -e "Run ${BLUE}./scripts/verify-deployment.sh${NC} to verify the deployment."
