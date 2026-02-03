# T5-401: Notification Service
# Spec: US-P5-06 (Notification Service)
"""
Notification Service - Consumes reminder events and delivers notifications.

This microservice:
- Subscribes to 'reminders' topic via Dapr Pub/Sub
- Stores notification state in database
- Marks notifications as sent (mock delivery for hackathon)
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None


# Models
class NotificationRecord(SQLModel, table=True):
    """Notification delivery record."""
    __tablename__ = "notification_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    user_id: str
    title: str
    notification_type: str = "reminder"
    status: str = "pending"  # pending, sent, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ReminderEventPayload(BaseModel):
    """Reminder event from Kafka."""
    task_id: int
    title: str
    due_at: Optional[str] = None
    remind_at: str
    user_id: str
    notification_type: str = "reminder"


# FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Consumes reminder events and delivers notifications",
    version="5.0.0"
)


@app.on_event("startup")
async def startup():
    """Initialize database tables on startup."""
    if engine:
        SQLModel.metadata.create_all(engine)
        logger.info("Notification Service started, database initialized")
    else:
        logger.warning("No DATABASE_URL configured, running without persistence")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "notification-service",
        "version": "5.0.0",
        "status": "running"
    }


# Dapr Subscription Configuration
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.
    Tells Dapr which topics to subscribe to and where to route events.
    """
    return [
        {
            "pubsubname": os.getenv("DAPR_PUBSUB_NAME", "kafka-pubsub"),
            "topic": "reminders",
            "route": "/api/events/reminders"
        }
    ]


@app.post("/api/events/reminders")
async def handle_reminder_event(request: Request):
    """
    Handle reminder events from Dapr Pub/Sub.

    Dapr sends events as CloudEvents format.
    """
    try:
        # Parse CloudEvent
        body = await request.json()
        logger.info(f"Received reminder event: {body}")

        # Extract data (Dapr wraps in CloudEvents format)
        data = body.get("data", body)

        # Parse reminder payload
        reminder = ReminderEventPayload(**data)

        # Create notification record
        if engine:
            with Session(engine) as session:
                notification = NotificationRecord(
                    task_id=reminder.task_id,
                    user_id=reminder.user_id,
                    title=reminder.title,
                    notification_type=reminder.notification_type,
                    status="pending"
                )
                session.add(notification)
                session.commit()
                session.refresh(notification)

                # Mock delivery (in production: send email/push/SMS)
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
                session.add(notification)
                session.commit()

                logger.info(f"Notification delivered for task {reminder.task_id}")

        return {"success": True, "message": "Notification processed"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/notifications/{user_id}")
async def get_user_notifications(user_id: str, limit: int = 20):
    """Get recent notifications for a user."""
    if not engine:
        return {"notifications": [], "message": "Database not configured"}

    with Session(engine) as session:
        statement = (
            select(NotificationRecord)
            .where(NotificationRecord.user_id == user_id)
            .order_by(NotificationRecord.created_at.desc())
            .limit(limit)
        )
        notifications = session.exec(statement).all()

        return {
            "notifications": [
                {
                    "id": n.id,
                    "task_id": n.task_id,
                    "title": n.title,
                    "type": n.notification_type,
                    "status": n.status,
                    "created_at": n.created_at.isoformat(),
                    "sent_at": n.sent_at.isoformat() if n.sent_at else None
                }
                for n in notifications
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
