"""
Task Search API (US5).

Task: US5 - Full-text task search
Spec: specs/features/task-crud.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import Optional

from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/{user_id}/search")
async def search_tasks(
    user_id: str,
    q: str = Query(..., min_length=1, description="Search query"),
    status_filter: Optional[str] = Query(None, alias="status"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Search tasks by title, description, or tags (US5).

    Args:
        user_id: User ID from URL path
        q: Search query string
        status_filter: Optional filter by status (all, pending, completed)
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Object with matching tasks array and counts

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Build search query
    search_term = f"%{q}%"

    # Fetch all user tasks first, then filter in Python for JSON array search
    all_tasks_query = select(Task).where(Task.user_id == user_id)
    all_tasks = session.exec(all_tasks_query).all()

    # Filter tasks that match search in title, description, or tags
    filtered_tasks = []
    for task in all_tasks:
        # Check title
        if task.title and q.lower() in task.title.lower():
            filtered_tasks.append(task)
            continue
        # Check description
        if task.description and q.lower() in task.description.lower():
            filtered_tasks.append(task)
            continue
        # Check tags
        if task.tags and any(q.lower() in tag.lower() for tag in task.tags):
            filtered_tasks.append(task)
            continue

    # Apply status filter
    if status_filter == "pending":
        tasks = [t for t in filtered_tasks if not t.completed]
    elif status_filter == "completed":
        tasks = [t for t in filtered_tasks if t.completed]
    else:
        tasks = filtered_tasks

    # Sort by most recent first
    tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)

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
        },
        "query": q
    }
