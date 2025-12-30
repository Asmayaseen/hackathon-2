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
