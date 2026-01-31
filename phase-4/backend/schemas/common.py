"""
Common/Shared Schemas.

Phase 4: Kubernetes Deployment
"""
from datetime import datetime
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    service: str
    version: str
    timestamp: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Schema for generic success response."""
    success: bool = True
    message: str
