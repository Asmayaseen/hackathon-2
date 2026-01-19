#!/bin/bash
# Phase 4: Minikube Deployment Script
# Evolution Todo - Local Kubernetes Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Phase 4: Minikube Deployment Script  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check minikube
    if ! command -v minikube &> /dev/null; then
        echo -e "${RED}ERROR: minikube not found. Please install it first.${NC}"
        echo "Run: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}ERROR: kubectl not found. Please install it first.${NC}"
        exit 1
    fi

    # Check helm
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}ERROR: helm not found. Please install it first.${NC}"
        echo "Run: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
        exit 1
    fi

    # Check docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}ERROR: docker not found. Please install it first.${NC}"
        exit 1
    fi

    echo -e "${GREEN}All prerequisites met!${NC}"
}

# Start Minikube
start_minikube() {
    echo ""
    echo -e "${YELLOW}Starting Minikube cluster...${NC}"

    # Check if already running
    if minikube status | grep -q "Running"; then
        echo -e "${GREEN}Minikube is already running.${NC}"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi

    # Enable addons
    echo -e "${YELLOW}Enabling addons...${NC}"
    minikube addons enable ingress
    minikube addons enable metrics-server

    echo -e "${GREEN}Minikube is ready!${NC}"
}

# Configure Docker to use Minikube's daemon
configure_docker() {
    echo ""
    echo -e "${YELLOW}Configuring Docker to use Minikube's daemon...${NC}"
    eval $(minikube docker-env)
    echo -e "${GREEN}Docker configured!${NC}"
}

# Build Docker images
build_images() {
    echo ""
    echo -e "${YELLOW}Building Docker images...${NC}"

    # Build backend
    echo "Building backend image..."
    docker build -t todo-backend:latest ./backend

    # Build frontend
    echo "Building frontend image..."
    docker build -t todo-frontend:latest ./frontend

    # Verify
    echo ""
    echo -e "${GREEN}Images built:${NC}"
    docker images | grep todo
}

# Check values-local.yaml exists
check_values_file() {
    echo ""
    echo -e "${YELLOW}Checking configuration...${NC}"

    if [ ! -f "values-local.yaml" ]; then
        echo -e "${RED}WARNING: values-local.yaml not found!${NC}"
        echo "Creating template..."

        cat > values-local.yaml << 'EOF'
# Local Minikube configuration
# IMPORTANT: Fill in your secrets before deploying!

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never

frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never
  service:
    type: NodePort
    nodePort: 30000

env:
  ENVIRONMENT: "local"

secrets:
  DATABASE_URL: "YOUR_DATABASE_URL_HERE"
  BETTER_AUTH_SECRET: "YOUR_BETTER_AUTH_SECRET_HERE"
  OPENAI_API_KEY: "YOUR_OPENAI_API_KEY_HERE"
  GROQ_API_KEY: "YOUR_GROQ_API_KEY_HERE"

ingress:
  enabled: false
EOF

        echo -e "${YELLOW}Please edit values-local.yaml with your secrets and run again.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Configuration file found!${NC}"
}

# Deploy with Helm
deploy_helm() {
    echo ""
    echo -e "${YELLOW}Deploying with Helm...${NC}"

    helm upgrade --install todo-app ./helm -f values-local.yaml

    echo -e "${GREEN}Helm release deployed!${NC}"
}

# Wait for pods to be ready
wait_for_pods() {
    echo ""
    echo -e "${YELLOW}Waiting for pods to be ready...${NC}"

    # Wait for backend
    echo "Waiting for backend..."
    kubectl wait --for=condition=ready pod -l app=todo-app-backend --timeout=120s || true

    # Wait for frontend
    echo "Waiting for frontend..."
    kubectl wait --for=condition=ready pod -l app=todo-app-frontend --timeout=120s || true

    echo ""
    echo -e "${GREEN}Current pod status:${NC}"
    kubectl get pods
}

# Setup port forwarding
setup_port_forward() {
    echo ""
    echo -e "${YELLOW}Setting up port forwarding...${NC}"

    # Kill existing port forwards
    pkill -f "kubectl port-forward" 2>/dev/null || true

    # Forward frontend
    kubectl port-forward svc/todo-app-frontend 3000:3000 &>/dev/null &

    # Forward backend
    kubectl port-forward svc/todo-app-backend 8000:8000 &>/dev/null &

    sleep 2
    echo -e "${GREEN}Port forwarding configured!${NC}"
}

# Print access information
print_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Deployment Complete!                  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Access your application:${NC}"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  Health:   http://localhost:8000/health"
    echo ""
    echo -e "${GREEN}Useful commands:${NC}"
    echo "  kubectl get pods          # Check pod status"
    echo "  kubectl logs -f <pod>     # View logs"
    echo "  helm uninstall todo-app   # Remove deployment"
    echo "  minikube dashboard        # Open K8s dashboard"
    echo ""
    echo -e "${GREEN}Minikube IP: $(minikube ip)${NC}"
}

# Main execution
main() {
    # Change to script directory
    cd "$(dirname "$0")"

    check_prerequisites
    start_minikube
    configure_docker
    build_images
    check_values_file
    deploy_helm
    wait_for_pods
    setup_port_forward
    print_info
}

# Run main function
main "$@"
