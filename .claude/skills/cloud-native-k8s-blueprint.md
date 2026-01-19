# Skill: cloud-native-k8s-blueprint

Cloud-Native Kubernetes Deployment Blueprint - production patterns for deploying containerized applications to Kubernetes.

## Overview

Deploy containerized applications to Kubernetes (Minikube, AKS, GKE, DOKS) using Helm charts, with proper configuration management, secrets handling, and monitoring.

```
Source Code → Docker Build → Container Registry → Helm Deploy → Kubernetes Cluster
```

## Quick Start: Local Minikube Deployment

### Prerequisites

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Step 1: Start Minikube Cluster

```bash
# Start cluster with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable ingress addon
minikube addons enable ingress

# Point Docker to Minikube's daemon (important!)
eval $(minikube docker-env)
```

### Step 2: Build Docker Images

```bash
# Build backend image (inside Minikube's Docker)
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Verify images
docker images | grep todo
```

### Step 3: Deploy with Helm

```bash
# Install/upgrade the application
helm upgrade --install todo-app ./helm \
  -f values-local.yaml \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest

# Check deployment status
kubectl get pods -w

# Check services
kubectl get svc
```

### Step 4: Access Application

```bash
# Get Minikube IP
minikube ip

# Port forward to access locally
kubectl port-forward svc/todo-frontend 3000:3000 &
kubectl port-forward svc/todo-backend 8000:8000 &

# Or use Minikube service
minikube service todo-frontend --url
```

## Helm Chart Structure

```
helm/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default values
├── values-local.yaml    # Local/Minikube overrides
├── values-prod.yaml     # Production overrides
└── templates/
    ├── _helpers.tpl     # Template helpers
    ├── backend.yaml     # Backend Deployment + Service
    ├── frontend.yaml    # Frontend Deployment + Service
    ├── configmap.yaml   # Configuration
    ├── secrets.yaml     # Secrets template
    └── ingress.yaml     # Ingress rules (optional)
```

## Backend Deployment Template

```yaml
# templates/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-backend
  labels:
    app: {{ .Release.Name }}-backend
spec:
  replicas: {{ .Values.backend.replicas | default 1 }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-backend
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-backend
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy | default "IfNotPresent" }}
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: database-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: openai-api-key
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: better-auth-secret
          envFrom:
            - configMapRef:
                name: {{ .Release.Name }}-config
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-backend
spec:
  type: {{ .Values.backend.service.type | default "ClusterIP" }}
  ports:
    - port: 8000
      targetPort: 8000
  selector:
    app: {{ .Release.Name }}-backend
```

## Frontend Deployment Template

```yaml
# templates/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-frontend
  labels:
    app: {{ .Release.Name }}-frontend
spec:
  replicas: {{ .Values.frontend.replicas | default 1 }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-frontend
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-frontend
    spec:
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy | default "IfNotPresent" }}
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "{{ .Values.frontend.apiUrl }}"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-frontend
spec:
  type: {{ .Values.frontend.service.type | default "ClusterIP" }}
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: {{ .Release.Name }}-frontend
```

## ConfigMap Template

```yaml
# templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  HOST: "0.0.0.0"
  PORT: "8000"
  ENVIRONMENT: {{ .Values.environment | default "development" }}
  LOG_LEVEL: {{ .Values.logLevel | default "INFO" }}
```

## Secrets Template

```yaml
# templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secrets
type: Opaque
stringData:
  database-url: {{ .Values.secrets.databaseUrl | quote }}
  openai-api-key: {{ .Values.secrets.openaiApiKey | quote }}
  better-auth-secret: {{ .Values.secrets.betterAuthSecret | quote }}
  groq-api-key: {{ .Values.secrets.groqApiKey | default "" | quote }}
```

## Values Files

### values.yaml (Defaults)

```yaml
# Default values for todo-app

backend:
  replicas: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP

frontend:
  replicas: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
  apiUrl: "http://todo-backend:8000"

environment: development
logLevel: INFO

# Secrets - OVERRIDE in values-local.yaml or via --set
secrets:
  databaseUrl: ""
  openaiApiKey: ""
  betterAuthSecret: ""
  groqApiKey: ""
```

### values-local.yaml (Minikube)

```yaml
# Local Minikube values - DO NOT COMMIT WITH REAL SECRETS

backend:
  replicas: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # Use local images
  service:
    type: NodePort

frontend:
  replicas: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never  # Use local images
  service:
    type: NodePort
  apiUrl: "http://todo-backend:8000"

environment: local

# Set these via environment or --set flag
secrets:
  databaseUrl: "${DATABASE_URL}"
  openaiApiKey: "${OPENAI_API_KEY}"
  betterAuthSecret: "${BETTER_AUTH_SECRET}"
```

## kubectl-ai Integration

Use kubectl-ai for AI-assisted Kubernetes operations:

```bash
# Install kubectl-ai
pip install kubectl-ai

# Deploy with natural language
kubectl-ai "deploy the todo app with 2 backend replicas"

# Scale services
kubectl-ai "scale todo-backend to handle more load"

# Debug issues
kubectl-ai "check why the backend pods are failing"

# Get logs
kubectl-ai "show me the last 50 lines of backend logs"

# Resource analysis
kubectl-ai "analyze resource usage of all pods"
```

## kagent Integration

Use kagent for advanced Kubernetes AI operations:

```bash
# Install kagent
pip install kagent

# Cluster health analysis
kagent "analyze the cluster health"

# Resource optimization
kagent "optimize resource allocation for todo-app"

# Security audit
kagent "check security issues in current deployment"

# Troubleshooting
kagent "why is my todo-backend not starting"
```

## Common Operations

### Rolling Update

```bash
# Update backend image
helm upgrade todo-app ./helm \
  --set backend.image.tag=v2.0.0 \
  --reuse-values

# Watch rollout
kubectl rollout status deployment/todo-app-backend
```

### Rollback

```bash
# Rollback to previous version
helm rollback todo-app 1

# Or rollback deployment directly
kubectl rollout undo deployment/todo-app-backend
```

### Scaling

```bash
# Scale via Helm
helm upgrade todo-app ./helm \
  --set backend.replicas=3 \
  --reuse-values

# Or scale directly
kubectl scale deployment/todo-app-backend --replicas=3
```

### Debugging

```bash
# Check pod status
kubectl get pods -l app=todo-app-backend

# View logs
kubectl logs -f deployment/todo-app-backend

# Exec into pod
kubectl exec -it deployment/todo-app-backend -- /bin/bash

# Describe pod for events
kubectl describe pod <pod-name>
```

## Health Checks

Add health endpoint to FastAPI backend:

```python
# main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/ready")
async def readiness_check():
    # Check database connection
    try:
        # Your DB check here
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

## Monitoring Commands

```bash
# Watch all resources
kubectl get all -w

# Resource usage
kubectl top pods
kubectl top nodes

# Events
kubectl get events --sort-by='.lastTimestamp'

# Logs with follow
kubectl logs -f -l app=todo-app-backend --all-containers
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete all resources
kubectl delete all -l app.kubernetes.io/instance=todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Troubleshooting

### ImagePullBackOff
```bash
# Check if using Minikube's Docker daemon
eval $(minikube docker-env)
docker images | grep todo

# Ensure imagePullPolicy: Never for local images
```

### CrashLoopBackOff
```bash
# Check logs
kubectl logs <pod-name> --previous

# Check environment variables
kubectl exec <pod-name> -- env
```

### Pending Pods
```bash
# Check node resources
kubectl describe node

# Check events
kubectl get events
```

## Best Practices

1. **Never commit secrets** - Use values-local.yaml (gitignored) or --set flags
2. **Use resource limits** - Prevent resource starvation
3. **Add health checks** - Enable proper rolling updates
4. **Use labels consistently** - For easy filtering and management
5. **Version your images** - Don't rely on :latest in production
6. **Use ConfigMaps** - For non-sensitive configuration
7. **Enable RBAC** - For security in multi-tenant clusters
