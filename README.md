# Evolution of Todo - Phase II: Advanced Console Application

A feature-rich Python console todo application built with **Pydantic**, **Typer**, and **Rich**. This is Phase II featuring advanced task management capabilities including priorities, tags, search, filtering, sorting, due dates, reminders, and recurring tasks.

## Features

### Core Features (Phase I)
- **Add** todos with title and optional description
- **List** todos in a formatted table with color-coded status
- **Complete** todos to mark them as done
- **Update** todo fields (title, description, status)
- **Delete** todos when no longer needed
- **In-memory storage** for fast, session-based task management

### Advanced Features (Phase II)

#### 🎯 Priorities & Tags (US1)
- **Priority Levels**: High, medium, low with color-coded display
- **Tags/Categories**: Multi-tag support (max 10 tags per task)
- **Tag Normalization**: Auto-lowercase, alphanumeric + hyphens
- **Filter by Priority**: `--priority high/medium/low`
- **Filter by Tags**: `--tags work,urgent` (AND logic)

#### 🔍 Search & Filter (US2)
- **Keyword Search**: Search in title and description (case-insensitive)
- **Advanced Filtering**: Combine keyword + status + priority + tags
- **Date Range Filtering**: Filter by creation date
- **AND Logic**: All filters combined with AND logic

#### 📊 Sort Tasks (US3)
- **Sort by Priority**: High → Medium → Low
- **Sort by Due Date**: Chronological with null dates last
- **Sort by Created Date**: Chronological ordering
- **Sort by Title**: Alphabetical (case-insensitive)
- **Sort Order**: Ascending or descending

#### ⏰ Due Dates & Reminders (US4)
- **Due Dates**: ISO 8601 format (YYYY-MM-DD HH:MM)
- **Overdue Indicator**: Bold red "OVERDUE!" for past-due tasks
- **Reminder Notifications**: 30-minute warning window
- **Auto-Check**: Reminders displayed on `list` command

#### ♻️ Recurring Tasks (US5)
- **Recurrence Patterns**: Daily, weekly, monthly
- **Auto-Creation**: Next instance auto-created on completion
- **Parent-Child Linking**: Track recurring task instances
- **Pattern Display**: Visual indicators (D/W/M) in task list

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

### Feature Demonstrations

**User Story 1: Priorities & Tags**
```bash
uv run python test_us1_demo.py
```
Demonstrates: Priority levels, tag filtering, tag normalization, combined filters

**User Story 2: Search & Filter**
```bash
uv run python test_us2_demo.py
```
Demonstrates: Keyword search, case-insensitive matching, combined filters, empty results

### Usage Examples

**Example 1: High-Priority Work Task with Deadline**
```bash
# Create urgent work task
uv run python main.py add "Quarterly Report" \
  --description "Prepare Q4 financial summary" \
  --priority high \
  --tags work,reports,urgent \
  --due-date "2025-01-15 17:00"

# View high-priority work tasks
uv run python main.py list --priority high --tags work --sort-by due_date
```

**Example 2: Weekly Recurring Task**
```bash
# Create weekly team meeting
uv run python main.py add "Team standup" \
  --description "Weekly team sync meeting" \
  --priority medium \
  --tags work,meeting \
  --due-date "2025-01-08 10:00" \
  --recurrence weekly

# Complete it (auto-creates next week's instance)
uv run python main.py complete 1
```

**Example 3: Search and Filter Workflow**
```bash
# Search for meeting-related tasks
uv run python main.py search "meeting"

# Find pending work tasks sorted by priority
uv run python main.py list --status pending --tags work --sort-by priority --order desc

# Find overdue tasks (list will show OVERDUE! in red)
uv run python main.py list --sort-by due_date
```

**Example 4: Task Organization with Tags**
```bash
# Add personal tasks
uv run python main.py add "Buy groceries" --tags personal,shopping --priority low
uv run python main.py add "Call dentist" --tags personal,health --priority medium

# Add work tasks
uv run python main.py add "Fix bug #456" --tags work,urgent,bug --priority high
uv run python main.py add "Write docs" --tags work,documentation --priority medium

# View by category
uv run python main.py list --tags work
uv run python main.py list --tags personal
```

**Note**: Since Phase II uses in-memory storage, each command invocation creates a fresh `TodoManager` instance. Use the demo scripts to see complete workflows in action.

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
- `priority`: `high` | `medium` | `low` (default: medium)
- `tags`: List of category labels (max 10, auto-normalized)
- `due_date`: Optional deadline (ISO 8601 datetime)
- `recurrence_pattern`: `daily` | `weekly` | `monthly` | None
- `recurrence_parent_id`: Link to parent task (for recurring instances)
- `created_at`: Auto-set creation timestamp
- `updated_at`: Auto-updated modification timestamp

**TodoManager** (Business logic service):
- In-memory storage using `dict[int, TodoItem]`
- Sequential ID generation starting from 1
- CRUD operations with O(1) lookups
- Advanced filtering with keyword search and AND logic
- Multi-criteria sorting (priority, due_date, created_at, title)
- Reminder checking (30-minute window)
- Automatic recurring task creation on completion

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

### `add` - Create a new todo

```bash
# Basic usage
uv run python main.py add "Task title"

# With all options
uv run python main.py add "Weekly report" \
  --description "Q4 financial summary" \
  --priority high \
  --tags work,reports,urgent \
  --due-date "2025-01-15 14:00" \
  --recurrence weekly
```

**Options:**
- `--description, -d`: Task details (max 1000 chars)
- `--priority, -p`: Priority level (high/medium/low, default: medium)
- `--tags, -t`: Comma-separated tags (max 10, auto-normalized)
- `--due-date`: Due date in YYYY-MM-DD HH:MM format
- `--recurrence, -r`: Recurrence pattern (daily/weekly/monthly, requires --due-date)

### `list` - Show all todos

```bash
# Show all tasks
uv run python main.py list

# Filter by status
uv run python main.py list --status pending

# Filter by priority
uv run python main.py list --priority high

# Filter by tags (AND logic)
uv run python main.py list --tags work,urgent

# Sort tasks
uv run python main.py list --sort-by priority --order desc
uv run python main.py list --sort-by due_date

# Date range filtering
uv run python main.py list --from "2025-01-01" --to "2025-01-31"

# Combine filters
uv run python main.py list --status pending --priority high --tags work
```

**Options:**
- `--status, -s`: Filter by status (pending/in_progress/completed)
- `--priority, -p`: Filter by priority (high/medium/low)
- `--tags, -t`: Filter by tags (comma-separated, AND logic)
- `--sort-by`: Sort field (priority/due_date/created_at/title, default: created_at)
- `--order`: Sort order (asc/desc, default: asc)
- `--from`: Filter tasks created on or after this date (YYYY-MM-DD)
- `--to`: Filter tasks created on or before this date (YYYY-MM-DD)

**Features:**
- Automatic reminder notifications for tasks due within 30 minutes
- Color-coded priorities (red=high, yellow=medium, green=low)
- Overdue indicator (bold red "OVERDUE!" for past-due tasks)
- Recurrence pattern display (D=daily, W=weekly, M=monthly)

### `search` - Search todos by keyword

```bash
# Basic keyword search
uv run python main.py search "meeting"

# Search with filters
uv run python main.py search "report" --priority high --tags work
```

**Features:**
- Searches in both title and description
- Case-insensitive matching
- Supports all list filters (status, priority, tags)

### `complete` - Mark todo as completed

```bash
uv run python main.py complete 1
```

**Features:**
- Automatically creates next instance for recurring tasks
- Shows notification with next due date for recurring tasks

### `update` - Modify todo fields

```bash
# Update individual fields
uv run python main.py update 1 --title "New title"
uv run python main.py update 1 --status in_progress
uv run python main.py update 1 --priority high
uv run python main.py update 1 --tags work,urgent
uv run python main.py update 1 --due-date "2025-01-20 10:00"
uv run python main.py update 1 --recurrence monthly

# Clear fields
uv run python main.py update 1 --due-date none
uv run python main.py update 1 --recurrence none

# Update multiple fields
uv run python main.py update 1 --priority high --tags work,urgent --status in_progress
```

**Options:**
- `--title`: New task title
- `--description, -d`: New description
- `--status, -s`: New status (pending/in_progress/completed)
- `--priority, -p`: New priority (high/medium/low)
- `--tags, -t`: New tags (replaces existing)
- `--due-date`: New due date (YYYY-MM-DD HH:MM or "none" to clear)
- `--recurrence, -r`: New recurrence pattern (daily/weekly/monthly or "none" to clear)

### `delete` - Remove a todo

```bash
uv run python main.py delete 1
```

### Field Values Reference

**Status:**
- `pending` - Not started (white in terminal)
- `in_progress` - Currently working (yellow)
- `completed` - Finished (green)

**Priority:**
- `high` - Urgent/important (red)
- `medium` - Normal priority (yellow)
- `low` - Can wait (green)

**Recurrence Patterns:**
- `daily` - Repeats every day
- `weekly` - Repeats every 7 days
- `monthly` - Repeats same day of month (handles month-end edge cases)

## Roadmap

### Phase I ✅
- In-memory console application
- Basic CRUD operations
- Rich terminal UI

### Phase II (Current) ✅
- Advanced task management features
- Priorities & tags/categories
- Search & filter capabilities
- Multi-criteria sorting
- Due dates & reminders
- Recurring tasks

### Phase III (Planned)
- FastAPI backend with Neon PostgreSQL
- Next.js frontend
- Multi-user support
- Persistent storage
- Real-time notifications

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
