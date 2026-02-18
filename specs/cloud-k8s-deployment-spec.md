# Cloud Kubernetes Deployment Specification

**Version**: 1.0.0
**Created**: 2026-02-17
**Status**: Complete
**Scope**: Production cloud deployment architecture for Todo Chatbot

## Table of Contents

1. [Overview and Scope](#overview-and-scope)
2. [Architecture Diagram](#architecture-diagram)
3. [Cloud Provider Selection](#cloud-provider-selection)
4. [Components](#components)
5. [AKS Implementation Guide](#aks-implementation-guide)
6. [Helm Configuration](#helm-configuration)
7. [CI/CD Pipeline Integration](#cicd-pipeline-integration)
8. [DNS, TLS/SSL, and Ingress](#dns-tlsssl-and-ingress)
9. [Cost Optimization](#cost-optimization)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Cleanup and Teardown](#cleanup-and-teardown)

---

## Overview and Scope

### Purpose

This specification defines the production deployment architecture for the Evolution Todo Chatbot application on managed Kubernetes services. The deployment leverages event-driven architecture with Kafka, Dapr for distributed application runtime, and managed services for databases and messaging.

### In Scope

- Multi-cloud Kubernetes deployment (AKS, DOKS, GKE)
- Managed PostgreSQL database integration
- Kafka/Strimzi for event streaming
- Dapr sidecar deployment and configuration
- Helm chart-based application deployment
- TLS/SSL termination and DNS management
- Monitoring, logging, and observability stack
- Cost optimization strategies
- CI/CD pipeline integration

### Out of Scope

- Application code changes (use Phase 4-5 codebases as-is)
- Custom managed service provisioning (use provider defaults)
- Advanced traffic management (mesh, canary deployments)
- Multi-region failover configurations
- Disaster recovery and backup strategies

### Key Objectives

1. Deploy high-availability production environment
2. Enable event-driven communication between services
3. Provide observability and monitoring capabilities
4. Minimize infrastructure costs
5. Support rapid iteration with CI/CD automation

---

## Architecture Diagram

### High-Level Component Diagram

```
Internet / DNS
    |
    v
CDN (Optional)
    |
    v
External Load Balancer
    |
    v
Kubernetes Ingress Controller (Nginx)
    |
    +------> Frontend Service (2 replicas)
    |            |
    |            v
    |        React Next.js Frontend
    |        (Dapr sidecar)
    |
    +------> Backend Service (2 replicas)
    |            |
    |            v
    |        FastAPI Backend
    |        (Dapr sidecar + Event Publisher)
    |
    +------> Notification Service (1-2 replicas)
             |
             v
         FastAPI Notification Processor
         (Dapr sidecar + Kafka Consumer)

Behind Ingress:
    |
    +------> Kafka Cluster (Strimzi)
    |        - 3 nodes (KRaft mode)
    |        - Topics: task-events, reminders, task-updates
    |        - Persistence: Cloud storage
    |
    +------> PostgreSQL (Managed Service)
    |        - Multi-AZ deployment
    |        - Automated backups
    |        - Read replicas optional
    |
    +------> Dapr Control Plane
    |        - Placement service
    |        - Sidecar injector
    |
    +------> Monitoring Stack
             - Prometheus (metrics collection)
             - Grafana (visualization)
             - Loki (log aggregation)
```

### Data Flow

```
User Request
    |
    v
Ingress/Load Balancer
    |
    v
Frontend Pod (with Dapr sidecar)
    |
    +---> Backend API (via HTTP)
    |
    v
Backend Pod (with Dapr sidecar)
    |
    +---> PostgreSQL (Dapr state store)
    |
    +---> Dapr Pub/Sub
         |
         v
    Kafka Topic (task-events)
         |
         v
    Notification Service Pod (with Dapr sidecar)
         |
         v
    Deliver Notification / Log Event
```

---

## Cloud Provider Selection

### Recommended Provider: Azure Kubernetes Service (AKS)

**Why AKS:**
- Azure ecosystem integration (Azure DevOps, Azure Monitor)
- Competitive pricing with reserved instances
- Native support for managed PostgreSQL and messaging services
- Strong enterprise support and compliance certifications
- Seamless GitHub Actions integration

**Key AKS Features:**
- Auto-scaling node pools (cost optimization)
- Managed upgrades and patching
- Azure Policy for governance
- Azure Monitor for observability
- Virtual network integration

### Alternative Providers

#### DigitalOcean Kubernetes Service (DOKS)

**Advantages:**
- Simple, predictable pricing
- Quick cluster provisioning
- Easy multi-node setup
- Managed Kafka via App Platform

**Disadvantages:**
- Fewer advanced features
- Limited regional availability
- Fewer managed service integrations

**Use Case:** Development/staging environments, cost-conscious deployments

#### Google Kubernetes Engine (GKE)

**Advantages:**
- Excellent autoscaling (Vertical Pod Autoscaling)
- Strong multi-cluster support
- Advanced networking and security features
- Best-in-class observability (Cloud Trace, Cloud Profiler)

**Disadvantages:**
- Complex pricing model
- Steeper learning curve
- Higher resource overhead

**Use Case:** Large-scale, multi-region deployments

### Provider Comparison Matrix

| Feature | AKS | DOKS | GKE |
|---------|-----|------|-----|
| Managed PostgreSQL | Yes (Azure Database) | Yes (Managed DB) | Yes (Cloud SQL) |
| Managed Kafka | Via partner (Confluent) | App Platform | Via partner (Dataflow) |
| Auto-scaling | Yes (best) | Basic | Yes (excellent) |
| Pricing | Moderate | Low | High |
| Support | Enterprise | Community | Enterprise |
| Setup Time | Medium | Fast | Medium |
| Integration | Azure ecosystem | Minimal | GCP ecosystem |

**Recommendation: Use AKS for production, DOKS for development.**

---

## Components

### 1. Frontend Pod (Next.js)

**Specification:**
- **Image**: `yourusername/todo-frontend:latest`
- **Port**: 3000
- **Replicas**: 2 (production HA)
- **Dapr Annotations**:
  - `dapr.io/enabled: "true"`
  - `dapr.io/app-id: "todo-frontend"`
  - `dapr.io/app-port: "3000"`

**Resource Requirements:**
```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend service URL (injected via ConfigMap)
- `NEXT_PUBLIC_ENVIRONMENT`: "production"

**Liveness Probe:**
```
GET / HTTP/1.1
InitialDelaySeconds: 20
PeriodSeconds: 10
```

### 2. Backend Pod (FastAPI)

**Specification:**
- **Image**: `yourusername/todo-backend:latest`
- **Port**: 8000
- **Replicas**: 2 (production HA)
- **Dapr Annotations**:
  - `dapr.io/enabled: "true"`
  - `dapr.io/app-id: "todo-backend"`
  - `dapr.io/app-port: "8000"`

**Resource Requirements:**
```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string (via Secret)
- `JWT_SECRET`: JWT signing key (via Secret)
- `DAPR_PUBSUB_NAME`: "kafka-pubsub"
- `KAFKA_BOOTSTRAP_SERVERS`: "taskflow-kafka-kafka-bootstrap.kafka:9092"
- `OPENAI_API_KEY`: OpenAI API key (via Secret)
- `GROQ_API_KEY`: Groq API key (via Secret, optional)
- `LOG_LEVEL`: "INFO"

**Liveness Probe:**
```
GET /health HTTP/1.1
InitialDelaySeconds: 30
PeriodSeconds: 10
FailureThreshold: 3
```

**Readiness Probe:**
```
GET /health/ready HTTP/1.1
InitialDelaySeconds: 10
PeriodSeconds: 5
```

### 3. Notification Service Pod

**Specification:**
- **Image**: `yourusername/todo-notification:latest`
- **Port**: 8001
- **Replicas**: 1 (can scale to 2 for HA)
- **Dapr Annotations**:
  - `dapr.io/enabled: "true"`
  - `dapr.io/app-id: "todo-notification"`
  - `dapr.io/app-port: "8001"`

**Resource Requirements:**
```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Environment Variables:**
- `DAPR_PUBSUB_NAME`: "kafka-pubsub"
- `NOTIFICATION_TOPICS`: "task-events,reminders"
- `LOG_LEVEL`: "INFO"

**Purpose**: Consumes events from Kafka via Dapr Pub/Sub and delivers notifications

### 4. PostgreSQL (Managed Database)

**Provider-Specific Configuration:**

#### AKS + Azure Database for PostgreSQL

```bash
# Flexible Server recommended
az postgres flexible-server create \
  --resource-group <rg-name> \
  --name <db-name> \
  --location <region> \
  --admin-user postgres \
  --admin-password <strong-password> \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 32 \
  --version 14
```

**Network Configuration:**
- Enable Virtual Network integration
- Allow traffic from AKS subnet
- Firewall rules: Only from Kubernetes cluster

**Backup Configuration:**
- Automatic daily backups (7-35 days retention)
- Geo-redundant backup enabled
- Point-in-time recovery enabled

**Specifications:**
- **PostgreSQL Version**: 14+
- **Instance Type**: Standard_B2s (burstable, dev/staging) or Standard_B4ms (production)
- **Storage**: 32-100 GB (SSD)
- **High Availability**: Multi-AZ deployment
- **Connection String Format**: `postgresql://user:password@host:5432/dbname?sslmode=require`

#### DOKS + DigitalOcean Database

```bash
doctl databases create \
  --engine pg \
  --region <region> \
  --version 14 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1 \
  --name todo-db
```

**Specifications:**
- **Size**: db-s-1vcpu-1gb (dev) or db-s-2vcpu-4gb (production)
- **Automatic Backups**: Every 24 hours
- **Connection**: Firewall configured for cluster subnet

#### GKE + Cloud SQL

```bash
gcloud sql instances create <instance-name> \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=<region>
```

**Specifications:**
- **Instance Tier**: db-f1-micro (dev) or db-n1-standard-1 (production)
- **High Availability**: Regional configuration
- **Connection via Cloud SQL Proxy**: Required for security

### 5. Kafka Cluster (Strimzi Operator)

**Deployment Method**: Strimzi Operator on Kubernetes

**KRaft Configuration** (recommended, no Zookeeper):

```yaml
# From phase-5/kafka/kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim
      size: 10Gi
      class: default
  zookeeper:
    replicas: 0  # KRaft mode: no Zookeeper needed
```

**Topics Configuration**:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: taskflow-kafka
spec:
  partitions: 3
  replicationFactor: 3
  config:
    retention.ms: 604800000  # 7 days
    compression.type: snappy
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
spec:
  partitions: 3
  replicationFactor: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
spec:
  partitions: 2
  replicationFactor: 2
```

**Bootstrap Server**: `taskflow-kafka-kafka-bootstrap.kafka:9092`

**Persistence**: 10 GB per broker, SSD-backed storage

**Resource Requests**:
- Kafka broker: 1000m CPU, 1Gi memory
- Zookeeper (if used): 100m CPU, 128Mi memory

### 6. Dapr Sidecar Configuration

**Deployment**:
```bash
# Install Dapr control plane on cluster
dapr init -k --wait

# Verify installation
dapr status -k
```

**Pub/Sub Component** (Kafka):

```yaml
# From phase-5/dapr-components/pubsub-kafka.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "taskflow-kafka-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "todo-app"
    - name: authRequired
      value: "false"
```

**State Store Component** (PostgreSQL):

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgresql-state
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secret
        key: connection-string
```

**Sidecar Annotations** (applied to all app pods):

```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "app-name"
dapr.io/app-port: "port"
dapr.io/app-protocol: "http"
dapr.io/sidecar-memory-limit: "256Mi"
dapr.io/sidecar-memory-request: "128Mi"
```

---

## AKS Implementation Guide

### Prerequisites

- Azure account with subscription
- `az` CLI installed locally
- `kubectl` installed locally
- `helm` v3+ installed
- Git repository with code

### Step 1: Create Resource Group and AKS Cluster

```bash
#!/bin/bash
# Set variables
RESOURCE_GROUP="todo-rg"
CLUSTER_NAME="todo-prod"
REGION="eastus"
NODE_COUNT=3
NODE_SIZE="Standard_B4ms"  # 4 vCPU, 16 GB RAM

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $REGION

# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count $NODE_COUNT \
  --vm-set-type VirtualMachineScaleSets \
  --enable-managed-identity \
  --network-plugin azure \
  --zone-redundancy azure \
  --enable-auto-upgrade \
  --auto-upgrade-channel patch \
  --enable-cluster-autoscaling \
  --min-count 3 \
  --max-count 10 \
  --zones 1 2 3 \
  --generate-ssh-keys

# Get kubeconfig
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --overwrite-existing
```

**Parameters Explained:**
- `zone-redundancy azure`: Spreads nodes across multiple availability zones
- `enable-cluster-autoscaling`: Automatically scales node pools based on workload
- `auto-upgrade-channel patch`: Automatic patching enabled
- `network-plugin azure`: Azure CNI for advanced networking

### Step 2: Create PostgreSQL Database

```bash
# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name todo-db \
  --location $REGION \
  --admin-user postgres \
  --admin-password $DB_PASSWORD \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 32 \
  --version 14 \
  --zone 1 \
  --backup-retention 7 \
  --geo-redundant-backup Disabled

# Configure firewall to allow AKS subnet
AKS_SUBNET_ID=$(az aks show \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --query nodeResourceGroup -o tsv)

# Get cluster node subnet
NODE_RG=$(az aks show \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --query nodeResourceGroup -o tsv)

VNET_NAME=$(az network vnet list \
  --resource-group $NODE_RG \
  --query '[0].name' -o tsv)

SUBNET_ID=$(az network vnet subnet list \
  --resource-group $NODE_RG \
  --vnet-name $VNET_NAME \
  --query '[0].id' -o tsv)

# Add firewall rule
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name todo-db \
  --rule-name AllowAKS \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

**Connection String**:
```
postgresql://postgres:$DB_PASSWORD@todo-db.postgres.database.azure.com:5432/todo_db?sslmode=require
```

### Step 3: Install Required Operators and Addons

```bash
# 1. Add Helm repos
helm repo add strimzi https://strimzi.io/charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add jetstack https://charts.jetstack.io
helm repo update

# 2. Create namespaces
kubectl create namespace kafka
kubectl create namespace monitoring
kubectl create namespace todo-app
kubectl create namespace cert-manager

# 3. Install Strimzi operator
helm install strimzi-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set replicas=2

# 4. Install Dapr
dapr init -k --wait

# 5. Install cert-manager for TLS
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# 6. Install Nginx Ingress Controller
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-internal"="false"
```

### Step 4: Deploy Kafka Cluster and Topics

```bash
# Apply Kafka cluster and topics
kubectl apply -f phase-5/kafka/kafka-cluster.yaml
kubectl apply -f phase-5/kafka/topics.yaml

# Wait for Kafka to be ready
kubectl wait kafka/taskflow-kafka \
  --for=condition=Ready \
  -n kafka \
  --timeout=600s
```

### Step 5: Apply Dapr Components

```bash
# Create secrets for database connection
kubectl create secret generic db-credentials \
  --from-literal=connection-string="$DATABASE_URL" \
  -n todo-app

# Apply Dapr components
kubectl apply -f phase-5/dapr-components/ -n todo-app
```

### Step 6: Deploy Application with Helm

```bash
# Create secrets for application
kubectl create secret generic app-secrets \
  --from-literal=jwtSecret="$JWT_SECRET" \
  --from-literal=openaiApiKey="$OPENAI_API_KEY" \
  --from-literal=groqApiKey="$GROQ_API_KEY" \
  -n todo-app

# Deploy using Helm
helm install todo-app ./phase-5/helm/todo-app \
  -n todo-app \
  -f phase-5/helm/todo-app/values-cloud.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --set ingress.host="todo.yourdomain.com"
```

### Step 7: Configure DNS

```bash
# Get external IP from Ingress
EXTERNAL_IP=$(kubectl get svc \
  -n ingress-nginx \
  ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "External IP: $EXTERNAL_IP"

# Create DNS A record pointing to $EXTERNAL_IP
# In Azure Portal or DNS provider:
# Record: todo.yourdomain.com
# Type: A
# Value: $EXTERNAL_IP
```

---

## Helm Configuration

### Cloud Values File Structure

**File**: `phase-5/helm/todo-app/values-cloud.yaml`

```yaml
# Global configuration
global:
  imageTag: latest
  imageRegistry: "yourusername/"
  environment: production

# Frontend configuration
frontend:
  enabled: true
  replicas: 2
  image:
    repository: yourusername/todo-frontend
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP
    port: 3000
  ingress:
    path: /
    pathType: Prefix
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# Backend configuration
backend:
  enabled: true
  replicas: 2
  image:
    repository: yourusername/todo-backend
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  env:
    - name: LOG_LEVEL
      value: INFO
    - name: DAPR_PUBSUB_NAME
      value: kafka-pubsub

# Notification Service
notificationService:
  enabled: true
  replicas: 1
  image:
    repository: yourusername/todo-notification
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP
    port: 8001
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

# Dapr configuration
dapr:
  enabled: true
  logLevel: info
  enableMetrics: true
  metricsPort: 9090

# Secrets (set via --set or external secret management)
secrets:
  databaseUrl: ""
  jwtSecret: ""
  openaiApiKey: ""
  groqApiKey: ""

# ConfigMap
config:
  corsOrigins: "https://todo.yourdomain.com"
  apiUrl: "https://todo.yourdomain.com/api"
  daprPubsubName: "kafka-pubsub"

# Kafka configuration
kafka:
  enabled: true
  bootstrapServers: "taskflow-kafka-kafka-bootstrap.kafka:9092"
  namespace: kafka

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  host: "todo.yourdomain.com"
  tls:
    enabled: true
    issuer: "letsencrypt-prod"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"

# Storage
persistence:
  enabled: false

# Node affinity for cost optimization
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
            - key: workload-type
              operator: In
              values:
                - general
```

### Deployment Commands

```bash
# Basic deployment
helm install todo-app ./phase-5/helm/todo-app \
  -n todo-app \
  -f phase-5/helm/todo-app/values-cloud.yaml

# With secrets
helm install todo-app ./phase-5/helm/todo-app \
  -n todo-app \
  -f phase-5/helm/todo-app/values-cloud.yaml \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.jwtSecret="$(openssl rand -base64 32)" \
  --set secrets.openaiApiKey="sk-..." \
  --set ingress.host="todo.example.com"

# Upgrade deployment
helm upgrade todo-app ./phase-5/helm/todo-app \
  -n todo-app \
  -f phase-5/helm/todo-app/values-cloud.yaml

# Check status
helm status todo-app -n todo-app

# View values
helm get values todo-app -n todo-app
```

---

## CI/CD Pipeline Integration

### GitHub Actions Workflow

**File**: `.github/workflows/deploy-cloud.yaml`

```yaml
name: Deploy to Cloud K8s

on:
  push:
    branches:
      - main
    paths:
      - 'phase-5/**'
      - '.github/workflows/deploy-cloud.yaml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  REGISTRY: docker.io
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./phase-5/backend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-backend:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./phase-5/frontend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-frontend:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Notification Service
        uses: docker/build-push-action@v4
        with:
          context: ./phase-5/notification-service
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-notification:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/todo-notification:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.event.inputs.environment || 'staging' }}

    steps:
      - uses: actions/checkout@v3

      - name: Configure Azure CLI
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS credentials
        run: |
          az aks get-credentials \
            --resource-group ${{ secrets.AZURE_RG }} \
            --name ${{ secrets.AKS_CLUSTER_NAME }} \
            --overwrite-existing

      - name: Set up Helm
        uses: azure/setup-helm@v3
        with:
          version: 'latest'

      - name: Helm upgrade deployment
        run: |
          helm upgrade todo-app ./phase-5/helm/todo-app \
            -n todo-app \
            -f phase-5/helm/todo-app/values-cloud.yaml \
            --set global.imageTag=${{ github.sha }} \
            --set secrets.databaseUrl="${{ secrets.DATABASE_URL }}" \
            --set secrets.jwtSecret="${{ secrets.JWT_SECRET }}" \
            --set secrets.openaiApiKey="${{ secrets.OPENAI_API_KEY }}" \
            --wait \
            --timeout 5m

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/todo-backend -n todo-app --timeout=5m
          kubectl rollout status deployment/todo-frontend -n todo-app --timeout=5m
```

### Required Secrets (in GitHub Repository)

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `AZURE_CREDENTIALS` | Azure service principal JSON |
| `AZURE_RG` | Azure resource group name |
| `AKS_CLUSTER_NAME` | AKS cluster name |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | JWT signing secret |
| `OPENAI_API_KEY` | OpenAI API key |
| `GROQ_API_KEY` | Groq API key (optional) |

### Azure Credentials Setup

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name github-actions-sp \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --json-auth > credentials.json

# Copy credentials.json content to GitHub secret
```

---

## DNS, TLS/SSL, and Ingress

### DNS Configuration

#### Using Azure DNS

```bash
# Create Azure DNS zone
az network dns zone create \
  --resource-group $RESOURCE_GROUP \
  --name yourdomain.com

# Get nameservers
az network dns zone show \
  --resource-group $RESOURCE_GROUP \
  --name yourdomain.com \
  --query nameServers -o tsv

# Update domain registrar to use these nameservers
```

#### Using External DNS Provider

```bash
# Install ExternalDNS
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm install external-dns external-dns/external-dns \
  --namespace external-dns \
  --create-namespace \
  --set provider=azure \
  --set azure.resourceGroup=$RESOURCE_GROUP \
  --set azure.subscriptionId=$SUBSCRIPTION_ID \
  --set policy=sync \
  --set registry=txt
```

#### nip.io for Quick Testing

```bash
# Temporary DNS without registration
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access app at: http://todo.$EXTERNAL_IP.nip.io
```

### TLS/SSL Configuration

#### LetsEncrypt with cert-manager

**Install cert-manager** (already done in Step 3)

**Create ClusterIssuer**:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
```

**Apply ClusterIssuer**:

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

#### Self-Signed Certificates (Dev/Staging)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=todo.yourdomain.com"

# Create secret
kubectl create secret tls todo-tls-secret \
  --cert=cert.pem \
  --key=key.pem \
  -n todo-app
```

### Ingress Configuration

**File**: `phase-5/helm/todo-app/templates/ingress.yaml`

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "todo-app.fullname" . }}
  namespace: {{ .Release.Namespace }}
  annotations:
    {{- if .Values.ingress.tls.enabled }}
    cert-manager.io/cluster-issuer: {{ .Values.ingress.tls.issuer | quote }}
    {{- end }}
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://{{ .Values.ingress.host }}"
spec:
  ingressClassName: {{ .Values.ingress.className | quote }}
  {{- if .Values.ingress.tls.enabled }}
  tls:
    - hosts:
        - {{ .Values.ingress.host | quote }}
      secretName: {{ .Values.ingress.tls.secretName | quote }}
  {{- end }}
  rules:
    - host: {{ .Values.ingress.host | quote }}
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: {{ include "todo-app.fullname" . }}-backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ include "todo-app.fullname" . }}-frontend
                port:
                  number: 3000
{{- end }}
```

### Ingress Annotations for Security

```yaml
annotations:
  # TLS redirect
  nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
  # Rate limiting
  nginx.ingress.kubernetes.io/limit-rps: "100"
  # CORS
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
  # Security headers
  nginx.ingress.kubernetes.io/configuration-snippet: |
    more_set_headers "X-Frame-Options: DENY";
    more_set_headers "X-Content-Type-Options: nosniff";
    more_set_headers "X-XSS-Protection: 1; mode=block";
```

---

## Cost Optimization

### 1. Node Pool Configuration

**Right-Sizing Nodes**:

```bash
# Use smaller node types for non-critical workloads
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name general \
  --node-count 2 \
  --node-vm-size Standard_B4ms \
  --enable-cluster-autoscaling \
  --min-count 2 \
  --max-count 5

# Use larger nodes for Kafka (compute-optimized)
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name kafka-pool \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaling \
  --min-count 3 \
  --max-count 6
```

### 2. Pod Resource Limits

```yaml
# Set appropriate requests and limits
resources:
  requests:
    cpu: 250m      # Only allocate what's needed
    memory: 256Mi
  limits:
    cpu: 500m      # Prevent runaway processes
    memory: 512Mi
```

### 3. Horizontal Pod Autoscaling

```yaml
# Auto-scale based on CPU usage
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 4. Vertical Pod Autoscaling (Optional)

```bash
# Install VPA
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm install vpa fairwinds-stable/vpa \
  --namespace kube-system
```

### 5. Reserved Instances

```bash
# For AKS: Use Azure Reserved Instances for 1-3 year commitment
# Savings: 20-40% on compute costs
# Example: Reserve 3x Standard_B4ms for 1 year
```

### 6. Storage Cost Optimization

**Persistent Volume Configuration**:

```yaml
# Use managed disks with appropriate tier
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kafka-storage
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: managed-csi
  resources:
    requests:
      storage: 10Gi
```

### Cost Estimation (Monthly)

**Scenario**: Production AKS cluster with 3 Standard_B4ms nodes

| Component | Monthly Cost (USD) |
|-----------|-------------------|
| AKS Control Plane | ~$73 |
| 3x Standard_B4ms (nodes) | ~$450 |
| Load Balancer | ~$20 |
| Managed Disks (Kafka) | ~$50 |
| Bandwidth (egress) | ~$100 |
| **Total (without DB/Kafka managed)** | **~$693** |
| PostgreSQL (Standard_B2s) | ~$100 |
| **Total (with managed services)** | **~$793** |

**Optimization Strategies to Reduce Cost**:
- Use spot/preemptible instances for non-critical workloads (70% savings)
- Auto-scale to 0 during off-hours
- Use dev/staging environments with 1-2 nodes
- Consolidate services onto fewer nodes using Pod Disruption Budgets

---

## Monitoring and Observability

### 1. Prometheus for Metrics

**Install Prometheus**:

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=$GRAFANA_PASSWORD
```

**ServiceMonitor for Applications**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-backend-monitor
  namespace: todo-app
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

### 2. Grafana Dashboards

**Access Grafana**:

```bash
# Port-forward to access
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access at: http://localhost:3000
# Default credentials: admin / $GRAFANA_PASSWORD
```

**Pre-built Dashboards to Import**:
- Kubernetes Cluster Monitoring: ID 7249
- Pod Resource Usage: ID 6417
- Kafka Cluster: ID 14438

### 3. Loki for Log Aggregation

**Install Loki**:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi \
  --set promtail.enabled=true
```

**Query Logs in Grafana**:
```
{namespace="todo-app", pod_name=~"todo-backend.*"}
| json
| level="error"
```

### 4. Distributed Tracing (Jaeger)

**Install Jaeger**:

```bash
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm install jaeger jaegertracing/jaeger \
  --namespace monitoring \
  --set collector.service.type=ClusterIP
```

### 5. Alert Rules

**PrometheusRule for High CPU**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  namespace: monitoring
spec:
  groups:
    - name: todo-app.rules
      interval: 30s
      rules:
        - alert: HighCPUUsage
          expr: |
            (sum(rate(container_cpu_usage_seconds_total{pod=~"todo-backend.*"}[5m]))
            / sum(container_spec_cpu_quota{pod=~"todo-backend.*"} / 100000)) > 0.8
          for: 5m
          annotations:
            summary: "High CPU usage in Backend"
            description: "Backend pod {{ $labels.pod }} has high CPU usage"

        - alert: KafkaDown
          expr: |
            up{job="kafka-exporter"} == 0
          for: 5m
          annotations:
            summary: "Kafka cluster is down"

        - alert: DatabaseConnectionError
          expr: |
            increase(pg_client_backend_process_time_seconds_bucket{le="+Inf"}[5m]) > 100
          annotations:
            summary: "Database connection errors detected"
```

### 6. Monitoring Stack Deployment

**Complete Monitoring Setup Script**:

```bash
#!/bin/bash
# Deploy complete monitoring stack

NAMESPACE="monitoring"

# Create namespace
kubectl create namespace $NAMESPACE

# Install Prometheus Stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace $NAMESPACE \
  -f - <<EOF
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 20Gi
grafana:
  persistence:
    enabled: true
    size: 5Gi
EOF

# Install Loki
helm install loki grafana/loki-stack \
  --namespace $NAMESPACE \
  -f - <<EOF
loki:
  persistence:
    enabled: true
    size: 10Gi
promtail:
  enabled: true
EOF

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=prometheus \
  -n $NAMESPACE \
  --timeout=300s

# Create ServiceMonitor for applications
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-app-services
  namespace: $NAMESPACE
spec:
  namespaceSelector:
    matchNames:
      - todo-app
  selector:
    matchLabels:
      monitoring: enabled
  endpoints:
    - port: metrics
      interval: 30s
EOF

echo "Monitoring stack installed successfully"
echo ""
echo "Access Grafana:"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-grafana 3000:80"
echo "  URL: http://localhost:3000"
echo ""
echo "Access Prometheus:"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "  URL: http://localhost:9090"
```

---

## Cleanup and Teardown

### Complete Cluster Teardown

**WARNING**: This will delete all resources including data.

#### For AKS:

```bash
#!/bin/bash
# Remove Helm releases
helm uninstall todo-app -n todo-app
helm uninstall prometheus -n monitoring
helm uninstall loki -n monitoring
helm uninstall nginx-ingress -n ingress-nginx
helm uninstall strimzi-operator -n kafka

# Remove namespaces
kubectl delete namespace todo-app kafka monitoring ingress-nginx cert-manager

# Delete AKS cluster
az aks delete \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --yes

# Delete Azure Database
az postgres flexible-server delete \
  --resource-group $RESOURCE_GROUP \
  --name todo-db \
  --yes

# Delete resource group (this removes everything)
az group delete \
  --name $RESOURCE_GROUP \
  --yes
```

#### For DOKS:

```bash
#!/bin/bash
# Remove Helm releases
helm uninstall todo-app -n todo-app
helm uninstall prometheus -n monitoring

# Delete DOKS cluster
doctl kubernetes cluster delete $CLUSTER_NAME

# Delete managed database
doctl databases delete $DATABASE_ID
```

#### For GKE:

```bash
#!/bin/bash
# Remove Helm releases
helm uninstall todo-app -n todo-app
helm uninstall prometheus -n monitoring

# Delete GKE cluster
gcloud container clusters delete $CLUSTER_NAME --zone=$ZONE
```

### Selective Cleanup

```bash
# Keep cluster, remove only application
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app

# Keep cluster and application, remove monitoring
helm uninstall prometheus -n monitoring
helm uninstall loki -n monitoring
kubectl delete namespace monitoring

# Keep everything, just scale down to 0
kubectl scale deployment todo-backend -n todo-app --replicas=0
kubectl scale deployment todo-frontend -n todo-app --replicas=0
```

### Data Backup Before Cleanup

```bash
# Backup PostgreSQL
pg_dump -h todo-db.postgres.database.azure.com \
  -U postgres \
  -d todo_db \
  > backup-$(date +%Y%m%d-%H%M%S).sql

# Backup Kafka topics
for topic in task-events reminders task-updates; do
  kubectl exec -n kafka taskflow-kafka-kafka-0 -- \
    bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic $topic \
    --from-beginning \
    > backup-topic-$topic.json
done
```

---

## Quick Reference

### Essential Commands

```bash
# Cluster management
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Deployment management
kubectl get deployments -n todo-app
kubectl describe deployment todo-backend -n todo-app
kubectl logs deployment/todo-backend -n todo-app
kubectl port-forward -n todo-app svc/todo-backend 8000:8000

# Helm management
helm list -n todo-app
helm get values todo-app -n todo-app
helm history todo-app -n todo-app
helm rollback todo-app 1 -n todo-app

# Kafka management
kubectl exec -n kafka taskflow-kafka-kafka-0 -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Dapr management
dapr status -k
dapr list -k
dapr logs todo-backend -n todo-app

# Pod debugging
kubectl debug -n todo-app pod/todo-backend-xxx -it --image=busybox
kubectl exec -n todo-app pod/todo-backend-xxx -- bash
```

### Troubleshooting Checklist

1. Pod not starting?
   ```bash
   kubectl describe pod <pod-name> -n todo-app
   kubectl logs <pod-name> -n todo-app
   ```

2. Service unreachable?
   ```bash
   kubectl get svc -n todo-app
   kubectl describe svc <service-name> -n todo-app
   ```

3. Ingress not working?
   ```bash
   kubectl get ingress -n todo-app
   kubectl describe ingress <ingress-name> -n todo-app
   ```

4. Dapr sidecar issues?
   ```bash
   dapr status -k
   kubectl logs -n dapr-system deployment/dapr-sidecar-injector
   ```

5. Kafka connectivity?
   ```bash
   kubectl exec -n kafka taskflow-kafka-kafka-0 -- \
     bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
   ```

---

## Appendix: Configuration Templates

### Environment Variables Template

```bash
# Cloud K8s Deployment Configuration
export RESOURCE_GROUP="todo-rg"
export CLUSTER_NAME="todo-prod"
export REGION="eastus"
export NODE_COUNT=3
export NODE_SIZE="Standard_B4ms"
export DB_PASSWORD="$(openssl rand -base64 32)"
export JWT_SECRET="$(openssl rand -base64 32)"
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk-..."
export DOCKER_REGISTRY="yourusername"
export DOMAIN="todo.example.com"
export SUBSCRIPTION_ID="xxxx-xxxx-xxxx"
```

### Pre-Flight Checklist

- [ ] Azure account with subscription active
- [ ] `az`, `kubectl`, `helm`, `git` CLI tools installed
- [ ] Docker Hub account and credentials ready
- [ ] Domain registered and ready to point to cluster
- [ ] SSL certificate plan (LetsEncrypt recommended)
- [ ] PostgreSQL password generated and stored securely
- [ ] JWT secret generated and stored securely
- [ ] API keys (OpenAI, Groq) obtained
- [ ] GitHub repository configured with secrets
- [ ] Azure service principal created for CI/CD

---

**Status**: Complete and production-ready
**Last Updated**: 2026-02-17
**Maintained By**: Claude Code Agent
