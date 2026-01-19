# Infrastructure Specification: Helm Charts

**Phase**: 4 - Local Kubernetes Deployment
**Created**: 2026-01-18
**Status**: Complete

## Overview

Helm chart specifications for deploying Todo application to Kubernetes.

## Chart Structure

```
helm/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration values
├── values-local.yaml    # Minikube-specific overrides
└── templates/
    ├── _helpers.tpl     # Template helper functions
    ├── backend.yaml     # Backend Deployment + Service
    ├── frontend.yaml    # Frontend Deployment + Service
    ├── configmap.yaml   # Non-sensitive configuration
    ├── secrets.yaml     # Sensitive configuration
    └── ingress.yaml     # Ingress rules (optional)
```

## Chart.yaml

| Field | Value |
|-------|-------|
| apiVersion | v2 |
| name | todo-app |
| description | Helm chart for Evolution Todo App |
| type | application |
| version | 0.1.0 |
| appVersion | 1.0.0 |

## Values Structure

### Backend Configuration

```yaml
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # For Minikube local images
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Frontend Configuration

```yaml
frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never
  service:
    type: NodePort
    port: 3000
    nodePort: 30000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

### Secrets Configuration

```yaml
secrets:
  DATABASE_URL: ""        # Neon PostgreSQL URL
  BETTER_AUTH_SECRET: ""  # JWT signing secret
  OPENAI_API_KEY: ""      # OpenAI API key
  GROQ_API_KEY: ""        # Groq API key (optional)
```

## Template Specifications

### Backend Deployment

- **Type**: Deployment
- **Replicas**: Configurable (default: 1)
- **Container Port**: 8000
- **Health Checks**:
  - Liveness: GET /health (30s initial, 10s period)
  - Readiness: GET /health (5s initial, 5s period)
- **Environment**: From ConfigMap + Secrets

### Frontend Deployment

- **Type**: Deployment
- **Replicas**: Configurable (default: 1)
- **Container Port**: 3000
- **Service Type**: NodePort (for Minikube access)

### ConfigMap

Contains non-sensitive environment variables:
- ENVIRONMENT
- LOG_LEVEL
- HOST
- PORT

### Secrets

Contains sensitive credentials:
- DATABASE_URL
- BETTER_AUTH_SECRET
- OPENAI_API_KEY
- GROQ_API_KEY

### Ingress (Optional)

- **Host**: todo.local
- **Paths**:
  - /api → backend:8000
  - / → frontend:3000

## Helm Commands

### Install

```bash
helm upgrade --install todo-app ./helm -f values-local.yaml
```

### Verify

```bash
helm list
kubectl get all
```

### Uninstall

```bash
helm uninstall todo-app
```

## Acceptance Criteria

- [ ] `helm lint` passes without errors
- [ ] `helm template` generates valid Kubernetes manifests
- [ ] Chart installs successfully on Minikube
- [ ] All pods reach Running state within 2 minutes
- [ ] Services are accessible via NodePort or port-forward
- [ ] Secrets are properly mounted as environment variables
- [ ] Health probes correctly detect service status
