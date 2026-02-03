# T5-301: Event Publisher
# Spec: US-P5-03, AD-02 (Dapr Pub/Sub)
"""
Publishes events to Kafka via Dapr Pub/Sub HTTP API.
Decouples backend from Kafka client dependencies.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Any

import httpx

from .schemas import TaskEvent, ReminderEvent, EventType, TaskData

logger = logging.getLogger(__name__)

# Dapr sidecar address (injected when running in K8s with Dapr)
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"


async def _publish_to_dapr(topic: str, data: dict) -> bool:
    """
    Publish event to Dapr Pub/Sub.

    Args:
        topic: Kafka topic name
        data: Event payload as dict

    Returns:
        True if published successfully, False otherwise
    """
    url = f"{DAPR_BASE_URL}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )

            if response.status_code in (200, 204):
                logger.info(f"Published event to {topic}: {data.get('event_type', 'unknown')}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {response.status_code} - {response.text}")
                return False

    except httpx.ConnectError:
        # Dapr sidecar not available (local dev without Dapr)
        logger.warning(f"Dapr sidecar not available, skipping publish to {topic}")
        return False
    except Exception as e:
        logger.error(f"Error publishing to {topic}: {e}")
        return False


async def publish_task_event(
    event_type: EventType,
    task: Any,  # Task SQLModel instance
    user_id: str
) -> bool:
    """
    Publish task event to Kafka via Dapr.

    Args:
        event_type: Type of event (created, updated, completed, deleted)
        task: Task model instance
        user_id: User ID who triggered the event

    Returns:
        True if published successfully
    """
    task_data = TaskData(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
        priority=task.priority,
        tags=task.tags or [],
        recurrence_pattern=task.recurrence_pattern,
        is_recurring=task.is_recurring
    )

    event = TaskEvent(
        event_type=event_type,
        task_id=task.id,
        task_data=task_data,
        user_id=user_id,
        timestamp=datetime.utcnow()
    )

    return await _publish_to_dapr(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))


async def publish_reminder_event(
    task_id: int,
    title: str,
    user_id: str,
    due_at: Optional[datetime] = None,
    remind_at: Optional[datetime] = None
) -> bool:
    """
    Publish reminder event to Kafka via Dapr.

    Args:
        task_id: Task ID
        title: Task title for notification
        user_id: User ID to notify
        due_at: When task is due
        remind_at: When reminder should fire

    Returns:
        True if published successfully
    """
    event = ReminderEvent(
        task_id=task_id,
        title=title,
        due_at=due_at,
        remind_at=remind_at or datetime.utcnow(),
        user_id=user_id
    )

    return await _publish_to_dapr(TOPIC_REMINDERS, event.model_dump(mode="json"))


async def publish_task_update(
    user_id: str,
    task_id: Optional[int] = None,
    action: str = "refresh"
) -> bool:
    """
    Publish real-time task update for client sync.

    Args:
        user_id: User ID whose clients should sync
        task_id: Specific task ID (optional)
        action: Action type (create, update, delete, complete, refresh)

    Returns:
        True if published successfully
    """
    data = {
        "event_type": "sync",
        "task_id": task_id,
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }

    return await _publish_to_dapr(TOPIC_TASK_UPDATES, data)
