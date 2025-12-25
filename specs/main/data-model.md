# Data Model - Phase I Console Todo App

**Date**: 2025-12-25
**Status**: Complete
**Related**: [plan.md](plan.md) | [research.md](research.md)

## Overview

This document defines the data model for Phase I console todo application. The model is designed for in-memory storage with clear migration path to Neon PostgreSQL (SQLModel) in Phase II.

## Entities

### TodoItem

**Description**: Core entity representing a single todo task with status tracking and timestamps.

**Location**: `src/core/todo_item.py`

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | `int` | Required, unique, > 0 | Auto-assigned | Sequential identifier starting from 1 |
| `title` | `str` | Required, 1-200 chars | - | Brief task description |
| `description` | `str` | Optional, max 1000 chars | `""` (empty) | Detailed task description |
| `status` | `Literal["pending", "in_progress", "completed"]` | Required, enum | `"pending"` | Current task state |
| `created_at` | `datetime` | Required, auto-set | `datetime.now()` | Timestamp of creation |
| `updated_at` | `datetime` | Required, auto-set | `datetime.now()` | Timestamp of last modification |

**Validation Rules**:
- `title` must not be empty or whitespace-only
- `title` max length: 200 characters (prevents terminal overflow)
- `description` max length: 1000 characters
- `status` must be one of: `"pending"`, `"in_progress"`, `"completed"`
- `created_at` cannot be modified after creation
- `updated_at` auto-updates on any field change

**State Transitions**:

```text
pending → in_progress → completed
  ↓           ↓              ↓
  ↓           ↓              ↓
  +---------------------------+
          (any status)
```

Valid transitions:
- `pending` → `in_progress` (start working)
- `pending` → `completed` (quick complete)
- `in_progress` → `completed` (finish work)
- Any status → Any status (allow corrections)

**Pydantic Model**:

```python
# src/core/todo_item.py
from pydantic import BaseModel, Field, field_validator
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

    class Config:
        """Pydantic configuration."""
        frozen = False  # Allow field updates via TodoManager
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Implement TodoItem model",
                "description": "Create Pydantic model with validation",
                "status": "completed",
                "created_at": "2025-12-25T10:00:00",
                "updated_at": "2025-12-25T11:30:00"
            }
        }
```

**Phase II Migration Path**:

```python
# Phase II: SQLModel (Pydantic + SQLAlchemy)
from sqlmodel import SQLModel, Field
from datetime import datetime

class TodoItem(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True)
    description: str = Field(default="", max_length=1000)
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Phase II additions:
    user_id: int = Field(foreign_key="users.id")  # Multi-user support
```

---

### TodoManager

**Description**: Business logic service managing the in-memory collection of TodoItem instances. Provides CRUD operations and enforces business rules.

**Location**: `src/core/todo_manager.py`

**Responsibilities**:
- Create new todos with auto-assigned IDs
- Retrieve todos by ID or list all
- Update todo fields (title, description, status)
- Delete todos by ID
- Manage sequential ID generation
- Enforce validation rules via Pydantic

**Storage Structure**:
- **Type**: `dict[int, TodoItem]`
- **Key**: TodoItem.id (integer)
- **Value**: TodoItem instance
- **ID Generation**: Sequential integers starting from 1

**Public API**:

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `add_todo` | `title: str, description: str = ""` | `TodoItem` | Create new todo with auto-assigned ID |
| `get_todo` | `todo_id: int` | `TodoItem \| None` | Retrieve todo by ID (None if not found) |
| `list_todos` | `status: str \| None = None` | `list[TodoItem]` | List all todos, optionally filtered by status |
| `update_todo` | `todo_id: int, **updates` | `TodoItem \| None` | Update todo fields (None if not found) |
| `complete_todo` | `todo_id: int` | `TodoItem \| None` | Set status to "completed" |
| `delete_todo` | `todo_id: int` | `bool` | Delete todo (True if deleted, False if not found) |

**Business Rules**:
- IDs are sequential and never reused (even after deletion)
- Title validation enforced by Pydantic on creation and update
- `updated_at` automatically set to current time on any modification
- `created_at` is immutable (cannot be changed after creation)
- Delete operation is idempotent (returns False if already deleted)

**Implementation Skeleton**:

```python
# src/core/todo_manager.py
from typing import Optional
from datetime import datetime
from .todo_item import TodoItem

class TodoManager:
    """
    Manages the in-memory collection of todos.

    Provides CRUD operations with automatic ID assignment and
    validation via Pydantic models.
    """

    def __init__(self) -> None:
        """Initialize empty todo collection."""
        self._todos: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        """
        Create a new todo with auto-assigned ID.

        Args:
            title: Task title (1-200 chars)
            description: Optional task details (max 1000 chars)

        Returns:
            Created TodoItem

        Raises:
            ValidationError: If title is invalid
        """
        todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Retrieve todo by ID. Returns None if not found."""
        return self._todos.get(todo_id)

    def list_todos(self, status: Optional[str] = None) -> list[TodoItem]:
        """
        List all todos, optionally filtered by status.

        Args:
            status: Optional filter ("pending", "in_progress", "completed")

        Returns:
            List of TodoItem instances (may be empty)
        """
        todos = list(self._todos.values())
        if status:
            todos = [t for t in todos if t.status == status]
        return sorted(todos, key=lambda t: t.created_at)

    def update_todo(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[TodoItem]:
        """
        Update todo fields. Returns None if not found.

        Args:
            todo_id: ID of todo to update
            title: New title (if provided)
            description: New description (if provided)
            status: New status (if provided)

        Returns:
            Updated TodoItem or None if not found

        Raises:
            ValidationError: If updates violate constraints
        """
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        # Update fields (Pydantic will validate)
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status

        # Always update timestamp
        update_data["updated_at"] = datetime.now()

        # Create updated todo (Pydantic validation)
        updated_todo = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def complete_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Set todo status to 'completed'. Returns None if not found."""
        return self.update_todo(todo_id, status="completed")

    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete todo by ID.

        Returns:
            True if deleted, False if not found
        """
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
```

---

## Relationships

**Phase I**: No relationships (single entity model)

**Phase II**: Relationships will be added for multi-user support:
- `TodoItem.user_id` → `User.id` (many-to-one)
- Future: `TodoItem.tags` → `Tag` (many-to-many)

---

## Invariants

1. **Unique IDs**: Every TodoItem has a unique `id` within the collection
2. **Sequential IDs**: IDs are assigned sequentially (1, 2, 3, ...) and never reused
3. **Non-Empty Titles**: `title` field cannot be empty or whitespace-only
4. **Valid Status**: `status` must be one of the three allowed values
5. **Immutable created_at**: `created_at` timestamp never changes after creation
6. **Auto-Updated updated_at**: `updated_at` automatically set on any modification

---

## Testing Requirements

### Unit Tests for TodoItem

```python
# tests/test_todo_item.py
def test_create_valid_todo():
    """TodoItem with valid fields should be created successfully."""

def test_title_cannot_be_empty():
    """TodoItem creation should fail if title is empty."""

def test_title_max_length():
    """TodoItem creation should fail if title exceeds 200 chars."""

def test_default_status_is_pending():
    """New TodoItem should have status='pending' by default."""

def test_timestamps_auto_set():
    """created_at and updated_at should be auto-set on creation."""
```

### Unit Tests for TodoManager

```python
# tests/test_todo_manager.py
def test_add_todo_assigns_sequential_id():
    """IDs should be assigned sequentially (1, 2, 3, ...)."""

def test_add_todo_returns_created_item():
    """add_todo should return the created TodoItem."""

def test_get_todo_returns_none_for_missing_id():
    """get_todo should return None if ID doesn't exist."""

def test_list_todos_returns_empty_list_initially():
    """list_todos should return [] when no todos exist."""

def test_list_todos_filters_by_status():
    """list_todos(status='completed') should only return completed todos."""

def test_update_todo_modifies_fields():
    """update_todo should modify specified fields and update timestamp."""

def test_complete_todo_sets_status():
    """complete_todo should set status to 'completed'."""

def test_delete_todo_removes_item():
    """delete_todo should remove item and return True."""

def test_delete_todo_returns_false_for_missing_id():
    """delete_todo should return False if ID doesn't exist."""

def test_ids_not_reused_after_deletion():
    """Deleting a todo should not allow its ID to be reused."""
```

---

**Data Model Complete**: Ready for contract definition and CLI implementation.
