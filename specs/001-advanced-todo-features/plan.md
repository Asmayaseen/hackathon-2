# Implementation Plan: Advanced Todo Features

**Branch**: `001-advanced-todo-features` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-advanced-todo-features/spec.md`

## Summary

Extend the Phase I console todo application with Intermediate and Advanced features including:
- **Intermediate**: Priorities (high/medium/low), Tags (categories), Search (keyword), Filter (multi-criteria), Sort (priority/date/title)
- **Advanced**: Due Dates (ISO 8601), Time Reminders (console notifications), Recurring Tasks (daily/weekly/monthly auto-generation)

**Technical Approach**: Extend existing Pydantic TodoItem model with 5 new fields, add 3 new TodoManager methods (filter/search/check_reminders), extend CLI with new options for add/list commands, and add new search command. All features maintain strict type safety (mypy --strict) and in-memory storage per Phase I requirements.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Pydantic 2.0+, Typer 0.15+, Rich 13.7+
**Storage**: In-memory (`dict[int, TodoItem]`) - Phase I requirement
**Testing**: pytest with existing test patterns (91 tests, 17 test classes)
**Target Platform**: Cross-platform console (Linux, macOS, Windows)
**Project Type**: Single project (console CLI application)
**Performance Goals**:
  - Search/filter: <1 second for 1000 tasks (SC-002)
  - Sort: <500ms for 100+ tasks (SC-004)
  - Reminder check: <5 seconds on startup (SC-005)
  - Recurring instance creation: <1 second (SC-006)
**Constraints**:
  - Must pass mypy --strict type checking
  - No external dependencies beyond current stack (UV, Pydantic, Typer, Rich, pytest)
  - In-memory storage only (no database for Phase I)
  - Console-only output (no GUI/web)
  - Single-user (no multi-user or concurrent access)
**Scale/Scope**:
  - Support up to 1000 tasks in memory
  - Up to 10 tags per task
  - 80-column terminal display (SC-008)
  - 5 prioritized user stories (P1-P5)
  - 30 functional requirements (FR-001 to FR-030)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development (NON-NEGOTIABLE)

✅ **PASS** - This plan generated from completed specification (spec.md)
- Specification completed with 5 user stories, 30 functional requirements, 13 success criteria
- All architectural decisions documented in this plan.md
- Tasks will be generated via `/sp.tasks` command
- Implementation will reference Task IDs from tasks.md
- Claude Code will generate all implementation code (no manual coding)

### II. Phased Evolution

✅ **PASS** - Phase I Extension (Intermediate + Advanced features)
- Building on existing Phase I console application
- Maintains in-memory storage (Phase I requirement)
- Prepares for Phase II migration to database (clean separation in core/)
- No phase skipping - this extends Phase I before moving to Phase II
- All features functional and testable independently

### III. Technology Stack Adherence

✅ **PASS** - Maintains Phase I mandatory stack
- Python 3.12+ (current: pyproject.toml specifies >=3.12)
- UV package manager (no changes)
- Pydantic 2.0+ for models (extending TodoItem)
- Typer 0.15+ for CLI (adding new options)
- Rich 13.7+ for terminal formatting (extending tables)
- pytest for testing (extending existing test classes)
- Claude Code + Spec-Kit Plus for development (this process)

No substitutions. No new dependencies introduced.

### IV. Independent User Stories

✅ **PASS** - 5 prioritized, independently testable user stories
- **P1**: Task Organization (Priorities + Tags) - Standalone MVP value
- **P2**: Search & Filter - Requires P1 data but independently testable
- **P3**: Sort Tasks - Enhances P1+P2 but independently implementable
- **P4**: Due Dates & Reminders - Standalone time management feature
- **P5**: Recurring Tasks - Builds on P4 but independently testable

Each story has:
- Clear priority justification (spec.md lines 10-97)
- Independent test description
- Given/When/Then acceptance scenarios (25+ total)
- Delivers standalone value as MVP increment

### V. Test-Driven Development (Conditional)

⚠️ **CONDITIONAL** - Tests NOT explicitly requested in specification
- TDD is optional per constitution (spec does not mandate tests)
- Focus on functional requirements and acceptance criteria
- However: Existing Phase I has 91 tests - RECOMMENDATION: Extend test coverage for quality assurance
- Acceptance criteria defined for all 5 user stories (spec.md lines 18-97)

**Decision**: Implement tests for critical features (priorities, tags, search, filter) but not mandatory for Phase I extension.

### VI. Stateless Architecture

✅ **PASS** - Maintains stateless in-memory design
- Phase I uses in-memory `dict[int, TodoItem]` (stateless per request)
- No session storage (console app runs per command)
- All state in memory (prepares for Phase II database migration)
- Server restarts (new command invocations) start fresh (Phase I behavior)
- Architecture separates core/ (business logic) from ui/ (CLI) for Phase II scalability

**Note**: Reminder system works only while app running (spec assumption #2) - acceptable for Phase I.

### VII. Documentation and Traceability

✅ **PASS** - Comprehensive documentation generated
- ✅ Constitution: `.specify/memory/constitution.md` (defines project principles)
- ✅ Spec: `specs/001-advanced-todo-features/spec.md` (WHAT to build, 233 lines)
- ✅ Plan: `specs/001-advanced-todo-features/plan.md` (this file - HOW to build)
- ✅ Research: `specs/001-advanced-todo-features/research.md` (technical decisions)
- ✅ Data Model: `specs/001-advanced-todo-features/data-model.md` (entity definitions)
- ✅ Contracts: `specs/001-advanced-todo-features/contracts/cli-commands.md` (API specifications)
- ⏳ Tasks: `specs/001-advanced-todo-features/tasks.md` (generated by `/sp.tasks`)
- ✅ CLAUDE.md: Runtime guidance for Claude Code (existing)
- ✅ Prompt History: `history/prompts/001-advanced-todo-features/001-advanced-todo-features-specification.spec.prompt.md`

All code will include comments linking to Task IDs from tasks.md.

**Overall Constitution Compliance**: ✅ **PASS** - All gates satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-advanced-todo-features/
├── spec.md              # Feature requirements (233 lines, 5 user stories, 30 FRs)
├── plan.md              # This file - implementation architecture
├── research.md          # Technical research findings
├── data-model.md        # Entity definitions (TodoItem extended, FilterCriteria, SortOptions)
├── contracts/
│   └── cli-commands.md  # CLI command specifications
├── tasks.md             # Task breakdown (generated by /sp.tasks)
└── checklists/
    └── requirements.md  # Specification quality validation
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── core/                       # Business logic (NO UI dependencies)
│   ├── __init__.py
│   ├── todo_item.py            # MODIFY: Add 5 new fields (priority, tags, due_date, recurrence_pattern, recurrence_parent_id)
│   └── todo_manager.py         # MODIFY: Add filter_todos, search_todos, check_reminders methods
└── ui/                         # User interface (depends on core/)
    ├── __init__.py
    └── cli.py                  # MODIFY: Extend add/list commands, add search command

tests/
├── __init__.py
├── test_todo_item.py           # EXTEND: Add TestTodoItemPriority, TestTodoItemTags, TestTodoItemDueDates, TestTodoItemRecurrence
├── test_todo_manager.py        # EXTEND: Add TestTodoManagerFilter, TestTodoManagerSearch, TestTodoManagerSort, TestTodoManagerRecurring
└── test_cli.py                 # EXTEND: Add TestCliSearch, extend TestCliAdd, TestCliList, TestCliUpdate
```

**Structure Decision**: Single project structure (Option 1) maintained from Phase I. Clean separation between core/ (business logic) and ui/ (CLI) enables Phase II migration to web application without core/ modifications.

## Complexity Tracking

No constitution violations. No complexity justifications required.

## Phase 0: Research & Technical Decisions

**Status**: ✅ **Complete** (research.md generated)

### Key Findings

1. **Pydantic Model Extension**: Existing TodoItem uses Field() constraints and field_validator patterns - ideal for adding priority/tags/due_date/recurrence fields.

2. **TodoManager Filtering**: Current list_todos() method uses list comprehensions for filtering - extend with multi-criteria filter_todos() method.

3. **Typer CLI Patterns**: Existing commands use Argument/Option decorators with type hints - extend add/list commands with new options.

4. **Rich Table Display**: Current table formatting uses color dictionaries for status - extend with priority colors and new columns.

5. **Test Coverage**: 91 existing tests across 17 test classes - extend existing test classes with new test methods.

### Research Artifacts

- **research.md**: Complete technical research (203 lines)
  - Language/version decisions (Python 3.12+)
  - Dependency analysis (Pydantic, Typer, Rich patterns)
  - Storage strategy (in-memory dict)
  - Testing approach (extend existing pytest classes)
  - Technology decisions (Literal types, datetime handling, recurrence mechanism)
  - Best practices (Pydantic validation, CLI error handling, type hints)
  - Integration patterns (model extension, manager methods, CLI commands)
  - Risk mitigation (date parsing, tag sanitization, reminder spam, sort validation)

## Phase 1: Design & Contracts

**Status**: ✅ **Complete** (data-model.md, contracts/ generated)

### Data Model

**File**: `data-model.md` (533 lines)

**Extended TodoItem** (5 new fields):
- `priority: Literal["high", "medium", "low"] = "medium"` - Task urgency level
- `tags: list[str] = []` - Category labels (max 10, lowercase alphanumeric + hyphens)
- `due_date: datetime | None = None` - Deadline with time (ISO 8601)
- `recurrence_pattern: Literal["daily", "weekly", "monthly"] | None = None` - Auto-repeat schedule
- `recurrence_parent_id: int | None = None` - Links recurring task instances

**New Entities**:
- **FilterCriteria**: Encapsulates search/filter parameters (keyword, status, priority, tags, date_from, date_to)
- **SortOptions**: Defines task ordering (sort_by: priority/due_date/created_at/title, sort_order: asc/desc)

**Validation Rules** (6 new validators):
1. `validate_tags`: Max 10 tags, lowercase, alphanumeric + hyphens, trim whitespace
2. `validate_recurrence`: Recurrence requires due_date (FR-030)
3. Priority enum validation (high/medium/low)
4. Status enum validation (existing: pending/in_progress/completed)
5. Title non-empty validation (existing)
6. Tag count limit (max 10)

**Relationships**:
- Self-referencing: Recurring tasks link via `recurrence_parent_id`
- Original task has `recurrence_pattern` set, `recurrence_parent_id=None`
- Instances have `recurrence_parent_id` pointing to original, inherit all attributes except id/status/timestamps

### CLI Contracts

**File**: `contracts/cli-commands.md` (688 lines)

**Extended Commands**:

1. **add** (Extended):
   - New options: `--priority/-p` (high/medium/low), `--tags/-t` (comma-separated), `--due-date` (YYYY-MM-DD HH:MM), `--recurrence/-r` (daily/weekly/monthly)
   - Validation: Recurrence requires due_date, max 10 tags
   - Output: Display new fields with color coding

2. **list** (Extended):
   - New options: `--priority/-p`, `--tags/-t`, `--keyword/-k`, `--from-date`, `--to-date`, `--sort-by` (priority/due_date/created_at/title), `--order` (asc/desc)
   - Filter logic: AND (all criteria must match)
   - Display: Rich table with priority colors, tag display (#tag), overdue indicator, filter summary

3. **search** (New Command):
   - Signature: `search <keyword> [--status] [--priority] [--tags]`
   - Behavior: Case-insensitive substring search in title + description
   - Output: Filtered table sorted by creation date

4. **update** (Extended):
   - New options: `--priority`, `--tags` (replaces existing), `--due-date` (or "none" to clear), `--recurrence/-r` (or "none" to remove)
   - Special: Clearing due_date removes recurrence automatically

5. **complete** (Auto-Create for Recurring):
   - New behavior: If task has `recurrence_pattern`, auto-creates next instance with:
     - Calculated next due_date (+1 day/+7 days/+1 month)
     - Status reset to "pending"
     - New ID, timestamps
     - All other attributes inherited

6. **delete** (Unchanged):
   - No changes from Phase I

**Performance Targets**:
- Add: <100ms
- List 1000 tasks: <1s (SC-002)
- Search 1000 tasks: <1s (SC-002)
- Filter + Sort: <500ms for 100+ tasks (SC-004)
- Complete (recurring): <1s including next instance (SC-006)

### Quick Start Guide

**File**: `quickstart.md` (to be created)

```markdown
# Quick Start: Advanced Todo Features

## Installation
\`\`\`bash
cd hackathon-2
uv sync
\`\`\`

## Basic Usage

### Create Tasks with Priorities
\`\`\`bash
# High-priority work task
uv run python main.py add "Quarterly report" -p high -t "work,reports"

# Medium-priority personal task with due date
uv run python main.py add "Dentist appointment" -p medium -t "health,personal" --due-date "2025-12-30 14:00"
\`\`\`

### Filter and Search
\`\`\`bash
# List all high-priority work tasks
uv run python main.py list -p high -t work

# Search for "meeting" in all tasks
uv run python main.py search "meeting"

# List pending tasks sorted by due date
uv run python main.py list -s pending --sort-by due_date
\`\`\`

### Recurring Tasks
\`\`\`bash
# Create weekly recurring task
uv run python main.py add "Team standup" -p medium -t "work,meetings" --due-date "2025-12-27 09:00" -r weekly

# Complete (auto-creates next instance)
uv run python main.py complete 1
\`\`\`

## Feature Guide

### Priority Levels
- **high**: Red bold display, urgent tasks
- **medium**: Yellow display, normal priority (default)
- **low**: Green display, when-possible tasks

### Tags
- Comma-separated: `-t "work,urgent,q4"`
- Max 10 per task
- Auto-normalized to lowercase
- Display with # prefix: `#work #urgent #q4`

### Due Dates
- Format: `YYYY-MM-DD HH:MM`
- Example: `--due-date "2025-12-30 14:00"`
- Overdue tasks shown in red bold

### Recurrence Patterns
- **daily**: Creates next instance tomorrow
- **weekly**: Creates next instance +7 days
- **monthly**: Creates next instance same day next month
- Requires due date
- Auto-creates on completion

### Filtering
- AND logic: All criteria must match
- Options: `--status`, `--priority`, `--tags`, `--keyword`, `--from-date`, `--to-date`
- Example: `list -s pending -p high -t work --keyword "report"`

### Sorting
- Fields: `priority`, `due_date`, `created_at`, `title`
- Order: `asc` (default) or `desc`
- Example: `list --sort-by priority --order desc`

## Testing
\`\`\`bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Type check
uv run mypy src/ --strict
\`\`\`

## Troubleshooting

### "Invalid date format" error
Use ISO 8601 format: `YYYY-MM-DD HH:MM`
Example: `2025-12-30 14:00`

### "Maximum 10 tags allowed" error
Reduce tag count. Split tasks if needed for different categorization.

### "Recurring tasks must have a due date" error
Add `--due-date` when using `--recurrence`:
\`\`\`bash
# Wrong:
add "Task" -r weekly

# Correct:
add "Task" --due-date "2025-12-27 09:00" -r weekly
\`\`\`

### Reminders not showing
Reminders only work while app is running (console app limitation).
Check for missed reminders on next app startup.
\`\`\`
```

## Architecture Decisions

### Decision 1: Priority Field Implementation

**Context**: Need to add urgency levels to tasks (FR-001).

**Options Considered**:
1. String field with validation
2. Integer field (1=high, 2=medium, 3=low)
3. Pydantic Literal type

**Decision**: Pydantic `Literal["high", "medium", "low"]` with default="medium"

**Rationale**:
- Type safety: mypy catches invalid priority values at compile time
- Auto-generates JSON schema for Phase II API
- Natural string values in CLI (user-friendly)
- Pydantic validation ensures only valid values stored

**Consequences**:
- CLI can accept any case ("High", "HIGH", "high") - normalize to lowercase
- Sorting requires custom logic (high=0, medium=1, low=2 mapping)
- Database migration (Phase II) uses VARCHAR(10) column

**Status**: ✅ **Approved**

---

### Decision 2: Tags Storage and Normalization

**Context**: Tasks need category labels (FR-002, FR-004).

**Options Considered**:
1. Comma-separated string
2. Set[str] (unique tags)
3. list[str] with validation

**Decision**: `list[str]` with field_validator for normalization

**Rationale**:
- Native Python list type (JSON serializable)
- Pydantic default_factory=list for empty lists
- field_validator enforces max 10 tags, lowercase, alphanumeric + hyphens
- Preserves tag order (list vs set)
- Easy filtering: `all(tag in todo.tags for tag in filter_tags)`

**Normalization Rules**:
1. Convert to lowercase
2. Trim whitespace
3. Replace invalid chars with hyphens
4. Remove consecutive hyphens
5. Maximum 10 tags per task

**Consequences**:
- Tags stored as `["work", "urgent", "q4"]` in model
- CLI input: `--tags "work,urgent,Q4"` normalized to lowercase
- Database (Phase II): PostgreSQL JSONB column with GIN index

**Status**: ✅ **Approved**

---

### Decision 3: Due Date and Timezone Handling

**Context**: Tasks need deadlines with time (FR-018, FR-019).

**Options Considered**:
1. String field with manual parsing
2. Python datetime with timezone
3. datetime without timezone (naive)
4. Third-party library (pendulum, arrow)

**Decision**: Python `datetime` with system local timezone

**Rationale**:
- Spec assumption #3: System local timezone only (no multi-timezone support)
- Python datetime is stdlib (no new dependencies)
- ISO 8601 format via strptime/strftime
- Timezone-aware via datetime.now() with timezone info

**Date Format**:
- **Input**: ISO 8601 `YYYY-MM-DD HH:MM` (e.g., "2025-12-30 14:00")
- **Storage**: datetime object with local timezone
- **Display**: Human-readable "MMM DD, YYYY H:MMAM/PM" (e.g., "Dec 30, 2025 2:00PM")

**Consequences**:
- Users must input dates in ISO format (no natural language "tomorrow")
- Overdue check: `todo.due_date < datetime.now()`
- Sorting nulls: Use `datetime.max` for tasks without due dates
- Phase II: Store as TIMESTAMP WITH TIME ZONE in PostgreSQL

**Status**: ✅ **Approved**

---

### Decision 4: Recurring Task Mechanism

**Context**: Automate repeating tasks (FR-025 to FR-030).

**Options Considered**:
1. Single task with "last completed" timestamp
2. Clone task on completion
3. Parent-child relationship with instance tracking

**Decision**: Parent-child relationship with `recurrence_parent_id`

**Rationale**:
- Tracks original recurring task (parent)
- Each completion creates new instance (child) with:
  - New ID, timestamps, status="pending"
  - Inherited: title, description, priority, tags, recurrence_pattern
  - Calculated next due_date based on pattern
- Allows viewing recurring task history (future feature)
- Enables editing recurrence series (future feature)

**Recurrence Calculation** (FR-027: use original schedule, not completion time):
- **Daily**: `due_date + timedelta(days=1)`
- **Weekly**: `due_date + timedelta(days=7)`
- **Monthly**: `due_date.replace(month=due_date.month + 1)` (same day of month)

**Validation** (FR-030): Recurring tasks MUST have due_date

**Consequences**:
- `complete_todo()` method checks `recurrence_pattern` and creates new instance
- Each instance is independent task (can be deleted individually)
- Original parent remains for reference
- Phase II: Track entire series via `recurrence_parent_id` query

**Status**: ✅ **Approved**

---

### Decision 5: Filter and Search Implementation

**Context**: Support multi-criteria filtering and keyword search (FR-006 to FR-012).

**Options Considered**:
1. Separate filter_by_X methods for each criterion
2. Single filter_todos() with optional parameters
3. FilterCriteria dataclass/Pydantic model

**Decision**: Single `filter_todos()` method with optional parameters + FilterCriteria model (for typing)

**Rationale**:
- Single method simplifies TodoManager API
- Optional parameters allow flexible filtering (any combination)
- AND logic: All specified filters must match
- FilterCriteria model provides type hints for CLI parsing (Phase II)

**Implementation**:
```python
def filter_todos(
    self,
    keyword: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> list[TodoItem]:
    todos = list(self._todos.values())
    if keyword:
        keyword_lower = keyword.lower()
        todos = [t for t in todos if keyword_lower in t.title.lower() or keyword_lower in t.description.lower()]
    if priority:
        todos = [t for t in todos if t.priority == priority]
    if tags:
        todos = [t for t in todos if all(tag in t.tags for tag in tags)]
    if status:
        todos = [t for t in todos if t.status == status]
    if date_from or date_to:
        todos = [t for t in todos if (not date_from or t.created_at >= date_from) and (not date_to or t.created_at <= date_to)]
    return todos
```

**Search Command**: Dedicated `search` command calls `filter_todos(keyword=...)` with optional status/priority/tags filters.

**Consequences**:
- Performance: O(n) filtering - acceptable for <1000 tasks (SC-002: <1s)
- Tag filter uses ALL (AND logic): `all(tag in todo.tags for tag in filter_tags)`
- Keyword search is case-insensitive substring match
- Phase II: Replace with database queries (indexed filtering)

**Status**: ✅ **Approved**

---

### Decision 6: Sort Implementation

**Context**: Allow sorting by different fields (FR-013 to FR-017).

**Options Considered**:
1. Separate sort_by_X methods
2. Single sort method with field parameter
3. SortOptions dataclass with field + order

**Decision**: Single method with `sort_by` and `sort_order` parameters + SortOptions model

**Rationale**:
- Dynamic sorting: `sorted(todos, key=lambda t: getattr(t, sort_by), reverse=(sort_order == "desc"))`
- Simple API: One method handles all sort fields
- SortOptions model provides type hints for CLI

**Implementation**:
```python
def sort_todos(self, todos: list[TodoItem], sort_by: str = "created_at", sort_order: str = "asc") -> list[TodoItem]:
    reverse = sort_order == "desc"

    # Special handling for due_date (nulls last)
    if sort_by == "due_date":
        return sorted(todos, key=lambda t: t.due_date or datetime.max, reverse=reverse)

    # Priority sorting (high=0, medium=1, low=2)
    if sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(todos, key=lambda t: priority_order[t.priority], reverse=reverse)

    # Default: use getattr for created_at, title
    return sorted(todos, key=lambda t: getattr(t, sort_by), reverse=reverse)
```

**Null Handling** (FR-014): Tasks without due_date sorted last (use `datetime.max`)

**Consequences**:
- Performance: O(n log n) Python sorted() - acceptable for 100+ tasks (SC-004: <500ms)
- CLI validates sort_by against allowed fields (priority/due_date/created_at/title)
- Maintains sort order when new tasks added (FR-017) - CLI re-calls sort after add

**Status**: ✅ **Approved**

---

### Decision 7: Reminder System (Console-Based)

**Context**: Notify users of upcoming due dates (FR-021 to FR-024).

**Options Considered**:
1. Background thread polling
2. Check on every list operation
3. Check only on startup
4. Hybrid: Startup + list operations

**Decision**: Hybrid approach (startup + list operations)

**Rationale**:
- Spec assumption #2: Console app, reminders only while running
- No background daemon needed (Phase I in-memory limitation)
- Acceptable performance: Check is O(n) scan of due_date field

**Implementation**:
```python
def check_reminders(self) -> list[TodoItem]:
    """Return tasks due within next 30 minutes."""
    now = datetime.now()
    soon = now + timedelta(minutes=30)
    reminders = [
        t for t in self._todos.values()
        if t.due_date and t.status != "completed" and now <= t.due_date <= soon
    ]
    return reminders
```

**Trigger Points**:
- App startup (FR-021): Check for overdue + upcoming
- `list` command: Check and display reminders before table
- `add` command with due_date: Check if new task is due soon

**Display** (FR-022):
```
[REMINDER] 2 tasks due soon:
  - ID 3: Team standup (due in 15 minutes)
  - ID 7: Client call (due in 28 minutes)
```

**Consequences**:
- Missed reminders (app closed): Shown on next startup
- No persistent reminder state (in-memory only)
- Performance acceptable: <5 seconds on startup (SC-005)
- Phase II: Replace with scheduled jobs (Dapr Jobs API, Phase V)

**Status**: ✅ **Approved**

---

## Implementation Sequence

### Phase 2: Task Breakdown (Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `specs/001-advanced-todo-features/tasks.md` with:
- Task groups organized by user story (P1-P5)
- Atomic, testable tasks with acceptance criteria
- Dependencies clearly marked
- Parallelizable tasks flagged with [P]
- Estimated 30-50 tasks total

**Task Structure**:
```markdown
## Task Group: P1 - Task Organization (Priority & Tags)

### T-001: Extend TodoItem model with priority field [P]
- Add `priority: Literal["high", "medium", "low"] = Field(default="medium")`
- Update ConfigDict json_schema_extra example
- Run mypy --strict verification

**Acceptance**:
- TodoItem can be created with priority="high"
- Default priority is "medium"
- Invalid priority raises ValidationError
- Type hints pass mypy --strict

**Files**: src/core/todo_item.py

### T-002: Add tags field with validation to TodoItem [P]
- Add `tags: list[str] = Field(default_factory=list)`
- Implement field_validator for tag normalization
- Enforce max 10 tags limit

**Acceptance**:
- Tags stored as lowercase alphanumeric + hyphens
- Max 10 tags enforced
- Whitespace trimmed
- Empty tags removed

**Files**: src/core/todo_item.py

[... continue for all 30-50 tasks ...]
```

### Phase 3: Implementation (After tasks.md)

**Command**: `/sp.implement` or manual implementation with Claude Code

**Workflow**:
1. For each task in tasks.md:
   - Read task acceptance criteria
   - Generate code with Claude Code
   - Reference Task ID in comments (`# T-001: Extend TodoItem model`)
   - Run mypy --strict validation
   - Run affected tests

2. Test-Driven Development (if tests requested):
   - Red: Write failing test for acceptance criteria
   - Green: Implement code to pass test
   - Refactor: Clean up while maintaining green tests

3. Documentation updates:
   - Update README.md with new features
   - Update CLI help text
   - Create/update quickstart.md

### Phase 4: Validation & Demo

**Acceptance Validation**:
- All 30 functional requirements (FR-001 to FR-030) implemented
- All 13 success criteria (SC-001 to SC-013) met
- All 25+ acceptance scenarios pass
- mypy --strict passes with zero errors
- pytest runs without failures
- quickstart.md workflow executes successfully

**Demo Workflow** (test_cli_workflow.py):
```python
# 1. Add tasks with priorities and tags
manager.add_todo("Quarterly report", priority="high", tags=["work", "reports"])
manager.add_todo("Team standup", priority="medium", tags=["work", "meetings"], due_date="2025-12-27 09:00", recurrence="weekly")

# 2. Filter and search
high_work_tasks = manager.filter_todos(priority="high", tags=["work"])
meeting_tasks = manager.filter_todos(keyword="meeting")

# 3. Sort tasks
sorted_by_priority = manager.sort_todos(high_work_tasks, sort_by="priority", sort_order="desc")

# 4. Complete recurring task (auto-creates next instance)
manager.complete_todo(2)  # Creates new weekly instance

# 5. Check reminders
reminders = manager.check_reminders()
```

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Due Date Parsing Errors** | Users frustrated by format requirements | Clear error messages with examples, help text shows format |
| **Tag Input Inconsistency** | Search/filter fails due to case/spacing | field_validator normalizes all tags (lowercase, trim) |
| **Reminder Notification Spam** | User overload with many overdue tasks | Only notify tasks due within 30 minutes (not all overdue) |
| **Sort Field Validation** | Runtime errors for invalid sort fields | CLI validates against enum before calling TodoManager |
| **Recurring Task Infinite Loops** | System creates unlimited instances | Create only one instance per completion, check if exists |
| **mypy --strict Failures** | Code doesn't type check | Incremental development with mypy validation per task |
| **Performance on Large Lists** | Slow filter/sort for 1000+ tasks | Acceptable per spec (<1s for 1000 tasks), optimize if needed |
| **In-Memory Limitation** | Data lost on app exit | Document clearly, remind users (Phase II adds persistence) |

## Non-Goals (Out of Scope)

Per spec Scope Boundaries:

- ❌ **Persistent storage (database)** - Deferred to Phase II
- ❌ **Natural language date parsing** - ISO format only
- ❌ **Complex recurrence patterns** - Only daily/weekly/monthly
- ❌ **Reminder delivery via email/SMS** - Console-only
- ❌ **Mobile or web interface** - CLI only
- ❌ **Multi-timezone support** - Local timezone only
- ❌ **Task dependencies or subtasks** - Future feature
- ❌ **Collaboration or task sharing** - Single-user app
- ❌ **Undo/redo functionality** - Not specified
- ❌ **Import/export to external formats** - Future feature
- ❌ **Calendar integration** - Not specified
- ❌ **Background daemon for reminders** - Show on next startup instead

## Appendix: File Modification Summary

### Files to Modify

| File | Lines | Changes | Complexity |
|------|-------|---------|------------|
| `src/core/todo_item.py` | 57 → ~120 | +5 fields, +2 validators | Medium |
| `src/core/todo_manager.py` | 139 → ~250 | +3 methods (filter/search/check_reminders), extend complete_todo | Medium |
| `src/ui/cli.py` | 139 → ~300 | Extend add/list commands, add search command | High |
| `tests/test_todo_item.py` | 193 → ~300 | +4 test classes (priority, tags, due_dates, recurrence) | Medium |
| `tests/test_todo_manager.py` | 386 → ~550 | +4 test classes (filter, search, sort, recurring) | High |
| `tests/test_cli.py` | 267 → ~400 | Extend add/list tests, add search tests | Medium |
| `README.md` | ~220 → ~350 | Document new features, update usage examples | Low |

**Total Estimated LOC**: ~1500 lines added/modified across 7 files

### Files to Create

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `specs/001-advanced-todo-features/quickstart.md` | User guide for new features | ~150 |
| `test_cli_workflow_advanced.py` | Demo script showcasing advanced features | ~100 |

## Approval Checklist

- [x] Constitution compliance verified (all 7 principles)
- [x] Technical context fully specified
- [x] Research completed and documented
- [x] Data model defined with validation rules
- [x] CLI contracts specified with examples
- [x] Architectural decisions documented
- [x] Risks identified with mitigation strategies
- [x] Implementation sequence planned
- [x] Non-goals explicitly stated

**Status**: ✅ **Ready for Phase 2 (Task Generation)** - Run `/sp.tasks` to generate task breakdown

**Next Command**: `/sp.tasks`
