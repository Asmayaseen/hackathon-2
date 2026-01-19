# Deployment Checklist: Phase 4 - Kubernetes Deployment

**Purpose**: Pre-deployment verification before deploying to Minikube
**Created**: 2026-01-19
**Feature**: [spec.md](../spec.md)

## Pre-Deployment Checks

### Environment

- [ ] Docker Desktop/Engine installed and running
- [ ] Minikube installed (`minikube version`)
- [ ] kubectl installed (`kubectl version`)
- [ ] Helm 3.x installed (`helm version`)
- [ ] Sufficient resources (4+ CPU, 8GB+ RAM)

### Secrets & Configuration

- [ ] DATABASE_URL configured (Neon PostgreSQL)
- [ ] BETTER_AUTH_SECRET set (32+ characters)
- [ ] OPENAI_API_KEY configured
- [ ] GROQ_API_KEY configured (optional)
- [ ] No secrets hardcoded in source files
- [ ] `.env` files excluded from git

### Docker Images

- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] Images have proper tags
- [ ] `.dockerignore` files exclude sensitive data

### Helm Charts

- [ ] `helm lint ./phase-4/helm` passes
- [ ] `helm template` generates valid manifests
- [ ] values.yaml has all required fields
- [ ] values-local.yaml configured for Minikube
- [ ] Secrets template properly base64 encodes values

## Deployment Steps

### 1. Start Minikube

```bash
# Start cluster
minikube start --cpus 4 --memory 8192

# Verify
minikube status
kubectl cluster-info
```

- [ ] Minikube cluster running
- [ ] kubectl context set to minikube

### 2. Build Docker Images

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# Verify
docker images | grep todo
```

- [ ] Backend image built
- [ ] Frontend image built
- [ ] Images visible in Minikube's Docker

### 3. Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-app

# Install release
helm install todo-app ./phase-4/helm \
  -n todo-app \
  -f ./phase-4/helm/values-local.yaml

# Verify
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

- [ ] Namespace created
- [ ] Helm release installed
- [ ] Backend pod Running
- [ ] Frontend pod Running
- [ ] Services created

### 4. Verify Application

```bash
# Port forward
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app &
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app &

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:3000
```

- [ ] Backend /health returns 200
- [ ] Backend /ready returns 200 (DB connected)
- [ ] Frontend loads
- [ ] Chatbot responds

## Post-Deployment Verification

### Functional Tests

- [ ] User can sign up
- [ ] User can sign in
- [ ] Chat messages sent successfully
- [ ] Tasks created via chat
- [ ] Voice transcription works (if configured)
- [ ] Urdu language supported

### Operations

- [ ] Logs accessible via `kubectl logs`
- [ ] Pod restarts work correctly
- [ ] Resource limits respected
- [ ] Health probes functioning

## Rollback Plan

If deployment fails:

```bash
# Uninstall release
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube
minikube stop
```

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| DevOps | | | |
| Reviewer | | | |

---

**Deployment Status**: ⬜ Not Started / 🟡 In Progress / ✅ Complete / ❌ Failed

**Notes**:
