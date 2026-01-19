# Minikube Deployment Guide - Phase 4

Complete guide for deploying Todo App to local Kubernetes using Minikube.

## Prerequisites

### 1. Install Required Tools

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
minikube version
kubectl version --client
helm version
```

### 2. Install Docker (if not installed)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Deployment Steps

### Step 1: Start Minikube Cluster

```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Step 2: Configure Docker Environment

**IMPORTANT:** Point your Docker CLI to Minikube's Docker daemon:

```bash
# This ensures images are built inside Minikube
eval $(minikube docker-env)

# Verify (should show minikube containers)
docker ps
```

### Step 3: Build Docker Images

```bash
# Navigate to phase-4 directory
cd /mnt/d/hackathon-2/phase-4

# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Verify images are built
docker images | grep todo
```

### Step 4: Create Secrets File

Create `values-local.yaml` with your secrets (DO NOT COMMIT):

```yaml
# values-local.yaml - Local Minikube configuration
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
  DATABASE_URL: "postgresql://user:password@neon.tech/dbname"
  BETTER_AUTH_SECRET: "your-better-auth-secret"
  OPENAI_API_KEY: "sk-your-openai-key"
  GROQ_API_KEY: "gsk-your-groq-key"

ingress:
  enabled: true
  host: todo.local
```

### Step 5: Deploy with Helm

```bash
# Install the Helm chart
helm upgrade --install todo-app ./helm -f values-local.yaml

# Watch deployment progress
kubectl get pods -w

# Check all resources
kubectl get all
```

### Step 6: Access the Application

**Option A: Port Forwarding (Recommended)**

```bash
# Forward frontend
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Forward backend
kubectl port-forward svc/todo-app-backend 8000:8000 &

# Access at http://localhost:3000
```

**Option B: NodePort**

```bash
# Get Minikube IP
minikube ip

# Access at http://<minikube-ip>:30000
```

**Option C: Minikube Tunnel (for LoadBalancer)**

```bash
# In a separate terminal
minikube tunnel

# Then access via LoadBalancer external IP
kubectl get svc
```

**Option D: Ingress**

```bash
# Add to /etc/hosts
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access at http://todo.local
```

## Verification Commands

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get svc

# View pod logs
kubectl logs -f deployment/todo-app-backend
kubectl logs -f deployment/todo-app-frontend

# Check pod details
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Troubleshooting

### ImagePullBackOff

```bash
# Make sure you're using Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Verify imagePullPolicy is Never in values
```

### CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> --previous

# Check environment variables
kubectl exec <pod-name> -- env

# Check secrets are set
kubectl get secret todo-app-secrets -o yaml
```

### Pending Pods

```bash
# Check resources
kubectl describe node

# Check if requests exceed available resources
kubectl top pods
kubectl top nodes
```

### Connection Refused

```bash
# Verify service is running
kubectl get svc

# Check endpoints
kubectl get endpoints

# Test from inside cluster
kubectl run -it --rm debug --image=busybox -- wget -qO- http://todo-app-backend:8000/health
```

## Useful Commands

```bash
# Rolling restart
kubectl rollout restart deployment/todo-app-backend

# Scale deployment
kubectl scale deployment/todo-app-backend --replicas=3

# View resource usage
kubectl top pods

# Execute into pod
kubectl exec -it deployment/todo-app-backend -- /bin/bash

# Port forward to specific pod
kubectl port-forward pod/<pod-name> 8000:8000
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete all resources
kubectl delete all -l app.kubernetes.io/instance=todo-app

# Stop Minikube
minikube stop

# Delete cluster completely
minikube delete
```

## Quick Start Script

Save as `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Starting Minikube..."
minikube start --cpus=4 --memory=8192 --driver=docker

echo "Configuring Docker environment..."
eval $(minikube docker-env)

echo "Building images..."
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

echo "Deploying with Helm..."
helm upgrade --install todo-app ./helm -f values-local.yaml

echo "Waiting for pods..."
kubectl wait --for=condition=ready pod -l app=todo-app-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-app-frontend --timeout=120s

echo "Setting up port forwarding..."
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &

echo ""
echo "Deployment complete!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
```

Make executable and run:

```bash
chmod +x deploy.sh
./deploy.sh
```
