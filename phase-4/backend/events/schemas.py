# T5-301: Event Schemas
# Spec: US-P5-03 (Event-Driven Task Operations)
"""
Pydantic schemas for event payloads.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Task event types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"
    RECURRENCE_TRIGGERED = "recurrence_triggered"


class TaskData(BaseModel):
    """Task data embedded in events."""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: str = "none"
    tags: List[str] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = None
    is_recurring: bool = False


class TaskEvent(BaseModel):
    """
    Task event payload for Kafka.

    Published to 'task-events' topic on all CRUD operations.
    """
    event_type: EventType
    task_id: int
    task_data: TaskData
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReminderEvent(BaseModel):
    """
    Reminder event payload for notifications.

    Published to 'reminders' topic when reminder is due.
    """
    task_id: int
    title: str
    due_at: Optional[datetime] = None
    remind_at: datetime
    user_id: str
    notification_type: str = "reminder"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskUpdateEvent(BaseModel):
    """
    Real-time task update event for client sync.

    Published to 'task-updates' topic for WebSocket delivery.
    """
    event_type: str  # "sync", "refresh"
    task_id: Optional[int] = None
    user_id: str
    action: str  # "create", "update", "delete", "complete"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
