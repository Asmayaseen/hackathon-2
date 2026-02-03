#!/bin/bash
# T5-101 to T5-104: Local Minikube Setup Script
# Sets up Kafka (Strimzi) and Dapr on Minikube

set -e

echo "=== Phase 5: Local Kubernetes Setup ==="

# Check prerequisites
command -v minikube >/dev/null 2>&1 || { echo "minikube required but not installed."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl required but not installed."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "helm required but not installed."; exit 1; }

# Start Minikube if not running
if ! minikube status | grep -q "Running"; then
    echo "Starting Minikube..."
    minikube start --memory=8192 --cpus=4 --driver=docker
fi

# Point docker to minikube
echo "Configuring Docker to use Minikube..."
eval $(minikube docker-env)

# === Install Strimzi Kafka Operator ===
echo ""
echo "=== Installing Strimzi Kafka Operator ==="
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Apply Strimzi operator
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
echo "Waiting for Strimzi operator..."
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

echo "✅ Strimzi Operator installed"

# === Deploy Kafka Cluster ===
echo ""
echo "=== Deploying Kafka Cluster ==="
kubectl apply -f phase-5/kafka/kafka-cluster.yaml

# Wait for Kafka (this takes a while)
echo "Waiting for Kafka cluster (this may take 2-3 minutes)..."
sleep 30
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=600s || {
    echo "Kafka cluster not ready yet, checking status..."
    kubectl get kafka -n kafka
    kubectl get pods -n kafka
}

echo "✅ Kafka Cluster deployed"

# === Create Kafka Topics ===
echo ""
echo "=== Creating Kafka Topics ==="
kubectl apply -f phase-5/kafka/topics.yaml

# Wait for topics
sleep 10
kubectl get kafkatopic -n kafka

echo "✅ Kafka Topics created"

# === Install Dapr ===
echo ""
echo "=== Installing Dapr ==="
command -v dapr >/dev/null 2>&1 || {
    echo "Installing Dapr CLI..."
    wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
}

# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr
echo "Verifying Dapr installation..."
dapr status -k

echo "✅ Dapr installed"

# === Apply Dapr Components ===
echo ""
echo "=== Applying Dapr Components ==="
kubectl apply -f phase-5/dapr-components/

echo "✅ Dapr components configured"

# === Build Docker Images ===
echo ""
echo "=== Building Docker Images ==="
echo "Building backend..."
docker build -t todo-backend:latest ./phase-4/backend/

echo "Building frontend..."
docker build -t todo-frontend:latest ./phase-4/frontend/ --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000

echo "Building notification service..."
docker build -t todo-notification:latest ./phase-5/notification-service/

echo "✅ Docker images built"

# === Summary ===
echo ""
echo "=========================================="
echo "✅ Phase 5 Local Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create values-local.yaml with your secrets"
echo "2. Deploy with Helm:"
echo "   helm install todo-app ./phase-5/helm/todo-app -f values-local.yaml"
echo ""
echo "3. Access the app:"
echo "   minikube service todo-app-frontend"
echo ""
echo "Useful commands:"
echo "  kubectl get pods                    # Check pod status"
echo "  kubectl logs -l app=todo-app-backend -f  # View backend logs"
echo "  dapr status -k                      # Check Dapr status"
echo "  kubectl get kafkatopic -n kafka     # Check Kafka topics"
