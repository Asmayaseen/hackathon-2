# ADR-006: Dapr + Kafka (Strimzi) for Event-Driven Architecture

**Status**: Accepted
**Date**: 2026-02-11
**Decision Makers**: asmayaseen
**Context**: Phase V event-driven distributed system architecture

## Context

Phase V transforms the monolithic Todo backend into an event-driven distributed system. Task mutations (create, update, complete, delete) must publish events consumed by downstream services: a notification microservice, audit logging, and real-time client sync. This requires decisions on three layers:

1. **Event broker**: What message bus carries events between services?
2. **Broker deployment**: Self-hosted operator vs managed cloud service?
3. **Application runtime**: How do services publish/subscribe without tight coupling to the broker?

The hackathon mandates Kafka and Dapr for Phase V.

### Requirements

- Events must be durable (survive pod restarts).
- Publishing must not block CRUD response times (fire-and-forget).
- The architecture must work on local Minikube and cloud Kubernetes (DOKS/AKS/GKE).
- Swapping the event broker (e.g., Kafka to Redis Streams) should require zero code changes.

## Decision

### Three-Layer Architecture

```
FastAPI Backend (producer)
    |
    | HTTP POST to localhost:3500 (Dapr sidecar)
    v
Dapr Pub/Sub Component (pubsub.kafka)
    |
    | Kafka protocol
    v
Strimzi Kafka Cluster (KRaft mode, no Zookeeper)
    |
    | Dapr subscription routing
    v
Notification Service (consumer, separate FastAPI microservice)
```

### Specific Choices

**1. Apache Kafka via Strimzi Operator (event broker)**

- Strimzi `Kafka` CRD with **KRaft mode** (no Zookeeper dependency).
- Kafka version 4.0.0, single-node for development, multi-node for cloud.
- Three topics with differentiated retention:

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| `task-events` | 3 | 7 days | All CRUD operations |
| `reminders` | 1 | 1 day | Scheduled reminder delivery |
| `task-updates` | 1 | 1 hour | Real-time client sync |

**2. Dapr as application runtime (abstraction layer)**

Five Dapr building blocks:

| Building Block | Component Type | Backend |
|---------------|---------------|---------|
| Pub/Sub | `pubsub.kafka` | Strimzi Kafka |
| State Store | `state.postgresql` | Neon PostgreSQL |
| Bindings | `bindings.cron` | 3 cron schedules |
| Secrets | `secretstores.kubernetes` | K8s Secrets |
| Service Invocation | `invoke` | Direct pod-to-pod |

**3. Fire-and-forget publishing pattern**

```python
# In task route handler (non-blocking)
asyncio.create_task(publish_task_event(EventType.CREATED, task, user_id))
```

Events are published via HTTP to the Dapr sidecar (`localhost:3500`). If the sidecar is unavailable (local dev without Dapr), a warning is logged and the request continues.

## Alternatives Considered

### Event Broker

| Option | Cost | Ops Complexity | Durability | Verdict |
|--------|------|---------------|------------|---------|
| **Strimzi Kafka (chosen, local)** | Free | Medium (operator manages lifecycle) | Excellent | Default for local/self-hosted |
| **Redpanda Cloud (cloud option)** | Free tier available | Low (managed) | Excellent | Documented as cloud alternative |
| Confluent Cloud | $400 credit, then ~$50/mo | Low (managed) | Excellent | Expensive after credits expire |
| Redis Streams | Free (existing Redis) | Low | Good (AOF persistence) | Weaker ordering guarantees, no ecosystem tooling |
| RabbitMQ | Free | Medium | Good | Not Kafka-compatible, weaker at high throughput |
| NATS JetStream | Free | Low | Good | Less mature ecosystem, fewer learning resources |

### Kafka Deployment Mode

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Strimzi KRaft (chosen)** | No Zookeeper, simpler topology, fewer pods, faster startup | KRaft GA only since Kafka 3.3 | Chosen: ZK removal eliminates 3+ pods of overhead |
| Strimzi with Zookeeper | Battle-tested, more documentation | 3 extra ZK pods, deprecated path | Rejected: unnecessary complexity |
| Helm chart (bitnami/kafka) | Simpler initial setup | No operator lifecycle management, manual upgrades | Rejected: Strimzi operator is more Kubernetes-native |

### Application Runtime

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Dapr sidecar (chosen)** | Vendor-agnostic HTTP API, YAML-only config swaps, built-in retries/dead-letter, 5 building blocks | Sidecar memory (~50MB/pod), requires `dapr init -k` | Chosen: mandated and architecturally sound |
| Direct kafka-python client | Full control, no sidecar overhead | Vendor lock-in, manual connection/retry, broker-specific code | Rejected: code changes required to swap brokers |
| CloudEvents + HTTP webhooks | Simple, no infrastructure dependency | No retry, no dead-letter, no state management | Rejected: insufficient for production reliability |

### Why Strimzi over Redpanda for Local Development

- Strimzi is the canonical Kafka-on-Kubernetes operator, widely documented.
- KRaft mode eliminates Zookeeper, reducing local resource requirements.
- Dapr's `pubsub.kafka` component works identically against Strimzi and Redpanda (Kafka-compatible protocol).
- Switching to Redpanda Cloud for production requires only a YAML config change (`pubsub-redpanda.yaml` already exists with SASL auth).

## Consequences

### Positive

- **Zero code changes for broker swap**: Dapr Pub/Sub abstracts the broker. `pubsub-kafka.yaml` (Strimzi) and `pubsub-redpanda.yaml` (managed) are interchangeable configs.
- **Non-blocking CRUD**: fire-and-forget publishing via `asyncio.create_task()` keeps task endpoint p95 < 200ms.
- **Microservice decoupling**: notification service consumes events independently; adding new consumers requires only a new Dapr subscription YAML.
- **Cron without custom code**: Dapr cron bindings handle reminder checks (5 min), recurring task generation (hourly), and cleanup (daily) without scheduler libraries.
- **Graceful degradation**: if Dapr sidecar is unavailable (local dev), events are silently skipped and CRUD still works.

### Negative

- **Resource overhead**: Strimzi Kafka + Dapr sidecars require ~4 CPU / 8 GB RAM minimum on Minikube. Not viable on machines with < 8 GB RAM.
- **Operational complexity**: three systems to understand (Kafka, Strimzi operator, Dapr) with separate failure modes.
- **Local development friction**: `dapr init -k`, Strimzi operator install, and topic creation are prerequisites before the first event flows.
- **Eventual consistency**: event consumers may lag; notification delivery is not guaranteed to be immediate.

### Risks

- Strimzi operator upgrades may introduce breaking CRD changes. Pin operator version in Helm charts.
- Dapr sidecar injection requires pod restart; rolling updates must account for sidecar readiness.
- KRaft mode in Kafka 4.0 is stable but has less community troubleshooting material than ZK-based deployments.

## Related

- ADR-003: `history/adr/003-dapr-for-event-driven-architecture.md` (Dapr over direct Kafka)
- Event publisher: `phase-4/backend/events/publisher.py`
- Event schemas: `phase-4/backend/events/schemas.py`
- Kafka manifests: `phase-5/kafka/kafka-cluster.yaml`, `phase-5/kafka/topics.yaml`
- Dapr components: `phase-5/dapr-components/pubsub-kafka.yaml`, `phase-5/dapr-components/pubsub-redpanda.yaml`
- Notification service: `phase-5/notification-service/main.py`
- Managed Kafka guide: `phase-5/kafka/MANAGED_KAFKA_SETUP.md`
- Phase V spec: `specs/phase-5/spec.md`
- Phase V plan: `specs/phase-5/plan.md` (AD-01, AD-02)
