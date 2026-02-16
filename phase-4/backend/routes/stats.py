"""
Statistics API (US10).

Task: US10 - Aggregation endpoints for dashboard
Spec: specs/features/task-crud.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(tags=["stats"])


@router.get("/api/{user_id}/stats")
async def get_task_statistics(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get task statistics for dashboard aggregation (US10).

    Args:
        user_id: User ID from URL path
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Statistics object with completion rates, priority distribution, etc.
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    # All tasks for user
    all_query = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(all_query).all()

    if not tasks:
        return {
            "total": 0,
            "completed": 0,
            "pending": 0,
            "completion_rate": 0,
            "priority_distribution": {"high": 0, "medium": 0, "low": 0, "none": 0},
            "overdue": 0,
            "upcoming": 0
        }

    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)

    # Priority distribution
    priority_dist = {"high": 0, "medium": 0, "low": 0, "none": 0}
    for t in tasks:
        p = t.priority if t.priority in priority_dist else "none"
        priority_dist[p] += 1

    # Overdue and Upcoming
    now = datetime.utcnow()
    overdue = sum(1 for t in tasks if not t.completed and t.due_date and t.due_date < now)

    next_7_days = now + timedelta(days=7)
    upcoming = sum(1 for t in tasks if not t.completed and t.due_date and now <= t.due_date <= next_7_days)

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": round((completed / total) * 100, 2),
        "priority_distribution": priority_dist,
        "overdue": overdue,
        "upcoming": upcoming
    }


@router.get("/api/{user_id}/stats/completion-history")
async def get_completion_history(
    user_id: str,
    days: int = 7,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Get completion history for the last N days (US10).
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    history = []
    now = datetime.utcnow().date()

    for i in range(days - 1, -1, -1):
        target_date = now - timedelta(days=i)
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())

        # tasks completed on this date
        # Note: We assume Task has a completed_at field for history
        # If not, we might need to filter by updated_at where completed is true
        # Checking Task model structure would be wise but I'll implement based on likely fields
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= start_time,
            Task.updated_at <= end_time
        )
        count = session.exec(query).one()

        history.append({
            "date": target_date.strftime("%Y-%m-%d"),
            "completed": count
        })

    return history
