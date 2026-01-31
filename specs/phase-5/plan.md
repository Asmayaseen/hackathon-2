# Phase 5: Advanced Cloud Deployment - Implementation Plan

**Version**: 1.0.0
**Created**: 2026-01-31
**Spec Reference**: specs/phase-5/spec.md

## Constitution Check

- [x] Spec-Driven Development followed (Specify → Plan → Tasks → Implement)
- [x] Phased Evolution: Building on Phase 4 Kubernetes deployment
- [x] Technology Stack: Kafka (Strimzi), Dapr, GitHub Actions, Cloud K8s
- [x] Stateless Architecture: All state in Neon DB via Dapr
- [x] Documentation: All decisions documented here

## Implementation Phases

### Phase 5A: Advanced Features + Kafka (Local)

1. **Extend Database Schema**
   - Add `recurrence_pattern` to tasks table (already exists)
   - Add `reminder_offset` field
   - Add `notifications` table for delivery tracking

2. **Backend Enhancements**
   - Recurring Task Engine: Auto-create next occurrence on completion
   - Reminder Scheduling: Create Dapr jobs for reminders
   - Event Publishing: Publish all task events to Kafka via Dapr

3. **Deploy Kafka on Minikube**
   - Install Strimzi operator
   - Create Kafka cluster (single replica for dev)
   - Create topics: task-events, reminders, task-updates

### Phase 5B: Dapr Integration (Local)

1. **Install Dapr on Minikube**
   - `dapr init -k`
   - Verify dapr-system namespace

2. **Create Dapr Components**
   - pubsub.kafka: Connect to Strimzi Kafka
   - state.postgresql: Connect to Neon DB
   - secretstores.kubernetes: For API keys

3. **Enable Dapr Sidecars**
   - Add annotations to deployments
   - Configure app-port for sidecar communication

4. **Refactor Backend for Dapr**
   - Replace direct Kafka calls with Dapr Pub/Sub HTTP API
   - Implement subscription endpoints for consuming events

### Phase 5C: Microservices

1. **Notification Service**
   - New FastAPI microservice
   - Subscribes to `reminders` topic
   - Stores notification status
   - Dockerfile + Helm chart

2. **Recurring Task Service** (Optional - can be in main backend)
   - Subscribes to `task-events`
   - On task completion with recurrence, creates next task
   - Publishes new task event

### Phase 5D: CI/CD Pipeline

1. **GitHub Actions Workflow**
   - Trigger: Push to main branch
   - Build: Docker images for frontend, backend, notification service
   - Push: To Docker Hub or cloud registry
   - Deploy: Helm upgrade to cloud cluster

2. **Workflow Steps**
   ```yaml
   - checkout
   - setup docker buildx
   - login to registry
   - build and push images
   - setup kubectl
   - helm upgrade --install
   - health check
   ```

### Phase 5E: Cloud Deployment

1. **Choose Cloud Provider**
   - DigitalOcean DOKS (recommended: $200 free credit)
   - Or Azure AKS / Google GKE

2. **Cluster Setup**
   - Create K8s cluster (2-3 nodes)
   - Install Dapr on cluster
   - Deploy Kafka (Strimzi or connect to Redpanda Cloud)

3. **Deploy Application**
   - Use Phase 4 Helm charts as base
   - Add Dapr annotations
   - Configure Ingress with TLS

4. **Configure External Access**
   - Domain setup (optional)
   - LoadBalancer or NodePort services

## Architecture Decisions

### AD-01: Kafka Deployment Strategy

**Decision**: Use Strimzi operator for self-hosted Kafka in Kubernetes

**Rationale**:
- Free (no cloud costs for Kafka)
- Learning experience with K8s operators
- Dapr abstracts client complexity
- Can swap to Redpanda Cloud later via Dapr component config

**Alternatives Considered**:
- Redpanda Cloud: Easier but external dependency
- Confluent Cloud: Expensive after free credits

### AD-02: Dapr Pub/Sub vs Direct Kafka Client

**Decision**: Use Dapr Pub/Sub HTTP API

**Rationale**:
- Decouples code from Kafka specifics
- Can swap backend (Redis, RabbitMQ) without code changes
- Simpler code (HTTP calls vs kafka-python)
- Dapr handles retries, dead-letter queues

### AD-03: Notification Service Scope

**Decision**: Implement as separate microservice with mock delivery

**Rationale**:
- Demonstrates microservice architecture
- Real email/SMS out of scope for hackathon
- Service stores notification state for demo

### AD-04: Cloud Provider

**Decision**: DigitalOcean DOKS (primary), with docs for AKS/GKE

**Rationale**:
- $200 free credit for 60 days
- Simple UI and CLI
- Good docs for beginners
- DOKS manages control plane

## Component Architecture

```
phase-5/
├── backend/                 # Enhanced Phase 4 backend
│   ├── events/             # Event publishing module
│   │   ├── __init__.py
│   │   ├── publisher.py    # Dapr pub/sub publisher
│   │   └── schemas.py      # Event schemas
│   ├── services/
│   │   ├── recurring.py    # Recurring task logic
│   │   └── reminders.py    # Reminder scheduling
│   └── subscriptions/      # Dapr subscription endpoints
│       └── handlers.py
├── notification-service/    # New microservice
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── dapr-components/         # Dapr YAML configs
│   ├── pubsub-kafka.yaml
│   ├── statestore-postgres.yaml
│   └── secrets-k8s.yaml
├── kafka/                   # Strimzi manifests
│   ├── kafka-cluster.yaml
│   └── topics.yaml
├── helm/                    # Enhanced Helm charts
│   └── todo-app/
│       ├── templates/
│       │   ├── notification-deployment.yaml
│       │   └── dapr-subscriptions.yaml
│       └── values-cloud.yaml
├── .github/
│   └── workflows/
│       └── deploy.yaml      # CI/CD pipeline
└── scripts/
    ├── setup-minikube.sh
    └── setup-cloud.sh
```

## API Changes

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/dapr/subscribe | Dapr subscription configuration |
| POST | /api/events/task-events | Dapr calls this on new events |
| POST | /api/events/reminders | Dapr calls this for reminders |
| GET | /api/{user_id}/notifications | Get user notifications |

### Event Publishing (via Dapr)

```python
# Instead of kafka-python:
async def publish_task_event(event_type: str, task: Task, user_id: str):
    await httpx.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json={
            "event_type": event_type,
            "task_id": task.id,
            "task_data": task.dict(),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Dependencies

### Backend (additions to pyproject.toml)
```toml
httpx = "^0.27.0"      # For Dapr HTTP calls
aiokafka = "^0.10.0"   # Optional: direct Kafka (backup)
```

### Notification Service
```
fastapi
uvicorn
httpx
sqlmodel
```

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Strimzi complexity | Use minimal config, single replica |
| Dapr learning curve | Follow official tutorials, simple components |
| Cloud costs | Use free tiers, cleanup after demo |
| CI/CD failures | Test locally first, add retry logic |

## Timeline Estimate

| Task | Complexity |
|------|------------|
| Kafka setup (Strimzi) | Medium |
| Dapr integration | Medium |
| Event publishing | Low |
| Notification Service | Medium |
| CI/CD pipeline | Medium |
| Cloud deployment | Medium |
| Testing & polish | Low |

## Success Validation

1. `kubectl get pods` shows all pods running with Dapr sidecars
2. Create task → event visible in Kafka topic
3. Task with reminder → notification delivered
4. Complete recurring task → next occurrence created
5. Push to GitHub → CI/CD deploys to cloud
6. Public URL accessible and functional
