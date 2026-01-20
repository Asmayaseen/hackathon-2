# Phase 4: Local Kubernetes Deployment

Evolution Todo App - Local Kubernetes deployment using Docker, Minikube, and Helm.

## Prerequisites

- Docker Desktop (or Docker Engine)
- Minikube
- kubectl
- Helm 3

### Install Prerequisites (Ubuntu/WSL2)

```bash
# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Quick Start

### 1. Set Environment Variables

```bash
# Required - Your Neon DB URL
export DATABASE_URL="postgresql://user:password@host/database?sslmode=require"

# Required - JWT Secret (same as BETTER_AUTH_SECRET)
export JWT_SECRET="your-jwt-secret-here"

# Optional - For AI Chatbot
export GROQ_API_KEY="your-groq-api-key"  # Free at console.groq.com
```

### 2. Run Deployment Script

```bash
cd phase-4
./deploy-local.sh
```

This script will:
1. Start Minikube cluster
2. Build Docker images
3. Deploy with Helm
4. Show access URLs

### 3. Access the Application

```bash
# Port forward to access locally
kubectl port-forward svc/todo-app-backend 8000:8000 &
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Open in browser
xdg-open http://localhost:3000
```

## Manual Deployment Steps

### Step 1: Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server

# Point Docker to Minikube
eval $(minikube docker-env)
```

### Step 2: Build Docker Images

```bash
# Build backend
docker build -t todo-backend:latest -f backend/Dockerfile ../phase-3/backend/

# Build frontend (need to update next.config.ts for standalone)
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-app-backend:8000 \
  -t todo-frontend:latest \
  -f frontend/Dockerfile ../phase-3/frontend/
```

### Step 3: Deploy with Helm

```bash
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-local.yaml \
  --set "secrets.databaseUrl=$DATABASE_URL" \
  --set "secrets.jwtSecret=$JWT_SECRET" \
  --set "secrets.groqApiKey=$GROQ_API_KEY"
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# View logs
kubectl logs -f deployment/todo-app-backend
kubectl logs -f deployment/todo-app-frontend
```

## Directory Structure

```
phase-4/
├── backend/
│   └── Dockerfile           # Backend container
├── frontend/
│   └── Dockerfile           # Frontend container
├── helm/
│   └── todo-app/
│       ├── Chart.yaml       # Helm chart metadata
│       ├── values.yaml      # Default values
│       ├── values-local.yaml # Minikube values
│       └── templates/
│           ├── _helpers.tpl
│           ├── backend.yaml
│           ├── frontend.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           └── ingress.yaml
├── deploy-local.sh          # Automated deployment script
└── README.md                # This file
```

## Troubleshooting

### Pod not starting?
```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'
```

### Container crashing?
```bash
kubectl logs <pod-name> --previous
```

### Database connection issues?
- Check DATABASE_URL is correctly set
- Neon DB requires SSL: `?sslmode=require`

### Image not found?
```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)
docker images | grep todo
```

## Commands Reference

```bash
# Scale backend
kubectl scale deployment/todo-app-backend --replicas=2

# Restart deployment
kubectl rollout restart deployment/todo-app-backend

# Uninstall
helm uninstall todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Containerization | Docker |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm 3 |
| Backend | FastAPI + Python 3.12 |
| Frontend | Next.js 16 |
| Database | Neon Serverless PostgreSQL |
| AI | Groq API (Llama 3.3) |
