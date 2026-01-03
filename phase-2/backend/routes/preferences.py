"""
User Preferences API (US9).

Task: US9 - Settings management
Spec: specs/database/schema.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from models import UserPreferences
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["preferences"])


class PreferencesUpdate(BaseModel):
    """Request model for updating user preferences."""
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    notification_sound: Optional[bool] = None
    default_priority: Optional[str] = None
    default_view: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/{user_id}/preferences")
async def get_user_preferences(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Retrieve user preferences (US9).

    Args:
        user_id: User ID from URL path
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        UserPreferences object
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    # Find preferences or create default
    prefs = session.get(UserPreferences, user_id)
    if not prefs:
        prefs = UserPreferences(user_id=user_id)
        session.add(prefs)
        session.commit()
        session.refresh(prefs)

    return prefs


@router.put("/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    data: PreferencesUpdate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Update user preferences (US9).

    Args:
        user_id: User ID from URL path
        data: Preferences to update
        session: Database session
        authenticated_user_id: User ID from JWT token

    Returns:
        Updated UserPreferences object
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    # Find existing preferences
    prefs = session.get(UserPreferences, user_id)
    if not prefs:
        prefs = UserPreferences(user_id=user_id)

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prefs, key, value)

    prefs.updated_at = datetime.utcnow()

    session.add(prefs)
    session.commit()
    session.refresh(prefs)

    return prefs
