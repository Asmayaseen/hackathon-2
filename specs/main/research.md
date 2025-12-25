# Phase 0: Research - Phase I Console Todo App

**Date**: 2025-12-25
**Status**: Complete
**Related**: [plan.md](plan.md) | [../00-architecture.md](../00-architecture.md)

## Overview

This document consolidates research findings for key technical decisions in Phase I implementation. All "NEEDS CLARIFICATION" items from the technical context are resolved here.

## Research Topics

### 1. Data Model: Pydantic vs Python Dataclass

**Decision**: Use **Pydantic BaseModel**

**Rationale**:
- **JSON Serialization**: Pydantic provides built-in `.model_dump()` and `.model_validate()` for JSON conversion (critical for Phase II API)
- **Validation**: Automatic validation of field types and constraints
- **SQLModel Migration**: Pydantic is the foundation for SQLModel (used in Phase II with Neon PostgreSQL)
- **Type Safety**: Full mypy --strict compliance with automatic type checking
- **Future-Proofing**: Zero refactoring needed when migrating TodoItem to SQLModel in Phase II

**Alternatives Considered**:
- **Python dataclass**: Simpler, stdlib-only, but requires manual JSON serialization and no built-in validation
- **attrs**: Third-party, powerful, but adds dependency and doesn't align with Phase II stack (SQLModel)

**Code Pattern**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class TodoItem(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = False  # Allow updates via todo_manager
```

**References**:
- Architecture spec recommendation: "Start with Pydantic to ease Phase II migration"
- Pydantic docs: https://docs.pydantic.dev/latest/
- SQLModel (Pydantic + SQLAlchemy): https://sqlmodel.tiangolo.com/

---

### 2. CLI Framework: Typer vs Argparse

**Decision**: Use **Typer**

**Rationale**:
- **Type Hints**: Automatic argument parsing from function signatures (no manual parser configuration)
- **Auto-Generated Help**: Rich help text generated from docstrings and type hints
- **Better Error Messages**: User-friendly validation errors out of the box
- **Rich Integration**: Built-in support for rich output (same maintainer: Sebastián Ramírez)
- **Modern Python**: Aligns with Pydantic philosophy (type hints over configuration)
- **Testing**: Easier to test with `CliRunner` utility

**Alternatives Considered**:
- **argparse**: Stdlib, zero dependencies, but verbose and lacks modern Python conventions
- **click**: Mature, powerful, but decorator-heavy and less type-safe than Typer

**Code Pattern**:
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def add(
    title: str = typer.Argument(..., help="Todo title"),
    description: str = typer.Option("", help="Optional description")
):
    """Add a new todo item."""
    # Implementation delegates to TodoManager
    pass

if __name__ == "__main__":
    app()
```

**References**:
- Typer docs: https://typer.tiangolo.com/
- Rich + Typer integration: https://typer.tiangolo.com/tutorial/printing/

---

### 3. Rich Library Best Practices

**Decision**: Use **rich.table.Table** for todo listings and **rich.console.Console** for formatted output

**Best Practices**:
- **Tables**: Use `Table` with columns (ID, Title, Status, Created) for `list` command
- **Colors**: Use semantic colors (green=completed, yellow=in_progress, white=pending)
- **Formatting**: Use `[bold]`, `[italic]`, `[underline]` for emphasis
- **Error Messages**: Use `console.print("[red]Error:[/red] {message}")`
- **Success Messages**: Use `console.print("[green]✓[/green] {message}")`
- **Panels**: Use `Panel` for grouped information or help text

**Code Pattern**:
```python
from rich.console import Console
from rich.table import Table

console = Console()

def display_todos(todos: list[TodoItem]):
    table = Table(title="My Todos", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_color = {
            "completed": "green",
            "in_progress": "yellow",
            "pending": "white"
        }[todo.status]

        table.add_row(
            str(todo.id),
            todo.title,
            f"[{status_color}]{todo.status}[/{status_color}]",
            todo.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)
```

**References**:
- Rich docs: https://rich.readthedocs.io/
- Table guide: https://rich.readthedocs.io/en/stable/tables.html

---

### 4. UV Project Structure and Configuration

**Decision**: Use **UV with pyproject.toml** following modern Python packaging standards

**pyproject.toml Structure**:
```toml
[project]
name = "evolution-of-todo"
version = "0.1.0"
description = "Phase I: In-memory console todo application"
requires-python = ">=3.13"
dependencies = [
    "pydantic>=2.0.0",
    "rich>=13.7.0",
    "typer>=0.15.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
]

[project.scripts]
todo = "src.ui.cli:app"

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**UV Commands**:
```bash
# Initialize project
uv init

# Add dependencies
uv add pydantic rich typer

# Add dev dependencies
uv add --dev pytest pytest-cov mypy

# Run application
uv run todo add "My first task"

# Run tests
uv run pytest

# Type check
uv run mypy src/
```

**References**:
- UV docs: https://docs.astral.sh/uv/
- Python packaging guide: https://packaging.python.org/en/latest/

---

### 5. Type Hints and Mypy Strict Compliance

**Decision**: Enforce **mypy --strict** for all source code

**Requirements**:
- All function parameters must have type hints
- All return types must be annotated
- No implicit `Any` types
- No untyped function definitions
- Strict optional checking (no implicit `None`)

**Code Pattern**:
```python
from typing import Optional

class TodoManager:
    def __init__(self) -> None:
        self._todos: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        """Add a new todo item. Returns the created item."""
        todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Get a todo by ID. Returns None if not found."""
        return self._todos.get(todo_id)

    def list_todos(self) -> list[TodoItem]:
        """List all todos."""
        return list(self._todos.values())
```

**Mypy Configuration** (in pyproject.toml):
```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
```

**References**:
- Mypy docs: https://mypy.readthedocs.io/
- Type hints PEP 484: https://peps.python.org/pep-0484/

---

### 6. In-Memory Storage Design

**Decision**: Use **dict[int, TodoItem]** for O(1) lookup by ID

**Rationale**:
- **Performance**: O(1) get/update/delete by ID
- **Simplicity**: Native Python data structure, no external dependencies
- **ID Management**: Sequential integer IDs starting from 1
- **Migration Path**: Dict keys become database primary keys in Phase II

**Code Pattern**:
```python
class TodoManager:
    def __init__(self) -> None:
        self._todos: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        todo = TodoItem(id=self._next_id, title=title, description=description)
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo. Returns True if deleted, False if not found."""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
```

**Alternatives Considered**:
- **list[TodoItem]**: Simpler but O(n) lookup, requires linear search by ID
- **OrderedDict**: No benefit over dict in Python 3.13 (dicts maintain insertion order)

---

## Summary of Technical Decisions

| Decision Area | Choice | Primary Reason |
|---------------|--------|----------------|
| Data Model | Pydantic BaseModel | Phase II migration (SQLModel) + validation |
| CLI Framework | Typer | Type safety + auto-help + Rich integration |
| Terminal UI | Rich (Table + Console) | Professional output + semantic formatting |
| Package Manager | UV + pyproject.toml | Modern Python packaging + reproducible builds |
| Type Checking | mypy --strict | Full type safety + early error detection |
| Storage | dict[int, TodoItem] | O(1) operations + simple migration to DB |

## Unresolved Items

**User Story Prioritization** (from Constitution Check):
- ⚠️ Architecture spec does not define explicit user stories with P1/P2/P3 priorities
- **Resolution Strategy**: Define user stories during Phase 1 (Design) based on implicit CRUD requirements
- **Proposed Stories**:
  - **P1**: Add todo (core value)
  - **P1**: List todos (core value)
  - **P1**: Complete todo (core workflow)
  - **P2**: Delete todo (data management)
  - **P2**: Update todo (nice-to-have editing)

This will be finalized in data-model.md and contracts/ generation.

---

**Research Complete**: All technical unknowns resolved. Ready to proceed to Phase 1 (Design).
