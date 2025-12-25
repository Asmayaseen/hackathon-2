# Quickstart Guide - Phase I Console Todo App

**Date**: 2025-12-25
**Audience**: Developers implementing Phase I
**Prerequisites**: Python 3.13+, UV package manager installed

## Table of Contents

1. [Setup](#setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Type Checking](#type-checking)
7. [Common Tasks](#common-tasks)

---

## Setup

### 1. Initialize UV Project (if not already done)

```bash
# Initialize project
uv init

# Verify Python version
uv run python --version  # Should be 3.13 or higher
```

### 2. Install Dependencies

```bash
# Install runtime dependencies
uv add pydantic rich typer

# Install dev dependencies
uv add --dev pytest pytest-cov mypy
```

### 3. Verify Installation

```bash
# Check installed packages
uv pip list
```

Expected output should include:
- `pydantic>=2.0.0`
- `rich>=13.7.0`
- `typer>=0.15.0`
- `pytest>=8.0.0`
- `pytest-cov>=4.1.0`
- `mypy>=1.8.0`

---

## Project Structure

```text
hackathon-2/
├── src/
│   ├── __init__.py
│   ├── core/              # Logic-Agent scope
│   │   ├── __init__.py
│   │   ├── todo_item.py   # Pydantic model
│   │   └── todo_manager.py # Business logic
│   └── ui/                # UI-Agent scope
│       ├── __init__.py
│       └── cli.py         # Typer CLI
│
├── tests/
│   ├── __init__.py
│   ├── test_todo_item.py
│   ├── test_todo_manager.py
│   └── test_cli.py
│
├── pyproject.toml         # UV configuration
└── README.md
```

**Key Principles**:
- `src/core/` = Business logic (MUST NOT import from `src/ui/`)
- `src/ui/` = User interface (depends on `src/core/`)
- `tests/` = Mirrors `src/` structure

---

## Development Workflow

### Step 1: Implement TodoItem (Logic-Agent)

**File**: `src/core/todo_item.py`

**Reference**: [data-model.md](data-model.md#todoitem)

**Key Points**:
- Use Pydantic `BaseModel`
- Add field validators for `title`
- Configure `frozen=False` for mutability
- Add type hints for all fields

**Example skeleton**:
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

class TodoItem(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
```

**Verify**:
```bash
# Type check
uv run mypy src/core/todo_item.py --strict

# Unit test (after writing tests)
uv run pytest tests/test_todo_item.py -v
```

---

### Step 2: Implement TodoManager (Logic-Agent)

**File**: `src/core/todo_manager.py`

**Reference**: [data-model.md](data-model.md#todomanager)

**Key Points**:
- Use `dict[int, TodoItem]` for storage
- Sequential ID generation starting from 1
- Return `None` for not-found cases (not exceptions)
- Update `updated_at` on modifications

**Example skeleton**:
```python
from typing import Optional
from datetime import datetime
from .todo_item import TodoItem

class TodoManager:
    def __init__(self) -> None:
        self._todos: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        todo = TodoItem(id=self._next_id, title=title, description=description)
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        return self._todos.get(todo_id)

    def list_todos(self, status: Optional[str] = None) -> list[TodoItem]:
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
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        update_data["updated_at"] = datetime.now()

        updated_todo = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def complete_todo(self, todo_id: int) -> Optional[TodoItem]:
        return self.update_todo(todo_id, status="completed")

    def delete_todo(self, todo_id: int) -> bool:
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
```

**Verify**:
```bash
# Type check
uv run mypy src/core/ --strict

# Unit tests
uv run pytest tests/test_todo_manager.py -v
```

---

### Step 3: Implement CLI (UI-Agent)

**File**: `src/ui/cli.py`

**Reference**: [contracts/cli-interface.md](contracts/cli-interface.md)

**Key Points**:
- Use Typer for command framework
- Use Rich for formatted output
- Create single `TodoManager` instance
- Handle errors gracefully with Rich error messages

**Example skeleton**:
```python
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from src.core.todo_manager import TodoManager

app = typer.Typer(help="Phase I Console Todo Application")
console = Console()
manager = TodoManager()

@app.command()
def add(
    title: str = typer.Argument(..., help="Todo title"),
    description: str = typer.Option("", "--description", "-d", help="Todo description")
) -> None:
    """Add a new todo item."""
    try:
        todo = manager.add_todo(title, description)
        console.print("[green]✓[/green] Todo added successfully!\n")
        console.print(f"  ID: {todo.id}")
        console.print(f"  Title: {todo.title}")
        console.print(f"  Status: {todo.status}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status")
) -> None:
    """List all todos."""
    todos = manager.list_todos(status)

    if not todos:
        msg = "No todos found" if not status else f"No todos found with status '{status}'"
        console.print(msg)
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
        color = status_colors[todo.status]

        table.add_row(
            str(todo.id),
            todo.title,
            f"[{color}]{todo.status}[/{color}]",
            todo.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

# Implement: complete, delete, update commands...

if __name__ == "__main__":
    app()
```

**Verify**:
```bash
# Type check
uv run mypy src/ --strict

# Integration tests
uv run pytest tests/test_cli.py -v
```

---

## Running the Application

### Configure Entry Point (pyproject.toml)

Add to `pyproject.toml`:
```toml
[project.scripts]
todo = "src.ui.cli:app"
```

### Run Commands

```bash
# Add a todo
uv run todo add "Implement data model"

# Add with description
uv run todo add "Create CLI" --description "Use Typer and Rich"

# List all todos
uv run todo list

# List by status
uv run todo list --status pending

# Complete a todo
uv run todo complete 1

# Update a todo
uv run todo update 2 --status in_progress

# Delete a todo
uv run todo delete 3

# Show help
uv run todo --help
uv run todo add --help
```

---

## Testing

### Run All Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_todo_manager.py -v

# Run specific test function
uv run pytest tests/test_todo_manager.py::test_add_todo_assigns_sequential_id -v
```

### Test Coverage

```bash
# Run tests with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Target**: 90%+ coverage for `src/core/` (business logic)

---

## Type Checking

### Run Mypy

```bash
# Type check all source code
uv run mypy src/ --strict

# Type check specific file
uv run mypy src/core/todo_item.py --strict

# Type check with detailed output
uv run mypy src/ --strict --show-error-codes
```

### Mypy Configuration (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
no_implicit_optional = true
```

---

## Common Tasks

### 1. Add New Dependency

```bash
# Runtime dependency
uv add <package-name>

# Dev dependency
uv add --dev <package-name>
```

### 2. Run Python REPL with Project Context

```bash
uv run python

>>> from src.core.todo_manager import TodoManager
>>> manager = TodoManager()
>>> manager.add_todo("Test task")
>>> manager.list_todos()
```

### 3. Format Code (if using ruff)

```bash
# Install ruff
uv add --dev ruff

# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/
```

### 4. Debugging with Rich Console

```python
from rich.console import Console
console = Console()

# Pretty print objects
console.print(todo)

# Debug with inspect
from rich import inspect
inspect(manager, methods=True)
```

---

## Troubleshooting

### Issue: "Module not found" Error

**Solution**: Ensure `__init__.py` files exist in all directories:
```bash
# Create missing __init__.py files
touch src/__init__.py
touch src/core/__init__.py
touch src/ui/__init__.py
touch tests/__init__.py
```

### Issue: Mypy Errors on Pydantic Models

**Solution**: Install Pydantic mypy plugin (usually auto-detected):
```toml
[tool.mypy]
plugins = ["pydantic.mypy"]
```

### Issue: Typer Commands Not Found

**Solution**: Ensure `[project.scripts]` is configured in `pyproject.toml` and run:
```bash
uv sync
```

---

## Next Steps

1. **Implement core logic** (`src/core/`) following [data-model.md](data-model.md)
2. **Write unit tests** for `TodoItem` and `TodoManager`
3. **Implement CLI** (`src/ui/cli.py`) following [cli-interface.md](contracts/cli-interface.md)
4. **Write integration tests** for CLI commands
5. **Verify type safety** with `mypy --strict`
6. **Achieve 90%+ test coverage** for core logic
7. **Test end-to-end workflows** manually

**Reference**: See [tasks.md](tasks.md) (to be generated by `/sp.tasks`) for atomic implementation tasks.

---

**Quickstart Complete**: Ready for `/sp.tasks` and `/sp.implement`
