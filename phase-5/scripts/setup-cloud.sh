#!/bin/bash
# T5-700: Cloud Kubernetes Setup Script
# Sets up Kafka (Strimzi) and Dapr on cloud K8s (DOKS/AKS/GKE)

set -e

# Configuration (override via environment)
CLUSTER_NAME=${CLUSTER_NAME:-"todo-prod"}
REGION=${REGION:-"nyc1"}
NODE_COUNT=${NODE_COUNT:-2}
NODE_SIZE=${NODE_SIZE:-"s-2vcpu-4gb"}

echo "=== Phase 5: Cloud Kubernetes Setup ==="

# Check cloud CLI
check_cloud_cli() {
    if command -v doctl >/dev/null 2>&1; then
        echo "Using DigitalOcean DOKS"
        CLOUD="doks"
    elif command -v az >/dev/null 2>&1; then
        echo "Using Azure AKS"
        CLOUD="aks"
    elif command -v gcloud >/dev/null 2>&1; then
        echo "Using Google GKE"
        CLOUD="gke"
    else
        echo "No cloud CLI found. Install one of: doctl, az, gcloud"
        exit 1
    fi
}

# Create cluster based on cloud provider
create_cluster() {
    case $CLOUD in
        doks)
            echo "Creating DOKS cluster..."
            doctl kubernetes cluster create $CLUSTER_NAME \
                --region $REGION \
                --node-pool "name=default;size=$NODE_SIZE;count=$NODE_COUNT" \
                --wait

            # Get kubeconfig
            doctl kubernetes cluster kubeconfig save $CLUSTER_NAME
            ;;

        aks)
            echo "Creating AKS cluster..."
            az aks create \
                --resource-group ${RESOURCE_GROUP:-"todo-rg"} \
                --name $CLUSTER_NAME \
                --node-count $NODE_COUNT \
                --generate-ssh-keys

            # Get kubeconfig
            az aks get-credentials --resource-group ${RESOURCE_GROUP:-"todo-rg"} --name $CLUSTER_NAME
            ;;

        gke)
            echo "Creating GKE cluster..."
            gcloud container clusters create $CLUSTER_NAME \
                --zone ${ZONE:-"us-central1-a"} \
                --num-nodes $NODE_COUNT

            # Get kubeconfig
            gcloud container clusters get-credentials $CLUSTER_NAME --zone ${ZONE:-"us-central1-a"}
            ;;
    esac
}

# Main setup
check_cloud_cli

echo ""
echo "=== Creating Kubernetes Cluster ==="
create_cluster

# Verify cluster
echo ""
echo "=== Verifying Cluster ==="
kubectl cluster-info
kubectl get nodes

# Install Strimzi
echo ""
echo "=== Installing Strimzi Kafka Operator ==="
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka
echo ""
echo "=== Deploying Kafka Cluster ==="
kubectl apply -f phase-5/kafka/kafka-cluster.yaml
echo "Waiting for Kafka cluster..."
sleep 60
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=600s

# Create topics
kubectl apply -f phase-5/kafka/topics.yaml

# Install Dapr
echo ""
echo "=== Installing Dapr ==="
dapr init -k --wait
dapr status -k

# Apply Dapr components
echo ""
echo "=== Applying Dapr Components ==="
kubectl apply -f phase-5/dapr-components/

# Install nginx ingress
echo ""
echo "=== Installing Nginx Ingress Controller ==="
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=300s

# Get external IP
echo ""
echo "Waiting for external IP..."
sleep 30
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"

# Summary
echo ""
echo "=========================================="
echo "✅ Cloud Kubernetes Setup Complete!"
echo "=========================================="
echo ""
echo "External IP: $EXTERNAL_IP"
echo ""
echo "Next steps:"
echo "1. Create values-cloud.yaml with secrets and set:"
echo "   ingress.enabled: true"
echo "   ingress.host: todo.$EXTERNAL_IP.nip.io"
echo ""
echo "2. Deploy with Helm:"
echo "   helm install todo-app ./phase-5/helm/todo-app -f values-cloud.yaml"
echo ""
echo "3. Access the app:"
echo "   http://todo.$EXTERNAL_IP.nip.io"
echo ""
echo "To tear down:"
case $CLOUD in
    doks) echo "   doctl kubernetes cluster delete $CLUSTER_NAME" ;;
    aks)  echo "   az aks delete --resource-group ${RESOURCE_GROUP:-"todo-rg"} --name $CLUSTER_NAME" ;;
    gke)  echo "   gcloud container clusters delete $CLUSTER_NAME" ;;
esac
