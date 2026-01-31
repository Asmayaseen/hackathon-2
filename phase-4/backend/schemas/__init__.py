"""
Pydantic Schemas for API Request/Response Validation.

Phase 4: Kubernetes Deployment
Separates API schemas from database models for clean architecture.

Organization:
- task.py: Task-related schemas
- user.py: User and auth schemas
- chat.py: AI chatbot schemas
- common.py: Shared schemas (pagination, responses)
"""
from .task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from .user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from .common import (
    PaginatedResponse,
    HealthResponse,
    ErrorResponse,
)

__all__ = [
    # Task schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    # Common schemas
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
]
