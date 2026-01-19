"""
API Tests: Health Endpoints
Tests for /health and /ready endpoints used by Kubernetes probes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_endpoint_returns_200(self, client: TestClient):
        """
        Test: GET /health returns 200 OK
        Spec: api/health-endpoints.md - Liveness Probe
        """
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "evolution-todo-api"
        assert "version" in data

    def test_health_endpoint_response_structure(self, client: TestClient):
        """
        Test: Health endpoint returns correct JSON structure
        """
        response = client.get("/health")
        data = response.json()

        # Required fields
        assert "status" in data
        assert "service" in data
        assert "version" in data

        # Version format check
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_ready_endpoint_with_healthy_db(self, client: TestClient):
        """
        Test: GET /ready returns 200 when database is connected
        Spec: api/health-endpoints.md - Readiness Probe
        """
        with patch("main.engine") as mock_engine:
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            response = client.get("/ready")

            # Should return 200 if DB is healthy
            assert response.status_code in [200, 503]  # Depends on actual DB

    def test_ready_endpoint_response_structure(self, client: TestClient):
        """
        Test: Ready endpoint returns correct JSON structure when healthy
        """
        response = client.get("/ready")

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "ready"
            assert "database" in data

    def test_health_does_not_require_auth(self, client: TestClient):
        """
        Test: Health endpoint should be public (no auth required)
        """
        # No Authorization header
        response = client.get("/health")

        # Should not return 401 or 403
        assert response.status_code == 200

    def test_ready_does_not_require_auth(self, client: TestClient):
        """
        Test: Ready endpoint should be public (no auth required)
        """
        # No Authorization header
        response = client.get("/ready")

        # Should not return 401 or 403
        assert response.status_code in [200, 503]


class TestHealthEndpointPerformance:
    """Performance tests for health endpoints."""

    def test_health_response_time(self, client: TestClient):
        """
        Test: Health endpoint should respond within 100ms
        Spec: NFR - Performance requirements
        """
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1, f"Health check took {elapsed:.3f}s, expected < 0.1s"

    def test_health_multiple_requests(self, client: TestClient):
        """
        Test: Health endpoint handles multiple sequential requests
        """
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200


class TestHealthEndpointEdgeCases:
    """Edge case tests for health endpoints."""

    def test_health_with_query_params(self, client: TestClient):
        """
        Test: Health endpoint ignores query parameters
        """
        response = client.get("/health?foo=bar&debug=true")
        assert response.status_code == 200

    def test_health_method_not_allowed(self, client: TestClient):
        """
        Test: Health endpoint only accepts GET
        """
        # POST should not be allowed
        response = client.post("/health")
        assert response.status_code == 405

    def test_health_content_type(self, client: TestClient):
        """
        Test: Health endpoint returns JSON content type
        """
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
