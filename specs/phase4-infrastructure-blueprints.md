# Phase IV Infrastructure Blueprints

**Created**: 2026-02-17
**Status**: Complete
**Methodology**: Spec-Driven Infrastructure Blueprint Model

## Overview

This document defines the infrastructure blueprints that govern how specs translate to deployable infrastructure. Each blueprint maps directly to Helm chart templates and Kubernetes resources. Phase IV deploys FastAPI backend + Next.js frontend to Minikube using Docker and Helm, with AI tools (Gordon, kubectl-ai, kagent) assisting operations.

---

## 1. Cluster Blueprint

**Purpose**: Define the Kubernetes cluster configuration.

**Spec Source**: `specs/phase-4/infrastructure/minikube.md`

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Driver | Docker | Best WSL2 compatibility |
| CPUs | 4 | Sufficient for 2 services + system |
| Memory | 8192 MB | Headroom for builds + pods |
| Kubernetes Version | v1.28+ | Stable release with HPA v2 |
| Addons | ingress, metrics-server | Traffic routing + monitoring |
| Registry | Local / minikube:5000 | Private image registry in cluster |

**Helm Mapping**: N/A (cluster-level, managed by Minikube)

**Verification Checklist**:
- [ ] `minikube status` shows Running for host, kubelet, apiserver
- [ ] `kubectl get nodes` returns Ready state
- [ ] `kubectl get addons` shows ingress and metrics-server enabled
- [ ] `docker run` accesses Minikube daemon

---

## 2. Service Blueprint

**Purpose**: Define each deployable service's configuration.

**Spec Source**: `specs/phase-4/infrastructure/docker.md`, `specs/phase-4/infrastructure/helm-charts.md`

### Backend Service (FastAPI)

| Parameter | Value | Helm Path |
|-----------|-------|-----------|
| Image | todo-backend:latest | backend.image.repository + tag |
| Port | 8000 | backend.service.port |
| Replicas | 1 (dev) / 2 (prod) | backend.replicas |
| CPU Request | 250m | backend.resources.requests.cpu |
| Memory Request | 256Mi | backend.resources.requests.memory |
| CPU Limit | 500m | backend.resources.limits.cpu |
| Memory Limit | 512Mi | backend.resources.limits.memory |
| Liveness Probe | GET /health, period 30s, 3 failures | backend.probes.liveness |
| Readiness Probe | GET /ready, period 10s, 3 failures | backend.probes.readiness |
| Startup Probe | GET /health, 5s period, 30 failures | backend.probes.startup |
| Pull Policy | Never (local) / Always (cloud) | backend.image.pullPolicy |
| Environment | Via ConfigMap | backend.env |
| Secrets | Via Secret mount | backend.secretMount |

### Frontend Service (Next.js)

| Parameter | Value | Helm Path |
|-----------|-------|-----------|
| Image | todo-frontend:latest | frontend.image.repository + tag |
| Port | 3000 | frontend.service.port |
| Replicas | 1 (dev) / 2 (prod) | frontend.replicas |
| CPU Request | 200m | frontend.resources.requests.cpu |
| Memory Request | 256Mi | frontend.resources.requests.memory |
| CPU Limit | 400m | frontend.resources.limits.cpu |
| Memory Limit | 512Mi | frontend.resources.limits.memory |
| Liveness Probe | GET /, period 30s, 3 failures | frontend.probes.liveness |
| Readiness Probe | GET /, period 10s, 3 failures | frontend.probes.readiness |
| API Backend | http://backend:8000 | frontend.env.BACKEND_URL |

**Helm Mapping**: `templates/backend.yaml`, `templates/frontend.yaml`

**Verification Checklist**:
- [ ] `kubectl get pods -n todo-app` shows Running status
- [ ] `kubectl get svc -n todo-app` lists ClusterIP services
- [ ] `kubectl logs deployment/todo-backend` shows successful startup
- [ ] Backend health check: `kubectl exec pod/todo-backend -- curl localhost:8000/health`
- [ ] Frontend responds: `kubectl port-forward svc/todo-frontend 3000:3000`

---

## 3. Scaling Blueprint

**Purpose**: Define auto-scaling behavior for production readiness.

**Spec Source**: `specs/phase-4/spec.md` (User Story 3: Horizontal Pod Autoscaling)

| Parameter | Backend | Frontend |
|-----------|---------|----------|
| Min Replicas | 1 | 1 |
| Max Replicas | 5 | 3 |
| CPU Target | 70% | 80% |
| Memory Target | 80% | N/A |
| Scale Up Cooldown | 60s | 60s |
| Scale Down Cooldown | 300s | 300s |
| Behavior | Conservative | Conservative |

**HPA Configuration**: Generated via `kubectl-ai apply-hpa`, stored in Helm values.yaml

**Scaling Triggers**:
1. Backend CPU > 70% → Add replica (max 1/min)
2. Backend Mem > 80% → Alert ops team (no auto-scale)
3. Frontend CPU > 80% → Add replica (max 1/min)

**Rollback**: `kubectl rollout undo deployment/todo-backend -n todo-app`

**Verification Checklist**:
- [ ] `kubectl get hpa -n todo-app` lists Backend and Frontend HPAs
- [ ] `kubectl-ai "check scaling status"` returns healthy metrics
- [ ] Load test: `kubectl run -it --image=busybox load -- wget -q -O- http://backend:8000/health` (repeat)
- [ ] Scale-up observed within 60s
- [ ] Scale-down after 5min idle

---

## 4. Resilience Blueprint

**Purpose**: Define failure recovery and self-healing behavior.

**Spec Source**: `specs/phase-4/checklists/deployment.md`

| Mechanism | Configuration | Purpose |
|-----------|--------------|---------|
| Restart Policy | Always | Auto-restart crashed pods |
| Liveness Probe | /health, 30s interval, 3 retries | Detect and restart hung processes |
| Readiness Probe | /ready, 10s interval, 3 retries | Gate inbound traffic to ready pods |
| Startup Probe | /health, 5s period, 30 failures | Allow slow startup (150s window) |
| PDB | minAvailable: 1 | Prevent total outage during updates |
| Rolling Update | maxSurge: 1, maxUnavailable: 0 | Zero-downtime deploys |
| Node Affinity | None (dev) / Spread (prod) | Avoid single-node failure |

**Failure Scenarios and Recovery**:

| Scenario | Detection | Recovery | Time |
|----------|-----------|----------|------|
| Pod crash | kubelet → restart | Auto-restart via restart policy | < 30s |
| Health check fail | Liveness probe | Pod killed, replaced by ReplicaSet | < 2min |
| OOM kill | Memory limit exceeded | Pod evicted, new pod scheduled | < 1min |
| Node failure | Node NotReady | Pod rescheduled to healthy node | < 2min |
| Image pull failure | ErrImagePull | Retain pod, alert ops (local: Never, cloud: Always) | N/A |
| Config error | Readiness probe fail | Traffic rerouted, pod unhealthy until fixed | N/A |

**AI-Assisted Diagnostics**:
- `kubectl-ai "why is pod failing"` → diagnose CrashLoopBackOff with logs
- `kagent "analyze cluster health"` → comprehensive health report with recommendations
- `Gordon "debug container crash"` → container-level diagnostics, strace capture

**Verification Checklist**:
- [ ] Force-kill backend pod: `kubectl delete pod -n todo-app -l app=todo-backend`
- [ ] Observe auto-restart within 30s
- [ ] Verify traffic flows to new pod immediately
- [ ] Disable health check, verify pod marked unready and traffic rerouted
- [ ] Re-enable and observe recovery

---

## Blueprint-to-Helm Mapping

| Blueprint | Helm Template | Values Key | Scope |
|-----------|--------------|------------|-------|
| Cluster | N/A | N/A | Minikube (out-of-scope) |
| Backend Service | templates/backend.yaml | backend.* | Deployment, Service, Probes |
| Frontend Service | templates/frontend.yaml | frontend.* | Deployment, Service, Probes |
| Backend Scaling | templates/hpa-backend.yaml | backend.autoscaling.* | HPA resource |
| Frontend Scaling | templates/hpa-frontend.yaml | frontend.autoscaling.* | HPA resource |
| Resilience | templates/pdb-backend.yaml | backend.pdb.* | PodDisruptionBudget |
| Config | templates/configmap.yaml | config.* | ConfigMap with env vars |
| Secrets | templates/secrets.yaml | secrets.* | Secret mount paths |
| Ingress | templates/ingress.yaml | ingress.* | Nginx ingress routes |

---

## Spec-Driven Development Governance

This blueprint model ensures:

1. **Every infrastructure decision traces to a spec**
   - No ad-hoc cluster configuration
   - All parameters documented in `specs/phase-4/*` before implementation

2. **Helm values are the single source of truth**
   - Specs define WHAT (requirements)
   - Helm implements HOW (Kubernetes resources)
   - `values.yaml` is version-controlled

3. **AI tools validate against specs**
   - `kubectl-ai` verifies compliance with blueprint targets
   - `kagent` audits cluster state against declared values
   - `Gordon` debugs deviations from spec

4. **Changes require spec updates first**
   - Spec → Plan → Tasks → Implementation cycle
   - No direct kubectl apply without spec justification

5. **Blueprints are version-controlled**
   - Git tracks all infrastructure evolution
   - Rollback = `git revert` + redeploy

---

## References

- **Phase IV Spec**: `specs/phase-4/spec.md`
- **Helm Charts**: `specs/phase-4/infrastructure/helm-charts.md`
- **Minikube Config**: `specs/phase-4/infrastructure/minikube.md`
- **Docker Builds**: `specs/phase-4/infrastructure/docker.md`
- **AI Cluster Ops**: `specs/ai-cluster-ops-spec.md`
- **Deployment Checklist**: `specs/phase-4/checklists/deployment.md`

**Last Updated**: 2026-02-17
**Next Review**: After Phase IV MVP deployment
