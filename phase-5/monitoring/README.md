# Monitoring & Logging Stack - Phase V

This directory contains the monitoring and logging configuration for the Todo App Phase V deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │  Todo App    │     │  Todo App    │     │ Notification │                 │
│  │  Backend     │     │  Frontend    │     │  Service     │                 │
│  │  + Dapr      │     │  + Dapr      │     │  + Dapr      │                 │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘                 │
│         │ metrics            │ logs               │ metrics                  │
│         │                    │                    │                          │
│         ▼                    ▼                    ▼                          │
│  ┌──────────────────────────────────────────────────────────┐               │
│  │                    Prometheus                             │               │
│  │  - Scrapes Dapr sidecar metrics (port 9090)              │               │
│  │  - Scrapes Kafka metrics                                  │               │
│  │  - ServiceMonitor/PodMonitor auto-discovery              │               │
│  └──────────────────────────┬───────────────────────────────┘               │
│                             │                                                │
│  ┌──────────────────────────┼───────────────────────────────┐               │
│  │                    Loki  │                                │               │
│  │  - Aggregates pod logs  │                                │               │
│  │  - Promtail collectors  │                                │               │
│  └──────────────────────────┼───────────────────────────────┘               │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────────────────────────────────────────────┐               │
│  │                    Grafana                                │               │
│  │  - Visualize metrics (Prometheus)                        │               │
│  │  - Query logs (Loki)                                     │               │
│  │  - Pre-built dashboards                                  │               │
│  │  - Alerting                                              │               │
│  └──────────────────────────────────────────────────────────┘               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Add Helm Repositories

```bash
# Add required Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 2. Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

### 3. Deploy Prometheus Stack

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f prometheus-values.yaml \
  -n monitoring \
  --wait
```

### 4. Deploy Loki Stack

```bash
helm install loki grafana/loki-stack \
  -f loki-values.yaml \
  -n monitoring \
  --wait
```

### 5. Apply Service Monitors

```bash
kubectl apply -f service-monitors.yaml
```

### 6. Import Grafana Dashboards

```bash
# Port-forward to Grafana
kubectl port-forward svc/todo-grafana 3000:80 -n monitoring

# Access at http://localhost:3000
# Default credentials: admin / todo-admin-2026

# Import dashboard from grafana-dashboards/todo-app-dashboard.json
```

## Access URLs

### Local (Minikube)

```bash
# Grafana
minikube service todo-grafana -n monitoring
# Or: kubectl port-forward svc/todo-grafana 3000:80 -n monitoring

# Prometheus
minikube service todo-prometheus-prometheus -n monitoring
# Or: kubectl port-forward svc/todo-prometheus-prometheus 9090:9090 -n monitoring

# AlertManager
kubectl port-forward svc/todo-prometheus-alertmanager 9093:9093 -n monitoring
```

### NodePort Access

| Service | NodePort | URL |
|---------|----------|-----|
| Grafana | 30300 | http://<minikube-ip>:30300 |
| Prometheus | 30090 | http://<minikube-ip>:30090 |

## Components

### Prometheus Stack

- **Prometheus**: Time-series metrics database
- **AlertManager**: Alert routing and management
- **Node Exporter**: Node-level metrics
- **Kube State Metrics**: Kubernetes object metrics

### Loki Stack

- **Loki**: Log aggregation system
- **Promtail**: Log collection agent

### Grafana

- **Pre-configured datasources**: Prometheus + Loki
- **Todo App Dashboard**: Custom dashboard for Phase V
- **Dapr Dashboard**: Community Dapr monitoring dashboard

## Metrics Collected

### Dapr Sidecar Metrics (Port 9090)

| Metric | Description |
|--------|-------------|
| `dapr_http_server_request_count` | HTTP request count by method/path |
| `dapr_http_server_latency_bucket` | HTTP latency histogram |
| `dapr_component_pubsub_outgoing_messages` | Published messages count |
| `dapr_component_pubsub_ingress_messages` | Consumed messages count |
| `dapr_component_loaded` | Component status (1=loaded) |

### Kafka Metrics (Strimzi)

| Metric | Description |
|--------|-------------|
| `kafka_server_BrokerTopicMetrics_MessagesInPerSec` | Messages in per second |
| `kafka_consumergroup_lag` | Consumer group lag |
| `kafka_server_ReplicaManager_PartitionCount` | Partition count |

### Application Metrics

| Metric | Description |
|--------|-------------|
| `http_requests_total` | Total HTTP requests |
| `http_request_duration_seconds` | Request latency |

## Alerting Rules

Basic alerts are configured for:

1. **High Error Rate**: >5% error rate for 5 minutes
2. **Pod Restart**: Container restarts detected
3. **High Latency**: p95 latency > 2 seconds
4. **Kafka Consumer Lag**: Lag > 1000 messages

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check targets
kubectl port-forward svc/todo-prometheus-prometheus 9090:9090 -n monitoring
# Visit http://localhost:9090/targets

# Check ServiceMonitor
kubectl get servicemonitor -n default
kubectl describe servicemonitor todo-backend-monitor
```

### Loki Not Receiving Logs

```bash
# Check Promtail
kubectl logs -l app=promtail -n monitoring

# Test Loki
curl -G http://localhost:3100/loki/api/v1/labels
```

### Grafana Dashboard Issues

```bash
# Check Grafana logs
kubectl logs -l app.kubernetes.io/name=grafana -n monitoring

# Verify datasources
# Go to Configuration > Data Sources in Grafana UI
```

## Resource Usage

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|------------|-----------|----------------|--------------|
| Prometheus | 200m | 500m | 256Mi | 512Mi |
| Grafana | 100m | 200m | 128Mi | 256Mi |
| AlertManager | 50m | 100m | 64Mi | 128Mi |
| Loki | 100m | 200m | 128Mi | 256Mi |
| Promtail | 50m | 100m | 64Mi | 128Mi |

**Total**: ~500m CPU, ~640Mi Memory (requests)

## Cleanup

```bash
# Uninstall monitoring stack
helm uninstall prometheus -n monitoring
helm uninstall loki -n monitoring
kubectl delete namespace monitoring
```

## Production Considerations

For production deployment:

1. **Enable persistence** for Prometheus and Loki
2. **Configure alerting** destinations (email, Slack, PagerDuty)
3. **Increase retention** based on requirements
4. **Set up RBAC** for Grafana users
5. **Enable TLS** for all endpoints
6. **Configure external storage** (S3, GCS) for long-term retention
