# Claude Code Rules - Phase 5 (Advanced Cloud Deployment)

This file provides runtime guidance for Phase 5 development tasks.

## Implementation Status

| Component | Status | Files |
|-----------|--------|-------|
| Kafka Cluster | ✅ Complete | `kafka/kafka-cluster.yaml` |
| Kafka Topics | ✅ Complete | `kafka/topics.yaml` |
| Dapr Components | ✅ Complete | `dapr-components/*.yaml` |
| Event Publisher | ✅ Complete | `backend/events/*.py` |
| Notification Service | ✅ Complete | `notification-service/*` |
| Helm Charts (Dapr) | ✅ Complete | `helm/todo-app/*` |
| CI/CD Pipeline | ✅ Complete | `.github/workflows/deploy.yaml` |
| Setup Scripts | ✅ Complete | `scripts/*.sh` |

## Project Context

Phase 5 transforms the Todo Chatbot into an event-driven, cloud-native distributed system using:
- **Kafka** (Strimzi) for event streaming
- **Dapr** for distributed application runtime
- **GitHub Actions** for CI/CD
- **Cloud Kubernetes** (DOKS/AKS/GKE) for production deployment

## Directory Structure

```
phase-5/
├── backend/
│   └── events/              # Event publishing module
│       ├── __init__.py
│       ├── publisher.py     # Dapr pub/sub publisher
│       └── schemas.py       # Event schemas
├── notification-service/    # New microservice
│   ├── main.py             # FastAPI service
│   ├── requirements.txt
│   └── Dockerfile
├── dapr-components/         # Dapr YAML configs
│   ├── pubsub-kafka.yaml   # Kafka pub/sub component
│   ├── statestore-postgres.yaml
│   └── secrets-k8s.yaml
├── kafka/                   # Strimzi manifests
│   ├── kafka-cluster.yaml  # KRaft mode cluster
│   └── topics.yaml         # Topic definitions
├── helm/
│   └── todo-app/           # Enhanced Helm charts
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml
│       ├── values-cloud.yaml
│       └── templates/
│           ├── backend.yaml (with Dapr)
│           ├── notification-service.yaml
│           └── ...
├── scripts/
│   ├── setup-minikube.sh   # Local setup
│   └── setup-cloud.sh      # Cloud setup
└── CLAUDE.md               # This file
```

## Quick Start

### Local Development (Minikube)

```bash
# 1. Start Minikube
minikube start --memory=8192 --cpus=4

# 2. Run setup script (installs Strimzi, Dapr, builds images)
./phase-5/scripts/setup-minikube.sh

# 3. Configure secrets
cp phase-5/helm/todo-app/values-local.yaml my-values.yaml
# Edit my-values.yaml with your DATABASE_URL, JWT_SECRET, etc.

# 4. Deploy
helm install todo-app ./phase-5/helm/todo-app -f my-values.yaml

# 5. Access
minikube service todo-app-frontend
```

### Cloud Deployment (DOKS/AKS/GKE)

```bash
# 1. Run cloud setup script
./phase-5/scripts/setup-cloud.sh

# 2. Configure for cloud
# Edit values-cloud.yaml with your domain and secrets

# 3. Deploy
helm install todo-app ./phase-5/helm/todo-app -f values-cloud.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET"
```

## Key Technologies

### Kafka (Strimzi)
- Operator-based Kafka on Kubernetes
- KRaft mode (no Zookeeper)
- Topics: `task-events`, `reminders`, `task-updates`
- Bootstrap: `taskflow-kafka-kafka-bootstrap.kafka:9092`

### Dapr Building Blocks
- **Pub/Sub**: Event streaming via Kafka
- **State Store**: PostgreSQL for conversation state
- **Secrets**: Kubernetes secrets integration

### Event Publishing Pattern
```python
from phase-5.backend.events import publish_task_event, EventType

# In task route handler
await publish_task_event(
    event_type=EventType.CREATED,
    task=task,
    user_id=user_id
)
```

## Spec References

- Feature Spec: `specs/phase-5/spec.md`
- Implementation Plan: `specs/phase-5/plan.md`
- Task Breakdown: `specs/phase-5/tasks.md`
- Constitution: `.specify/memory/constitution.md`

## Task Status

### T5-100: Kafka Setup
- [x] T5-102: Kafka cluster YAML
- [x] T5-103: Topics YAML
- [ ] T5-101: Install Strimzi (runtime)
- [ ] T5-104: Test connectivity (runtime)

### T5-200: Dapr Integration
- [x] T5-202: Pub/Sub component
- [x] T5-203: State store component
- [x] T5-204: Secrets component
- [x] T5-205: Backend Dapr annotations

### T5-300: Event Publishing
- [x] T5-301: Event publisher module
- [x] T5-302: Integrate in task CRUD ✅ DONE
- [x] T5-303: Dapr subscriptions
- [x] T5-304: Subscription endpoints ✅ DONE

### T5-400: Notification Service
- [x] T5-401: Service scaffold
- [x] T5-404: Helm template

### T5-500: Recurring Tasks
- [x] T5-501: Auto-create next occurrence ✅ DONE
- [x] T5-502: Integrated in MCP + API ✅ DONE

### T5-600: CI/CD
- [x] T5-601: GitHub Actions workflow

### T5-700: Cloud Deployment
- [ ] T5-701-705: Cloud cluster setup (runtime)

## Integration Complete

### Files Modified in Phase 4 Backend:
- `phase-4/backend/events/` - Event publisher module (copied)
- `phase-4/backend/routes/tasks.py` - CRUD event publishing + recurring logic
- `phase-4/backend/routes/events.py` - Dapr subscription endpoints (NEW)
- `phase-4/backend/mcp_server.py` - MCP tool event publishing + recurring
- `phase-4/backend/main.py` - Events router included

### Event Flow:
```
Task Create/Update/Delete/Complete
        ↓
publish_task_event() [fire and forget]
        ↓
Dapr Sidecar HTTP API
        ↓
Kafka (task-events topic)
        ↓
Notification Service / Audit Service
```

### Recurring Task Flow:
```
Complete Recurring Task
        ↓
Mark task.completed = True
        ↓
create_next_occurrence()
        ↓
New Task (next due date)
        ↓
Publish CREATED event
```

## Next Steps (Runtime)

1. **Start Minikube** and run setup script:
   ```bash
   minikube start --cpus=4 --memory=8g
   ./phase-5/scripts/setup-minikube.sh
   ```

2. **Configure secrets** in `values-local.yaml`

3. **Deploy with Helm**:
   ```bash
   helm install todo-app ./phase-5/helm/todo-app -f values-local.yaml
   ```

4. **Test event flow**:
   ```bash
   # Watch Kafka events
   kubectl exec -n kafka taskflow-kafka-kafka-0 -- \
     bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
     --topic task-events --from-beginning
   ```

5. **Test NL recurring task**:
   ```
   "Add weekly team meeting for Monday 10 AM"
   "Complete the team meeting task"
   → Verify next occurrence auto-created
   ```

