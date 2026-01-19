# =============================================================================
# Phase 4: Minikube Deployment Script (PowerShell)
# Evolution Todo - Local Kubernetes Deployment
# =============================================================================

$ErrorActionPreference = "Stop"

# Configuration
$RELEASE_NAME = "todo-app"
$NAMESPACE = "todo-app"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "=== Phase 4: Minikube Deployment ===" -ForegroundColor Blue
Write-Host "Project Directory: $PROJECT_DIR"

# -----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# -----------------------------------------------------------------------------
Write-Host "`n[1/6] Checking prerequisites..." -ForegroundColor Yellow

function Test-Command {
    param($Command)
    if (!(Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $Command is not installed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ $Command found" -ForegroundColor Green
}

Test-Command "docker"
Test-Command "minikube"
Test-Command "kubectl"
Test-Command "helm"

# -----------------------------------------------------------------------------
# Step 2: Start Minikube
# -----------------------------------------------------------------------------
Write-Host "`n[2/6] Starting Minikube..." -ForegroundColor Yellow

$minikubeStatus = minikube status 2>&1
if ($minikubeStatus -match "Running") {
    Write-Host "✓ Minikube is already running" -ForegroundColor Green
} else {
    Write-Host "Starting Minikube with 4 CPUs and 8GB memory..."
    minikube start --cpus 4 --memory 8192 --driver=docker
}

# Verify cluster
kubectl cluster-info

# -----------------------------------------------------------------------------
# Step 3: Configure Docker Environment
# -----------------------------------------------------------------------------
Write-Host "`n[3/6] Configuring Docker environment..." -ForegroundColor Yellow

# Set Docker environment for Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
Write-Host "✓ Docker configured to use Minikube's daemon" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 4: Build Docker Images
# -----------------------------------------------------------------------------
Write-Host "`n[4/6] Building Docker images..." -ForegroundColor Yellow

Write-Host "Building backend image..."
docker build -t todo-backend:latest "$PROJECT_DIR\backend"
Write-Host "✓ Backend image built" -ForegroundColor Green

Write-Host "Building frontend image..."
docker build -t todo-frontend:latest "$PROJECT_DIR\frontend"
Write-Host "✓ Frontend image built" -ForegroundColor Green

# Verify images
Write-Host "`nDocker images:"
docker images | Select-String "todo"

# -----------------------------------------------------------------------------
# Step 5: Create Namespace and Deploy with Helm
# -----------------------------------------------------------------------------
Write-Host "`n[5/6] Deploying with Helm..." -ForegroundColor Yellow

# Create namespace if not exists
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
Write-Host "✓ Namespace '$NAMESPACE' ready" -ForegroundColor Green

# Check if release exists
$existingRelease = helm list -n $NAMESPACE 2>&1 | Select-String $RELEASE_NAME
if ($existingRelease) {
    Write-Host "Upgrading existing release..."
    helm upgrade $RELEASE_NAME "$PROJECT_DIR\helm\todo-app" `
        -n $NAMESPACE `
        -f "$PROJECT_DIR\helm\todo-app\values.yaml" `
        --set backend.image.pullPolicy=Never `
        --set frontend.image.pullPolicy=Never
} else {
    Write-Host "Installing new release..."
    helm install $RELEASE_NAME "$PROJECT_DIR\helm\todo-app" `
        -n $NAMESPACE `
        -f "$PROJECT_DIR\helm\todo-app\values.yaml" `
        --set backend.image.pullPolicy=Never `
        --set frontend.image.pullPolicy=Never
}

Write-Host "✓ Helm release deployed" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 6: Wait for Pods and Verify
# -----------------------------------------------------------------------------
Write-Host "`n[6/6] Waiting for pods to be ready..." -ForegroundColor Yellow

Write-Host "Waiting for backend pod..."
kubectl wait --for=condition=ready pod -l app=todo-app-backend -n $NAMESPACE --timeout=120s 2>&1

Write-Host "Waiting for frontend pod..."
kubectl wait --for=condition=ready pod -l app=todo-app-frontend -n $NAMESPACE --timeout=120s 2>&1

# Show status
Write-Host "`n=== Deployment Status ===" -ForegroundColor Blue
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# -----------------------------------------------------------------------------
# Access Instructions
# -----------------------------------------------------------------------------
Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "`nTo access the application:"
Write-Host "  # Option 1: Port Forward" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/$RELEASE_NAME-backend 8000:8000 -n $NAMESPACE"
Write-Host "  kubectl port-forward svc/$RELEASE_NAME-frontend 3000:3000 -n $NAMESPACE"
Write-Host ""
Write-Host "  # Option 2: Minikube Service" -ForegroundColor Yellow
Write-Host "  minikube service $RELEASE_NAME-frontend -n $NAMESPACE"
Write-Host ""
Write-Host "  # Verify Health" -ForegroundColor Yellow
Write-Host "  Invoke-RestMethod http://localhost:8000/health"
Write-Host ""
Write-Host "Run " -NoNewline
Write-Host ".\scripts\verify-deployment.ps1" -ForegroundColor Blue -NoNewline
Write-Host " to verify the deployment."
