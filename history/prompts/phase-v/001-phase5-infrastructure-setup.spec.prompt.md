---
id: 001
title: Phase 5 Infrastructure Setup
stage: spec
date: 2026-02-01
surface: agent
model: claude-opus-4-5
feature: phase-v
branch: main
user: hackathon
command: "Phase V init"
labels: ["kafka", "dapr", "kubernetes", "cicd", "event-driven"]
links:
  spec: specs/phase-5/spec.md
  plan: specs/phase-5/plan.md
  tasks: specs/phase-5/tasks.md
files:
  - phase-5/kafka/kafka-cluster.yaml
  - phase-5/kafka/topics.yaml
  - phase-5/dapr-components/pubsub-kafka.yaml
  - phase-5/dapr-components/statestore-postgres.yaml
  - phase-5/dapr-components/secrets-k8s.yaml
  - phase-5/backend/events/__init__.py
  - phase-5/backend/events/publisher.py
  - phase-5/backend/events/schemas.py
  - phase-5/notification-service/main.py
  - phase-5/notification-service/requirements.txt
  - phase-5/notification-service/Dockerfile
  - phase-5/helm/todo-app/Chart.yaml
  - phase-5/helm/todo-app/values.yaml
  - phase-5/helm/todo-app/values-local.yaml
  - phase-5/helm/todo-app/values-cloud.yaml
  - phase-5/helm/todo-app/templates/backend.yaml
  - phase-5/helm/todo-app/templates/notification-service.yaml
  - phase-5/helm/todo-app/templates/frontend.yaml
  - phase-5/helm/todo-app/templates/ingress.yaml
  - phase-5/helm/todo-app/templates/configmap.yaml
  - phase-5/helm/todo-app/templates/secrets.yaml
  - phase-5/helm/todo-app/templates/_helpers.tpl
  - phase-5/scripts/setup-minikube.sh
  - phase-5/scripts/setup-cloud.sh
  - .github/workflows/deploy.yaml
  - phase-5/CLAUDE.md
tests: []
---

## Prompt

Phase V: Advanced Cloud Deployment - Hackathon Todo Evolution. Phases I-IV complete (console -> web -> AI chatbot -> Minikube).

MANDATORY: Spec-Driven ONLY. No manual code.

Objectives:
- Intermediate: Priorities/Tags/Search/Filter/Sort
- Advanced: Recurring/Due/Reminders
- Event-Driven: Kafka + Full Dapr (PubSub/State/Bindings/Secrets)
- Cloud Deploy: DOKS primary (or AKS/GKE/OKE)
- CI/CD GitHub Actions
- Monitoring

START: "As main-agent, load constitution, init phase-v specs using subagents."

## Response

Loaded constitution v1.1.0 and executed Phase V initialization as main agent.

### Completed Tasks (Spec Artifacts)

| Task ID | Description | Status |
|---------|-------------|--------|
| T5-102 | Kafka Cluster YAML (KRaft mode) | ✅ |
| T5-103 | Kafka Topics (task-events, reminders, task-updates) | ✅ |
| T5-202 | Dapr Pub/Sub Component (Kafka) | ✅ |
| T5-203 | Dapr State Store Component (PostgreSQL) | ✅ |
| T5-204 | Dapr Secrets Component (Kubernetes) | ✅ |
| T5-205 | Backend Helm with Dapr Annotations | ✅ |
| T5-301 | Event Publisher Module (Python) | ✅ |
| T5-401 | Notification Service Scaffold | ✅ |
| T5-404 | Notification Service Helm Template | ✅ |
| T5-601 | GitHub Actions CI/CD Workflow | ✅ |

### Key Deliverables

1. **Kafka Infrastructure** (`phase-5/kafka/`)
   - Strimzi KRaft cluster (no Zookeeper)
   - 3 topics with appropriate partitioning

2. **Dapr Components** (`phase-5/dapr-components/`)
   - Kafka pub/sub with subscriptions
   - PostgreSQL state store for Neon
   - Kubernetes secrets integration

3. **Event Publisher** (`phase-5/backend/events/`)
   - Pydantic schemas for TaskEvent, ReminderEvent
   - Async publisher via Dapr HTTP API
   - Graceful fallback when Dapr unavailable

4. **Notification Service** (`phase-5/notification-service/`)
   - FastAPI microservice
   - Dapr subscription endpoint
   - Notification state persistence

5. **Helm Charts** (`phase-5/helm/todo-app/`)
   - Dapr sidecar annotations
   - Multi-environment values files
   - Ingress configuration

6. **CI/CD Pipeline** (`.github/workflows/deploy.yaml`)
   - Docker build & push
   - Helm deployment
   - Health checks

7. **Setup Scripts** (`phase-5/scripts/`)
   - `setup-minikube.sh`: Local development
   - `setup-cloud.sh`: DOKS/AKS/GKE deployment

### Remaining Runtime Tasks

- T5-101: Install Strimzi Operator (requires running Minikube)
- T5-201: Install Dapr on K8s (requires running cluster)
- T5-302: Integrate event publishing in backend CRUD
- T5-700 series: Cloud cluster deployment

### Architecture

```
KUBERNETES CLUSTER
├── Backend (FastAPI + Dapr Sidecar)
│   └── Publishes to kafka-pubsub
├── Notification Service (FastAPI + Dapr Sidecar)
│   └── Subscribes to reminders topic
├── Frontend (Next.js)
├── Kafka (Strimzi KRaft)
│   ├── task-events (3 partitions)
│   ├── reminders (1 partition)
│   └── task-updates (1 partition)
└── Dapr Components
    ├── pubsub.kafka
    ├── state.postgresql
    └── secretstores.kubernetes
```

## Outcome

Phase 5 infrastructure scaffolding complete. All Kubernetes manifests, Helm charts, Dapr components, and CI/CD pipeline created. Ready for runtime deployment on Minikube or cloud Kubernetes.
