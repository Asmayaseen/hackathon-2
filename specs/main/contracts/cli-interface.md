# CLI Interface Contract - Phase I Console Todo App

**Date**: 2025-12-25
**Status**: Complete
**Related**: [../data-model.md](../data-model.md) | [../plan.md](../plan.md)

## Overview

This document defines the command-line interface contract for the Phase I todo application. All commands use Typer framework with Rich formatting for output.

**Entry Point**: `uv run todo <command> [arguments] [options]`

**Technology**: Typer (CLI framework) + Rich (terminal UI)

---

## Commands

### 1. add - Add New Todo

**Signature**:
```bash
todo add <title> [--description TEXT]
```

**Arguments**:
- `<title>` (required): Todo title (1-200 characters)

**Options**:
- `--description TEXT`, `-d TEXT`: Optional detailed description (max 1000 chars)

**Behavior**:
1. Validate title (1-200 chars, not empty/whitespace)
2. Call `TodoManager.add_todo(title, description)`
3. Display success message with assigned ID

**Output** (success):
```text
✓ Todo added successfully!

  ID: 1
  Title: Implement data model
  Status: pending
```

**Output** (error - empty title):
```text
Error: Title cannot be empty or whitespace
```

**Output** (error - title too long):
```text
Error: Title must be 200 characters or less (got 250)
```

**User Stories**: P1 - Add todo (core value)

---

### 2. list - List All Todos

**Signature**:
```bash
todo list [--status STATUS]
```

**Options**:
- `--status STATUS`, `-s STATUS`: Filter by status (pending/in_progress/completed)

**Behavior**:
1. Call `TodoManager.list_todos(status=<filter>)`
2. Display todos in Rich table format
3. Show empty message if no todos match

**Output** (with todos):
```text
┌────┬─────────────────────────────┬────────────┬──────────────────┐
│ ID │ Title                       │ Status     │ Created          │
├────┼─────────────────────────────┼────────────┼──────────────────┤
│ 1  │ Implement data model        │ completed  │ 2025-12-25 10:00 │
│ 2  │ Create CLI interface        │ in_progress│ 2025-12-25 11:00 │
│ 3  │ Write unit tests            │ pending    │ 2025-12-25 12:00 │
└────┴─────────────────────────────┴────────────┴──────────────────┘
```

**Output** (no todos):
```text
No todos found.
```

**Output** (filtered, no matches):
```text
No todos found with status 'completed'.
```

**Table Formatting**:
- **completed** status: Green text
- **in_progress** status: Yellow text
- **pending** status: White text
- **ID** column: Dimmed style
- **Created** column: Dimmed style, format `YYYY-MM-DD HH:MM`

**User Stories**: P1 - List todos (core value)

---

### 3. complete - Mark Todo as Completed

**Signature**:
```bash
todo complete <id>
```

**Arguments**:
- `<id>` (required): Todo ID (positive integer)

**Behavior**:
1. Call `TodoManager.complete_todo(id)`
2. Display success message with todo title
3. Show error if ID not found

**Output** (success):
```text
✓ Todo #3 marked as completed: "Write unit tests"
```

**Output** (error - not found):
```text
Error: Todo #999 not found
```

**User Stories**: P1 - Complete todo (core workflow)

---

### 4. delete - Delete Todo

**Signature**:
```bash
todo delete <id>
```

**Arguments**:
- `<id>` (required): Todo ID (positive integer)

**Behavior**:
1. Call `TodoManager.delete_todo(id)`
2. Display success message
3. Show error if ID not found

**Output** (success):
```text
✓ Todo #2 deleted successfully
```

**Output** (error - not found):
```text
Error: Todo #999 not found
```

**User Stories**: P2 - Delete todo (data management)

---

### 5. update - Update Todo Fields

**Signature**:
```bash
todo update <id> [--title TEXT] [--description TEXT] [--status STATUS]
```

**Arguments**:
- `<id>` (required): Todo ID (positive integer)

**Options**:
- `--title TEXT`, `-t TEXT`: New title (1-200 chars)
- `--description TEXT`, `-d TEXT`: New description (max 1000 chars)
- `--status STATUS`, `-s STATUS`: New status (pending/in_progress/completed)

**Behavior**:
1. Validate at least one option is provided
2. Call `TodoManager.update_todo(id, **fields)`
3. Display success message with updated fields
4. Show error if ID not found or validation fails

**Output** (success):
```text
✓ Todo #1 updated successfully

  ID: 1
  Title: Implement data model (updated)
  Description: Complete Pydantic model with validation
  Status: completed
  Updated: 2025-12-25 14:30
```

**Output** (error - no fields):
```text
Error: At least one field must be provided (--title, --description, or --status)
```

**Output** (error - not found):
```text
Error: Todo #999 not found
```

**Output** (error - invalid status):
```text
Error: Invalid status 'done'. Must be one of: pending, in_progress, completed
```

**User Stories**: P2 - Update todo (nice-to-have editing)

---

## Global Options

All commands support these global options:

- `--help`, `-h`: Display command help
- `--version`, `-v`: Display application version

**Example**:
```bash
todo --help
todo add --help
```

---

## Error Handling

All errors are displayed with Rich formatting:

```text
[red]Error:[/red] <error message>
```

**Common Errors**:
- **Validation Error**: Pydantic validation fails (title too long, invalid status, etc.)
- **Not Found Error**: Todo ID does not exist
- **Empty Input Error**: Required argument missing

**Exit Codes**:
- `0`: Success
- `1`: Validation error or not found
- `2`: Usage error (missing required arguments)

---

## User Journey Examples

### Journey 1: Quick Todo Workflow

```bash
# Add a new todo
$ todo add "Review pull requests"
✓ Todo added successfully!
  ID: 1

# Mark as completed
$ todo complete 1
✓ Todo #1 marked as completed: "Review pull requests"

# List all todos
$ todo list
┌────┬──────────────────────┬───────────┬──────────────────┐
│ ID │ Title                │ Status    │ Created          │
├────┼──────────────────────┼───────────┼──────────────────┤
│ 1  │ Review pull requests │ completed │ 2025-12-25 10:00 │
└────┴──────────────────────┴───────────┴──────────────────┘
```

### Journey 2: Detailed Todo Management

```bash
# Add todo with description
$ todo add "Implement authentication" --description "OAuth2 with JWT tokens"
✓ Todo added successfully!
  ID: 2

# Update status to in_progress
$ todo update 2 --status in_progress
✓ Todo #2 updated successfully

# List in-progress todos
$ todo list --status in_progress
┌────┬──────────────────────────┬────────────┬──────────────────┐
│ ID │ Title                    │ Status     │ Created          │
├────┼──────────────────────────┼────────────┼──────────────────┤
│ 2  │ Implement authentication │ in_progress│ 2025-12-25 11:00 │
└────┴──────────────────────────┴────────────┴──────────────────┘
```

### Journey 3: Error Handling

```bash
# Try to complete non-existent todo
$ todo complete 999
Error: Todo #999 not found

# Try to add todo with empty title
$ todo add ""
Error: Title cannot be empty or whitespace

# Try to update without any fields
$ todo update 1
Error: At least one field must be provided (--title, --description, or --status)
```

---

## Implementation Mapping

| CLI Command | TodoManager Method | TodoItem Fields |
|-------------|-------------------|-----------------|
| `todo add` | `add_todo(title, description)` | Creates new TodoItem |
| `todo list` | `list_todos(status)` | Displays id, title, status, created_at |
| `todo complete` | `complete_todo(id)` | Updates status to "completed" |
| `todo delete` | `delete_todo(id)` | Removes TodoItem |
| `todo update` | `update_todo(id, **fields)` | Updates title/description/status |

---

## Testing Requirements

### CLI Integration Tests

```python
# tests/test_cli.py
from typer.testing import CliRunner
from src.ui.cli import app

def test_add_todo_success():
    """CLI 'add' command should create todo and display success."""

def test_list_todos_displays_table():
    """CLI 'list' command should display todos in Rich table."""

def test_complete_todo_success():
    """CLI 'complete' command should mark todo as completed."""

def test_delete_todo_success():
    """CLI 'delete' command should remove todo."""

def test_update_todo_success():
    """CLI 'update' command should modify todo fields."""

def test_add_todo_empty_title_shows_error():
    """CLI 'add' with empty title should display error message."""

def test_complete_nonexistent_todo_shows_error():
    """CLI 'complete' with invalid ID should display error."""

def test_help_displays_usage():
    """CLI '--help' should display usage information."""
```

---

**CLI Contract Complete**: Ready for implementation in `src/ui/cli.py`
