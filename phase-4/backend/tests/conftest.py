"""
Pytest configuration and fixtures for Phase 4 backend tests
"""
import os
import sys

# CRITICAL: Set environment BEFORE any imports
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ.setdefault("GROQ_API_KEY", "test-mock-key")  # Mock for agent.py

# Ensure the backend module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create test database tables before any tests run"""
    from db import create_db_and_tables
    create_db_and_tables()
    yield
    # Cleanup: remove test.db after tests
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(test_client):
    """Get auth headers for authenticated requests"""
    # Register a test user
    test_client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    })

    # Login to get token
    response = test_client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "testpassword123"
    })

    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}
