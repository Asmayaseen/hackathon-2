# Tasks: Phase 4 Local Kubernetes Deployment

**Feature Branch**: `phase-4`
**Created**: 2026-01-16
**Updated**: 2026-01-18
**Status**: Complete
**Input**: Design documents from `/mnt/d/hackathon-2/specs/phase-4/`
**Prerequisites**: plan.md, spec.md

## Task Legend

- `[x]` = Complete
- `[ ]` = Pending
- `[P]` = Production critical
- `[US#]` = User Story reference

---

## Phase 1: Docker Containerization (User Story 1 - P1)

### T001: Create Backend Dockerfile ✅
**Status**: Complete
**File**: `phase-4/backend/Dockerfile`
**Spec Reference**: `infrastructure/docker.md`

- [x] Multi-stage build with Python 3.12-slim
- [x] Non-root user for security
- [x] Health check command included
- [x] Optimized layer caching

**Test**: `docker build -t todo-backend:latest ./phase-4/backend`

---

### T002: Create Frontend Dockerfile ✅
**Status**: Complete
**File**: `phase-4/frontend/Dockerfile`
**Spec Reference**: `infrastructure/docker.md`

- [x] Multi-stage build (deps → builder → runner)
- [x] Next.js standalone output
- [x] Non-root user for security
- [x] Environment variable support

**Test**: `docker build -t todo-frontend:latest ./phase-4/frontend`

---

### T003: Create .dockerignore Files ✅
**Status**: Complete
**Files**: `phase-4/backend/.dockerignore`, `phase-4/frontend/.dockerignore`

- [x] Exclude node_modules, __pycache__, .git
- [x] Exclude .env files (secrets)
- [x] Exclude test files and docs

---

### T004: Build and Verify Backend Image
**Status**: Ready for Testing
**Command**:
```bash
cd phase-4/backend
docker build -t todo-backend:latest .
docker run -d -p 8000:8000 --env-file .env todo-backend:latest
curl http://localhost:8000/health
```

**Expected**: `{"status": "healthy", "service": "evolution-todo-api", "version": "1.0.0"}`

---

### T005: Build and Verify Frontend Image
**Status**: Ready for Testing
**Command**:
```bash
cd phase-4/frontend
docker build -t todo-frontend:latest .
docker run -d -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 todo-frontend:latest
curl http://localhost:3000
```

**Expected**: HTML response with Next.js app

---

## Phase 2: Helm Chart Development (User Story 2 - P2)

### T006: Initialize Helm Chart Structure ✅
**Status**: Complete
**Directory**: `phase-4/helm/`
**Spec Reference**: `infrastructure/helm-charts.md`

- [x] Chart.yaml with metadata
- [x] values.yaml with defaults
- [x] templates/ directory structure
- [x] _helpers.tpl for reusable functions

---

### T007: Create values.yaml ✅
**Status**: Complete
**File**: `phase-4/helm/values.yaml`

- [x] Backend image configuration
- [x] Frontend image configuration
- [x] Resource limits (CPU/memory)
- [x] Ingress configuration
- [x] Secrets reference

---

### T008: Create Kubernetes Secret Template ✅
**Status**: Complete
**File**: `phase-4/helm/templates/secrets.yaml`

- [x] DATABASE_URL secret
- [x] BETTER_AUTH_SECRET
- [x] OPENAI_API_KEY
- [x] GROQ_API_KEY
- [x] Base64 encoding

---

### T009: Create ConfigMap Template ✅
**Status**: Complete
**File**: `phase-4/helm/templates/configmap.yaml`

- [x] Non-sensitive configuration
- [x] Environment-specific settings
- [x] API URLs

---

### T010: Create Backend Deployment & Service ✅
**Status**: Complete
**File**: `phase-4/helm/templates/backend.yaml`
**Spec Reference**: `infrastructure/helm-charts.md`

- [x] Deployment with replicas
- [x] Container spec with resources
- [x] Liveness probe (/health)
- [x] Readiness probe (/ready)
- [x] Service (ClusterIP)
- [x] Secret and ConfigMap mounts

---

### T011: Create Frontend Deployment & Service ✅
**Status**: Complete
**File**: `phase-4/helm/templates/frontend.yaml`

- [x] Deployment with replicas
- [x] Container spec with resources
- [x] Service (ClusterIP or NodePort)
- [x] ConfigMap mounts

---

### T012: Create Ingress Template ✅
**Status**: Complete
**File**: `phase-4/helm/templates/ingress.yaml`

- [x] Ingress resource (optional)
- [x] TLS configuration support
- [x] Path-based routing

---

### T013: Verify Helm Chart
**Status**: Ready for Testing
**Command**:
```bash
cd phase-4/helm
helm lint .
helm template todo-app . --debug
```

**Expected**: No errors or warnings from lint

---

## Phase 3: Minikube Deployment (User Story 3 - P3)

### T014: Create Local Values File ✅
**Status**: Complete
**File**: `phase-4/helm/values-local.yaml`

- [x] Local registry settings
- [x] NodePort for local access
- [x] Resource limits for Minikube

---

### T015: Create Deployment Script ✅
**Status**: Complete
**File**: `phase-4/deploy.sh`

- [x] Minikube start command
- [x] Docker image build
- [x] Helm install command
- [x] Port-forward setup
- [x] Status verification

---

### T016: Create Deployment Documentation ✅
**Status**: Complete
**File**: `phase-4/MINIKUBE_DEPLOYMENT.md`

- [x] Prerequisites list
- [x] Step-by-step instructions
- [x] Troubleshooting guide
- [x] Verification commands

---

### T017: Deploy to Minikube
**Status**: Ready for Testing
**Commands**:
```bash
# Start Minikube
minikube start --cpus 4 --memory 8192

# Set docker env
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:latest ./phase-4/backend
docker build -t todo-frontend:latest ./phase-4/frontend

# Install Helm release
helm install todo-app ./phase-4/helm -f ./phase-4/helm/values-local.yaml

# Verify
kubectl get pods
kubectl get services
```

---

### T018: Verify Application
**Status**: Pending (requires running cluster)
**Commands**:
```bash
# Port forward
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## Phase 4: AIOps Documentation (User Story 4 - P4)

### T019: Create AIOps Guide ✅
**Status**: Complete
**File**: `phase-4/AIOPS_GUIDE.md`
**Spec Reference**: `infrastructure/aiops.md`

- [x] kubectl-ai installation
- [x] kagent installation
- [x] Gordon (Docker AI) usage
- [x] Example commands
- [x] Troubleshooting

---

### T020: Create Cloud-Native Skill ✅
**Status**: Complete
**File**: `.claude/skills/cloud-native-k8s-blueprint.md`

- [x] Minikube patterns
- [x] Helm deployment patterns
- [x] AIOps integration
- [x] Troubleshooting patterns

---

### T021: Add Health Endpoints to Backend ✅
**Status**: Complete
**Files**:
- `phase-3/backend/main.py`
- `phase-4/backend/main.py`
**Spec Reference**: `api/health-endpoints.md`

- [x] GET /health (liveness)
- [x] GET /ready (readiness with DB check)

---

### T022: Update Skills Index ✅
**Status**: Complete
**File**: `.claude/skills/SKILLS-INDEX.md`

- [x] Added cloud-native-k8s-blueprint
- [x] Added ChatKit skills

---

## Summary

| Phase | Tasks | Complete | Pending |
|-------|-------|----------|---------|
| 1. Docker | 5 | 3 | 2 (testing) |
| 2. Helm | 8 | 7 | 1 (testing) |
| 3. Minikube | 5 | 3 | 2 (deployment) |
| 4. AIOps | 4 | 4 | 0 |
| **Total** | **22** | **17** | **5** |

**Note**: Pending tasks require a running Minikube cluster for verification.

---

## Files Created/Modified

### New Files
- `specs/phase-4/api/health-endpoints.md`
- `specs/phase-4/infrastructure/docker.md`
- `specs/phase-4/infrastructure/helm-charts.md`
- `specs/phase-4/infrastructure/minikube.md`
- `specs/phase-4/infrastructure/aiops.md`
- `phase-4/MINIKUBE_DEPLOYMENT.md`
- `phase-4/AIOPS_GUIDE.md`
- `phase-4/deploy.sh`
- `phase-4/helm/templates/_helpers.tpl`
- `phase-4/helm/templates/ingress.yaml`
- `.claude/skills/cloud-native-k8s-blueprint.md`

### Modified Files
- `specs/phase-4/spec.md` - Updated with related specs
- `specs/phase-4/plan.md` - Updated with implementation details
- `specs/phase-4/tasks.md` - This file
- `phase-4/helm/values.yaml` - Added ingress config
- `phase-4/helm/templates/backend.yaml` - Added health probes
- `phase-3/backend/main.py` - Added health endpoints
- `phase-4/backend/main.py` - Added health endpoints
- `.claude/skills/SKILLS-INDEX.md` - Added new skills
