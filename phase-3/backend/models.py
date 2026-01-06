"""
Database models for Evolution Todo API.

Task: 1.2, T009-T015
Spec: specs/database/schema.md, specs/1-phase2-advanced-features/data-model.md
"""
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Theme(str, Enum):
    """User interface theme options."""
    LIGHT = "light"
    DARK = "dark"


class User(SQLModel, table=True):
    """User model (managed by Better Auth)."""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """Task model for todo items with Phase 2 advanced features."""
    __tablename__ = "tasks"

    # Existing fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase 2 Advanced Features (T009)
    due_date: Optional[datetime] = None
    priority: str = Field(default="none")
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None
    is_recurring: bool = Field(default=False)
    parent_recurring_id: Optional[int] = Field(default=None, foreign_key="tasks.id")


class TaskHistory(SQLModel, table=True):
    """Task modification history for audit log (T010)."""
    __tablename__ = "task_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(foreign_key="users.id")
    action: str
    old_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserPreferences(SQLModel, table=True):
    """User settings and preferences (T011)."""
    __tablename__ = "user_preferences"

    user_id: str = Field(primary_key=True, foreign_key="users.id")
    theme: str = Field(default="light")
    notifications_enabled: bool = Field(default=True)
    notification_sound: bool = Field(default=True)
    default_priority: str = Field(default="none")
    default_view: str = Field(default="all")
    language: str = Field(default="en")
    timezone: str = Field(default="UTC")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Tag(SQLModel, table=True):
    """Tag model for task categorization (T012)."""
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    name: str = Field(max_length=50)
    color: str = Field(default="#6B7280", max_length=7)
    usage_count: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)


class Notification(SQLModel, table=True):
    """Scheduled notification reminders (T013)."""
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(foreign_key="users.id")
    scheduled_time: datetime
    sent: bool = Field(default=False)
    notification_type: str = Field(default="reminder")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None


# Phase III: AI Chatbot Models (T-CHAT-001)
class Conversation(SQLModel, table=True):
    """
    Chat conversation sessions for stateless persistence.

    Task: T-CHAT-001
    Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-1)

    Purpose: Store conversation metadata to enable stateless chat endpoint.
    Each user can have multiple conversations (chat sessions).
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Individual chat messages in conversations.

    Task: T-CHAT-001
    Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-2)

    Purpose: Store message history for conversation context.
    Enables server restarts without losing chat history (stateless architecture).
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(...)  # "user" | "assistant"
    content: str = Field(...)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
