# Phase V: Event-Driven Integration Specification

**Version**: 1.0.0
**Created**: 2026-02-01
**Status**: Implementation

## Overview

Integrate Phase 5 event-driven infrastructure with Phase 4 backend. Enable Kafka event publishing for all task CRUD operations via Dapr Pub/Sub.

## User Stories

### US-INT-01: Event Publishing on Task Create (P1)
**As a** system
**I want** task creation to publish a "created" event to Kafka
**So that** downstream services can react to new tasks

**Acceptance Criteria:**
- [ ] Creating task via API publishes to `task-events` topic
- [ ] Creating task via MCP tool publishes to `task-events` topic
- [ ] Event contains: event_type, task_id, task_data, user_id, timestamp
- [ ] Publishing failure does not block task creation

### US-INT-02: Event Publishing on Task Complete (P1)
**As a** system
**I want** task completion to publish a "completed" event
**So that** recurring task logic can create next occurrence

**Acceptance Criteria:**
- [ ] Completing task publishes to `task-events` topic
- [ ] If task is recurring, next occurrence is auto-created
- [ ] New occurrence is published as separate "created" event

### US-INT-03: Event Publishing on Task Update/Delete (P1)
**As a** system
**I want** all task modifications to publish events
**So that** audit logging and sync services can track changes

**Acceptance Criteria:**
- [ ] Update publishes "updated" event
- [ ] Delete publishes "deleted" event
- [ ] Events include old/new values for auditing

### US-INT-04: Reminder Event Publishing (P2)
**As a** system
**I want** reminder scheduling to publish to reminders topic
**So that** Notification Service can deliver notifications

**Acceptance Criteria:**
- [ ] Task with reminder_offset triggers reminder event
- [ ] Reminder event published at remind_at time
- [ ] Notification Service receives and processes reminder

### US-INT-05: Dapr Subscription Endpoints (P1)
**As a** backend service
**I want** endpoints for Dapr to deliver subscribed events
**So that** I can react to events from other services

**Acceptance Criteria:**
- [ ] POST /api/events/task-events receives Dapr events
- [ ] POST /api/events/reminders receives Dapr events
- [ ] GET /dapr/subscribe returns subscription config

## Technical Implementation

### Event Publishing Integration

```python
# In routes/tasks.py - after create_task
from events import publish_task_event, EventType

# After session.commit()
await publish_task_event(EventType.CREATED, new_task, user_id)
```

### MCP Tool Integration

```python
# In mcp_server.py - after task creation
from events import publish_task_event, EventType

# After session.commit()
import asyncio
asyncio.create_task(publish_task_event(EventType.CREATED, task, user_id))
```

### Recurring Task Auto-Creation

```python
# In complete_task endpoint
if task.is_recurring and task.recurrence_pattern:
    next_task = create_next_occurrence(task)
    session.add(next_task)
    session.commit()
    await publish_task_event(EventType.CREATED, next_task, user_id)
```

## API Changes

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /dapr/subscribe | Dapr subscription configuration |
| POST | /api/events/task-events | Receive task events from Dapr |
| POST | /api/events/reminders | Receive reminder events from Dapr |

### Dapr Subscription Response

```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/api/events/task-events"
  }
]
```

## Dependencies

- Phase 5 events module: `phase-5/backend/events/`
- httpx for Dapr HTTP calls
- Dapr sidecar running (graceful fallback if not)

## Testing

### Local Test (Minikube)

1. Start Minikube with Strimzi + Dapr
2. Deploy backend with Dapr sidecar
3. Create task via API or chat
4. Verify event in Kafka:
   ```bash
   kubectl exec -n kafka taskflow-kafka-kafka-0 -- bin/kafka-console-consumer.sh \
     --bootstrap-server localhost:9092 --topic task-events --from-beginning
   ```

### NL Demo Script

```
User: "Add high priority weekly meeting for Monday 10 AM"
→ Task created with recurrence_pattern="weekly"
→ Event published to task-events
→ Kafka logs show: {"event_type":"created","task_id":1,...}

User: "Complete the meeting task"
→ Task marked complete
→ Event published: {"event_type":"completed",...}
→ Next occurrence auto-created
→ Event published: {"event_type":"created","task_id":2,...}
```

## Success Criteria

1. All CRUD operations publish events
2. Recurring tasks auto-create on completion
3. Events visible in Kafka consumer
4. Notification Service receives reminder events
5. Publishing failure does not break main flow
