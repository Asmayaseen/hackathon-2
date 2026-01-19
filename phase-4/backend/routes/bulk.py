"""
Bulk Operations API (US6).

Task: US6 - Batch task updates and deletions
Spec: specs/features/task-crud.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from typing import List, Optional
from pydantic import BaseModel, Field

from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["bulk"])


class BulkUpdate(BaseModel):
    """Request model for bulk updates."""
    task_ids: List[int] = Field(..., min_length=1)
    completed: Optional[bool] = None
    priority: Optional[str] = None
    delete: bool = Field(default=False)


@router.post("/{user_id}/tasks/bulk")
async def bulk_task_operations(
    user_id: str,
    data: BulkUpdate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Perform bulk operations on tasks (US6).

    Args:
        user_id: User ID from URL path
        data: Bulk operation data (IDs and fields to update)
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Summary of the operation

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot perform operations on other users' tasks"
        )

    # Fetch tasks belonging to the user
    query = select(Task).where(
        Task.user_id == user_id,
        col(Task.id).in_(data.task_ids)
    )
    tasks = session.exec(query).all()

    found_ids = {t.id for t in tasks}
    missing_ids = [tid for tid in data.task_ids if tid not in found_ids]

    if data.delete:
        # Delete operation
        for task in tasks:
            session.delete(task)
        action = "deleted"
    else:
        # Update operation
        for task in tasks:
            if data.completed is not None:
                task.completed = data.completed
            if data.priority is not None:
                task.priority = data.priority
            session.add(task)
        action = "updated"

    session.commit()

    return {
        "message": f"Successfully {action} {len(tasks)} tasks",
        "count": len(tasks),
        "missing_ids": missing_ids if missing_ids else None
    }
