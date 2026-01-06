"""
Shared pytest fixtures for Evolution Todo backend tests.

This module provides fixtures for:
- Database sessions with transaction rollback (for test isolation)
- FastAPI test client with authentication
- Mock objects for external services (OpenAI, Groq)
- Test data factories for models
- Sample audio files for voice transcription tests

All tests use these fixtures to ensure consistency and isolation.
"""
import pytest
import os
import tempfile
import jwt
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Generator, Dict, Any
import io

# Import app and models
from main import app
from models import User, Task, Conversation, Message
from db import get_session
from middleware.auth import JWT_SECRET, JWT_ALGORITHM


# ==============================================================================
# Database Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine (session-scoped for performance).

    Uses in-memory SQLite for fast, isolated tests.
    All tables are created once per test session.
    """
    # Use in-memory SQLite for tests (fast and isolated)
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False}  # Required for SQLite
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Provide a database session with automatic rollback for test isolation.

    Each test gets a fresh transaction that is rolled back after the test,
    ensuring tests don't interfere with each other.

    Usage:
        def test_something(db_session):
            task = Task(user_id="user1", title="Test")
            db_session.add(task)
            db_session.commit()
            # Changes are rolled back automatically after test
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback transaction (ensures test isolation)
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_get_session(db_session: Session):
    """
    Override FastAPI's get_session dependency with test database session.

    This ensures all API endpoints use the test database instead of production.
    """
    def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


# ==============================================================================
# Authentication Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def jwt_secret() -> str:
    """Return JWT secret for token generation."""
    return JWT_SECRET


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """
    Create a test user in the database.

    Returns:
        User with id="test_user_123", email="test@example.com"
    """
    user = User(
        id="test_user_123",
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password_here",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_2(db_session: Session) -> User:
    """
    Create a second test user for multi-user tests.

    Returns:
        User with id="test_user_456", email="test2@example.com"
    """
    user = User(
        id="test_user_456",
        email="test2@example.com",
        name="Test User 2",
        password_hash="hashed_password_here",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user: User, jwt_secret: str) -> str:
    """
    Generate a valid JWT token for test_user.

    Returns:
        JWT token string for Authorization header
    """
    payload = {
        "user_id": test_user.id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
def auth_token_user_2(test_user_2: User, jwt_secret: str) -> str:
    """
    Generate a valid JWT token for test_user_2.

    Returns:
        JWT token string for Authorization header
    """
    payload = {
        "user_id": test_user_2.id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
def expired_token(test_user: User, jwt_secret: str) -> str:
    """
    Generate an expired JWT token for testing authentication failures.

    Returns:
        Expired JWT token string
    """
    payload = {
        "user_id": test_user.id,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    token = jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Generate HTTP headers with valid authentication token.

    Usage:
        response = client.post("/api/user123/chat", headers=auth_headers, json={...})

    Returns:
        Dict with Authorization header
    """
    return {
        "Authorization": f"Bearer {auth_token}"
    }


@pytest.fixture(scope="function")
def auth_headers_user_2(auth_token_user_2: str) -> Dict[str, str]:
    """
    Generate HTTP headers with valid authentication token for user 2.

    Returns:
        Dict with Authorization header
    """
    return {
        "Authorization": f"Bearer {auth_token_user_2}"
    }


# ==============================================================================
# FastAPI Test Client Fixtures
# ==============================================================================

@pytest.fixture(scope="function")
def client(override_get_session) -> TestClient:
    """
    Provide a FastAPI TestClient for API endpoint testing.

    The client automatically uses the test database (via override_get_session).

    Usage:
        def test_endpoint(client, auth_headers):
            response = client.post("/api/user123/chat", headers=auth_headers, json={...})
            assert response.status_code == 200

    Returns:
        TestClient instance
    """
    return TestClient(app)


# ==============================================================================
# Mock Fixtures for External Services
# ==============================================================================

@pytest.fixture(scope="function")
def mock_openai_client():
    """
    Mock OpenAI client for AI agent tests.

    Prevents actual API calls during tests and provides controlled responses.

    Usage:
        with mock_openai_client as mock_client:
            # Configure mock responses
            mock_client.chat.completions.create.return_value = ...
    """
    with patch("agent.client") as mock_client:
        # Configure default mock behavior
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked AI response"
        mock_response.choices[0].message.tool_calls = None

        mock_client.chat.completions.create.return_value = mock_response

        yield mock_client


@pytest.fixture(scope="function")
def mock_whisper_transcription():
    """
    Mock OpenAI Whisper transcription for voice tests.

    Prevents actual API calls and provides controlled transcription responses.

    Usage:
        with mock_whisper_transcription as mock_whisper:
            mock_whisper.return_value.text = "Custom transcription"
    """
    with patch("routes.voice.client") as mock_client:
        # Configure default transcription response
        mock_transcription = MagicMock()
        mock_transcription.text = "This is a test transcription"
        mock_transcription.language = "en"

        mock_client.audio.transcriptions.create.return_value = mock_transcription

        yield mock_client


@pytest.fixture(scope="function")
def mock_mcp_tools():
    """
    Mock MCP tools for agent tests.

    Prevents actual tool execution and provides controlled tool responses.
    """
    with patch("agent.list_tools") as mock_list_tools, \
         patch("agent.call_tool") as mock_call_tool:

        # Mock tool list
        mock_list_tools.return_value = []

        # Mock tool execution
        from mcp.types import TextContent
        mock_call_tool.return_value = [
            TextContent(type="text", text="Mocked tool result")
        ]

        yield {
            "list_tools": mock_list_tools,
            "call_tool": mock_call_tool
        }


# ==============================================================================
# Test Data Fixtures
# ==============================================================================

@pytest.fixture(scope="function")
def sample_task(db_session: Session, test_user: User) -> Task:
    """
    Create a sample task for testing.

    Returns:
        Task with title="Sample Task", user_id=test_user.id
    """
    task = Task(
        user_id=test_user.id,
        title="Sample Task",
        description="This is a sample task for testing",
        completed=False,
        priority="medium",
        tags=["test", "sample"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture(scope="function")
def sample_conversation(db_session: Session, test_user: User) -> Conversation:
    """
    Create a sample conversation for testing.

    Returns:
        Conversation with user_id=test_user.id
    """
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation


@pytest.fixture(scope="function")
def sample_messages(db_session: Session, test_user: User, sample_conversation: Conversation) -> list[Message]:
    """
    Create sample messages in a conversation.

    Returns:
        List of 3 messages (user -> assistant -> user)
    """
    messages = [
        Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role="user",
            content="Hello, create a task for me",
            created_at=datetime.utcnow()
        ),
        Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role="assistant",
            content="Sure! What task would you like to create?",
            tool_calls=[],
            created_at=datetime.utcnow()
        ),
        Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role="user",
            content="Buy groceries tomorrow",
            created_at=datetime.utcnow()
        )
    ]

    for msg in messages:
        db_session.add(msg)
    db_session.commit()

    return messages


@pytest.fixture(scope="function")
def sample_audio_file() -> io.BytesIO:
    """
    Create a sample audio file (binary data) for voice transcription tests.

    Returns:
        BytesIO object with fake audio data
    """
    # Create fake audio data (in production, this would be actual audio bytes)
    audio_data = b"RIFF" + b"\x00" * 100  # Minimal WAV-like header + data
    return io.BytesIO(audio_data)


# ==============================================================================
# Task Factory Fixtures
# ==============================================================================

@pytest.fixture(scope="function")
def task_factory(db_session: Session):
    """
    Factory fixture for creating multiple tasks with custom attributes.

    Usage:
        def test_multiple_tasks(task_factory):
            task1 = task_factory(title="Task 1", priority="high")
            task2 = task_factory(title="Task 2", completed=True)

    Returns:
        Factory function that creates tasks
    """
    def _create_task(
        user_id: str = "test_user_123",
        title: str = "Test Task",
        description: str = None,
        completed: bool = False,
        priority: str = "none",
        tags: list = None,
        due_date: datetime = None,
        recurrence_pattern: str = None
    ) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            tags=tags or [],
            due_date=due_date,
            recurrence_pattern=recurrence_pattern,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _create_task


@pytest.fixture(scope="function")
def conversation_factory(db_session: Session):
    """
    Factory fixture for creating multiple conversations.

    Usage:
        def test_multiple_conversations(conversation_factory):
            conv1 = conversation_factory(user_id="user1")
            conv2 = conversation_factory(user_id="user2")

    Returns:
        Factory function that creates conversations
    """
    def _create_conversation(user_id: str = "test_user_123") -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        return conversation

    return _create_conversation
