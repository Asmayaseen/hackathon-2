#!/bin/bash
# =============================================================================
# Phase 4: Deployment Verification Script
# Evolution Todo - Verify Kubernetes Deployment
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
RELEASE_NAME="todo-app"
NAMESPACE="todo-app"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}=== Phase 4: Deployment Verification ===${NC}"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Function to check and report
check() {
    local name=$1
    local command=$2

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}: $name"
        ((PASS_COUNT++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $name"
        ((FAIL_COUNT++))
        return 1
    fi
}

# -----------------------------------------------------------------------------
# 1. Cluster Checks
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/5] Cluster Status${NC}"

check "Minikube is running" "minikube status | grep -q 'Running'"
check "kubectl can connect" "kubectl cluster-info"
check "Namespace exists" "kubectl get namespace $NAMESPACE"

# -----------------------------------------------------------------------------
# 2. Pod Checks
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/5] Pod Status${NC}"

check "Backend pod exists" "kubectl get pods -n $NAMESPACE -l app=todo-app-backend -o name | grep -q pod"
check "Frontend pod exists" "kubectl get pods -n $NAMESPACE -l app=todo-app-frontend -o name | grep -q pod"

# Check pod status
BACKEND_STATUS=$(kubectl get pods -n $NAMESPACE -l app=todo-app-backend -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Unknown")
FRONTEND_STATUS=$(kubectl get pods -n $NAMESPACE -l app=todo-app-frontend -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Unknown")

check "Backend pod is Running" "[ '$BACKEND_STATUS' = 'Running' ]"
check "Frontend pod is Running" "[ '$FRONTEND_STATUS' = 'Running' ]"

# -----------------------------------------------------------------------------
# 3. Service Checks
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/5] Service Status${NC}"

check "Backend service exists" "kubectl get svc ${RELEASE_NAME}-backend -n $NAMESPACE"
check "Frontend service exists" "kubectl get svc ${RELEASE_NAME}-frontend -n $NAMESPACE"

# -----------------------------------------------------------------------------
# 4. Health Endpoint Checks
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/5] Health Endpoints${NC}"

# Start port-forward in background
echo "Starting port-forward for health checks..."
kubectl port-forward svc/${RELEASE_NAME}-backend $BACKEND_PORT:$BACKEND_PORT -n $NAMESPACE &> /dev/null &
PF_PID=$!
sleep 3

# Check health endpoint
if curl -s http://localhost:$BACKEND_PORT/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ PASS${NC}: Backend /health returns healthy"
    ((PASS_COUNT++))
else
    echo -e "${RED}✗ FAIL${NC}: Backend /health check failed"
    ((FAIL_COUNT++))
fi

# Check ready endpoint
if curl -s http://localhost:$BACKEND_PORT/ready | grep -q "ready"; then
    echo -e "${GREEN}✓ PASS${NC}: Backend /ready returns ready"
    ((PASS_COUNT++))
else
    echo -e "${YELLOW}⚠ WARN${NC}: Backend /ready check failed (DB may not be connected)"
fi

# Cleanup port-forward
kill $PF_PID 2>/dev/null || true

# -----------------------------------------------------------------------------
# 5. Resource Checks
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/5] Resource Status${NC}"

check "ConfigMap exists" "kubectl get configmap ${RELEASE_NAME}-config -n $NAMESPACE"
check "Secret exists" "kubectl get secret ${RELEASE_NAME}-secrets -n $NAMESPACE"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}=== Verification Summary ===${NC}"
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed! Deployment is healthy.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}Some checks failed. Review the issues above.${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# Additional Info
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}=== Deployment Details ===${NC}"
echo -e "\nPods:"
kubectl get pods -n $NAMESPACE -o wide

echo -e "\nServices:"
kubectl get svc -n $NAMESPACE

echo -e "\nRecent Events:"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -5
