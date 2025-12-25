# Architecture Specification: Phase I - In-Memory Console App

**Phase**: I - In-Memory Console Application
**Created**: 2025-12-25
**Status**: Draft
**Technology Stack**: Python 3.13+, Rich, Typer/argparse, UV package manager

## Overview

This specification defines the architectural foundation for Phase I of the Evolution of Todo project. The architecture establishes a clean separation of concerns between business logic and user interface, preparing the codebase for future evolution into a full-stack web application.

## Directory Structure

The project MUST follow this directory structure:

```
hackathon-2/
├── src/
│   ├── __init__.py
│   ├── core/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── todo_item.py   # TodoItem data class
│   │   └── todo_manager.py # TodoManager business logic
│   └── ui/                # User interface layer
│       ├── __init__.py
│       └── cli.py         # CLI implementation with rich
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_todo_item.py
│   ├── test_todo_manager.py
│   └── test_cli.py
├── pyproject.toml         # UV project configuration
├── README.md
└── specs/                 # Specification documents
    └── 00-architecture.md # This file
```

**Rationale**:
- `src/core/` contains all business logic, making it reusable across different interfaces (CLI, web, API)
- `src/ui/` isolates presentation layer, allowing easy replacement in future phases
- `tests/` mirrors source structure for clear test organization
- This structure aligns with Phase II migration where `src/core/` becomes the FastAPI backend foundation

## Subagent Roles

Two logical agent roles are defined for development workflow. These roles represent separation of concerns, not separate codebases.

### Logic-Agent

**Responsibility**: Business logic and data management

**Scope**:
- `src/core/todo_item.py`: TodoItem data class
- `src/core/todo_manager.py`: TodoManager business logic class
- Core business rules and data validation
- In-memory data storage implementation

**Key Responsibilities**:
- Define TodoItem structure with required fields (id, title, description, status, created_at, updated_at)
- Implement CRUD operations (Create, Read, Update, Delete) for todos
- Manage in-memory storage (list or dictionary)
- Enforce business rules (e.g., unique IDs, valid status transitions)
- Provide clean API for UI layer to consume

**Constraints**:
- MUST NOT depend on any UI framework
- MUST be testable independently of UI
- MUST use Python dataclasses or Pydantic models for TodoItem
- MUST NOT import anything from `src/ui/`

### UI-Agent

**Responsibility**: Command-line interface and user interaction

**Scope**:
- `src/ui/cli.py`: CLI implementation using rich library
- User input parsing (Typer or argparse)
- Output formatting and display
- User interaction flows

**Key Responsibilities**:
- Implement command-line interface with commands: add, list, complete, delete, update
- Use `rich` library for beautiful terminal output (tables, colors, formatting)
- Parse command-line arguments using `typer` (preferred) or `argparse`
- Handle user errors gracefully with helpful messages
- Call TodoManager methods to perform operations

**Constraints**:
- MUST NOT contain business logic
- MUST delegate all data operations to TodoManager
- MUST use rich for all output formatting
- MUST handle errors from core layer gracefully

## Dependencies

### Required Dependencies

The following dependencies MUST be installed via UV:

```toml
[project]
name = "evolution-of-todo"
version = "0.1.0"
requires-python = ">=3.13"

dependencies = [
    "rich>=13.7.0",      # Terminal formatting and display
    "typer>=0.15.0",     # CLI framework (preferred)
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",     # Testing framework
    "pytest-cov>=4.1.0", # Coverage reporting
]
```

**Dependency Rationale**:

- **rich** (REQUIRED): Modern terminal formatting library
  - Provides rich text, tables, progress bars, and colors
  - Enhances user experience with professional CLI output
  - Zero-configuration beautiful defaults

- **typer** (PREFERRED): CLI framework built on top of click
  - Type hints for automatic argument parsing
  - Automatic help generation
  - Better developer experience than argparse
  - Can be replaced with `argparse` (stdlib) if minimal dependencies preferred

- **pytest** (DEV): Testing framework
  - Simple, powerful test discovery and execution
  - Required only if test-driven development is adopted

### Alternative: argparse (stdlib)

If minimal dependencies are required, `argparse` MAY be used instead of `typer`:

```python
# No additional dependency required - argparse is in standard library
import argparse
```

**Trade-off**:
- ✅ Zero external dependencies
- ❌ More verbose code
- ❌ Manual help text generation
- ❌ No automatic type validation

## Key Design Decisions

### 1. In-Memory Storage

**Decision**: Use Python list or dictionary for storage in Phase I

**Rationale**:
- Simplest implementation for console app
- No database dependency required
- Easy to migrate to persistent storage in Phase II
- Sufficient for single-user, single-session use case

**Implications**:
- Data lost on application exit (acceptable for Phase I)
- No concurrent access concerns
- Fast operations (no I/O overhead)

### 2. Data Class Design

**Decision**: Use Python `dataclass` or Pydantic `BaseModel` for TodoItem

**Rationale**:
- Type safety and validation
- Automatic `__init__`, `__repr__`, `__eq__` methods
- Pydantic provides JSON serialization for Phase II API
- Aligns with SQLModel (Pydantic + SQLAlchemy) for Phase II

**Recommended**: Start with Pydantic to ease Phase II migration

### 3. CLI Framework Choice

**Decision**: Prefer Typer over argparse

**Rationale**:
- Type hints reduce boilerplate
- Automatic help generation from docstrings
- Better error messages
- Easier testing
- Modern Python conventions

**Fallback**: argparse if zero-dependency requirement emerges

### 4. Separation of Concerns

**Decision**: Strict separation between core and ui layers

**Rationale**:
- Core logic reusable in Phase II (FastAPI backend)
- UI can be replaced without touching business logic
- Independent testing of logic and interface
- Aligns with clean architecture principles

**Enforcement**:
- Core MUST NOT import from ui
- UI MUST only call public TodoManager methods
- Tests verify no circular dependencies

## Non-Functional Requirements

### Performance
- **NFR-001**: CLI commands MUST respond within 100ms for in-memory operations
- **NFR-002**: Support up to 10,000 todos in memory without performance degradation

### Usability
- **NFR-003**: All CLI commands MUST provide helpful error messages using rich formatting
- **NFR-004**: CLI MUST display todos in a readable table format using rich.table
- **NFR-005**: Help text MUST be automatically generated from command docstrings

### Maintainability
- **NFR-006**: Code MUST follow PEP 8 style guidelines
- **NFR-007**: All public methods MUST have type hints
- **NFR-008**: Core logic MUST be independently testable without UI

### Portability
- **NFR-009**: Application MUST run on Windows, macOS, and Linux
- **NFR-010**: Dependencies MUST be managed via UV for reproducible builds

## Migration Path to Phase II

This architecture is designed for seamless evolution:

1. **Core Logic → FastAPI Backend**:
   - `TodoManager` methods become API endpoints
   - `TodoItem` dataclass becomes SQLModel for database
   - In-memory storage replaced with Neon PostgreSQL

2. **CLI → Web Frontend**:
   - `src/ui/cli.py` replaced with Next.js frontend
   - Rich tables become HTML tables or React components
   - Typer commands become API calls

3. **Testing Strategy**:
   - Core tests remain valid (business logic unchanged)
   - UI tests replaced with API integration tests
   - Add frontend E2E tests

## Success Criteria

- **SC-001**: TodoManager can be imported and used without any UI dependencies
- **SC-002**: CLI displays todos in a formatted rich table with proper columns
- **SC-003**: All CRUD operations execute successfully from command line
- **SC-004**: Application runs via `uv run` without additional setup
- **SC-005**: Code passes type checking with `mypy --strict`
- **SC-006**: Core logic has 90%+ test coverage (if TDD adopted)

## Constraints and Assumptions

### Constraints
- MUST use Python 3.13+
- MUST use UV for package management
- MUST follow Spec-Driven Development workflow
- MUST NOT write code before completing spec → plan → tasks workflow

### Assumptions
- Single user operating in single terminal session
- Data persistence not required in Phase I (acceptable to lose data on exit)
- No authentication or authorization needed
- No concurrent access to todo data

### Out of Scope for Phase I
- Data persistence (covered in Phase II)
- Multi-user support (covered in Phase II)
- Web interface (covered in Phase II)
- AI chatbot (covered in Phase III)
- Reminders and notifications (covered in Phase III+)
- Kubernetes deployment (covered in Phase IV-V)

## Next Steps

1. **Planning Phase**: Run `/sp.plan` to create `specs/00-architecture/plan.md`
   - Research Python dataclasses vs Pydantic
   - Design TodoItem schema
   - Design TodoManager API
   - Plan CLI command structure with Typer

2. **Task Breakdown**: Run `/sp.tasks` to create `specs/00-architecture/tasks.md`
   - Break down into atomic implementation tasks
   - Map tasks to user stories (defined in feature specs)
   - Mark parallelizable tasks

3. **Implementation**: Run `/sp.implement` or work with Claude Code
   - Execute tasks in dependency order
   - Reference Task IDs in code comments
   - Validate against acceptance criteria

---

**Version**: 1.0.0
**Author**: System Architect (Claude Sonnet 4.5)
**Review Status**: Awaiting approval
