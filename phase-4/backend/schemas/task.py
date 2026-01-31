"""
Task Schemas for API validation.

Phase 4: Kubernetes Deployment
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = Field(default="none", pattern="^(high|medium|low|none)$")
    tags: List[str] = Field(default_factory=list)
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(high|medium|low|none)$")
    tags: Optional[List[str]] = None
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    priority: str
    tags: List[str]
    recurrence_pattern: Optional[str]
    reminder_offset: Optional[int]
    is_recurring: bool

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
