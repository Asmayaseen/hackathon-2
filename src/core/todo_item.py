# T014, T015, T016: TodoItem Pydantic model with validation
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Literal


class TodoItem(BaseModel):
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-assigned by TodoManager)
        title: Brief task description (1-200 chars)
        description: Detailed task description (optional, max 1000 chars)
        status: Current state (pending/in_progress/completed)
        created_at: Creation timestamp (auto-set)
        updated_at: Last modification timestamp (auto-set)
    """

    model_config = ConfigDict(
        frozen=False,  # Allow field updates via TodoManager
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Implement TodoItem model",
                "description": "Create Pydantic model with validation",
                "status": "completed",
                "created_at": "2025-12-25T10:00:00",
                "updated_at": "2025-12-25T11:30:00"
            }
        }
    )

    id: int = Field(gt=0, description="Unique identifier")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=1000, description="Task details")
    status: Literal["pending", "in_progress", "completed"] = Field(
        default="pending",
        description="Current task state"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last modification timestamp"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
