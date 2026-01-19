# Infrastructure Specification: AIOps Tools

**Phase**: 4 - Local Kubernetes Deployment
**Created**: 2026-01-18
**Status**: Complete

## Overview

AI-assisted DevOps tools for Kubernetes operations.

## Tools Overview

| Tool | Purpose | Availability |
|------|---------|--------------|
| kubectl-ai | Natural language kubectl commands | Install via pip |
| kagent | Advanced cluster analysis | Install via pip |
| Gordon | Docker AI Agent | Docker Desktop 4.53+ |

## kubectl-ai

### Installation

```bash
pip install kubectl-ai
export OPENAI_API_KEY="sk-your-key"
```

### Use Cases

| Operation | Example Command |
|-----------|-----------------|
| Deploy | `kubectl-ai "deploy todo-app with 2 replicas"` |
| Scale | `kubectl-ai "scale todo-backend to 3 replicas"` |
| Debug | `kubectl-ai "why is todo-backend failing"` |
| Logs | `kubectl-ai "show last 100 lines of backend logs"` |
| Status | `kubectl-ai "show all pods and their status"` |

### Example Workflow

```bash
# Check deployment status
kubectl-ai "show me all pods in default namespace"

# Scale if needed
kubectl-ai "scale todo-backend deployment to handle more load"

# Debug issues
kubectl-ai "check why the backend pods are failing"

# View logs
kubectl-ai "show error logs from todo-backend"
```

## kagent

### Installation

```bash
pip install kagent
export OPENAI_API_KEY="sk-your-key"
```

### Use Cases

| Operation | Example Command |
|-----------|-----------------|
| Health | `kagent "analyze cluster health"` |
| Optimize | `kagent "optimize resource allocation"` |
| Security | `kagent "check security issues"` |
| Troubleshoot | `kagent "why is my app not starting"` |

### Example Workflow

```bash
# Overall health check
kagent "analyze the health of my kubernetes cluster"

# Resource optimization
kagent "identify over-provisioned resources"

# Security audit
kagent "check for security vulnerabilities in deployments"
```

## Docker AI Agent (Gordon)

### Prerequisites

- Docker Desktop 4.53+
- Enable in Settings > Beta features > Docker AI

### Use Cases

| Operation | Example Command |
|-----------|-----------------|
| Capabilities | `docker ai "what can you do"` |
| Build Help | `docker ai "optimize my Dockerfile"` |
| Debug | `docker ai "why is container exiting"` |
| Security | `docker ai "scan image for vulnerabilities"` |

### Example Workflow

```bash
# Get help with Dockerfile
docker ai "create optimized Dockerfile for Python FastAPI app"

# Debug container issues
docker ai "why is my backend container crashing"

# Optimize image
docker ai "how can I reduce image size"
```

## Integration with Phase 4

### Deployment Workflow

1. **Build with Gordon** (if available):
   ```bash
   docker ai "build optimized images for frontend and backend"
   ```

2. **Deploy with kubectl-ai**:
   ```bash
   kubectl-ai "deploy todo-app helm chart"
   ```

3. **Verify with kagent**:
   ```bash
   kagent "check if todo-app is healthy"
   ```

### Troubleshooting Workflow

1. **Identify issues**:
   ```bash
   kagent "why are pods failing"
   ```

2. **Get logs**:
   ```bash
   kubectl-ai "show error logs from last hour"
   ```

3. **Fix and restart**:
   ```bash
   kubectl-ai "restart backend with increased memory"
   ```

## Fallback: Manual Commands

If AI tools are unavailable, use standard kubectl:

```bash
# List pods
kubectl get pods -o wide

# View logs
kubectl logs -f deployment/todo-app-backend

# Scale
kubectl scale deployment todo-app-backend --replicas=3

# Describe
kubectl describe pod <pod-name>

# Port forward
kubectl port-forward svc/todo-app-backend 8000:8000
```

## Acceptance Criteria

- [ ] kubectl-ai installed and configured
- [ ] kagent installed and configured
- [ ] Gordon enabled (if Docker Desktop supports)
- [ ] At least one AI tool used for deployment/debugging
- [ ] Usage documented in PHR or README
- [ ] Fallback manual commands documented
