# Infrastructure Specification: Minikube Deployment

**Phase**: 4 - Local Kubernetes Deployment
**Created**: 2026-01-18
**Status**: Complete

## Overview

Local Kubernetes deployment specifications using Minikube.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Minikube | Latest | Local Kubernetes cluster |
| kubectl | Latest | Kubernetes CLI |
| Helm | 3.x | Package manager |
| Docker | Latest | Container runtime |

## Cluster Configuration

### Minikube Start Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| --cpus | 4 | Sufficient for frontend + backend |
| --memory | 8192 | 8GB for comfortable operation |
| --driver | docker | Most compatible driver |

### Required Addons

| Addon | Purpose |
|-------|---------|
| ingress | HTTP routing (optional) |
| metrics-server | Resource monitoring |

## Deployment Flow

### Step 1: Start Cluster

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step 2: Configure Docker

```bash
eval $(minikube docker-env)
```

**Critical**: This ensures images are built inside Minikube's Docker daemon.

### Step 3: Build Images

```bash
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

### Step 4: Deploy with Helm

```bash
helm upgrade --install todo-app ./helm -f values-local.yaml
```

### Step 5: Verify Deployment

```bash
kubectl get pods
kubectl get svc
```

### Step 6: Access Application

**Option A: Port Forward**
```bash
kubectl port-forward svc/todo-app-frontend 3000:3000
kubectl port-forward svc/todo-app-backend 8000:8000
```

**Option B: NodePort**
```bash
minikube ip  # Get IP
# Access at http://<minikube-ip>:30000
```

**Option C: Minikube Tunnel**
```bash
minikube tunnel
```

## Resource Requirements

### Minimum Cluster Resources

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| Memory | 4GB | 8GB |
| Disk | 20GB | 40GB |

### Per-Pod Resources

| Service | CPU Request | Memory Request |
|---------|-------------|----------------|
| Backend | 100m | 128Mi |
| Frontend | 100m | 128Mi |

## Networking

### Service Types

| Service | Type | Port | Access |
|---------|------|------|--------|
| Backend | ClusterIP | 8000 | Internal only |
| Frontend | NodePort | 3000:30000 | External via NodePort |

### Internal Communication

- Frontend → Backend: `http://todo-app-backend:8000`
- Uses Kubernetes DNS for service discovery

## Troubleshooting

### Common Issues

1. **ImagePullBackOff**
   - Ensure `eval $(minikube docker-env)` was run
   - Check `imagePullPolicy: Never` in values

2. **CrashLoopBackOff**
   - Check logs: `kubectl logs <pod-name>`
   - Verify environment variables are set

3. **Pending Pods**
   - Check resources: `kubectl describe node`
   - Increase Minikube resources

4. **Connection Refused**
   - Verify services: `kubectl get svc`
   - Check endpoints: `kubectl get endpoints`

## Cleanup

```bash
helm uninstall todo-app
minikube stop
minikube delete  # Full cleanup
```

## Acceptance Criteria

- [ ] Minikube cluster starts successfully
- [ ] Both images build inside Minikube's Docker
- [ ] Helm chart installs without errors
- [ ] All pods reach Running state
- [ ] Application is accessible via port-forward
- [ ] Chatbot functionality works end-to-end
- [ ] Logs show successful startup
- [ ] Cleanup removes all resources
