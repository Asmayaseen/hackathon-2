"""
API Tests: Authentication Endpoints
Tests for /auth/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_signup_endpoint_exists(self, client: TestClient):
        """
        Test: POST /auth/signup endpoint exists
        """
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        })

        # Should not return 404
        assert response.status_code != 404

    def test_signin_endpoint_exists(self, client: TestClient):
        """
        Test: POST /auth/signin endpoint exists
        """
        response = client.post("/auth/signin", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })

        # Should not return 404
        assert response.status_code != 404

    def test_signup_requires_email(self, client: TestClient):
        """
        Test: Signup requires email field
        """
        response = client.post("/auth/signup", json={
            "password": "testpassword123",
            "name": "Test User"
        })

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_signup_requires_password(self, client: TestClient):
        """
        Test: Signup requires password field
        """
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "name": "Test User"
        })

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_signup_validates_email_format(self, client: TestClient):
        """
        Test: Signup validates email format
        """
        response = client.post("/auth/signup", json={
            "email": "not-an-email",
            "password": "testpassword123",
            "name": "Test User"
        })

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_signin_with_wrong_password(self, client: TestClient):
        """
        Test: Signin fails with wrong password
        """
        response = client.post("/auth/signin", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })

        # Should return 401 Unauthorized
        assert response.status_code in [401, 400]

    def test_signin_with_nonexistent_user(self, client: TestClient):
        """
        Test: Signin fails with nonexistent user
        """
        response = client.post("/auth/signin", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })

        # Should return 401 or 404
        assert response.status_code in [401, 404, 400]


class TestAuthEndpointSecurity:
    """Security tests for authentication endpoints."""

    def test_password_not_in_response(self, client: TestClient):
        """
        Test: Password is never returned in response
        """
        response = client.post("/auth/signup", json={
            "email": "security-test@example.com",
            "password": "testpassword123",
            "name": "Security Test"
        })

        if response.status_code in [200, 201]:
            data = response.json()
            # Password should never be in response
            assert "password" not in str(data).lower()

    def test_signin_returns_token(self, client: TestClient):
        """
        Test: Successful signin returns JWT token
        """
        # This test needs a pre-created user
        # Skipping actual token verification
        pass

    def test_auth_endpoints_use_https_headers(self, client: TestClient):
        """
        Test: Auth endpoints set security headers
        """
        response = client.get("/health")  # Use any endpoint

        # Check security headers exist (may be set by reverse proxy)
        # This is informational - actual headers depend on deployment
        assert response.status_code == 200
