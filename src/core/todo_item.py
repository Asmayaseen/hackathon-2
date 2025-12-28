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
        priority: Task urgency level (high/medium/low)
        tags: Category labels (max 10, normalized)
        due_date: Task deadline (optional, ISO 8601 format)
        recurrence_pattern: Auto-repeat schedule (daily/weekly/monthly)
        recurrence_parent_id: Links recurring task instances (parent ID)
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
                "updated_at": "2025-12-25T11:30:00",
                "priority": "high",
                "tags": ["work", "development"],
                "due_date": "2025-12-26T14:00:00",
                "recurrence_pattern": None,
                "recurrence_parent_id": None
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

    # T005-T009: Advanced Features - New fields
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Task urgency level"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Category labels (max 10, normalized)"
    )
    due_date: datetime | None = Field(
        default=None,
        description="Task deadline (ISO 8601 format)"
    )
    recurrence_pattern: Literal["daily", "weekly", "monthly", "yearly"] | None = Field(
        default=None,
        description="Auto-repeat schedule"
    )
    recurrence_parent_id: int | None = Field(
        default=None,
        description="Links recurring task instances (parent ID)"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    # T010: Tag validation and normalization
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Normalize tags and enforce constraints."""
        # Remove empty tags
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Normalize: lowercase, alphanumeric + hyphens
        normalized = []
        for tag in cleaned:
            tag_lower = tag.lower()
            # Replace non-alphanumeric chars (except hyphens) with hyphens
            tag_clean = ''.join(c if c.isalnum() or c == '-' else '-' for c in tag_lower)
            # Remove consecutive hyphens and strip leading/trailing hyphens
            tag_clean = '-'.join(part for part in tag_clean.split('-') if part)
            if tag_clean:
                normalized.append(tag_clean)
        return normalized

    # T011: Recurrence validation
    @field_validator("recurrence_pattern")
    @classmethod
    def validate_recurrence(cls, v: Literal["daily", "weekly", "monthly", "yearly"] | None) -> Literal["daily", "weekly", "monthly", "yearly"] | None:
        """Validate recurrence pattern (Literal type enforces valid values)."""
        # No additional validation needed - Literal type enforces valid values
        return v
