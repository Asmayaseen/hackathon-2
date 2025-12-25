# Implementation Plan: Phase I - In-Memory Console Todo App

**Branch**: `main` | **Date**: 2025-12-25 | **Spec**: [../00-architecture.md](../00-architecture.md)
**Input**: Feature specification from `/specs/00-architecture.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Python 3.13+ console-based todo application with clean separation between business logic (`src/core/`) and user interface (`src/ui/`). The application will use in-memory storage for Phase I, with architecture designed for seamless migration to FastAPI backend and Next.js frontend in Phase II. Core technologies: Rich for terminal UI, Typer for CLI framework, Pydantic for data models, and UV for package management.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: rich>=13.7.0 (terminal UI), typer>=0.15.0 (CLI framework), pydantic>=2.0.0 (data models)
**Storage**: In-memory (Python list or dict) for Phase I; designed for Neon PostgreSQL migration in Phase II
**Testing**: pytest>=8.0.0, pytest-cov>=4.1.0 (optional for TDD if requested)
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: Single console application with modular architecture
**Performance Goals**: CLI commands respond within 100ms; support up to 10,000 todos without degradation
**Constraints**:
- Strict separation: core/ cannot import from ui/
- All public methods must have type hints
- Must follow PEP 8 style guidelines
- Must pass mypy --strict type checking

**Scale/Scope**:
- Single-user, single-session console application
- ~5 CLI commands (add, list, complete, delete, update)
- 2 core modules (todo_item.py, todo_manager.py)
- 1 UI module (cli.py)
- Foundation for Phase II full-stack evolution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-Driven Development
- **Status**: PASS
- **Evidence**: Architecture spec (`specs/00-architecture.md`) created first; now executing `/sp.plan` workflow; `/sp.tasks` and `/sp.implement` will follow in order
- **Note**: No code will be written before plan.md and tasks.md are complete and approved

### ✅ Principle II: Phased Evolution
- **Status**: PASS
- **Evidence**: This is Phase I (In-memory console application) as defined in constitution
- **Migration Path**: Architecture explicitly designs for Phase II evolution (FastAPI + Next.js)
- **Note**: src/core/ business logic will become backend; UI layer will be replaced with web frontend

### ✅ Principle III: Technology Stack Adherence
- **Status**: PASS
- **Phase I Stack Compliance**:
  - ✅ Python 3.13+ (required)
  - ✅ UV package manager (required)
  - ✅ Rich for terminal UI (modern, professional CLI output)
  - ✅ Typer for CLI framework (type-safe, auto-help generation)
  - ✅ Pydantic for data models (prepares for Phase II SQLModel migration)

### ⚠️ Principle IV: Independent User Stories
- **Status**: NEEDS CLARIFICATION
- **Issue**: Architecture spec does not define user stories with priorities (P1, P2, P3)
- **Resolution**: User stories will be defined in separate feature specs or extracted during Phase 0 research
- **Assumption**: Basic CRUD operations (add, list, complete, delete, update) are implicit P1 stories

### ✅ Principle V: Test-Driven Development (Conditional)
- **Status**: PASS (conditional)
- **Evidence**: pytest dependencies listed as optional; TDD not mandated for Phase I
- **Note**: If tests are requested during implementation, Red-Green-Refactor will be enforced

### N/A Principle VI: Stateless Architecture
- **Status**: NOT APPLICABLE
- **Reason**: Phase I uses in-memory storage; statelessness becomes mandatory in Phase II (FastAPI backend)
- **Future**: Phase II backend will be stateless with all state in Neon PostgreSQL

### ✅ Principle VII: Documentation and Traceability
- **Status**: PASS
- **Evidence**:
  - Constitution: `.specify/memory/constitution.md` exists
  - Spec: `specs/00-architecture.md` exists
  - Plan: `specs/main/plan.md` (this file, in progress)
  - Tasks: Will be created by `/sp.tasks`
  - PHRs: Will be auto-generated after each command
  - ADRs: Will be created for significant architectural decisions (e.g., Pydantic vs dataclass)

**GATE RESULT**: ✅ PASS with 1 clarification needed (user stories)
**ACTION**: Proceed to Phase 0 research; resolve user story prioritization during research phase

## Project Structure

### Documentation (this feature)

```text
specs/
├── 00-architecture.md   # Architecture foundation spec (already exists)
└── main/
    ├── plan.md          # This file (/sp.plan command output)
    ├── research.md      # Phase 0 output (to be created)
    ├── data-model.md    # Phase 1 output (to be created)
    ├── quickstart.md    # Phase 1 output (to be created)
    ├── contracts/       # Phase 1 output (to be created)
    └── tasks.md         # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
hackathon-2/
├── src/
│   ├── __init__.py
│   ├── core/              # Business logic layer (Logic-Agent scope)
│   │   ├── __init__.py
│   │   ├── todo_item.py   # TodoItem Pydantic model
│   │   └── todo_manager.py # TodoManager business logic
│   └── ui/                # User interface layer (UI-Agent scope)
│       ├── __init__.py
│       └── cli.py         # CLI implementation with Rich + Typer
│
├── tests/                 # Test suite (mirrors src/ structure)
│   ├── __init__.py
│   ├── test_todo_item.py
│   ├── test_todo_manager.py
│   └── test_cli.py
│
├── pyproject.toml         # UV project configuration
├── README.md
├── CLAUDE.md              # Claude Code runtime instructions
├── .specify/              # SpecKit Plus templates and scripts
│   └── memory/
│       └── constitution.md
└── specs/                 # Specification documents
    ├── 00-architecture.md
    └── main/
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── contracts/
        └── tasks.md
```

**Structure Decision**:

Selected **Option 1: Single project (console application)** structure as defined in the architecture spec.

**Rationale**:
- **Separation of Concerns**: `src/core/` contains pure business logic (Logic-Agent), `src/ui/` contains interface code (UI-Agent)
- **Phase II Migration**: `src/core/` becomes FastAPI backend foundation with minimal changes; `src/ui/` gets replaced with Next.js frontend
- **Dependency Rule**: Core cannot import from UI (enforced by tests); UI depends on Core
- **Test Organization**: `tests/` mirrors `src/` structure for clarity
- **Modularity**: Clean separation enables independent testing and parallel development of logic and interface

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: N/A - No constitution violations detected. All gates passed.

The architecture follows constitutional principles:
- Spec-driven workflow enforced
- Phase I structure as mandated
- Technology stack compliant
- Minimal complexity for console application
- Clear separation of concerns without over-engineering

---

## Phase 0: Research (Completed)

**Status**: ✅ Complete

**Output**: [research.md](research.md)

**Key Decisions Documented**:
1. **Pydantic vs Dataclass**: Chose Pydantic for validation + Phase II SQLModel migration
2. **Typer vs Argparse**: Chose Typer for type safety + auto-help + Rich integration
3. **Rich Best Practices**: Defined table formatting and semantic color usage
4. **UV Configuration**: Modern Python packaging with pyproject.toml
5. **Type Checking**: Enforced mypy --strict for all source code
6. **Storage Design**: dict[int, TodoItem] for O(1) operations

**Resolved Clarifications**:
- User story prioritization defined (P1: add, list, complete; P2: delete, update)

---

## Phase 1: Design & Contracts (Completed)

**Status**: ✅ Complete

**Output**:
- [data-model.md](data-model.md) - TodoItem and TodoManager specifications
- [contracts/cli-interface.md](contracts/cli-interface.md) - CLI command specifications
- [quickstart.md](quickstart.md) - Developer implementation guide
- CLAUDE.md - Updated with Phase I technology stack

### Design Summary

**Data Model**:
- **TodoItem**: Pydantic model with 6 fields (id, title, description, status, created_at, updated_at)
- **TodoManager**: Business logic service with CRUD operations
- **Storage**: dict[int, TodoItem] with sequential ID generation
- **Validation**: Pydantic field validators for title constraints

**CLI Interface**:
- **5 Commands**: add, list, complete, delete, update
- **Framework**: Typer with Rich formatting
- **Error Handling**: User-friendly Rich error messages
- **User Journeys**: Documented common workflows

**Agent Separation**:
- **Logic-Agent** (src/core/): TodoItem + TodoManager (no UI dependencies)
- **UI-Agent** (src/ui/): CLI commands (depends on core)

---

## Post-Design Constitution Check

*Re-evaluation after Phase 1 design completion*

### ✅ Principle I: Spec-Driven Development
- **Status**: PASS
- **Evidence**: All design artifacts completed before implementation; plan.md, research.md, data-model.md, contracts/, quickstart.md created
- **Next**: Proceed to `/sp.tasks` for task breakdown, then `/sp.implement`

### ✅ Principle II: Phased Evolution
- **Status**: PASS
- **Evidence**: Phase I design complete; explicit migration paths documented for Phase II
- **Migration Readiness**:
  - TodoItem → SQLModel (add table=True, user_id foreign key)
  - TodoManager methods → FastAPI endpoints
  - CLI commands → Next.js frontend + API calls

### ✅ Principle III: Technology Stack Adherence
- **Status**: PASS
- **Evidence**: All Phase I requirements met:
  - ✅ Python 3.13+
  - ✅ UV package manager (pyproject.toml configured)
  - ✅ Pydantic (data models)
  - ✅ Rich (terminal UI)
  - ✅ Typer (CLI framework)
  - ✅ pytest, mypy (dev tools)

### ✅ Principle IV: Independent User Stories
- **Status**: PASS (resolved)
- **Evidence**: User stories defined with priorities in research.md and contracts/cli-interface.md
- **Stories**:
  - P1: Add todo, List todos, Complete todo (core workflow)
  - P2: Delete todo, Update todo (data management)
- **Independence**: Each command operates standalone; can be implemented and tested independently

### ✅ Principle V: Test-Driven Development (Conditional)
- **Status**: PASS (optional)
- **Evidence**: Test requirements documented in data-model.md (unit tests) and cli-interface.md (integration tests)
- **Coverage Target**: 90%+ for src/core/ (business logic)
- **Note**: TDD enforced if tests explicitly requested during implementation

### N/A Principle VI: Stateless Architecture
- **Status**: NOT APPLICABLE (Phase I in-memory app)
- **Phase II Readiness**: Design ensures clean transition to stateless FastAPI backend

### ✅ Principle VII: Documentation and Traceability
- **Status**: PASS
- **Evidence**:
  - ✅ Constitution: .specify/memory/constitution.md
  - ✅ Architecture Spec: specs/00-architecture.md
  - ✅ Plan: specs/main/plan.md (this file)
  - ✅ Research: specs/main/research.md
  - ✅ Data Model: specs/main/data-model.md
  - ✅ Contracts: specs/main/contracts/cli-interface.md
  - ✅ Quickstart: specs/main/quickstart.md
  - ✅ Agent Context: CLAUDE.md (updated)
  - Pending: tasks.md (via `/sp.tasks`), PHR (via automated creation)

**POST-DESIGN GATE RESULT**: ✅ PASS - All principles satisfied

---

## Architectural Decisions

The following architecturally significant decisions were made during planning:

### 1. Data Model Choice: Pydantic over Dataclass

**Decision**: Use Pydantic BaseModel for TodoItem

**Context**: Phase I needs a data class with validation; Phase II requires JSON serialization for API

**Options Considered**:
- Python dataclass (stdlib, simple, but no validation or JSON serialization)
- Pydantic BaseModel (validation + JSON + SQLModel migration path)
- attrs (powerful but adds dependency, doesn't align with Phase II stack)

**Decision**: Pydantic BaseModel

**Rationale**:
- Automatic field validation (title length, status enum)
- Built-in JSON serialization (.model_dump(), .model_validate())
- Direct migration to SQLModel in Phase II (add table=True, no refactoring)
- Type safety with mypy --strict compliance
- Aligns with FastAPI ecosystem (Phase II backend)

**Consequences**:
- ✅ Zero refactoring needed for Phase II database migration
- ✅ Strong type safety and validation out of the box
- ✅ Better developer experience with automatic validation errors
- ⚠️ Adds external dependency (but required for Phase II anyway)

**Status**: Approved

---

### 2. CLI Framework: Typer over Argparse

**Decision**: Use Typer for CLI implementation

**Context**: Need CLI framework for Phase I console application

**Options Considered**:
- argparse (stdlib, zero dependencies, but verbose and manual)
- Typer (type hints + auto-help + Rich integration)
- Click (mature, but less type-safe)

**Decision**: Typer

**Rationale**:
- Type hints for automatic argument parsing (less boilerplate)
- Auto-generated help text from docstrings
- Built-in Rich integration (same maintainer: Sebastián Ramírez)
- Better error messages with validation
- Modern Python philosophy (type hints over configuration)
- Easier testing with CliRunner

**Consequences**:
- ✅ Less code to write and maintain
- ✅ Better user experience with Rich formatting
- ✅ Type-safe command definitions
- ⚠️ Adds external dependency (but lightweight and well-maintained)

**Status**: Approved

---

### 3. Storage Structure: dict[int, TodoItem] over list[TodoItem]

**Decision**: Use dict with integer keys for in-memory storage

**Context**: Need efficient in-memory storage for Phase I

**Options Considered**:
- list[TodoItem] (simpler, but O(n) lookup by ID)
- dict[int, TodoItem] (O(1) operations, direct mapping to DB primary keys)
- OrderedDict (no benefit in Python 3.13)

**Decision**: dict[int, TodoItem]

**Rationale**:
- O(1) get/update/delete by ID (vs O(n) with list)
- Direct mapping to database primary keys in Phase II
- Sequential ID generation (1, 2, 3, ...) mimics auto-increment
- Simple migration: dict keys become PostgreSQL primary keys

**Consequences**:
- ✅ Better performance for lookups and updates
- ✅ Clean migration to relational database
- ✅ Simpler TodoManager implementation
- ⚠️ IDs not reused after deletion (acceptable for this use case)

**Status**: Approved

---

**ADR Suggestion**: 📋 Architectural decisions detected for: (1) Data model choice, (2) CLI framework, (3) Storage structure

These decisions have long-term impact on Phase II migration and system architecture. Consider documenting in ADR?

**Command**: `/sp.adr "Phase I Technology Stack Choices"`

---

## Summary

**Planning Status**: ✅ Complete - Ready for task breakdown

**Artifacts Created**:
1. ✅ plan.md (this file) - Implementation plan with technical context and structure
2. ✅ research.md - Technical research and decision rationale
3. ✅ data-model.md - TodoItem and TodoManager specifications
4. ✅ contracts/cli-interface.md - CLI command contracts and user journeys
5. ✅ quickstart.md - Developer implementation guide
6. ✅ CLAUDE.md - Updated with Phase I technology stack

**Key Design Decisions**:
- Pydantic for data models (validation + Phase II migration)
- Typer for CLI framework (type safety + Rich integration)
- dict[int, TodoItem] for storage (O(1) operations + DB migration)
- Strict separation: core/ (business logic) vs ui/ (interface)

**Constitution Compliance**: ✅ All principles satisfied

---

## Next Steps

1. **Task Breakdown** (User Action Required):
   ```bash
   /sp.tasks
   ```
   - Generate atomic, testable tasks in `specs/main/tasks.md`
   - Map tasks to user stories (P1: add, list, complete; P2: delete, update)
   - Mark parallelizable tasks with [P]
   - Link tasks to data-model.md and cli-interface.md

2. **Implementation** (After User Approval):
   ```bash
   /sp.implement
   ```
   - Execute tasks in dependency order
   - Generate code via Claude Code (Logic-Agent + UI-Agent)
   - Reference Task IDs in code comments
   - Validate against acceptance criteria

3. **Optional: Document ADRs** (User Decision):
   ```bash
   /sp.adr "Phase I Technology Stack Choices"
   ```
   - Document Pydantic vs dataclass decision
   - Document Typer vs argparse decision
   - Document storage structure decision

---

**Plan Complete** | **Version**: 1.0.0 | **Date**: 2025-12-25
