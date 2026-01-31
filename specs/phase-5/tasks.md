# Phase 5: Advanced Cloud Deployment - Tasks

**Version**: 1.0.0
**Created**: 2026-01-31
**Plan Reference**: specs/phase-5/plan.md

## Task Overview

| Group | Tasks | Status |
|-------|-------|--------|
| T5-100: Kafka Setup | 4 tasks | Pending |
| T5-200: Dapr Integration | 5 tasks | Pending |
| T5-300: Event Publishing | 4 tasks | Pending |
| T5-400: Notification Service | 4 tasks | Pending |
| T5-500: Recurring Tasks | 3 tasks | Pending |
| T5-600: CI/CD Pipeline | 4 tasks | Pending |
| T5-700: Cloud Deployment | 5 tasks | Pending |

---

## T5-100: Kafka Setup (Strimzi on Minikube)

### T5-101: Install Strimzi Operator
**Spec**: US-P5-03, AD-01
**Priority**: P1
**Depends**: None

**Description**: Install Strimzi Kafka operator on Minikube

**Steps**:
1. Create kafka namespace
2. Apply Strimzi operator manifests
3. Wait for operator pods to be ready

**Acceptance**:
- [ ] `kubectl get pods -n kafka` shows strimzi-cluster-operator running
- [ ] CRDs for Kafka, KafkaTopic installed

**Commands**:
```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

---

### T5-102: Create Kafka Cluster
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-101

**Description**: Deploy single-node Kafka cluster using Strimzi

**Deliverable**: `phase-5/kafka/kafka-cluster.yaml`

**Acceptance**:
- [ ] Kafka cluster running (1 broker)
- [ ] Kafka accessible at `taskflow-kafka-kafka-bootstrap.kafka:9092`

---

### T5-103: Create Kafka Topics
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-102

**Description**: Create required Kafka topics

**Topics**:
- task-events (3 partitions)
- reminders (1 partition)
- task-updates (1 partition)

**Deliverable**: `phase-5/kafka/topics.yaml`

**Acceptance**:
- [ ] All 3 topics created
- [ ] `kubectl get kafkatopic -n kafka` shows topics

---

### T5-104: Test Kafka Connectivity
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-103

**Description**: Verify Kafka is working with producer/consumer test

**Acceptance**:
- [ ] Can produce message to task-events
- [ ] Can consume message from task-events

---

## T5-200: Dapr Integration

### T5-201: Install Dapr on Minikube
**Spec**: US-P5-05
**Priority**: P1
**Depends**: None [P]

**Description**: Install Dapr runtime on Kubernetes

**Commands**:
```bash
dapr init -k
kubectl get pods -n dapr-system
```

**Acceptance**:
- [ ] dapr-operator, dapr-sidecar-injector, dapr-placement running
- [ ] `dapr status -k` shows healthy

---

### T5-202: Create Dapr Pub/Sub Component
**Spec**: US-P5-05, AD-02
**Priority**: P1
**Depends**: T5-103, T5-201

**Description**: Configure Dapr to use Strimzi Kafka for pub/sub

**Deliverable**: `phase-5/dapr-components/pubsub-kafka.yaml`

**Acceptance**:
- [ ] Component created in default namespace
- [ ] Backend can publish via `http://localhost:3500/v1.0/publish/kafka-pubsub/task-events`

---

### T5-203: Create Dapr State Store Component
**Spec**: US-P5-05
**Priority**: P2
**Depends**: T5-201

**Description**: Configure Dapr state store with PostgreSQL (Neon)

**Deliverable**: `phase-5/dapr-components/statestore-postgres.yaml`

**Acceptance**:
- [ ] Can save state via Dapr API
- [ ] Can retrieve state via Dapr API

---

### T5-204: Create Dapr Secrets Component
**Spec**: US-P5-05
**Priority**: P2
**Depends**: T5-201

**Description**: Configure Dapr to read Kubernetes secrets

**Deliverable**: `phase-5/dapr-components/secrets-k8s.yaml`

**Acceptance**:
- [ ] Can read secrets via Dapr API

---

### T5-205: Enable Dapr Sidecar on Backend
**Spec**: US-P5-05
**Priority**: P1
**Depends**: T5-202

**Description**: Add Dapr annotations to backend deployment

**Changes**: Update `helm/todo-app/templates/backend.yaml`

**Annotations**:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "todo-backend"
dapr.io/app-port: "8000"
```

**Acceptance**:
- [ ] Backend pod has 2 containers (app + daprd sidecar)
- [ ] Sidecar logs show connection to Kafka

---

## T5-300: Event Publishing

### T5-301: Create Event Publisher Module
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-205

**Description**: Create module for publishing events via Dapr

**Deliverables**:
- `phase-5/backend/events/__init__.py`
- `phase-5/backend/events/publisher.py`
- `phase-5/backend/events/schemas.py`

**Acceptance**:
- [ ] `publish_task_event(event_type, task, user_id)` function works
- [ ] Events sent to Dapr sidecar

---

### T5-302: Integrate Event Publishing in Task CRUD
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-301

**Description**: Publish events on create, update, delete, complete

**Changes**: Update task route handlers in `main.py`

**Acceptance**:
- [ ] Creating task publishes "created" event
- [ ] Updating task publishes "updated" event
- [ ] Deleting task publishes "deleted" event
- [ ] Completing task publishes "completed" event

---

### T5-303: Create Dapr Subscription Config
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-302

**Description**: Configure Dapr subscriptions for consuming events

**Deliverable**: `phase-5/dapr-components/subscriptions.yaml`

**Acceptance**:
- [ ] Subscription routes events to correct endpoints

---

### T5-304: Implement Event Subscription Endpoint
**Spec**: US-P5-03
**Priority**: P1
**Depends**: T5-303

**Description**: Create endpoint for Dapr to deliver events

**Endpoint**: `POST /api/events/task-events`

**Acceptance**:
- [ ] Endpoint receives events from Dapr
- [ ] Events logged for verification

---

## T5-400: Notification Service

### T5-401: Create Notification Service Scaffold
**Spec**: US-P5-06, AD-03
**Priority**: P2
**Depends**: T5-200 [P]

**Description**: Create new FastAPI microservice for notifications

**Deliverables**:
- `phase-5/notification-service/main.py`
- `phase-5/notification-service/requirements.txt`
- `phase-5/notification-service/Dockerfile`

**Acceptance**:
- [ ] Service starts and has /health endpoint
- [ ] Dockerfile builds successfully

---

### T5-402: Implement Reminder Subscription
**Spec**: US-P5-06
**Priority**: P2
**Depends**: T5-401, T5-202

**Description**: Subscribe to reminders topic via Dapr

**Acceptance**:
- [ ] Service receives reminder events
- [ ] Logs reminder details

---

### T5-403: Store Notification State
**Spec**: US-P5-06
**Priority**: P2
**Depends**: T5-402

**Description**: Track notification delivery status

**Acceptance**:
- [ ] Notification records created in database
- [ ] Status updated after "delivery" (mock)

---

### T5-404: Add Notification Service to Helm Chart
**Spec**: US-P5-06
**Priority**: P2
**Depends**: T5-401

**Description**: Create Helm templates for notification service

**Deliverable**: `helm/todo-app/templates/notification-deployment.yaml`

**Acceptance**:
- [ ] Service deploys with Dapr sidecar
- [ ] Service accessible within cluster

---

## T5-500: Recurring Tasks

### T5-501: Implement Recurring Task Logic
**Spec**: US-P5-01
**Priority**: P1
**Depends**: T5-302

**Description**: Auto-create next occurrence when recurring task completed

**Changes**: Update `main.py` complete_task endpoint

**Acceptance**:
- [ ] Completing daily task creates next day's task
- [ ] Completing weekly task creates next week's task
- [ ] Original task marked complete

---

### T5-502: Handle Cancel Recurrence
**Spec**: US-P5-01
**Priority**: P1
**Depends**: T5-501

**Description**: Allow user to cancel future occurrences

**Endpoint**: `POST /api/{user_id}/tasks/{task_id}/recurrence/cancel`

**Acceptance**:
- [ ] Canceling recurrence clears pattern
- [ ] No new occurrences created after cancel

---

### T5-503: Display Recurrence in UI
**Spec**: US-P5-01
**Priority**: P2
**Depends**: T5-501

**Description**: Show recurrence info on task cards

**Acceptance**:
- [ ] Recurrence badge/icon visible
- [ ] Recurrence pattern displayed

---

## T5-600: CI/CD Pipeline

### T5-601: Create GitHub Actions Workflow
**Spec**: US-P5-07
**Priority**: P2
**Depends**: T5-400, T5-500

**Description**: Automated build and deploy pipeline

**Deliverable**: `.github/workflows/deploy.yaml`

**Acceptance**:
- [ ] Workflow triggers on push to main
- [ ] Builds all Docker images

---

### T5-602: Configure Container Registry
**Spec**: US-P5-07
**Priority**: P2
**Depends**: T5-601

**Description**: Push images to Docker Hub or cloud registry

**Acceptance**:
- [ ] Images pushed with version tags
- [ ] Images accessible from cloud cluster

---

### T5-603: Add Kubernetes Deployment Step
**Spec**: US-P5-07
**Priority**: P2
**Depends**: T5-602

**Description**: Deploy to cluster via Helm in CI/CD

**Acceptance**:
- [ ] Helm upgrade runs successfully
- [ ] New version deployed

---

### T5-604: Add Health Check Step
**Spec**: US-P5-07
**Priority**: P2
**Depends**: T5-603

**Description**: Verify deployment health post-deploy

**Acceptance**:
- [ ] Pipeline waits for pods ready
- [ ] Fails if health check fails

---

## T5-700: Cloud Deployment

### T5-701: Create Cloud Kubernetes Cluster
**Spec**: US-P5-08
**Priority**: P2
**Depends**: T5-600

**Description**: Set up DOKS/AKS/GKE cluster

**Acceptance**:
- [ ] Cluster running with 2+ nodes
- [ ] kubectl configured to access cluster

---

### T5-702: Install Dapr on Cloud Cluster
**Spec**: US-P5-08
**Priority**: P2
**Depends**: T5-701

**Description**: Install Dapr runtime on cloud K8s

**Acceptance**:
- [ ] Dapr components healthy
- [ ] Sidecar injection working

---

### T5-703: Deploy Kafka to Cloud
**Spec**: US-P5-08
**Priority**: P2
**Depends**: T5-702

**Description**: Deploy Strimzi Kafka or connect to Redpanda Cloud

**Acceptance**:
- [ ] Kafka accessible from pods
- [ ] Topics created

---

### T5-704: Deploy Application to Cloud
**Spec**: US-P5-08
**Priority**: P2
**Depends**: T5-703

**Description**: Deploy full stack via Helm

**Acceptance**:
- [ ] All pods running with sidecars
- [ ] Services accessible

---

### T5-705: Configure Ingress and TLS
**Spec**: US-P5-08
**Priority**: P2
**Depends**: T5-704

**Description**: Set up external access with HTTPS

**Acceptance**:
- [ ] Application accessible via public URL
- [ ] HTTPS working (or HTTP for hackathon)

---

## Task Execution Order

**Phase 1 (Parallel Setup)**:
- T5-101 → T5-102 → T5-103 → T5-104 (Kafka)
- T5-201 (Dapr) [P]

**Phase 2 (Integration)**:
- T5-202 → T5-205 → T5-301 → T5-302 → T5-303 → T5-304

**Phase 3 (Services)**:
- T5-401 → T5-402 → T5-403 → T5-404 (Notification)
- T5-501 → T5-502 → T5-503 (Recurring)

**Phase 4 (CI/CD)**:
- T5-601 → T5-602 → T5-603 → T5-604

**Phase 5 (Cloud)**:
- T5-701 → T5-702 → T5-703 → T5-704 → T5-705
