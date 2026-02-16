# Managed Kafka Integration Guide

This document explains how to configure the Todo App with managed Kafka services (Redpanda Cloud or Confluent Cloud) as an alternative to self-hosted Strimzi.

## Architecture Decision Record

### Decision: Support Both Self-Hosted and Managed Kafka

**Context:**
- Hackathon requires Kafka for event-driven architecture
- Self-hosted Strimzi provides free, full-control option
- Managed services offer simpler setup and production-readiness

**Decision:**
Support both deployment modes with Dapr abstraction:
1. **Local/Dev**: Self-hosted Strimzi (free, learning experience)
2. **Cloud/Prod**: Redpanda Cloud (managed, serverless free tier)

**Benefits:**
- Dapr pub/sub abstraction allows swapping backends via config
- No code changes required between local and cloud
- Students learn both patterns

---

## Option 1: Redpanda Cloud (Recommended)

### Why Redpanda?
- Kafka-compatible API
- Free serverless tier (no credit card required for basic usage)
- No Zookeeper complexity
- Fast setup (<5 minutes)

### Setup Steps

#### 1. Create Redpanda Cloud Account
```
1. Go to https://redpanda.com/cloud
2. Sign up with email or GitHub
3. Select "Serverless" cluster type
4. Choose region closest to your K8s cluster
```

#### 2. Create Topics
In Redpanda Console, create these topics:
| Topic | Partitions | Retention |
|-------|------------|-----------|
| task-events | 3 | 7 days |
| reminders | 1 | 1 day |
| task-updates | 1 | 1 hour |

#### 3. Generate Credentials
```
1. Go to Security > SCRAM Users
2. Create new user (e.g., "todo-app")
3. Select SCRAM-SHA-256
4. Copy username and password
```

#### 4. Get Bootstrap Server
```
1. Go to Overview > Connection
2. Copy the Bootstrap server URL
   Format: <cluster-id>.<region>.cloud.redpanda.com:9092
```

#### 5. Create Kubernetes Secret
```bash
kubectl create secret generic redpanda-credentials \
  --from-literal=brokers='your-cluster.region.cloud.redpanda.com:9092' \
  --from-literal=username='your-username' \
  --from-literal=password='your-password'
```

#### 6. Apply Redpanda Dapr Component
```bash
kubectl apply -f phase-5/dapr-components/pubsub-redpanda.yaml
```

#### 7. Verify Connection
```bash
# Check Dapr sidecar logs
kubectl logs -l app=todo-backend -c daprd | grep kafka

# Expected output:
# "component kafka-pubsub is ready"
```

---

## Option 2: Confluent Cloud

### Setup Steps

#### 1. Create Confluent Cloud Account
```
1. Go to https://confluent.io/get-started
2. Sign up (free $400 credit for 30 days)
3. Create a Basic cluster
```

#### 2. Create Topics
In Confluent Console:
| Topic | Partitions |
|-------|------------|
| task-events | 3 |
| reminders | 1 |
| task-updates | 1 |

#### 3. Generate API Keys
```
1. Go to Data Integration > API Keys
2. Create API Key (Cluster scope)
3. Copy Key and Secret
```

#### 4. Create Kubernetes Secret
```bash
kubectl create secret generic confluent-credentials \
  --from-literal=brokers='pkc-xxxxx.region.gcp.confluent.cloud:9092' \
  --from-literal=api-key='YOUR_API_KEY' \
  --from-literal=api-secret='YOUR_API_SECRET'
```

#### 5. Update Dapr Component
Edit `pubsub-redpanda.yaml` and uncomment the Confluent section.

---

## Option 3: Self-Hosted Strimzi (Default)

This is the default configuration already in `pubsub-kafka.yaml`.

### When to Use
- Local development on Minikube
- Learning Kubernetes operators
- Cost-sensitive deployments
- Full control over configuration

### Advantages
- Free (only compute costs)
- No external dependencies
- Full Kafka features
- Great learning experience

### Setup
```bash
# Already configured - just deploy
kubectl apply -f phase-5/kafka/kafka-cluster.yaml
kubectl apply -f phase-5/kafka/topics.yaml
kubectl apply -f phase-5/dapr-components/pubsub-kafka.yaml
```

---

## Switching Between Providers

Thanks to Dapr's abstraction, switching between Kafka providers requires only configuration changes:

### Switch to Redpanda Cloud
```bash
# 1. Create secret with Redpanda credentials
kubectl create secret generic redpanda-credentials ...

# 2. Replace the Dapr component
kubectl delete -f phase-5/dapr-components/pubsub-kafka.yaml
kubectl apply -f phase-5/dapr-components/pubsub-redpanda.yaml

# 3. Restart pods to pick up new config
kubectl rollout restart deployment/todo-backend
kubectl rollout restart deployment/notification-service
```

### Switch Back to Strimzi
```bash
kubectl delete -f phase-5/dapr-components/pubsub-redpanda.yaml
kubectl apply -f phase-5/dapr-components/pubsub-kafka.yaml
kubectl rollout restart deployment/todo-backend
kubectl rollout restart deployment/notification-service
```

**No code changes required!** Dapr handles the difference.

---

## Environment Configuration

### Helm Values for Managed Kafka

```yaml
# values-cloud.yaml additions
kafka:
  # Set to false when using managed Kafka
  selfHosted: false

  # Redpanda Cloud settings
  redpanda:
    enabled: true
    existingSecret: redpanda-credentials

  # Disable Strimzi deployment
  strimzi:
    enabled: false
```

### Environment Variables

The backend doesn't need Kafka environment variables when using Dapr - all configuration is in Dapr components.

---

## Verification

### Test Event Publishing
```bash
# Create a task via API
curl -X POST http://localhost:8000/api/test-user/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test managed Kafka"}'

# Check Redpanda Console for messages in task-events topic
```

### Monitor Consumer Lag
```bash
# In Redpanda Console: Topics > task-events > Consumer Groups
# Should show "todo-service" consumer group with minimal lag
```

---

## Troubleshooting

### Connection Refused
```bash
# Check secret exists
kubectl get secret redpanda-credentials -o yaml

# Verify broker URL format
# Should be: cluster-id.region.cloud.redpanda.com:9092
```

### Authentication Failed
```bash
# Check Dapr sidecar logs
kubectl logs <pod> -c daprd | grep -i auth

# Common issues:
# - Wrong SASL mechanism (use SCRAM-SHA-256 for Redpanda)
# - API key vs SCRAM credentials confusion (Confluent uses API keys)
```

### TLS Handshake Failed
```bash
# Ensure TLS is enabled in Dapr component
# tls: "true"
# tlsSkipVerify: "false"
```

---

## Cost Comparison

| Provider | Free Tier | Paid Starting At |
|----------|-----------|------------------|
| **Strimzi (Self-hosted)** | Free (compute only) | N/A |
| **Redpanda Cloud** | Serverless free tier | $0.10/GB transferred |
| **Confluent Cloud** | $400 credit (30 days) | ~$50/month basic |
| **CloudKarafka** | 5 topics free | $19/month |

**Recommendation for Hackathon:**
1. **Development**: Self-hosted Strimzi on Minikube
2. **Cloud Demo**: Redpanda Cloud serverless (free)

---

## Summary

The Todo App supports multiple Kafka deployment options:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KAFKA PROVIDER OPTIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                    │
│  │   LOCAL DEV     │     │   CLOUD PROD    │                    │
│  │                 │     │                 │                    │
│  │  Strimzi/KRaft  │     │ Redpanda Cloud  │                    │
│  │  (Self-hosted)  │     │   (Managed)     │                    │
│  │                 │     │                 │                    │
│  │  Free, Full     │     │ Serverless,     │                    │
│  │  Control        │     │ Free Tier       │                    │
│  └────────┬────────┘     └────────┬────────┘                    │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
│                       ▼                                          │
│           ┌─────────────────────┐                                │
│           │   DAPR PUB/SUB      │                                │
│           │   (Abstraction)     │                                │
│           └─────────────────────┘                                │
│                       │                                          │
│                       ▼                                          │
│           ┌─────────────────────┐                                │
│           │   TODO APP CODE     │                                │
│           │   (No changes!)     │                                │
│           └─────────────────────┘                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
