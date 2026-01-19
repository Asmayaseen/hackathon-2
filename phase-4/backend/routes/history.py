"""
Task History API (US7).

Task: US7 - Audit log retrieval
Spec: specs/database/schema.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from models import TaskHistory
from db import get_session
from middleware.auth import verify_token

router = APIRouter(tags=["history"])


@router.get("/api/{user_id}/history")
async def get_task_history(
    user_id: str,
    task_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Retrieve task modification history (US7).

    Args:
        user_id: User ID from URL path
        task_id: Optional filter by task ID
        limit: Number of records to return
        offset: Number of records to skip
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        List of history records
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' history"
        )

    # Build query
    query = select(TaskHistory).where(TaskHistory.user_id == user_id)

    if task_id:
        query = query.where(TaskHistory.task_id == task_id)

    query = query.order_by(TaskHistory.timestamp.desc()).offset(offset).limit(limit)

    history = session.exec(query).all()

    return {
        "history": history,
        "count": len(history),
        "offset": offset,
        "limit": limit
    }
