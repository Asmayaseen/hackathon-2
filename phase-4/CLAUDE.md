# Claude Code Rules - Phase 4 (Local Kubernetes)

This file provides runtime guidance for Phase 4 deployment tasks.

## Project Context
Phase 4 focuses on containerizing the Phase 3 Todo Chatbot and deploying it to a local Minikube Kubernetes cluster using Helm.

## Navigation
- Specs: `specs/phase-4/`
- Backend: `phase-4/backend/`
- Frontend: `phase-4/frontend/`
- Helm Charts: `phase-4/helm/`

## Workflow Standards
1. **Containerization**: Use multi-stage builds. Minimize image size.
2. **Kubernetes**: Use Helm for templating. Avoid hardcoded values in manifests.
3. **Secrets**: NEVER commit secrets. Use `secrets.yaml` templates and local value overrides or environment variables.
4. **Verification**: Always verify deployments with `kubectl get pods`, `kubectl logs`, and application access checks.

## Commands
- **Docker Build**: `docker build -t todo-backend ./backend`
- **Helm Install**: `helm install todo-app ./helm -f values-local.yaml`
- **Minikube**: `minikube start`, `eval $(minikube docker-env)`

## Spec References
- Feature Spec: `@specs/phase-4/spec.md`
- Plan: `@specs/phase-4/plan.md`
- Tasks: `@specs/phase-4/tasks.md`
