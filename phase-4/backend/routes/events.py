# T5-304: Dapr Event Subscription Endpoints
# Spec: specs/features/phase-v-integration.md (US-INT-05)
"""
Endpoints for receiving events from Dapr Pub/Sub.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["events"])

DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub")


# Dapr Subscription Configuration
@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics to subscribe to and where to route events.
    Called automatically by Dapr sidecar on startup.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": DAPR_PUBSUB_NAME,
            "topic": "task-events",
            "route": "/api/events/task-events"
        },
        {
            "pubsubname": DAPR_PUBSUB_NAME,
            "topic": "reminders",
            "route": "/api/events/reminders"
        }
    ]


class TaskEventPayload(BaseModel):
    """Incoming task event from Kafka via Dapr."""
    event_type: str
    task_id: int
    task_data: dict
    user_id: str
    timestamp: str


class ReminderEventPayload(BaseModel):
    """Incoming reminder event from Kafka via Dapr."""
    task_id: int
    title: str
    due_at: Optional[str] = None
    remind_at: str
    user_id: str


@router.post("/api/events/task-events")
async def handle_task_event(request: Request):
    """
    Receive task events from Dapr Pub/Sub.

    Dapr sends events in CloudEvents format.
    This endpoint is called when events are published to 'task-events' topic.

    Use cases:
    - Audit logging
    - Analytics tracking
    - Cross-service sync

    Returns:
        Success acknowledgment (Dapr requires 2xx response)
    """
    try:
        # Parse CloudEvent body
        body = await request.json()
        logger.info(f"Received task event: {body}")

        # Extract data (Dapr wraps in CloudEvents format)
        data = body.get("data", body)

        # Log event for audit
        event_type = data.get("event_type", "unknown")
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        logger.info(f"Task event processed: {event_type} for task {task_id} by user {user_id}")

        # TODO: Add audit logging to database if needed
        # TODO: Trigger analytics pipeline

        return {"success": True, "event_type": event_type, "task_id": task_id}

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        # Return success to avoid Dapr retry loops
        # Log error for investigation
        return JSONResponse(
            status_code=200,
            content={"success": False, "error": str(e)}
        )


@router.post("/api/events/reminders")
async def handle_reminder_event(request: Request):
    """
    Receive reminder events from Dapr Pub/Sub.

    Called when reminder events are published (e.g., from Dapr Jobs or cron).

    Use cases:
    - Trigger in-app notifications
    - Log reminder delivery

    Returns:
        Success acknowledgment
    """
    try:
        body = await request.json()
        logger.info(f"Received reminder event: {body}")

        data = body.get("data", body)

        task_id = data.get("task_id")
        title = data.get("title")
        user_id = data.get("user_id")

        logger.info(f"Reminder for task {task_id}: '{title}' for user {user_id}")

        # TODO: Trigger notification delivery
        # This could be:
        # - In-app notification (store in notifications table)
        # - Email (via email service)
        # - Push notification (via push service)

        return {"success": True, "task_id": task_id, "delivered": True}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        return JSONResponse(
            status_code=200,
            content={"success": False, "error": str(e)}
        )
