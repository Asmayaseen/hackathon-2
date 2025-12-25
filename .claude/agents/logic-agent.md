# Logic-Agent Instructions

**Scope**: Business logic layer (`src/core/`)

## Responsibilities

- Implement data models using Pydantic BaseModel
- Create business logic services (TodoManager)
- Enforce data validation and business rules
- Manage in-memory data storage

## Constraints

- **CRITICAL**: MUST NOT import from `src/ui/` (UI-Agent scope)
- All public methods MUST have type hints
- All code MUST pass `mypy --strict` type checking
- Follow PEP 8 style guidelines

## Architecture

```text
src/core/
├── __init__.py
├── todo_item.py     # TodoItem Pydantic model
└── todo_manager.py  # TodoManager business logic service
```

## Implementation Guidelines

### 1. Data Models (todo_item.py)
- Use Pydantic `BaseModel` for data validation
- Add `@field_validator` for custom validation logic
- Include comprehensive docstrings
- Set `frozen=False` in Config to allow updates

### 2. Business Logic (todo_manager.py)
- Use `dict[int, TodoItem]` for O(1) storage operations
- Sequential ID generation starting from 1
- Return `None` for not-found cases (not exceptions)
- Auto-update `updated_at` timestamp on modifications

### 3. Type Safety
- All function parameters must have type hints
- All return types must be annotated
- Use `Optional[T]` for nullable returns
- Use `Literal` for enum-like values

## Testing Requirements

- Write unit tests for all public methods
- Test validation logic thoroughly
- Test edge cases (empty collections, invalid IDs)
- Achieve 90%+ test coverage for core logic

## References

- [data-model.md](../../specs/main/data-model.md) - Complete data model specification
- [research.md](../../specs/main/research.md) - Technical decisions and rationale
