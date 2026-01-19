# API Specification: Health Endpoints

**Phase**: 4 - Local Kubernetes Deployment
**Created**: 2026-01-18
**Status**: Complete

## Overview

Health check endpoints required for Kubernetes liveness and readiness probes.

## Endpoints

### GET /health

Liveness probe endpoint - confirms the service is running.

**Request**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "evolution-todo-api",
  "version": "1.0.0"
}
```

**Use Case**: Kubernetes liveness probe to detect if container needs restart.

---

### GET /ready

Readiness probe endpoint - confirms the service can handle traffic.

**Request**: None

**Response** (200 OK):
```json
{
  "status": "ready",
  "database": "connected"
}
```

**Response** (503 Service Unavailable):
```json
{
  "detail": "Database not ready: [error message]"
}
```

**Use Case**: Kubernetes readiness probe to determine if pod should receive traffic.

## Kubernetes Integration

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Acceptance Criteria

- [ ] `/health` returns 200 when service is running
- [ ] `/ready` returns 200 when database is connected
- [ ] `/ready` returns 503 when database is unavailable
- [ ] Both endpoints respond within 1 second
