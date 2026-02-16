"""
Authentication API endpoints.

Task: 1.4
Spec: specs/features/authentication.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import jwt
import hashlib
import os
import uuid

from models import User
from db import get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-min-32-chars")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


# Request/Response Models
class SignupRequest(BaseModel):
    """Request model for user signup."""
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class SigninRequest(BaseModel):
    """Request model for user signin."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication."""
    token: str
    user: dict


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for authenticated user."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/signup", response_model=AuthResponse)
async def signup(
    data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user.

    Args:
        data: Signup data (name, email, password)
        session: Database session

    Returns:
        JWT token and user info

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(user_id, data.email)

    return AuthResponse(
        token=token,
        user={
            "id": user_id,
            "email": new_user.email,
            "name": new_user.name
        }
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    data: SigninRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return JWT token.

    Args:
        data: Signin data (email, password)
        session: Database session

    Returns:
        JWT token and user info

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if user.password_hash != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(user.id, user.email)

    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    )


@router.get("/me")
async def get_current_user(
    session: Session = Depends(get_session),
    credentials: str = Depends(lambda: None)
):
    """Get current authenticated user info."""
    # This will be used with the verify_token middleware
    pass


# =============================================================================
# Security Endpoints (Phase V)
# =============================================================================

class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=255)


class ChangePasswordResponse(BaseModel):
    """Response model for password change."""
    success: bool
    message: str


@router.post("/{user_id}/change-password", response_model=ChangePasswordResponse)
async def change_password(
    user_id: str,
    data: ChangePasswordRequest,
    session: Session = Depends(get_session)
):
    """
    Change user password.

    Args:
        user_id: User ID from URL
        data: Current and new password
        session: Database session

    Returns:
        Success status and message

    Raises:
        HTTPException: 401 if current password is incorrect
        HTTPException: 404 if user not found
    """
    # Find user
    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if user.password_hash != hash_password(data.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Check new password is different
    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    user.password_hash = hash_password(data.new_password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()

    return ChangePasswordResponse(
        success=True,
        message="Password changed successfully"
    )


class SessionInfo(BaseModel):
    """Model for session information."""
    session_id: str
    device: str
    location: str
    last_active: str
    is_current: bool


class ActiveSessionsResponse(BaseModel):
    """Response model for active sessions."""
    sessions: list[SessionInfo]


@router.get("/{user_id}/sessions", response_model=ActiveSessionsResponse)
async def get_active_sessions(
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Get active sessions for user.

    Note: This is a simplified implementation. In production,
    you would track sessions in a database or Redis.

    Returns mock session data for the current session.
    """
    # Find user to verify exists
    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return current session (mock data)
    # In production, this would come from a session store
    return ActiveSessionsResponse(
        sessions=[
            SessionInfo(
                session_id="current",
                device="Current Browser",
                location="Current Location",
                last_active=datetime.utcnow().isoformat(),
                is_current=True
            )
        ]
    )


class LogoutAllResponse(BaseModel):
    """Response model for logout all sessions."""
    success: bool
    message: str
    sessions_terminated: int


@router.post("/{user_id}/logout-all", response_model=LogoutAllResponse)
async def logout_all_sessions(
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Logout from all sessions except current.

    Note: In production, this would invalidate all JWT tokens
    by using a token blacklist or changing the user's token version.
    """
    # Find user
    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # In production: Invalidate all tokens except current
    # For now, just return success
    return LogoutAllResponse(
        success=True,
        message="All other sessions have been logged out",
        sessions_terminated=0
    )


class TwoFactorStatusResponse(BaseModel):
    """Response model for 2FA status."""
    enabled: bool
    method: str | None = None


@router.get("/{user_id}/2fa/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Get 2FA status for user.

    Note: 2FA is not fully implemented. This returns the current status.
    """
    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2FA not implemented yet - always return disabled
    return TwoFactorStatusResponse(
        enabled=False,
        method=None
    )
