# Implementation Plan: Phase 4 Local Kubernetes Deployment

**Branch**: `phase-4` | **Date**: 2026-01-16 | **Spec**: `/mnt/d/hackathon-2/specs/phase-4/spec.md`
**Input**: Phase 4 Spec

## Summary

Containerize the existing Phase 3 Chatbot application (Next.js Frontend, FastAPI Backend) and deploy it to a local Kubernetes cluster (Minikube) using Helm charts. This enables a cloud-native development workflow and prepares for cloud deployment in Phase 5.

## Technical Context

**Language/Version**: Python 3.12+ (Backend), Node.js 20+ (Frontend)
**Primary Dependencies**: Docker, Kubernetes (Minikube), Helm
**Storage**: Neon Serverless PostgreSQL (External), Kubernetes Secrets for credentials
**Testing**: Manual verification via `kubectl` and browser; Spec-driven acceptance tests.
**Target Platform**: Minikube (Linux/WSL2/macOS)
**Project Type**: Full-stack Web Application (Containerized)
**Performance Goals**: Pod startup < 30s, stable connectivity between frontend/backend.
**Constraints**: Local resource usage (Minikube), External DB connectivity.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec-Driven**: Spec created and reviewed.
- [x] **Phased Evolution**: Building on Phase 3.
- [x] **Tech Stack**: Using Docker, Minikube, Helm, kubectl-ai as required.
- [x] **Independent Stories**: User stories are split by concern (Docker, Helm, K8s).
- [x] **Stateless**: Backend and Frontend are stateless containers.
- [x] **Cloud-Native**: Docker and Kubernetes adoption.

## Project Structure

### Documentation (this feature)

```text
specs/phase-4/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
phase-4/
├── backend/            # FastAPI Source
│   ├── Dockerfile      # Backend Container Config
│   └── ...
├── frontend/           # Next.js Source
│   ├── Dockerfile      # Frontend Container Config
│   └── ...
├── helm/               # Helm Charts
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── backend-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── ingress.yaml
│       └── ...
└── CLAUDE.md           # Phase 4 Runtime instructions
```

## Architecture

1.  **Containerization**:
    *   **Frontend**: Multi-stage Docker build for Next.js.
    *   **Backend**: Python slim image, install dependencies (uv), expose port 8000.
2.  **Orchestration (Kubernetes)**:
    *   **Deployments**: Manage pods for frontend and backend.
    *   **Services**: `ClusterIP` for backend (internal), `NodePort` or `LoadBalancer` (via Minikube tunnel) for frontend.
    *   **Config/Secrets**: `ConfigMap` for non-sensitive env vars, `Secret` for API keys and DB URL.
3.  **Deployment (Helm)**:
    *   Single Chart or Umrella Chart strategy to deploy both components together or independently. We will use a single chart with sub-components or simple templates for simplicity in this phase.
