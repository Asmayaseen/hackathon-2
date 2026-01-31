# Claude Code Rules - Phase 5 (Advanced Cloud Deployment)

This file provides runtime guidance for Phase 5 development tasks.

## Project Context

Phase 5 transforms the Todo Chatbot into an event-driven, cloud-native distributed system using:
- **Kafka** (Strimzi) for event streaming
- **Dapr** for distributed application runtime
- **GitHub Actions** for CI/CD
- **Cloud Kubernetes** (DOKS/AKS/GKE) for production deployment

## Spec-Driven Development

All implementation MUST follow:
1. Read spec: `@specs/phase-5/spec.md`
2. Follow plan: `@specs/phase-5/plan.md`
3. Execute tasks: `@specs/phase-5/tasks.md`
4. Reference Task IDs in all code

## Directory Structure

```
phase-5/
├── backend/                 # Enhanced backend with events
│   └── events/             # Event publishing module
├── notification-service/    # New microservice
├── dapr-components/         # Dapr YAML configs
├── kafka/                   # Strimzi manifests
├── helm/                    # Enhanced Helm charts
├── .github/workflows/       # CI/CD pipeline
└── scripts/                 # Setup scripts
```

## Key Technologies

### Kafka (Strimzi)
- Operator-based Kafka on Kubernetes
- Topics: task-events, reminders, task-updates
- Access: `taskflow-kafka-kafka-bootstrap.kafka:9092`

### Dapr
- Sidecar pattern for distributed capabilities
- Pub/Sub via HTTP API (no Kafka client needed)
- State management, secrets, service invocation

### Dapr Pub/Sub Pattern
```python
# Publishing events
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event_data
)
```

## Commands

```bash
# Kafka setup
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Dapr setup
dapr init -k
dapr status -k

# Apply Dapr components
kubectl apply -f phase-5/dapr-components/

# Deploy with Helm
helm upgrade --install todo-app ./phase-5/helm/todo-app -f values-local.yaml
```

## Spec References

- Feature Spec: `@specs/phase-5/spec.md`
- Plan: `@specs/phase-5/plan.md`
- Tasks: `@specs/phase-5/tasks.md`
- Constitution: `@.specify/memory/constitution.md`

## Task Execution

Start with T5-100 series (Kafka Setup), then T5-200 (Dapr Integration).
Mark tasks complete in tasks.md as you progress.
