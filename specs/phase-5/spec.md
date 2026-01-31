# Phase 5: Advanced Cloud Deployment Specification

**Version**: 1.0.0
**Created**: 2026-01-31
**Status**: Draft

## Overview

Transform the Phase 4 Todo Chatbot into an event-driven, cloud-native distributed system using Kafka for messaging and Dapr for distributed application runtime. Deploy to production-grade Kubernetes on cloud providers.

## Objectives

1. Implement Advanced Level features (Recurring Tasks, Due Dates & Reminders)
2. Add event-driven architecture with Kafka
3. Integrate Dapr for distributed application runtime
4. Deploy to Minikube locally with full Dapr stack
5. Deploy to cloud Kubernetes (DigitalOcean DOKS/Azure AKS/Google GKE)
6. Set up CI/CD pipeline with GitHub Actions
7. Configure monitoring and logging

## User Stories

### US-P5-01: Recurring Tasks (P1)
**As a** user
**I want** to create recurring tasks
**So that** repetitive tasks are automatically scheduled

**Acceptance Criteria:**
- [ ] User can set recurrence pattern (daily, weekly, monthly, custom)
- [ ] When recurring task is completed, next occurrence is auto-created
- [ ] User can cancel all future occurrences
- [ ] Recurrence info displayed on task card

**Test Scenario:**
```gherkin
Given I create a task "Team standup" with recurrence "daily"
When I mark the task as complete
Then a new task "Team standup" is created for the next day
And the completed task is marked as done
```

### US-P5-02: Due Date Reminders (P1)
**As a** user
**I want** to receive reminders before task deadlines
**So that** I don't miss important tasks

**Acceptance Criteria:**
- [ ] User can set reminder offset (15min, 1hr, 1day before)
- [ ] Reminders are delivered via notification service
- [ ] User can view pending reminders
- [ ] Reminders work even after server restart (persisted)

**Test Scenario:**
```gherkin
Given I create a task "Submit report" due at 5:00 PM with 1hr reminder
When the time reaches 4:00 PM
Then I receive a reminder notification
```

### US-P5-03: Event-Driven Task Operations (P1)
**As a** system
**I want** all task operations published to Kafka
**So that** services can react to changes asynchronously

**Acceptance Criteria:**
- [ ] Task create/update/delete/complete events published to `task-events` topic
- [ ] Events include: event_type, task_id, task_data, user_id, timestamp
- [ ] Recurring Task Service consumes events to spawn next occurrences
- [ ] Audit Service consumes events for activity logging

**Test Scenario:**
```gherkin
Given a Kafka consumer subscribed to "task-events"
When I create a task "Buy groceries"
Then an event with type "created" is published
And the event contains the full task data
```

### US-P5-04: Reminder Scheduling via Dapr (P1)
**As a** system
**I want** reminders scheduled via Dapr Jobs API
**So that** notifications fire at exact times without polling

**Acceptance Criteria:**
- [ ] When task with reminder is created, Dapr job is scheduled
- [ ] Job fires at remind_at time and publishes to `reminders` topic
- [ ] Notification Service consumes and delivers reminder
- [ ] Jobs survive pod restarts

**Test Scenario:**
```gherkin
Given I create a task with reminder at 3:00 PM
When the time reaches 3:00 PM
Then Dapr triggers the job callback
And a reminder event is published
```

### US-P5-05: Dapr Pub/Sub Integration (P1)
**As a** developer
**I want** to use Dapr Pub/Sub instead of direct Kafka client
**So that** code is decoupled from messaging infrastructure

**Acceptance Criteria:**
- [ ] Backend publishes events via Dapr HTTP API
- [ ] Dapr component configured for Kafka/Strimzi
- [ ] Services subscribe via Dapr subscription model
- [ ] Can swap Kafka for Redis without code changes

### US-P5-06: Notification Service (P2)
**As a** microservice
**I want** a dedicated Notification Service
**So that** reminder delivery is decoupled from main app

**Acceptance Criteria:**
- [ ] Separate container/deployment for Notification Service
- [ ] Subscribes to `reminders` topic via Dapr
- [ ] Stores notification state in database
- [ ] Marks notifications as sent

### US-P5-07: CI/CD Pipeline (P2)
**As a** developer
**I want** automated build and deployment via GitHub Actions
**So that** changes are deployed automatically

**Acceptance Criteria:**
- [ ] On push to main: build Docker images
- [ ] Push images to container registry
- [ ] Deploy to Kubernetes via Helm
- [ ] Run health checks post-deployment

### US-P5-08: Cloud Kubernetes Deployment (P2)
**As an** operator
**I want** the app deployed to cloud Kubernetes
**So that** it's accessible publicly with high availability

**Acceptance Criteria:**
- [ ] Deploy to DigitalOcean DOKS (or Azure AKS/Google GKE)
- [ ] Dapr installed on cloud cluster
- [ ] Kafka accessible (Strimzi in-cluster or Redpanda Cloud)
- [ ] Ingress configured for external access
- [ ] TLS/HTTPS enabled

### US-P5-09: Monitoring & Logging (P3)
**As an** operator
**I want** centralized logging and metrics
**So that** I can monitor system health

**Acceptance Criteria:**
- [ ] Structured JSON logging from all services
- [ ] Logs aggregated (stdout for K8s)
- [ ] Health endpoints for all services
- [ ] Dapr observability enabled

## Technical Requirements

### Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Backend API | Recurring Service, Audit | All CRUD operations |
| `reminders` | Dapr Jobs/Backend | Notification Service | Scheduled reminders |
| `task-updates` | Backend API | WebSocket Service (future) | Real-time sync |

### Dapr Components

| Component | Type | Purpose |
|-----------|------|---------|
| `kafka-pubsub` | pubsub.kafka | Event streaming |
| `statestore` | state.postgresql | Conversation/task state |
| `kubernetes-secrets` | secretstores.kubernetes | API keys, credentials |

### Event Schemas

**Task Event:**
```json
{
  "event_type": "created|updated|completed|deleted",
  "task_id": 123,
  "task_data": { "title": "...", "completed": false, ... },
  "user_id": "user-uuid",
  "timestamp": "2026-01-31T12:00:00Z"
}
```

**Reminder Event:**
```json
{
  "task_id": 123,
  "title": "Task title",
  "due_at": "2026-01-31T17:00:00Z",
  "remind_at": "2026-01-31T16:00:00Z",
  "user_id": "user-uuid"
}
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (Cloud)                         │
│                                                                       │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                 │
│  │  Frontend   │   │   Backend   │   │ Notification│                 │
│  │  + Dapr     │──▶│  + Dapr     │   │  Service    │                 │
│  │  Sidecar    │   │  Sidecar    │   │  + Dapr     │                 │
│  └─────────────┘   └──────┬──────┘   └──────┬──────┘                 │
│                           │                  │                        │
│                    ┌──────▼──────────────────▼──────┐                 │
│                    │         DAPR COMPONENTS        │                 │
│                    │  ┌────────────────────────┐    │                 │
│                    │  │   pubsub.kafka         │────┼──▶ Kafka/Strimzi│
│                    │  │   state.postgresql     │────┼──▶ Neon DB      │
│                    │  │   secretstores.k8s     │    │                 │
│                    │  └────────────────────────┘    │                 │
│                    └────────────────────────────────┘                 │
│                                                                       │
│  ┌─────────────┐   ┌─────────────┐                                   │
│  │  Recurring  │   │   Audit     │                                   │
│  │  Task Svc   │   │   Service   │                                   │
│  │  + Dapr     │   │  + Dapr     │                                   │
│  └─────────────┘   └─────────────┘                                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Deployment Environments

| Environment | Platform | Kafka | Purpose |
|-------------|----------|-------|---------|
| Local | Minikube | Strimzi (in-cluster) | Development |
| Cloud | DOKS/AKS/GKE | Redpanda Cloud or Strimzi | Production |

## Out of Scope

- WebSocket real-time sync (future enhancement)
- Email/SMS notification delivery (mock for hackathon)
- Multi-region deployment
- Advanced auto-scaling

## Success Criteria

1. All advanced features working (recurring, reminders)
2. Kafka events flowing between services
3. Dapr sidecars injected and functioning
4. CI/CD pipeline deploying to cloud
5. Application accessible via public URL
6. Demo video showing end-to-end flow

## References

- hackathon.md: Phase V requirements
- constitution.md: Project principles
- Phase 4 Helm charts: Base for Phase 5
