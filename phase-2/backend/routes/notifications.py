"""
Notifications API (US8).

Task: US8 - Scheduled reminder retrieval
Spec: specs/database/schema.md
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from models import Notification
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/{user_id}/notifications")
async def get_notifications(
    user_id: str,
    unread_only: bool = Query(True, alias="unread"),
    limit: int = Query(20, le=50),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Retrieve user notifications (US8).

    Args:
        user_id: User ID from URL path
        unread_only: Filter by unsent/unread status
        limit: Number of records to return
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        List of notifications
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' notifications"
        )

    # Build query
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.sent == False)

    query = query.order_by(Notification.scheduled_time.desc()).limit(limit)

    notifications = session.exec(query).all()

    return {
        "notifications": notifications,
        "count": len(notifications)
    }


@router.patch("/{user_id}/notifications/{notification_id}/read")
async def mark_notification_as_read(
    user_id: str,
    notification_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """Mark a notification as read/sent."""
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.sent = True
    notification.sent_at = datetime.utcnow()
    session.add(notification)
    session.commit()
    session.refresh(notification)

    return notification
