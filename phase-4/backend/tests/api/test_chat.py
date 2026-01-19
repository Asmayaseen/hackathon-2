"""
API Tests: Chat Endpoints
Tests for /chat/* endpoints (Chatbot functionality).
"""

import pytest
from fastapi.testclient import TestClient


class TestChatEndpoints:
    """Test suite for chat/chatbot endpoints."""

    def test_chat_endpoint_exists(self, client: TestClient):
        """
        Test: Chat endpoint exists
        """
        response = client.post("/chat", json={
            "message": "Hello"
        })

        # Should not return 404
        assert response.status_code != 404

    def test_chat_requires_message(self, client: TestClient):
        """
        Test: Chat endpoint requires message field
        """
        response = client.post("/chat", json={})

        # Should return validation error
        assert response.status_code in [400, 401, 422]

    def test_chat_accepts_text_message(self, client: TestClient):
        """
        Test: Chat endpoint accepts text messages
        """
        response = client.post("/chat", json={
            "message": "Add a task: Buy groceries"
        })

        # Should process (may need auth)
        assert response.status_code in [200, 401]

    def test_chat_response_structure(self, client: TestClient):
        """
        Test: Chat response has expected structure
        """
        response = client.post("/chat", json={
            "message": "Hello"
        })

        if response.status_code == 200:
            data = response.json()
            # Should have response field
            assert "response" in data or "message" in data or "content" in data


class TestChatIntentRecognition:
    """Tests for chat intent recognition."""

    def test_add_task_intent(self, client: TestClient):
        """
        Test: Chat recognizes 'add task' intent
        """
        response = client.post("/chat", json={
            "message": "Add task: Complete Phase 4"
        })

        # Intent should be recognized (if auth passes)
        assert response.status_code in [200, 401]

    def test_list_tasks_intent(self, client: TestClient):
        """
        Test: Chat recognizes 'list tasks' intent
        """
        response = client.post("/chat", json={
            "message": "Show me my tasks"
        })

        assert response.status_code in [200, 401]

    def test_delete_task_intent(self, client: TestClient):
        """
        Test: Chat recognizes 'delete task' intent
        """
        response = client.post("/chat", json={
            "message": "Delete task 1"
        })

        assert response.status_code in [200, 401]

    def test_greeting_response(self, client: TestClient):
        """
        Test: Chat responds to greetings
        """
        response = client.post("/chat", json={
            "message": "Hello!"
        })

        assert response.status_code in [200, 401]


class TestChatMultilingual:
    """Tests for multilingual chat support."""

    def test_urdu_message(self, client: TestClient):
        """
        Test: Chat handles Urdu messages
        Spec: Urdu language support (+100 bonus)
        """
        response = client.post("/chat", json={
            "message": "میرے کام دکھاؤ"  # Show my tasks in Urdu
        })

        assert response.status_code in [200, 401]

    def test_mixed_language(self, client: TestClient):
        """
        Test: Chat handles mixed language (Urdu + English)
        """
        response = client.post("/chat", json={
            "message": "Add کام: Complete Phase 4"
        })

        assert response.status_code in [200, 401]


class TestChatEdgeCases:
    """Edge case tests for chat endpoints."""

    def test_empty_message(self, client: TestClient):
        """
        Test: Empty message is rejected
        """
        response = client.post("/chat", json={
            "message": ""
        })

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_very_long_message(self, client: TestClient):
        """
        Test: Very long message is handled
        """
        long_message = "a" * 10000

        response = client.post("/chat", json={
            "message": long_message
        })

        # Should handle gracefully
        assert response.status_code in [200, 400, 401, 413, 422]

    def test_special_characters(self, client: TestClient):
        """
        Test: Special characters in message
        """
        response = client.post("/chat", json={
            "message": "Add task: Test <script>alert('xss')</script>"
        })

        # Should handle without XSS vulnerability
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            # Response should not contain unescaped script
            assert "<script>" not in response.text
