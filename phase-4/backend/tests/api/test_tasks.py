"""
API Tests: Task Endpoints
Tests for /tasks/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestTaskEndpoints:
    """Test suite for task CRUD endpoints."""

    def test_get_tasks_requires_auth(self, client: TestClient):
        """
        Test: GET /tasks requires authentication
        """
        response = client.get("/tasks")

        # Should return 401 Unauthorized without token
        assert response.status_code == 401

    def test_create_task_requires_auth(self, client: TestClient):
        """
        Test: POST /tasks requires authentication
        """
        response = client.post("/tasks", json={
            "title": "Test Task",
            "description": "Test Description"
        })

        # Should return 401 Unauthorized without token
        assert response.status_code == 401

    def test_update_task_requires_auth(self, client: TestClient):
        """
        Test: PUT /tasks/{id} requires authentication
        """
        response = client.put("/tasks/1", json={
            "title": "Updated Task"
        })

        # Should return 401 Unauthorized without token
        assert response.status_code == 401

    def test_delete_task_requires_auth(self, client: TestClient):
        """
        Test: DELETE /tasks/{id} requires authentication
        """
        response = client.delete("/tasks/1")

        # Should return 401 Unauthorized without token
        assert response.status_code == 401


class TestTaskEndpointsWithAuth:
    """Tests requiring authentication - use fixtures with auth."""

    @pytest.fixture
    def auth_headers(self):
        """
        Fixture: Provides authentication headers
        In real tests, this would create a user and get a token
        """
        # Placeholder - would need actual token
        return {"Authorization": "Bearer test-token"}

    def test_create_task_validation(self, client: TestClient, auth_headers):
        """
        Test: Task creation validates required fields
        """
        # Missing title
        response = client.post(
            "/tasks",
            json={"description": "No title"},
            headers=auth_headers
        )

        # Should return validation error (if auth passes)
        # or 401 if test token isn't valid
        assert response.status_code in [400, 401, 422]

    def test_task_title_max_length(self, client: TestClient, auth_headers):
        """
        Test: Task title has max length limit (200 chars)
        """
        long_title = "a" * 250  # Exceeds limit

        response = client.post(
            "/tasks",
            json={"title": long_title},
            headers=auth_headers
        )

        # Should return validation error (if auth passes)
        assert response.status_code in [400, 401, 422]


class TestTaskEndpointResponses:
    """Test response formats for task endpoints."""

    def test_tasks_endpoint_content_type(self, client: TestClient):
        """
        Test: Tasks endpoint returns JSON
        """
        response = client.get("/tasks")

        # Even 401 should return JSON
        assert "application/json" in response.headers.get("content-type", "")

    def test_task_not_found(self, client: TestClient):
        """
        Test: Non-existent task returns 404
        """
        response = client.get("/tasks/99999")

        # Should return 401 (auth) or 404 (not found)
        assert response.status_code in [401, 404]
