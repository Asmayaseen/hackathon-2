# Changelog - Phase IV: Local Kubernetes Deployment

All notable changes to Phase IV of the Evolution Todo project are documented here.

## [1.0.0] - 2026-01-23

### Added
- **Dockerfiles**: Multi-stage production-ready Dockerfiles for both services
  - Backend: Python 3.12 slim with UV package manager, non-root user (UID 10001)
  - Frontend: Node 20 slim with standalone Next.js output, non-root user

- **Docker Compose**: Local development configuration (`docker-compose.yml`)
  - Service networking with `todo-network` bridge
  - Health checks for backend dependency
  - Environment variable injection from `.env` files

- **Helm Charts**: Complete Kubernetes deployment package
  - `Chart.yaml`: Helm chart metadata (v1.0.0)
  - `values.yaml`: Default configuration values
  - `values-local.yaml`: Minikube-specific overrides
  - `values-dev.yaml`: Development environment values
  - `values-prod.yaml`: Production environment values
  - Templates:
    - `backend.yaml`: Backend Deployment + Service
    - `frontend.yaml`: Frontend Deployment + Service
    - `configmap.yaml`: Non-sensitive configuration
    - `secrets.yaml`: Sensitive data (DB URL, JWT, API keys)
    - `ingress.yaml`: Optional ingress configuration
    - `_helpers.tpl`: Template helper functions

- **AIOps Integration**: AI-assisted Kubernetes operations
  - kubectl-ai support for natural language K8s commands
  - kagent support for cluster analysis
  - Gordon (Docker AI) documentation

- **Testing**: Basic test suites for both services
  - Backend: Health check, API endpoint, and auth tests
  - Frontend: Integration and route tests

- **Documentation**:
  - `README.md`: Complete deployment guide
  - `AIOPS_GUIDE.md`: kubectl-ai and kagent usage
  - `CHANGELOG.md`: This file

### Fixed
- **Backend Build Error**: Fixed `OSError: Readme file does not exist`
  - Root cause: `.dockerignore` had `*.md` which excluded `README.md`
  - Fix: Added `!README.md` exception to `.dockerignore`

- **Worker Crash Loop**: Fixed backend pods restarting continuously
  - Root cause: 4 workers overwhelming Minikube resources
  - Fix: Added `WORKERS` to ConfigMap, set to `1` for local deployment

- **Helm readinessProbe**: Changed path from `/health` to `/ready`
  - Properly separates liveness (is it alive?) from readiness (can it serve?)

- **Docker Compose Paths**: Fixed context paths from `../backend` to `./backend`

### Deployment Commands

```bash
# Quick Start
cd phase-4
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 ./frontend
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-local.yaml \
  --set "secrets.databaseUrl=$DATABASE_URL" \
  --set "secrets.jwtSecret=$JWT_SECRET" \
  --set "secrets.groqApiKey=$GROQ_API_KEY"

# Access
kubectl port-forward svc/todo-app-backend 8000:8000 &
kubectl port-forward svc/todo-app-frontend 3000:3000 &
```

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Containerization | Docker | 28.x |
| Orchestration | Kubernetes/Minikube | 1.32.x |
| Package Manager | Helm | 3.x |
| Backend Runtime | Python | 3.12 |
| Backend Framework | FastAPI | 0.128.x |
| Frontend Runtime | Node.js | 20.x |
| Frontend Framework | Next.js | 16.x |
| Database | Neon PostgreSQL | Serverless |
| AI Backend | Groq/OpenAI | Latest |

### Contributors
- Evolution Todo Team
- Claude Code AI Assistant

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-23 | Initial Phase IV release with Kubernetes deployment |
