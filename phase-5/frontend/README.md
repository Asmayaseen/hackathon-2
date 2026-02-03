# Phase 5 Frontend

Phase 5 reuses the **Phase 4 frontend** with no modifications.

## Location
The frontend code is located at: `phase-4/frontend/`

## Why?
Phase 5 focuses on backend infrastructure changes:
- Kafka event streaming (Strimzi)
- Dapr pub/sub integration
- Notification microservice
- Cloud Kubernetes deployment

The frontend UI remains unchanged - it already supports all task CRUD operations, chat, and notifications.

## Building
```bash
# Build from phase-4/frontend
docker build -t todo-frontend:latest ./phase-4/frontend/
```
