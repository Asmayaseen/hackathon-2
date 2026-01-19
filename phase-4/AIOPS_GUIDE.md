# AIOps Guide - kubectl-ai & kagent

AI-assisted Kubernetes operations for Phase 4 deployment.

## Overview

AIOps tools enable natural language interaction with Kubernetes clusters:

| Tool | Purpose | Best For |
|------|---------|----------|
| **kubectl-ai** | Natural language kubectl commands | Day-to-day operations, quick tasks |
| **kagent** | Advanced cluster analysis | Health checks, optimization, security |
| **Gordon** | Docker AI Agent | Container building, debugging |

## kubectl-ai Setup

### Installation

```bash
# Install via pip
pip install kubectl-ai

# Or via homebrew (macOS)
brew install kubectl-ai

# Set OpenAI API key
export OPENAI_API_KEY="sk-your-key"

# Verify installation
kubectl-ai --help
```

### Configuration

```bash
# Create config file
cat > ~/.kubectl-ai.yaml << EOF
model: gpt-4
temperature: 0.1
require_confirmation: true
EOF
```

### Usage Examples

#### Deployment Operations

```bash
# Deploy the application
kubectl-ai "deploy todo-app with 2 replicas using helm chart in ./helm"

# Scale deployment
kubectl-ai "scale todo-backend to 3 replicas"

# Rolling update
kubectl-ai "update todo-backend image to version 2.0"

# Rollback
kubectl-ai "rollback todo-backend to previous version"
```

#### Monitoring & Debugging

```bash
# Check pod status
kubectl-ai "show me all pods and their status"

# View logs
kubectl-ai "show last 100 lines of todo-backend logs"

# Resource usage
kubectl-ai "what's the CPU and memory usage of all pods"

# Debug failing pod
kubectl-ai "why is todo-backend pod failing"
```

#### Service Operations

```bash
# List services
kubectl-ai "show all services with their endpoints"

# Expose service
kubectl-ai "expose todo-backend as NodePort on port 30080"

# Port forward
kubectl-ai "forward local port 8080 to todo-backend service"
```

#### Configuration

```bash
# View secrets
kubectl-ai "list all secrets in default namespace"

# Update configmap
kubectl-ai "add LOG_LEVEL=DEBUG to todo-app-config configmap"

# Apply changes
kubectl-ai "restart todo-backend deployment to pick up new config"
```

## kagent Setup

### Installation

```bash
# Install kagent
pip install kagent

# Or from source
git clone https://github.com/kagent-dev/kagent
cd kagent && pip install -e .

# Configure API key
export OPENAI_API_KEY="sk-your-key"
```

### Usage Examples

#### Cluster Analysis

```bash
# Overall health check
kagent "analyze the health of my kubernetes cluster"

# Resource analysis
kagent "show resource utilization across all nodes"

# Identify issues
kagent "find any problems in the cluster"
```

#### Optimization

```bash
# Resource optimization
kagent "optimize resource allocation for todo-app"

# Cost analysis
kagent "identify over-provisioned resources"

# Scaling recommendations
kagent "should I scale up todo-backend based on current metrics"
```

#### Security

```bash
# Security audit
kagent "check for security issues in current deployment"

# RBAC analysis
kagent "review RBAC permissions for todo-app"

# Network policies
kagent "suggest network policies for todo-app"
```

#### Troubleshooting

```bash
# Diagnose issues
kagent "why is my todo-backend not starting"

# Memory analysis
kagent "is there a memory leak in todo-backend"

# Network issues
kagent "check connectivity between frontend and backend"
```

## Docker AI Agent (Gordon)

### Setup

```bash
# Requires Docker Desktop 4.53+
# Enable in Docker Desktop: Settings > Beta features > Docker AI

# Verify
docker ai "what can you do"
```

### Usage Examples

```bash
# Build assistance
docker ai "build an optimized Dockerfile for my Python FastAPI app"

# Debug container
docker ai "why is my container exiting immediately"

# Optimize image
docker ai "how can I reduce the size of my frontend image"

# Security scan
docker ai "check my backend image for vulnerabilities"

# Compose help
docker ai "create docker-compose for local development"
```

## Combined Workflow

### Day 1: Initial Deployment

```bash
# 1. Build with Gordon
docker ai "build optimized images for frontend and backend"

# 2. Deploy with kubectl-ai
kubectl-ai "deploy todo-app helm chart with 1 replica each"

# 3. Verify with kagent
kagent "check if todo-app deployment is healthy"
```

### Day 2: Scaling

```bash
# 1. Analyze load
kagent "analyze current load on todo-backend"

# 2. Scale appropriately
kubectl-ai "scale todo-backend based on kagent recommendations"

# 3. Verify
kubectl-ai "show me the new pod distribution"
```

### Day 3: Troubleshooting

```bash
# 1. Identify issue
kagent "why are response times increasing"

# 2. Get specific logs
kubectl-ai "show error logs from todo-backend in last hour"

# 3. Fix and restart
kubectl-ai "restart todo-backend with increased memory limit"
```

## Best Practices

### 1. Always Confirm Destructive Operations

```bash
# Enable confirmation mode
kubectl-ai --require-confirmation "delete all pods"
```

### 2. Use Specific Contexts

```bash
# Specify namespace
kubectl-ai "in namespace production, scale backend to 5"

# Specify cluster
kubectl-ai "on minikube cluster, check pod status"
```

### 3. Chain Operations Safely

```bash
# First preview
kubectl-ai "show me what would happen if I delete all evicted pods"

# Then execute
kubectl-ai "delete all evicted pods --confirm"
```

### 4. Log Important Operations

```bash
# Keep audit trail
kubectl-ai "scale backend to 5" | tee -a ops.log
```

## Comparison: When to Use What

| Scenario | Tool | Example |
|----------|------|---------|
| Quick status check | kubectl-ai | "show pod status" |
| Complex debugging | kagent | "why is latency high" |
| Build optimization | Gordon | "optimize Dockerfile" |
| Security audit | kagent | "check security issues" |
| Rolling updates | kubectl-ai | "update image tag" |
| Cost optimization | kagent | "identify waste" |

## Fallback: Manual kubectl

If AI tools are unavailable:

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

## Troubleshooting AI Tools

### API Key Issues

```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test API
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Rate Limits

```bash
# Reduce requests
export KUBECTL_AI_CACHE=true

# Use smaller model
kubectl-ai --model gpt-3.5-turbo "list pods"
```

### Connection Issues

```bash
# Check kubectl config
kubectl config current-context

# Verify cluster access
kubectl cluster-info

# Test without AI
kubectl get nodes
```
