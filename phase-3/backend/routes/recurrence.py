"""
Recurring Tasks Management (US4).

Task: US4 - Handle task recurrence patterns
Spec: specs/features/task-crud.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional

from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["recurrence"])


@router.post("/{user_id}/tasks/{task_id}/complete")
async def complete_task_with_recurrence(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Complete a task and create next instance if recurring (US4).

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Updated task object

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Find task
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Mark as completed
    task.completed = True
    task.updated_at = datetime.utcnow()

    # Handle recurrence (US4)
    if task.is_recurring and task.recurrence_pattern:
        next_task = _create_next_recurring_instance(task, session)
        if next_task:
            session.add(next_task)

    session.commit()
    session.refresh(task)

    return task


def _create_next_recurring_instance(parent_task: Task, session: Session) -> Optional[Task]:
    """Create next instance of a recurring task based on pattern."""
    if not parent_task.recurrence_pattern or not parent_task.due_date:
        return None

    pattern = parent_task.recurrence_pattern.lower()
    next_due = None

    if pattern == "daily":
        next_due = parent_task.due_date + timedelta(days=1)
    elif pattern == "weekly":
        next_due = parent_task.due_date + timedelta(weeks=1)
    elif pattern == "biweekly":
        next_due = parent_task.due_date + timedelta(weeks=2)
    elif pattern == "monthly":
        # Approximate month as 30 days
        next_due = parent_task.due_date + timedelta(days=30)
    else:
        return None

    if not next_due:
        return None

    # Create next instance
    new_task = Task(
        user_id=parent_task.user_id,
        title=parent_task.title,
        description=parent_task.description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        due_date=next_due,
        priority=parent_task.priority,
        tags=parent_task.tags,
        recurrence_pattern=parent_task.recurrence_pattern,
        reminder_offset=parent_task.reminder_offset,
        is_recurring=True,
        parent_recurring_id=parent_task.id
    )

    return new_task
