# Research: Advanced Todo Features Implementation

**Feature**: 001-advanced-todo-features
**Date**: 2025-12-25
**Status**: Complete

## Executive Summary

Phase I codebase analysis reveals a well-structured foundation with clean separation between business logic (core/) and UI (ui/). The existing Pydantic + Typer + Rich architecture is ideally suited for extension with advanced features. All patterns needed for priorities, tags, search, filter, sort, due dates, and recurring tasks already exist in the codebase.

## Technical Context Resolution

### Language & Version
**Decision**: Python 3.12+
**Rationale**: Current `pyproject.toml` specifies `requires-python = ">=3.12"`. Phase I already uses Python 3.12 patterns (union types with `|`, `datetime` enhancements).
**Alternatives considered**: Python 3.13 (mentioned in constitution), but 3.12 is more widely adopted and sufficient.

### Primary Dependencies
**Decision**: Maintain existing stack (Pydantic 2.0+, Typer 0.15+, Rich 13.7+)
**Rationale**:
- Pydantic 2.x provides `Field()`, `Literal`, `field_validator` patterns perfect for extending TodoItem
- Typer's type-hint-driven CLI aligns with adding new options
- Rich's table formatting easily extends with new columns
**Alternatives considered**: None - constitution mandates this stack for Phase I.

### Storage Strategy
**Decision**: In-memory storage (`dict[int, TodoItem]`) maintained for Phase I
**Rationale**: Constitution mandates in-memory storage for Phase I. Current `TodoManager._todos` dict provides O(1) lookups and efficient filtering (O(n)).
**Migration Path**: Phase II will move to Neon PostgreSQL - current architecture separates business logic (core/) from storage, enabling clean migration.

### Testing Framework
**Decision**: pytest with existing patterns (91 tests, 17 test classes)
**Rationale**: Comprehensive test suite already exists with patterns for:
- Pydantic model validation (TestTodoItemValidation)
- Manager CRUD operations (TestTodoManagerAdd, Update, Delete)
- CLI command testing with CliRunner (TestCliAdd, List, Update)
**Coverage**: Business logic fully covered; extend existing test classes for new features.

### Type Checking
**Decision**: mypy --strict (already enforced)
**Rationale**: `pyproject.toml` has `[tool.mypy]` with `strict = true`, `disallow_untyped_defs = true`, and pydantic plugin enabled.
**Impact**: All new methods must include full type hints including return types.

### Performance Targets
**Decision**:
- Search/filter: <1 second for 1000 tasks
- Sort: <500ms for 100+ tasks
- Reminder check: <5 seconds on startup
**Rationale**: From spec success criteria (SC-002, SC-004, SC-005). In-memory operations easily meet these targets.
**Validation**: Implement performance tests in `tests/test_performance.py`.

## Key Architectural Patterns Identified

### 1. Pydantic Model Extension Pattern

**Current Pattern** (todo_item.py:7-48):
```python
class TodoItem(BaseModel):
    id: int = Field(gt=0, description="Unique identifier")
    title: str = Field(min_length=1, max_length=200)
    status: Literal["pending", "in_progress", "completed"] = Field(default="pending")

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
```

**Extension for Advanced Features**:
- Use `Literal["high", "medium", "low"]` for priority enum
- Use `list[str]` with `default_factory=list` for tags
- Use `datetime | None` for optional due_date
- Use `Literal["daily", "weekly", "monthly"] | None` for recurrence
- Add `field_validator` for tags (max 10, lowercase, sanitize)

### 2. TodoManager Filtering Pattern

**Current Pattern** (todo_manager.py:55-68):
```python
def list_todos(self, status: Optional[str] = None) -> list[TodoItem]:
    todos = list(self._todos.values())
    if status:
        todos = [t for t in todos if t.status == status]
    return sorted(todos, key=lambda t: t.created_at)
```

**Extension for Multi-Criteria Filtering**:
- Build filter criteria dict from optional parameters
- Apply filters sequentially with AND logic (list comprehensions)
- Support keyword search (case-insensitive, title + description)
- Support tag filtering (all tags must match)
- Support date range filtering (created_at between dates)

### 3. Typer CLI Command Pattern

**Current Pattern** (cli.py:23-41):
```python
@app.command()
def add(
    title: str = typer.Argument(..., help="Todo title"),
    description: str = typer.Option("", "--description", "-d")
) -> None:
    """Add a new todo."""
    try:
        todo = manager.add_todo(title, description)
        console.print("[green][OK][/green] Todo added!")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e.errors()[0]['msg']}")
        raise typer.Exit(1)
```

**Extension for New Options**:
- Add `--priority/-p` option with validation
- Add `--tags/-t` option (comma-separated string, parse to list)
- Add `--due-date/-d` option (ISO format string, parse to datetime)
- Add `--recurrence/-r` option (daily/weekly/monthly enum)
- Maintain error handling pattern with ValidationError + typer.Exit(1)

### 4. Rich Table Display Pattern

**Current Pattern** (cli.py:46-67):
```python
table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID", style="dim", width=6)
table.add_column("Title", style="cyan")
table.add_column("Status", justify="center")

for todo in todos:
    color = {"completed": "green", "in_progress": "yellow", "pending": "white"}[todo.status]
    table.add_row(
        str(todo.id),
        todo.title,
        f"[{color}]{todo.status}[/{color}]"
    )
console.print(table)
```

**Extension for New Columns**:
- Add "Priority" column with color coding (high=red, medium=yellow, low=green)
- Add "Tags" column with space-separated `#tag` format
- Add "Due Date" column with overdue highlighting (red bold for past dates)
- Add "Recurrence" column with pattern display (daily/weekly/monthly icon)
- Maintain 80-column terminal width (spec SC-008)

## Technology Decisions

### Priority Field Implementation
**Decision**: `Literal["high", "medium", "low"]` with default="medium"
**Rationale**:
- Matches spec FR-001 (three priority levels)
- Provides compile-time type checking (mypy --strict)
- Auto-generates JSON schema for API documentation (Phase II prep)
**Alternatives considered**: String enum - rejected due to less type safety

### Tags Storage Format
**Decision**: `list[str]` with lowercase alphanumeric + hyphens
**Rationale**:
- Native list type (no external dependencies)
- Easy filtering with `all(tag in todo.tags for tag in filter_tags)`
- Lowercase normalization prevents "Work" vs "work" duplicates
**Alternatives considered**: Set[str] - rejected as Pydantic serialization prefers lists

### Date/Time Handling
**Decision**: Python `datetime` with system local timezone
**Rationale**:
- Spec assumption #3: System local timezone only (no multi-timezone)
- Spec FR-019: Store as datetime objects with timezone awareness
- Use `datetime.now()` for current time, `strptime()` for parsing ISO format
**Alternatives considered**: `pendulum` library - rejected to avoid new dependency

### Recurring Task Mechanism
**Decision**: Store recurrence pattern + parent ID; generate new instance on completion
**Rationale**:
- Spec FR-026: Auto-create new instance when recurring task completed
- Spec FR-027: Calculate next date from original schedule, not completion time
- Parent ID links instances for potential future features (view series)
**Implementation**: Add `recurrence_pattern` and `recurrence_parent_id` nullable fields

### Reminder System
**Decision**: In-memory timer check on list/startup operations
**Rationale**:
- Spec assumption #2: Console app with in-memory storage, reminders only while running
- Spec FR-022: Display console notifications for tasks due within 30 minutes
- Check on startup (FR-021) and during list operations
**Alternatives considered**: Background thread - deferred to avoid complexity for Phase I

### Search Algorithm
**Decision**: Case-insensitive substring matching with `in` operator
**Rationale**:
- Spec FR-006: Case-insensitive keyword search across title and description
- Python's `str.lower()` + `in` operator is simple and fast for in-memory lists
- Meets performance target (SC-002: <1 second for 1000 tasks)
**Alternatives considered**: Regex matching - unnecessary complexity for substring search

### Sort Implementation
**Decision**: Python `sorted()` with `key=lambda` and dynamic `getattr()`
**Rationale**:
- Spec FR-013 to FR-016: Sort by priority, due_date, created_at, title
- Dynamic sort field via `sorted(todos, key=lambda t: getattr(t, sort_field))`
- Null handling for due_date: Use `or datetime.max` to sort nulls last
**Implementation**: Reverse parameter for asc/desc ordering

## Best Practices

### Pydantic Validation
**Practice**: Use `field_validator` for complex validation
**Example**: Tags validator to enforce max 10 tags, lowercase conversion, sanitization
**Benefit**: Validation errors caught at model creation, not during business logic

### CLI Error Handling
**Practice**: Catch `ValidationError` separately from general exceptions
**Example**: Extract first error message with `e.errors()[0]['msg']` for user-friendly output
**Benefit**: Clear error messages guide users to fix input

### Type Hints
**Practice**: Full type annotations for all functions, including return types
**Example**: `def filter_todos(...) -> list[TodoItem]:`
**Benefit**: Passes mypy --strict validation, prevents runtime type errors

### Testing Strategy
**Practice**: Extend existing test classes; one test class per feature area
**Example**: TestTodoManagerFilter, TestTodoManagerSort, TestCliSearch
**Benefit**: Maintains existing test organization, easy to run feature-specific tests

### Rich Formatting
**Practice**: Use color dictionaries for status-based coloring
**Example**: `priority_colors = {"high": "red", "medium": "yellow", "low": "green"}`
**Benefit**: Centralizes color choices, easy to update styling

## Integration Patterns

### Adding New Fields to TodoItem
**Pattern**: Define field with constraints, add validator if needed
**Steps**:
1. Add field to TodoItem class with `Field()` constraints
2. Add `field_validator` classmethod if complex validation needed
3. Update `model_config` JSON schema example
4. Run mypy to verify type hints
5. Add tests to `test_todo_item.py::TestTodoItemValidation`

### Extending TodoManager Methods
**Pattern**: Add new method following existing signatures
**Steps**:
1. Define method with typed parameters and return type
2. Extract todos list from `self._todos.values()`
3. Apply filters/transformations with list comprehensions
4. Return sorted list if applicable
5. Add tests to appropriate `test_todo_manager.py::Test*` class

### Adding CLI Commands
**Pattern**: Create `@app.command()` function with typed parameters
**Steps**:
1. Define command function with Typer decorators
2. Add Arguments (positional) and Options (named flags)
3. Wrap in try-except for ValidationError and general errors
4. Use Rich console.print for output
5. Add tests to appropriate `test_cli.py::TestCli*` class

## Risk Mitigation

### Risk: Due Date Parsing Errors
**Mitigation**: Provide clear format guidance in error messages
**Implementation**: Show example format "YYYY-MM-DD HH:MM" in help text and error output

### Risk: Tag Input Inconsistency
**Mitigation**: Sanitize tags on input (lowercase, trim, filter empty)
**Implementation**: `field_validator("tags")` normalizes all tags before storage

### Risk: Reminder Notification Spam
**Mitigation**: Only notify for tasks due within 30 minutes (not all overdue)
**Implementation**: Filter `due_date` between `now()` and `now() + timedelta(minutes=30)`

### Risk: Sort Field Attribute Errors
**Mitigation**: Validate sort_by parameter against allowed fields
**Implementation**: CLI validates against `["priority", "due_date", "created_at", "title"]` enum

### Risk: Recurring Task Infinite Loops
**Mitigation**: Only create one new instance per completion
**Implementation**: Check if next instance already exists before creating (by parent_id + due_date)

## Performance Considerations

### Filtering Performance
**Current**: O(n) linear scan of task list
**Acceptable**: Meets spec SC-002 (<1 second for 1000 tasks)
**Future**: Phase II database migration will use indexed queries

### Sorting Performance
**Current**: O(n log n) Python sorted()
**Acceptable**: Meets spec SC-004 (<500ms for 100+ tasks)
**Optimization**: Not needed for in-memory Phase I

### Reminder Check Performance
**Current**: O(n) scan on startup and list operations
**Acceptable**: Meets spec SC-005 (<5 seconds on startup)
**Optimization**: Cache next reminder time to avoid full scan

## Dependencies & Constraints

### No New Dependencies
**Constraint**: Constitution prohibits new dependencies beyond current stack
**Verification**: All features implementable with Pydantic, Typer, Rich, Python stdlib
**Stdlib modules used**: `datetime` (dates), `typing` (type hints)

### In-Memory Storage Limitation
**Constraint**: Phase I must use in-memory storage (constitution)
**Impact**: Reminders only work while app running (spec assumption #2)
**Mitigation**: Check for missed reminders on app startup (spec FR-021)

### Type Safety Requirement
**Constraint**: Must pass mypy --strict (constitution + existing pyproject.toml)
**Impact**: All functions require full type annotations
**Validation**: CI runs `mypy src/ --strict` (add to GitHub Actions if needed)

## Conclusion

The Phase I codebase provides an excellent foundation for advanced features. All required patterns (Pydantic validation, Typer CLI, Rich formatting) are already established. Extension points are clear:

1. **TodoItem**: Add 4 new fields (priority, tags, due_date, recurrence)
2. **TodoManager**: Add 3 new methods (filter_todos, search_todos, check_reminders)
3. **CLI**: Extend 2 commands (add, list) and add 1 new command (search)
4. **Tests**: Add 6 new test classes (one per major feature area)

No architectural changes required. No new dependencies needed. Clean separation between core/ and ui/ enables independent testing and future Phase II migration.

**Status**: Ready for Phase 1 (Data Model & Contracts)
