# ADR-003: Dapr Over Direct Kafka Client for Event-Driven Architecture

**Status**: Accepted
**Date**: 2026-01-18
**Decision Makers**: asmayaseen
**Context**: Phase V event-driven architecture

## Context

Phase V requires an event-driven architecture where task mutations publish events consumed by downstream services (notifications, recurring tasks, audit). The choice is between using Kafka client libraries directly or abstracting through Dapr.

## Decision

Use **Dapr** as the distributed application runtime with 5 building blocks: Pub/Sub (Kafka), State Store (PostgreSQL), Bindings (Cron), Secrets (K8s), and Service Invocation.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **Dapr (chosen)** | Vendor-agnostic, simple HTTP API, YAML config for backends, built-in retries | Sidecar overhead, learning curve, alpha features |
| Direct kafka-python | Full control, no abstraction overhead | Vendor lock-in, connection management, manual retries |
| CloudEvents + HTTP | Simple, no sidecar | No built-in retry, no state management, no service discovery |

## Rationale

- Dapr is specified in the hackathon requirements
- Pub/Sub abstraction means Kafka can be swapped for RabbitMQ or Redis with YAML change only
- Cron bindings replace custom scheduler code for reminders and recurring tasks
- Kubernetes-native: Dapr sidecar injected via annotations
- Non-blocking event publishing (fire-and-forget) keeps CRUD response times low

## Consequences

- **Positive**: Clean separation of concerns, infrastructure-agnostic, 5 building blocks in one runtime
- **Negative**: Dapr sidecar adds memory/CPU overhead per pod, requires `dapr init -k`
- **Mitigated by**: Lightweight sidecar (~50MB), acceptable for K8s clusters with 4+ CPUs

## Related

- `specs/features/phase-v-integration.md`
- `phase-5/dapr-components/*.yaml`
- `phase-4/backend/events/publisher.py`
