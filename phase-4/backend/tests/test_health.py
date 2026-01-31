"""
Phase 4: Backend Health Check Tests
Tests for /health and /ready endpoints required for Kubernetes probes
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test suite for Kubernetes health check endpoints"""

    def test_health_endpoint_returns_200(self):
        """Test /health returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_healthy_status(self):
        """Test /health returns healthy status in response body"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_ready_endpoint_returns_200(self):
        """Test /ready returns 200 OK when app is ready"""
        response = client.get("/ready")
        assert response.status_code == 200

    def test_ready_endpoint_returns_ready_status(self):
        """Test /ready returns ready status"""
        response = client.get("/ready")
        data = response.json()
        assert data["status"] == "ready"


class TestAPIEndpoints:
    """Test suite for core API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200

    def test_docs_endpoint_available(self):
        """Test OpenAPI docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_available(self):
        """Test OpenAPI JSON schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    def test_signup_endpoint_exists(self):
        """Test /api/auth/signup endpoint is accessible"""
        response = client.post("/api/auth/signup", json={
            "email": "testuser_signup@example.com",
            "password": "testpassword123",
            "name": "Test User"
        })
        # Should return 200/201 (success) or 400 (user exists) - not 404
        assert response.status_code in [200, 201, 400, 422]

    def test_signin_endpoint_exists(self):
        """Test /api/auth/signin endpoint is accessible"""
        # First signup a user
        client.post("/api/auth/signup", json={
            "email": "testuser_signin@example.com",
            "password": "testpassword123",
            "name": "Test User"
        })
        # Then try signin
        response = client.post("/api/auth/signin", json={
            "email": "testuser_signin@example.com",
            "password": "testpassword123"
        })
        # Should return 200 (success) or 401 (invalid) - not 404
        assert response.status_code in [200, 401, 422]

    def test_me_endpoint_is_accessible(self):
        """Test /api/auth/me endpoint exists"""
        response = client.get("/api/auth/me")
        # Endpoint exists (200 or 401 depending on auth implementation)
        assert response.status_code in [200, 401]


class TestTaskEndpoints:
    """Test suite for task CRUD endpoints (require user_id)"""

    def test_tasks_endpoint_with_invalid_user(self):
        """Test /api/{user_id}/tasks returns 401/404 for invalid user"""
        response = client.get("/api/999/tasks")
        # Should return 401 (no auth) or 404 (user not found)
        assert response.status_code in [401, 404]

    def test_task_routes_exist_in_openapi(self):
        """Test task routes are documented in OpenAPI spec"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        paths = data.get("paths", {})
        # Check that task-related paths exist
        task_paths = [p for p in paths.keys() if "tasks" in p]
        assert len(task_paths) > 0, "Task routes should be in OpenAPI spec"
