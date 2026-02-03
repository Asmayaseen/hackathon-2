# T5-301: Event Publishing Module
# Spec: US-P5-03 (Event-Driven Task Operations)
"""
Event publishing module for Phase 5 event-driven architecture.
Uses Dapr Pub/Sub to publish task events to Kafka.
"""

from .publisher import publish_task_event, publish_reminder_event
from .schemas import TaskEvent, ReminderEvent, EventType

__all__ = [
    "publish_task_event",
    "publish_reminder_event",
    "TaskEvent",
    "ReminderEvent",
    "EventType",
]
