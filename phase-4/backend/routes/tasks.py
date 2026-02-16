"""
Task CRUD API endpoints.

Task: 1.7, 1.8, 1.9, T5-302
Spec: specs/api/rest-endpoints.md, specs/features/phase-v-integration.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from models import Task
from db import get_session
from middleware.auth import verify_token
import asyncio
import logging

# Phase 5: Event Publishing (T5-302)
try:
    from events import publish_task_event, publish_reminder_event, EventType
    EVENTS_ENABLED = True
except ImportError:
    EVENTS_ENABLED = False
    logging.warning("Events module not available, event publishing disabled")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


# Helper function for async event publishing in background
def fire_and_forget(coro):
    """Fire and forget coroutine - don't block main request."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(coro)
        else:
            loop.run_until_complete(coro)
    except Exception as e:
        logger.warning(f"Event publishing failed (non-blocking): {e}")


# Request/Response Models
class TaskCreate(BaseModel):
    """Request model for creating a task (T022)."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    # Phase 2 Advanced Features
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(default="none")
    tags: Optional[list[str]] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskUpdate(BaseModel):
    """Request model for updating a task (T024)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    # Phase 2 Advanced Features
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskResponse(BaseModel):
    """Response model for task operations."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    # Phase 2 Advanced Features
    due_date: Optional[datetime] = None
    priority: str = "none"
    tags: list[str] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None
    is_recurring: bool = False
    parent_recurring_id: Optional[int] = None


@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    due_filter: Optional[str] = Query(None, alias="due"),
    sort_by: Optional[str] = Query("created_at", alias="sort"),
    sort_order: Optional[str] = Query("desc", alias="order"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get all tasks for a user with optional filtering and sorting (US2).

    Args:
        user_id: User ID from URL path
        status_filter: Filter by status (all, pending, completed)
        priority_filter: Filter by priority (all, high, medium, low, none)
        due_filter: Filter by due date (all, today, overdue, week)
        sort_by: Sort by field (created_at, due_date, priority, title)
        sort_order: Sort direction (asc, desc)
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Object with tasks array and counts

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    # 'all' or None - no filter needed

    # Apply priority filter (US2)
    if priority_filter and priority_filter != "all":
        query = query.where(Task.priority == priority_filter)

    # Apply due date filter (US2)
    now = datetime.now(timezone.utc)
    if due_filter == "today":
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)
        query = query.where(Task.due_date >= today_start, Task.due_date <= today_end)
    elif due_filter == "overdue":
        query = query.where(Task.due_date < now, Task.completed == False)
    elif due_filter == "week":
        week_end = now + timedelta(days=7)
        query = query.where(Task.due_date >= now, Task.due_date <= week_end)

    # Apply sorting (US2)
    sort_field = None
    if sort_by == "created_at":
        sort_field = Task.created_at
    elif sort_by == "due_date":
        sort_field = Task.due_date
    elif sort_by == "priority":
        # Priority order: high > medium > low > none
        priority_order = {
            "high": 0,
            "medium": 1,
            "low": 2,
            "none": 3
        }
        # For now, sort by string (will refine if needed)
        sort_field = Task.priority
    elif sort_by == "title":
        sort_field = Task.title
    else:
        sort_field = Task.created_at  # default

    if sort_field:
        if sort_order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())

    # Execute query
    tasks = session.exec(query).all()

    # Calculate counts
    total = len(tasks)
    pending = sum(1 for t in tasks if not t.completed)
    completed = sum(1 for t in tasks if t.completed)

    return {
        "tasks": tasks,
        "count": {
            "total": total,
            "pending": pending,
            "completed": completed
        }
    }


@router.post("/{user_id}/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Create a new task for a user.

    Args:
        user_id: User ID from URL path
        task_data: Task creation data (title, description)
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Created task object

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 400 if validation fails
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users"
        )

    # Validate priority (T025)
    if task_data.priority and task_data.priority not in ['high', 'medium', 'low', 'none']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid priority. Must be one of: high, medium, low, none"
        )

    # Validate due_date (T026) - prevent past dates unless explicitly allowed
    if task_data.due_date:
        # Make both datetimes timezone-aware for comparison
        now_utc = datetime.now(timezone.utc)
        if task_data.due_date < now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past"
            )

    # Create new task (T022, T023)
    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        # Phase 2 Advanced Features
        due_date=task_data.due_date,
        priority=task_data.priority or "none",
        tags=task_data.tags or [],
        recurrence_pattern=task_data.recurrence_pattern,
        reminder_offset=task_data.reminder_offset,
        is_recurring=bool(task_data.recurrence_pattern)
    )

    # Save to database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    # Phase 5: Publish task created event (T5-302)
    if EVENTS_ENABLED:
        fire_and_forget(publish_task_event(EventType.CREATED, new_task, user_id))
        logger.info(f"Published CREATED event for task {new_task.id}")

    return new_task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get a specific task by ID.

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Task object

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

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Update a task.

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        task_data: Task update data (title, description, completed)
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
            detail="Cannot update other users' tasks"
        )

    # Find task
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Phase 2 Advanced Features (T024)
    if task_data.priority is not None:
        # Validate priority (T025)
        if task_data.priority not in ['high', 'medium', 'low', 'none']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Must be one of: high, medium, low, none"
            )
        task.priority = task_data.priority

    if task_data.due_date is not None:
        # Allow editing overdue tasks, but prevent setting new past dates (T026)
        now_utc = datetime.now(timezone.utc)
        if task_data.due_date < now_utc and task.due_date is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past"
            )
        task.due_date = task_data.due_date

    if task_data.tags is not None:
        task.tags = task_data.tags

    if task_data.recurrence_pattern is not None:
        task.recurrence_pattern = task_data.recurrence_pattern
        task.is_recurring = bool(task_data.recurrence_pattern)

    if task_data.reminder_offset is not None:
        task.reminder_offset = task_data.reminder_offset

    task.updated_at = datetime.now(timezone.utc)

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Phase 5: Publish task updated event (T5-302)
    if EVENTS_ENABLED:
        fire_and_forget(publish_task_event(EventType.UPDATED, task, user_id))
        logger.info(f"Published UPDATED event for task {task.id}")

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Delete a task.

    Args:
        user_id: User ID from URL path
        task_id: Task ID from URL path
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' tasks"
        )

    # Find task
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Phase 5: Capture task data before deletion for event (T5-302)
    task_copy = Task(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
        priority=task.priority,
        tags=task.tags,
        recurrence_pattern=task.recurrence_pattern,
        is_recurring=task.is_recurring,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

    # Delete task
    session.delete(task)
    session.commit()

    # Phase 5: Publish task deleted event (T5-302)
    if EVENTS_ENABLED:
        fire_and_forget(publish_task_event(EventType.DELETED, task_copy, user_id))
        logger.info(f"Published DELETED event for task {task_copy.id}")

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Toggle task completion status.

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
            detail="Cannot update other users' tasks"
        )

    # Find task
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion status
    was_completed = task.completed
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Phase 5: Publish task completed/uncompleted event (T5-302)
    if EVENTS_ENABLED:
        event_type = EventType.COMPLETED if task.completed else EventType.UPDATED
        fire_and_forget(publish_task_event(event_type, task, user_id))
        logger.info(f"Published {event_type.value} event for task {task.id}")

    # Phase 5: Auto-create next occurrence for recurring tasks (T5-500)
    if task.completed and task.is_recurring and task.recurrence_pattern:
        next_task = create_next_occurrence(task, user_id)
        if next_task:
            session.add(next_task)
            session.commit()
            session.refresh(next_task)
            logger.info(f"Created next recurring occurrence: task {next_task.id}")

            # Publish created event for new occurrence
            if EVENTS_ENABLED:
                fire_and_forget(publish_task_event(EventType.CREATED, next_task, user_id))

    return task


def create_next_occurrence(task: Task, user_id: str) -> Optional[Task]:
    """
    Create next occurrence for a recurring task.

    Task: T5-500
    Spec: specs/phase-5/spec.md (US-P5-01)

    Args:
        task: Completed recurring task
        user_id: User ID

    Returns:
        New task for next occurrence, or None if invalid
    """
    if not task.recurrence_pattern:
        return None

    # Calculate next due date based on pattern
    base_date = task.due_date or datetime.now(timezone.utc)

    if task.recurrence_pattern == "daily":
        next_due = base_date + timedelta(days=1)
    elif task.recurrence_pattern == "weekly":
        next_due = base_date + timedelta(weeks=1)
    elif task.recurrence_pattern == "monthly":
        # Add approximately one month (30 days)
        next_due = base_date + timedelta(days=30)
    else:
        # Unknown pattern
        logger.warning(f"Unknown recurrence pattern: {task.recurrence_pattern}")
        return None

    # Create new task
    new_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        completed=False,
        due_date=next_due,
        priority=task.priority,
        tags=task.tags or [],
        recurrence_pattern=task.recurrence_pattern,
        is_recurring=True,
        parent_recurring_id=task.id,
        reminder_offset=task.reminder_offset,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    return new_task
