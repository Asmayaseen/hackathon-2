"""
Task CRUD API endpoints.

Task: 1.7, 1.8, 1.9
Spec: specs/api/rest-endpoints.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["tasks"])


# Request/Response Models
class TaskCreate(BaseModel):
    """Request model for creating a task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Response model for task operations."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get all tasks for a user with optional status filtering.

    Args:
        user_id: User ID from URL path
        status_filter: Filter tasks by status (all, pending, completed)
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

    # Sort by created_at descending (newest first)
    query = query.order_by(Task.created_at.desc())

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

    # Create new task
    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Save to database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

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

    task.updated_at = datetime.utcnow()

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

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

    # Delete task
    session.delete(task)
    session.commit()

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
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
