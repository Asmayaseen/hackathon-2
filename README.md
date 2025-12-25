# Evolution of Todo - Phase I: Console Application

A Python-based console todo application built with **Pydantic**, **Typer**, and **Rich**. This is Phase I of a multi-phase evolution toward a full-stack web application.

## Features

- **Add** todos with title and optional description
- **List** todos in a formatted table with color-coded status
- **Complete** todos to mark them as done
- **Update** todo fields (title, description, status)
- **Delete** todos when no longer needed
- **In-memory storage** for fast, session-based task management

## Tech Stack

- **Python 3.12+** - Modern Python with type hints
- **UV** - Fast Python package manager
- **Pydantic 2.0+** - Data validation and settings management
- **Typer** - CLI framework with type hints
- **Rich** - Beautiful terminal formatting
- **mypy** - Static type checking (strict mode)

## Installation

### Prerequisites

- Python 3.12 or higher
- UV package manager ([installation guide](https://docs.astral.sh/uv/))

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hackathon-2
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Verify installation:
   ```bash
   uv run mypy src/ --strict
   ```

## Usage

### Running the Application

Due to the in-memory nature of Phase I, use the test script for a complete workflow:

```bash
uv run python test_cli_workflow.py
```

This demonstrates:
- Adding multiple todos
- Listing todos in a Rich table
- Completing todos with color-coded status
- Updating todo fields
- Deleting todos

### Individual CLI Commands

You can run individual commands via the main.py entry point:

```bash
# Add a todo
uv run python main.py add "My task" --description "Task details"

# List all todos (note: separate invocations won't share state)
uv run python main.py list

# Complete a todo
uv run python main.py complete 1

# Update a todo
uv run python main.py update 1 --status in_progress

# Delete a todo
uv run python main.py delete 1

# Get help
uv run python main.py --help
```

**Alternative**: You can also run directly via Python module:
```bash
uv run python -m src.ui.cli add "My task"
```

**Note**: Since Phase I uses in-memory storage, each command invocation creates a fresh `TodoManager` instance. Use `test_cli_workflow.py` to see the complete workflow in action.

## Project Structure

```
hackathon-2/
├── main.py                # Entry point (calls src.ui.cli)
├── src/
│   ├── core/              # Business logic (Logic-Agent)
│   │   ├── todo_item.py   # TodoItem Pydantic model
│   │   └── todo_manager.py # TodoManager service
│   └── ui/                # User interface (UI-Agent)
│       └── cli.py         # Typer CLI application
├── tests/                 # Test suite (mirrors src/)
├── .claude/
│   └── agents/            # Sub-agent instructions
│       ├── logic-agent.md
│       └── ui-agent.md
├── specs/                 # Design documents
│   └── main/
│       ├── plan.md
│       ├── data-model.md
│       ├── contracts/
│       └── tasks.md
├── pyproject.toml         # UV configuration
├── test_cli_workflow.py   # Workflow demonstration
└── README.md
```

## Architecture

### Separation of Concerns

- **src/core/** - Pure business logic, no UI dependencies
- **src/ui/** - CLI interface, depends on core
- **tests/** - Test suite mirroring src/ structure

### Data Model

**TodoItem** (Pydantic model):
- `id`: Unique sequential identifier
- `title`: Task title (1-200 chars, required)
- `description`: Optional details (max 1000 chars)
- `status`: `pending` | `in_progress` | `completed`
- `created_at`: Auto-set creation timestamp
- `updated_at`: Auto-updated modification timestamp

**TodoManager** (Business logic service):
- In-memory storage using `dict[int, TodoItem]`
- Sequential ID generation starting from 1
- CRUD operations with O(1) lookups

## Development

### Type Checking

```bash
uv run mypy src/ --strict
```

### Running Tests (Optional)

Tests are optional for Phase I. To run them when implemented:

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Code Quality

- **PEP 8** style guidelines enforced
- **mypy --strict** passes with zero errors
- All public methods have type hints
- Comprehensive docstrings

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create a new todo | `add "Task" --description "Details"` |
| `list` | Show all todos | `list --status pending` |
| `complete` | Mark todo as completed | `complete 1` |
| `update` | Modify todo fields | `update 1 --status in_progress` |
| `delete` | Remove a todo | `delete 1` |

### Status Values

- `pending` - Not started (white in terminal)
- `in_progress` - Currently working (yellow)
- `completed` - Finished (green)

## Roadmap

### Phase I (Current) ✅
- In-memory console application
- Basic CRUD operations
- Rich terminal UI

### Phase II (Planned)
- FastAPI backend with Neon PostgreSQL
- Next.js frontend
- Multi-user support
- Persistent storage

## Contributing

This project follows Spec-Driven Development (SDD):

1. All features start with a specification in `specs/`
2. Tasks are defined in `specs/main/tasks.md`
3. Implementation follows the task plan
4. Type safety enforced with mypy --strict

## License

[Add your license here]

## Credits

Built with:
- [Pydantic](https://docs.pydantic.dev/)
- [Typer](https://typer.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)
- [UV](https://docs.astral.sh/uv/)
