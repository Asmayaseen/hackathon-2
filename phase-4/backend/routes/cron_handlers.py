"""
Dapr Cron Binding Handlers

This module handles scheduled tasks triggered by Dapr cron bindings:
- reminder-cron: Check for due tasks and send reminders (every 5 minutes)
- recurring-task-cron: Generate next occurrences for completed recurring tasks (hourly)
- cleanup-cron: Clean up old notifications and completed tasks (daily)

Dapr calls these endpoints based on the binding-cron.yaml configuration.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlmodel import Session, select

from db import get_session
from models import Task, Notification

# Import event publisher for Dapr pub/sub integration
try:
    from events.publisher import EventPublisher
    event_publisher = EventPublisher()
except ImportError:
    event_publisher = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cron", tags=["cron"])


@router.post("/reminder-cron")
async def handle_reminder_cron(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Dapr Cron Binding: reminder-cron
    Schedule: Every 5 minutes

    Checks for tasks with due dates approaching and:
    1. Creates notification records
    2. Publishes reminder events to Kafka via Dapr pub/sub

    This endpoint is called automatically by Dapr based on the cron schedule.
    """
    logger.info("Reminder cron triggered at %s", datetime.now(timezone.utc))

    # Get current time and reminder windows
    now = datetime.now(timezone.utc)

    # Check for tasks due in the next 15, 30, 60 minutes
    reminder_windows = [
        (15, "15_minutes"),
        (30, "30_minutes"),
        (60, "1_hour"),
        (1440, "1_day"),  # 24 hours
    ]

    reminders_sent = 0

    for minutes, window_name in reminder_windows:
        window_start = now
        window_end = now + timedelta(minutes=minutes)

        # Find tasks due within this window that haven't been reminded
        statement = select(Task).where(
            Task.due_date.isnot(None),
            Task.due_date >= window_start,
            Task.due_date <= window_end,
            Task.completed == False
        )

        tasks = session.exec(statement).all()

        for task in tasks:
            # Check if reminder should be sent based on reminder_offset
            if task.reminder_offset and task.due_date:
                remind_at = task.due_date - timedelta(minutes=task.reminder_offset)
                if now < remind_at:
                    continue  # Not time to remind yet

            # Check if notification already exists for this task
            existing = session.exec(
                select(Notification).where(
                    Notification.task_id == task.id,
                    Notification.sent == False
                )
            ).first()
            if existing:
                continue  # Already has pending notification

            # Create notification record
            notification = Notification(
                user_id=task.user_id,
                task_id=task.id,
                notification_type="reminder",
                scheduled_time=task.due_date,
                created_at=now
            )
            session.add(notification)

            # Publish reminder event via Dapr
            if event_publisher:
                await event_publisher.publish_reminder_event(
                    task_id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    due_at=task.due_date,
                    remind_at=now
                )

            reminders_sent += 1
            logger.info(
                "Reminder sent for task %d (user: %s, due: %s)",
                task.id, task.user_id, task.due_date
            )

    session.commit()

    return {
        "status": "success",
        "triggered_at": now.isoformat(),
        "reminders_sent": reminders_sent
    }


@router.post("/recurring-task-cron")
async def handle_recurring_task_cron(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Dapr Cron Binding: recurring-task-cron
    Schedule: Every hour (at minute 0)

    Checks for completed recurring tasks and creates the next occurrence.
    This ensures recurring tasks are always regenerated even if the
    completion webhook fails.
    """
    logger.info("Recurring task cron triggered at %s", datetime.now(timezone.utc))

    now = datetime.now(timezone.utc)
    tasks_created = 0

    # Find completed recurring tasks without a next occurrence
    statement = select(Task).where(
        Task.is_recurring == True,
        Task.completed == True,
        Task.recurrence_pattern.isnot(None)
    )

    completed_recurring = session.exec(statement).all()

    for task in completed_recurring:
        # Check if next occurrence already exists
        next_occurrence_query = select(Task).where(
            Task.parent_recurring_id == task.id,
            Task.completed == False
        )
        existing_next = session.exec(next_occurrence_query).first()

        if existing_next:
            continue  # Next occurrence already exists

        # Calculate next due date
        next_due = calculate_next_due_date(
            task.due_date or task.completed_at or now,
            task.recurrence_pattern
        )

        if next_due:
            # Create next occurrence
            new_task = Task(
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags,
                due_date=next_due,
                is_recurring=True,
                recurrence_pattern=task.recurrence_pattern,
                parent_recurring_id=task.id,
                reminder_offset=task.reminder_offset,
                created_at=now,
                completed=False
            )
            session.add(new_task)
            tasks_created += 1

            # Publish event
            if event_publisher:
                await event_publisher.publish_task_event(
                    event_type="created",
                    task_id=new_task.id,
                    user_id=new_task.user_id,
                    task_data={
                        "title": new_task.title,
                        "due_date": next_due.isoformat() if next_due else None,
                        "is_recurring": True,
                        "parent_id": task.id
                    }
                )

            logger.info(
                "Created recurring task occurrence: %s (parent: %d, next_due: %s)",
                new_task.title, task.id, next_due
            )

    session.commit()

    return {
        "status": "success",
        "triggered_at": now.isoformat(),
        "tasks_created": tasks_created
    }


@router.post("/cleanup-cron")
async def handle_cleanup_cron(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Dapr Cron Binding: cleanup-cron
    Schedule: Daily at midnight UTC

    Performs cleanup operations:
    1. Remove notifications older than 30 days
    2. Archive completed tasks older than 90 days (optional)
    3. Clean up orphaned records
    """
    logger.info("Cleanup cron triggered at %s", datetime.now(timezone.utc))

    now = datetime.now(timezone.utc)
    cleanup_stats = {
        "notifications_deleted": 0,
        "tasks_archived": 0
    }

    # Delete old notifications (older than 30 days)
    thirty_days_ago = now - timedelta(days=30)
    old_notifications = session.exec(
        select(Notification).where(
            Notification.created_at < thirty_days_ago,
            Notification.read == True
        )
    ).all()

    for notification in old_notifications:
        session.delete(notification)
        cleanup_stats["notifications_deleted"] += 1

    session.commit()

    logger.info(
        "Cleanup completed: %d notifications deleted",
        cleanup_stats["notifications_deleted"]
    )

    return {
        "status": "success",
        "triggered_at": now.isoformat(),
        "cleanup_stats": cleanup_stats
    }


def calculate_next_due_date(
    current_due: datetime,
    pattern: str
) -> Optional[datetime]:
    """
    Calculate the next due date based on recurrence pattern.

    Patterns:
    - daily: Add 1 day
    - weekly: Add 7 days
    - biweekly: Add 14 days
    - monthly: Add 1 month (handles month-end cases)
    """
    if not current_due or not pattern:
        return None

    pattern = pattern.lower()

    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "biweekly":
        return current_due + timedelta(weeks=2)
    elif pattern == "monthly":
        # Handle month-end cases
        next_month = current_due.month + 1
        next_year = current_due.year
        if next_month > 12:
            next_month = 1
            next_year += 1

        # Try to keep the same day, but handle month-end overflow
        try:
            return current_due.replace(year=next_year, month=next_month)
        except ValueError:
            # Day doesn't exist in next month (e.g., Jan 31 -> Feb)
            # Go to last day of next month
            if next_month == 12:
                next_next_month = 1
                next_next_year = next_year + 1
            else:
                next_next_month = next_month + 1
                next_next_year = next_year

            return datetime(next_next_year, next_next_month, 1) - timedelta(days=1)

    return None


# Health check endpoint for cron handlers
@router.get("/health")
async def cron_health():
    """Health check for cron handler endpoints"""
    return {
        "status": "healthy",
        "service": "cron-handlers",
        "bindings": [
            "reminder-cron",
            "recurring-task-cron",
            "cleanup-cron"
        ]
    }
