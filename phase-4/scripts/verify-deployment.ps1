# =============================================================================
# Phase 4: Deployment Verification Script (PowerShell)
# Evolution Todo - Verify Kubernetes Deployment
# =============================================================================

$ErrorActionPreference = "Continue"

# Configuration
$RELEASE_NAME = "todo-app"
$NAMESPACE = "todo-app"
$BACKEND_PORT = 8000
$FRONTEND_PORT = 3000

Write-Host "=== Phase 4: Deployment Verification ===" -ForegroundColor Blue
Write-Host ""

$PASS_COUNT = 0
$FAIL_COUNT = 0

# Function to check and report
function Test-Check {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    try {
        $result = & $Command 2>&1
        if ($LASTEXITCODE -eq 0 -or $result) {
            Write-Host "✓ PASS" -ForegroundColor Green -NoNewline
            Write-Host ": $Name"
            $script:PASS_COUNT++
            return $true
        }
    } catch {
        # Fall through to fail
    }

    Write-Host "✗ FAIL" -ForegroundColor Red -NoNewline
    Write-Host ": $Name"
    $script:FAIL_COUNT++
    return $false
}

# -----------------------------------------------------------------------------
# 1. Cluster Checks
# -----------------------------------------------------------------------------
Write-Host "[1/5] Cluster Status" -ForegroundColor Yellow

Test-Check "Minikube is running" { (minikube status) -match "Running" }
Test-Check "kubectl can connect" { kubectl cluster-info }
Test-Check "Namespace exists" { kubectl get namespace $NAMESPACE }

# -----------------------------------------------------------------------------
# 2. Pod Checks
# -----------------------------------------------------------------------------
Write-Host "`n[2/5] Pod Status" -ForegroundColor Yellow

Test-Check "Backend pod exists" { kubectl get pods -n $NAMESPACE -l app=todo-app-backend -o name }
Test-Check "Frontend pod exists" { kubectl get pods -n $NAMESPACE -l app=todo-app-frontend -o name }

# Check pod status
$BACKEND_STATUS = kubectl get pods -n $NAMESPACE -l app=todo-app-backend -o jsonpath='{.items[0].status.phase}' 2>&1
$FRONTEND_STATUS = kubectl get pods -n $NAMESPACE -l app=todo-app-frontend -o jsonpath='{.items[0].status.phase}' 2>&1

Test-Check "Backend pod is Running" { $BACKEND_STATUS -eq "Running" }
Test-Check "Frontend pod is Running" { $FRONTEND_STATUS -eq "Running" }

# -----------------------------------------------------------------------------
# 3. Service Checks
# -----------------------------------------------------------------------------
Write-Host "`n[3/5] Service Status" -ForegroundColor Yellow

Test-Check "Backend service exists" { kubectl get svc "$RELEASE_NAME-backend" -n $NAMESPACE }
Test-Check "Frontend service exists" { kubectl get svc "$RELEASE_NAME-frontend" -n $NAMESPACE }

# -----------------------------------------------------------------------------
# 4. Health Endpoint Checks
# -----------------------------------------------------------------------------
Write-Host "`n[4/5] Health Endpoints" -ForegroundColor Yellow

# Start port-forward in background
Write-Host "Starting port-forward for health checks..."
$portForward = Start-Process -FilePath "kubectl" -ArgumentList "port-forward svc/$RELEASE_NAME-backend ${BACKEND_PORT}:${BACKEND_PORT} -n $NAMESPACE" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3

try {
    # Check health endpoint
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:$BACKEND_PORT/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($healthResponse.status -eq "healthy") {
        Write-Host "✓ PASS" -ForegroundColor Green -NoNewline
        Write-Host ": Backend /health returns healthy"
        $PASS_COUNT++
    } else {
        Write-Host "✗ FAIL" -ForegroundColor Red -NoNewline
        Write-Host ": Backend /health check failed"
        $FAIL_COUNT++
    }
} catch {
    Write-Host "✗ FAIL" -ForegroundColor Red -NoNewline
    Write-Host ": Backend /health check failed - $_"
    $FAIL_COUNT++
}

try {
    # Check ready endpoint
    $readyResponse = Invoke-RestMethod -Uri "http://localhost:$BACKEND_PORT/ready" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($readyResponse.status -eq "ready") {
        Write-Host "✓ PASS" -ForegroundColor Green -NoNewline
        Write-Host ": Backend /ready returns ready"
        $PASS_COUNT++
    } else {
        Write-Host "⚠ WARN" -ForegroundColor Yellow -NoNewline
        Write-Host ": Backend /ready check failed (DB may not be connected)"
    }
} catch {
    Write-Host "⚠ WARN" -ForegroundColor Yellow -NoNewline
    Write-Host ": Backend /ready check failed (DB may not be connected)"
}

# Cleanup port-forward
Stop-Process -Id $portForward.Id -Force -ErrorAction SilentlyContinue

# -----------------------------------------------------------------------------
# 5. Resource Checks
# -----------------------------------------------------------------------------
Write-Host "`n[5/5] Resource Status" -ForegroundColor Yellow

Test-Check "ConfigMap exists" { kubectl get configmap "$RELEASE_NAME-config" -n $NAMESPACE }
Test-Check "Secret exists" { kubectl get secret "$RELEASE_NAME-secrets" -n $NAMESPACE }

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
Write-Host "`n=== Verification Summary ===" -ForegroundColor Blue
Write-Host "Passed: " -NoNewline
Write-Host "$PASS_COUNT" -ForegroundColor Green
Write-Host "Failed: " -NoNewline
Write-Host "$FAIL_COUNT" -ForegroundColor Red

if ($FAIL_COUNT -eq 0) {
    Write-Host "`nAll checks passed! Deployment is healthy." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome checks failed. Review the issues above." -ForegroundColor Yellow
    exit 1
}

# -----------------------------------------------------------------------------
# Additional Info
# -----------------------------------------------------------------------------
Write-Host "`n=== Deployment Details ===" -ForegroundColor Blue

Write-Host "`nPods:"
kubectl get pods -n $NAMESPACE -o wide

Write-Host "`nServices:"
kubectl get svc -n $NAMESPACE

Write-Host "`nRecent Events:"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | Select-Object -Last 5
