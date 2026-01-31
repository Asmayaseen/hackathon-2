# Phase 4: Local Kubernetes Deployment

Evolution Todo App - Local Kubernetes deployment using Docker, Minikube, and Helm.

## Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose
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
export GROQ_API_KEY="your-groq-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

### 2. Deploy to Minikube

```bash
cd phase-4

# Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker

# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly in Minikube
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 ./frontend

# Deploy with Helm
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-local.yaml \
  --set "secrets.databaseUrl=$DATABASE_URL" \
  --set "secrets.jwtSecret=$JWT_SECRET" \
  --set "secrets.groqApiKey=$GROQ_API_KEY" \
  --set "secrets.openaiApiKey=$OPENAI_API_KEY"
```

### 3. Access the Application

```bash
# Port forward to access locally
kubectl port-forward svc/todo-app-backend 8000:8000 &
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Open in browser
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
```

## Docker Compose (Alternative)

If Minikube has issues, use Docker Compose for local testing:

```bash
cd phase-4

# Build and run with Docker Compose
docker-compose up --build

# Access at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Complete Deployment Commands

### Step 1: Start Minikube

```bash
# Start cluster
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable useful addons
minikube addons enable ingress
minikube addons enable metrics-server

# Point Docker to Minikube (IMPORTANT!)
eval $(minikube docker-env)
```

### Step 2: Build Docker Images

```bash
cd phase-4

# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image (with API URL)
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -t todo-frontend:latest \
  ./frontend

# Verify images exist
docker images | grep todo
```

### Step 3: Deploy with Helm

```bash
# Install/upgrade the release
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-local.yaml \
  --set "secrets.databaseUrl=$DATABASE_URL" \
  --set "secrets.jwtSecret=$JWT_SECRET" \
  --set "secrets.groqApiKey=$GROQ_API_KEY" \
  --set "secrets.openaiApiKey=$OPENAI_API_KEY"
```

### Step 4: Verify Deployment

```bash
# Check pods are running
kubectl get pods

# Check services
kubectl get svc

# Watch pod status
kubectl get pods -w

# View backend logs
kubectl logs -f deployment/todo-app-backend

# View frontend logs
kubectl logs -f deployment/todo-app-frontend
```

### Step 5: Access Application

```bash
# Option A: Port Forward (Recommended)
kubectl port-forward svc/todo-app-backend 8000:8000 &
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Option B: NodePort URLs
minikube service todo-app-frontend --url
minikube service todo-app-backend --url

# Option C: Minikube tunnel (for LoadBalancer)
minikube tunnel
```

## AIOps Tools

### Docker AI Agent (Gordon)

Enable in Docker Desktop: Settings > Beta features > Docker AI

```bash
# Ask Gordon for help
docker ai "What can you do?"

# Build optimized images
docker ai "build an optimized Dockerfile for my Python FastAPI app"

# Debug issues
docker ai "why is my container exiting immediately"
```

### kubectl-ai

```bash
# Install
pip install kubectl-ai
export OPENAI_API_KEY="your-key"

# Usage examples
kubectl-ai "show me all pods and their status"
kubectl-ai "scale todo-app-backend to 3 replicas"
kubectl-ai "show last 100 lines of backend logs"
kubectl-ai "why is the backend pod failing"
```

### kagent

```bash
# Install
pip install kagent
export OPENAI_API_KEY="your-key"

# Usage examples
kagent "analyze the health of my kubernetes cluster"
kagent "check for security issues in current deployment"
kagent "optimize resource allocation for todo-app"
```

## Directory Structure

```
phase-4/
├── backend/
│   ├── Dockerfile           # Backend container
│   ├── main.py             # FastAPI app
│   └── pyproject.toml      # Python dependencies
├── frontend/
│   ├── Dockerfile          # Frontend container
│   ├── next.config.ts      # Next.js config (standalone)
│   └── package.json        # Node dependencies
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
├── docker-compose.yml       # Docker Compose config
├── AIOPS_GUIDE.md          # kubectl-ai & kagent guide
└── README.md               # This file
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

### Frontend can't reach backend?
```bash
# Check backend service
kubectl get svc todo-app-backend
# Test backend health
kubectl exec -it <frontend-pod> -- curl http://todo-app-backend:8000/health
```

## Commands Reference

```bash
# Scale deployment
kubectl scale deployment/todo-app-backend --replicas=2

# Restart deployment
kubectl rollout restart deployment/todo-app-backend

# View resource usage
kubectl top pods

# Uninstall Helm release
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
| AI DevOps | kubectl-ai, kagent, Gordon |
| Backend | FastAPI + Python 3.12 |
| Frontend | Next.js 16 |
| Database | Neon Serverless PostgreSQL |
| AI | OpenAI Agents SDK, Groq API |

## Hackathon Deliverables

- [x] Dockerfile for backend (multi-stage, non-root user)
- [x] Dockerfile for frontend (multi-stage, standalone)
- [x] docker-compose.yml for local testing
- [x] Helm charts in /helm directory
- [x] Minikube deployment instructions
- [x] kubectl commands documented
- [x] AIOps guide (Gordon, kubectl-ai, kagent)
