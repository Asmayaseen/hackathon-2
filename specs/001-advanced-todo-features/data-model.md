# Data Model: Advanced Todo Features

**Feature**: 001-advanced-todo-features
**Date**: 2025-12-25
**Status**: Phase 1 Complete

## Entity Overview

### TodoItem (Extended)

**Purpose**: Represents a single task with organization, scheduling, and automation capabilities.

**Extends**: Current TodoItem model (src/core/todo_item.py)

**New Attributes**:
- `priority`: Task urgency level (high/medium/low)
- `tags`: Category labels for organization
- `due_date`: Optional deadline with time
- `recurrence_pattern`: Automatic repetition schedule
- `recurrence_parent_id`: Links recurring task instances

### FilterCriteria (New)

**Purpose**: Encapsulates search and filter parameters for task queries.

**Attributes**:
- `keyword`: Text search term
- `status`: Task completion state filter
- `priority`: Urgency level filter
- `tags`: Category label filters (AND logic)
- `date_from`, `date_to`: Date range filter

### SortOptions (New)

**Purpose**: Defines task list ordering preferences.

**Attributes**:
- `sort_by`: Field name (priority/due_date/created_at/title)
- `sort_order`: Direction (asc/desc)

## Entity Definitions

### TodoItem

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

class TodoItem(BaseModel):
    """
    Represents a single todo task with organization and scheduling features.

    Extends Phase I TodoItem with:
    - Priority levels for urgency management
    - Tags for categorization
    - Due dates for deadline tracking
    - Recurrence patterns for repeating tasks
    """

    # Existing attributes (Phase I)
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

    # New attributes (Phase I Extended - Advanced Features)
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Task urgency level"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Category labels (max 10)"
    )
    due_date: datetime | None = Field(
        default=None,
        description="Deadline with time (ISO 8601)"
    )
    recurrence_pattern: Literal["daily", "weekly", "monthly"] | None = Field(
        default=None,
        description="Automatic repetition schedule"
    )
    recurrence_parent_id: int | None = Field(
        default=None,
        description="ID of original recurring task"
    )

    # Configuration
    model_config = ConfigDict(
        frozen=False,  # Allow updates via model_copy()
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Weekly team meeting",
                "description": "Discuss project progress",
                "status": "pending",
                "priority": "high",
                "tags": ["work", "meetings"],
                "due_date": "2025-12-30T14:00:00",
                "recurrence_pattern": "weekly",
                "created_at": "2025-12-25T10:00:00",
                "updated_at": "2025-12-25T10:00:00"
            }
        }
    )

    # Validators (existing + new)
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """
        Validate and normalize tags.

        Rules:
        - Maximum 10 tags per task
        - Convert to lowercase
        - Trim whitespace
        - Allow alphanumeric and hyphens only
        - Remove empty strings
        """
        # Remove empty tags
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]

        # Enforce maximum
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Normalize: lowercase, alphanumeric + hyphens
        normalized = []
        for tag in cleaned:
            # Convert to lowercase
            tag_lower = tag.lower()
            # Remove invalid characters (keep alphanumeric and hyphens)
            tag_clean = ''.join(c if c.isalnum() or c == '-' else '-' for c in tag_lower)
            # Remove consecutive hyphens
            tag_clean = '-'.join(part for part in tag_clean.split('-') if part)
            if tag_clean:
                normalized.append(tag_clean)

        return normalized

    @field_validator("recurrence_pattern")
    @classmethod
    def validate_recurrence(cls, v: str | None, info) -> str | None:
        """
        Ensure recurrence pattern is only set when due_date exists.

        FR-030: Recurring tasks require due dates for recurrence calculation.
        """
        if v is not None:
            # Note: info.data contains already-validated fields
            # If due_date validation hasn't run yet, it will be in values
            due_date = info.data.get('due_date')
            if due_date is None:
                raise ValueError("Recurring tasks must have a due_date")
        return v
```

**Field Constraints**:

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| id | int | Yes | > 0 | Auto-assigned |
| title | str | Yes | 1-200 chars, no whitespace-only | - |
| description | str | No | Max 1000 chars | "" |
| status | Literal | No | pending\|in_progress\|completed | "pending" |
| priority | Literal | No | high\|medium\|low | "medium" |
| tags | list[str] | No | Max 10, lowercase, alphanumeric+hyphens | [] |
| due_date | datetime\|None | No | ISO 8601 format | None |
| recurrence_pattern | Literal\|None | No | daily\|weekly\|monthly, requires due_date | None |
| recurrence_parent_id | int\|None | No | Links to parent recurring task | None |
| created_at | datetime | No | Auto-generated | now() |
| updated_at | datetime | No | Auto-updated on model_copy() | now() |

**Business Rules**:

1. **Priority Default**: New tasks default to "medium" priority (FR-001)
2. **Tag Normalization**: Tags stored as lowercase alphanumeric with hyphens (FR-004)
3. **Tag Limit**: Maximum 10 tags per task (Edge case: Maximum tags)
4. **Recurrence Requirement**: Tasks with recurrence_pattern MUST have due_date (FR-030)
5. **Recurrence Parent**: Only recurring task instances have recurrence_parent_id set
6. **Immutability**: Use model_copy(update={...}) for updates to trigger validation

**State Transitions**:

```
pending → in_progress → completed
  ↓           ↓            ↓
  ←───────────┴────────────┘ (can update back to any state)

Special: completed (recurring) → auto-create new pending instance
```

### FilterCriteria

```python
from datetime import datetime

class FilterCriteria(BaseModel):
    """
    Encapsulates task filtering parameters.

    Supports multi-criteria filtering with AND logic:
    - Text search (keyword in title or description)
    - Status filter (pending/in_progress/completed)
    - Priority filter (high/medium/low)
    - Tag filter (all tags must match - AND logic)
    - Date range filter (created between dates)
    """

    keyword: str | None = Field(
        default=None,
        description="Search term for title/description (case-insensitive)"
    )
    status: Literal["pending", "in_progress", "completed"] | None = Field(
        default=None,
        description="Task completion state filter"
    )
    priority: Literal["high", "medium", "low"] | None = Field(
        default=None,
        description="Task urgency level filter"
    )
    tags: list[str] | None = Field(
        default=None,
        description="Category filters (AND logic - all must match)"
    )
    date_from: datetime | None = Field(
        default=None,
        description="Start of date range (inclusive)"
    )
    date_to: datetime | None = Field(
        default=None,
        description="End of date range (inclusive)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keyword": "meeting",
                "status": "pending",
                "priority": "high",
                "tags": ["work", "urgent"],
                "date_from": "2025-12-20T00:00:00",
                "date_to": "2025-12-31T23:59:59"
            }
        }
    )
```

**Filter Logic**:
- All filters use AND logic (task must match ALL specified criteria)
- Keyword search is case-insensitive substring match
- Tag filter requires ALL tags to be present (not ANY)
- Date range is inclusive on both ends
- Unspecified filters are ignored (None = no filter)

### SortOptions

```python
from typing import Literal

class SortOptions(BaseModel):
    """
    Defines task list ordering preferences.

    Supports sorting by:
    - priority: high → medium → low
    - due_date: earliest → latest (null dates last)
    - created_at: newest → oldest (or reverse)
    - title: alphabetical A-Z (or reverse)
    """

    sort_by: Literal["priority", "due_date", "created_at", "title"] = Field(
        default="created_at",
        description="Field to sort by"
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort direction (ascending or descending)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sort_by": "due_date",
                "sort_order": "asc"
            }
        }
    )
```

**Sort Behavior**:

| sort_by | asc | desc | Null Handling |
|---------|-----|------|---------------|
| priority | low → medium → high | high → medium → low | N/A (always has value) |
| due_date | earliest → latest | latest → earliest | Null dates always last |
| created_at | oldest → newest | newest → oldest | N/A (always has value) |
| title | A → Z | Z → A | N/A (always has value) |

## Relationships

### TodoItem Relationships

**Self-referencing (Recurring Tasks)**:
```
TodoItem (parent, recurrence_pattern="weekly")
  ├─> TodoItem (instance 1, recurrence_parent_id=parent.id)
  ├─> TodoItem (instance 2, recurrence_parent_id=parent.id)
  └─> TodoItem (instance 3, recurrence_parent_id=parent.id)
```

**Relationship Rules**:
- Original recurring task has `recurrence_pattern` set, `recurrence_parent_id=None`
- Instances have `recurrence_parent_id` pointing to original
- Instances inherit: title, description, priority, tags, recurrence_pattern
- Instances DO NOT inherit: id (new), status (reset to pending), created_at (new), updated_at (new)
- Instances calculate new due_date based on pattern

## Data Flow

### Task Creation Flow

```
User Input (CLI)
  ↓
Parse & Validate (Typer)
  ↓
Create TodoItem (Pydantic validation)
  ├─ Validate title (not empty)
  ├─ Validate tags (max 10, normalize)
  └─ Validate recurrence (requires due_date)
  ↓
Store in TodoManager._todos[id]
  ↓
Return TodoItem
```

### Filter Flow

```
User Input (CLI filters)
  ↓
Parse to FilterCriteria
  ↓
TodoManager.filter_todos(criteria)
  ├─ Extract all todos from dict
  ├─ Apply keyword filter (if specified)
  ├─ Apply status filter (if specified)
  ├─ Apply priority filter (if specified)
  ├─ Apply tags filter (AND logic, if specified)
  └─ Apply date range filter (if specified)
  ↓
Return filtered list[TodoItem]
```

### Sort Flow

```
Filtered List
  ↓
TodoManager.sort_todos(options)
  ├─ Extract sort field via getattr(todo, sort_by)
  ├─ Handle null due_dates (use datetime.max for nulls)
  └─ Apply Python sorted() with key and reverse
  ↓
Return sorted list[TodoItem]
```

### Recurring Task Completion Flow

```
User Completes Recurring Task
  ↓
TodoManager.complete_todo(id)
  ├─ Check if recurrence_pattern is set
  ├─ If yes:
  │   ├─ Calculate next due_date
  │   │   ├─ daily: due_date + 1 day
  │   │   ├─ weekly: due_date + 7 days
  │   │   └─ monthly: due_date + 1 month (same day)
  │   ├─ Create new TodoItem
  │   │   ├─ Inherit: title, description, priority, tags, recurrence_pattern
  │   │   ├─ New: id, status="pending", created_at, updated_at
  │   │   └─ Set: due_date=calculated, recurrence_parent_id=current.id
  │   └─ Add to _todos
  └─ Mark current task as completed
  ↓
Return completed TodoItem
```

## Validation Rules

### Cross-Field Validation

1. **Recurrence Requires Due Date** (FR-030):
   ```python
   if recurrence_pattern is not None and due_date is None:
       raise ValueError("Recurring tasks must have a due_date")
   ```

2. **Tag Count Limit**:
   ```python
   if len(tags) > 10:
       raise ValueError("Maximum 10 tags allowed per task")
   ```

3. **Status Enum**:
   ```python
   if status not in ["pending", "in_progress", "completed"]:
       raise ValueError("Invalid status")
   ```

### Field-Level Validation

1. **Title Non-Empty**:
   ```python
   if not title.strip():
       raise ValueError("Title cannot be empty or whitespace")
   ```

2. **Tag Normalization**:
   ```python
   normalized_tags = [tag.strip().lower() for tag in tags]
   # Remove non-alphanumeric except hyphens
   cleaned_tags = [''.join(c if c.isalnum() or c == '-' else '-' for c in tag) for tag in normalized_tags]
   ```

## Migration from Phase I

### Backward Compatibility

**Existing TodoItem instances**:
- All new fields have defaults (priority="medium", tags=[], due_date=None, recurrence_pattern=None, recurrence_parent_id=None)
- No migration required for in-memory Phase I data
- Phase I tests continue to pass with new fields using defaults

**Database Migration (Phase II)**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags JSONB DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20) NULL;
ALTER TABLE tasks ADD COLUMN recurrence_parent_id INTEGER NULL;

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

## Performance Considerations

### In-Memory (Phase I)

**Filtering Performance**: O(n) where n = number of tasks
- Acceptable for up to 1000 tasks (spec SC-002: <1 second)
- List comprehensions are optimized in CPython

**Sorting Performance**: O(n log n) Python sorted()
- Acceptable for 100+ tasks (spec SC-004: <500ms)

**Tag Lookup**: O(t * n) where t = number of filter tags, n = number of tasks
- `all(tag in todo.tags for tag in filter_tags)` checks each tag
- Acceptable for small tag counts (max 10 tags per task)

### Database (Phase II)

**Recommended Indexes**:
- `priority` (B-tree index for filtering)
- `due_date` (B-tree index for sorting and range queries)
- `tags` (GIN index for array contains queries)
- `status` (already indexed in Phase I)
- Composite index on `(status, priority, due_date)` for common filter combinations

## Examples

### Example 1: High-Priority Work Task with Due Date

```python
todo = TodoItem(
    id=1,
    title="Prepare Q4 presentation",
    description="Create slides for quarterly review meeting",
    status="pending",
    priority="high",
    tags=["work", "presentations", "q4"],
    due_date=datetime(2025, 12, 30, 14, 0),  # Dec 30, 2025 at 2:00 PM
    recurrence_pattern=None,
    recurrence_parent_id=None
)
```

### Example 2: Weekly Recurring Task

```python
# Original recurring task
recurring_todo = TodoItem(
    id=2,
    title="Team standup meeting",
    description="Daily standup at 9 AM",
    status="pending",
    priority="medium",
    tags=["work", "meetings"],
    due_date=datetime(2025, 12, 27, 9, 0),  # Next Monday at 9 AM
    recurrence_pattern="weekly",
    recurrence_parent_id=None
)

# After completion, auto-generated instance
next_instance = TodoItem(
    id=3,  # New ID
    title="Team standup meeting",  # Inherited
    description="Daily standup at 9 AM",  # Inherited
    status="pending",  # Reset
    priority="medium",  # Inherited
    tags=["work", "meetings"],  # Inherited
    due_date=datetime(2026, 1, 3, 9, 0),  # +7 days
    recurrence_pattern="weekly",  # Inherited
    recurrence_parent_id=2,  # Links to original
    created_at=datetime(2025, 12, 27, 9, 5),  # New timestamp
    updated_at=datetime(2025, 12, 27, 9, 5)  # New timestamp
)
```

### Example 3: Filtered Search

```python
criteria = FilterCriteria(
    keyword="meeting",
    status="pending",
    priority="high",
    tags=["work"],
    date_from=datetime(2025, 12, 20),
    date_to=datetime(2025, 12, 31)
)

# Returns all pending high-priority work tasks with "meeting" in title/description,
# created between Dec 20-31, 2025
filtered_todos = manager.filter_todos(criteria)
```

### Example 4: Sorted List

```python
options = SortOptions(
    sort_by="due_date",
    sort_order="asc"
)

# Returns tasks sorted by due date (earliest first), null dates last
sorted_todos = manager.sort_todos(filtered_todos, options)
```

## Summary

**New Fields**: 5 (priority, tags, due_date, recurrence_pattern, recurrence_parent_id)
**New Entities**: 2 (FilterCriteria, SortOptions)
**Validation Rules**: 6 (title, tags, recurrence, priority, status, tag count)
**Relationships**: 1 (self-referencing for recurring tasks)

**Storage**: In-memory dict (Phase I), PostgreSQL JSONB (Phase II)
**Performance**: O(n) filtering, O(n log n) sorting - acceptable for spec targets

**Ready for**: Phase 2 (Contract generation and tasks breakdown)
