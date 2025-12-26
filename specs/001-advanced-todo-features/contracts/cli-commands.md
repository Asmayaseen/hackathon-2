# CLI Command Contracts: Advanced Todo Features

**Feature**: 001-advanced-todo-features
**Date**: 2025-12-25
**Interface Type**: Command Line Interface (Typer)

## Command Overview

### Extended Commands (Phase I + New Features)

| Command | Purpose | New Options | Status |
|---------|---------|-------------|--------|
| `add` | Create task | --priority, --tags, --due-date, --recurrence | Extended |
| `list` | Display tasks | --priority, --tags, --sort-by, --order, --keyword, --from-date, --to-date | Extended |
| `update` | Modify task | --priority, --tags, --due-date, --recurrence | Extended |
| `search` | Find tasks | --priority, --tags, --status | New |
| `complete` | Mark done | (unchanged) | Existing |
| `delete` | Remove task | (unchanged) | Existing |

## Command Specifications

### 1. `add` - Create New Task (Extended)

**Purpose**: Create a new todo task with organization and scheduling features.

**Signature**:
```bash
python main.py add <title> [OPTIONS]
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| title | Argument | Yes | - | - | Task title (1-200 chars) |
| description | Option | No | -d, --description | "" | Task details (max 1000 chars) |
| priority | Option | No | -p, --priority | "medium" | Urgency: high, medium, low |
| tags | Option | No | -t, --tags | "" | Comma-separated tags (max 10) |
| due-date | Option | No | --due-date | None | Deadline in YYYY-MM-DD HH:MM format |
| recurrence | Option | No | -r, --recurrence | None | Repeat: daily, weekly, monthly |

**Examples**:
```bash
# Basic task
python main.py add "Buy groceries"

# High-priority work task with due date
python main.py add "Quarterly report" -p high -t "work,reports" --due-date "2025-12-30 14:00"

# Recurring weekly task
python main.py add "Team standup" -p medium -t "work,meetings" --due-date "2025-12-27 09:00" -r weekly

# With description
python main.py add "Call dentist" -d "Schedule annual checkup" -p high -t "health,personal"
```

**Output Success**:
```
[OK] Todo added successfully!

  ID: 1
  Title: Quarterly report
  Priority: [H] high
  Tags: #work #reports
  Due Date: Dec 30, 2025 2:00 PM
  Status: pending
  Recurrence: None
```

**Output Error (Invalid Priority)**:
```
Error: Invalid priority 'urgent'. Must be one of: high, medium, low
```

**Output Error (Invalid Date)**:
```
Error: Invalid date format. Use YYYY-MM-DD HH:MM
Example: 2025-12-30 14:00
```

**Output Error (Recurrence Without Due Date)**:
```
Error: Recurring tasks must have a due date
Use --due-date to specify when the task repeats
```

**Output Error (Too Many Tags)**:
```
Error: Maximum 10 tags allowed per task
You provided: work, project, urgent, meeting, team, q4, important, review, presentation, slides, deadline
```

**Validation Rules**:
- Title: 1-200 chars, not empty/whitespace-only
- Priority: Must be "high", "medium", or "low" (case-insensitive, converted to lowercase)
- Tags: Max 10, comma-separated, normalized to lowercase alphanumeric + hyphens
- Due date: ISO 8601 format YYYY-MM-DD HH:MM, must be parseable
- Recurrence: Must be "daily", "weekly", or "monthly"; requires --due-date

**Return Code**:
- 0: Success
- 1: Validation error or exception

---

### 2. `list` - Display Tasks (Extended)

**Purpose**: Display tasks with filtering, searching, and sorting capabilities.

**Signature**:
```bash
python main.py list [OPTIONS]
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| status | Option | No | -s, --status | None | Filter: pending, in_progress, completed |
| priority | Option | No | -p, --priority | None | Filter: high, medium, low |
| tags | Option | No | -t, --tags | None | Filter: comma-separated tags (AND logic) |
| keyword | Option | No | -k, --keyword | None | Search in title/description |
| from-date | Option | No | --from-date | None | Start of date range (YYYY-MM-DD) |
| to-date | Option | No | --to-date | None | End of date range (YYYY-MM-DD) |
| sort-by | Option | No | --sort-by | "created_at" | Sort by: priority, due_date, created_at, title |
| order | Option | No | --order | "asc" | Sort order: asc, desc |

**Examples**:
```bash
# All tasks (default: sorted by creation date ascending)
python main.py list

# High-priority pending tasks
python main.py list -s pending -p high

# Work tasks with "meeting" keyword
python main.py list -t work -k meeting

# Tasks created in December 2025, sorted by due date
python main.py list --from-date "2025-12-01" --to-date "2025-12-31" --sort-by due_date

# All tasks sorted by priority (high to low)
python main.py list --sort-by priority --order desc

# Complex filter: pending work tasks with urgent tag, sorted by due date
python main.py list -s pending -t "work,urgent" --sort-by due_date
```

**Output Success (Tasks Found)**:
```
Showing 3 tasks (filtered by: status=pending, priority=high, tags=[work])

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ ID ┃ Title                ┃ Priority ┃ Status   ┃ Due Date         ┃ Tags           ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 1  │ Quarterly report     │ [H] high │ pending  │ Dec 30, 2025 2PM │ #work #reports │
│ 3  │ Team standup         │ [H] high │ pending  │ Dec 27, 2025 9AM │ #work #meeting │
│ 5  │ Code review          │ [H] high │ pending  │ OVERDUE!         │ #work #urgent  │
└────┴──────────────────────┴──────────┴──────────┴──────────────────┴────────────────┘

Sorted by: due_date (asc)
```

**Output Success (No Tasks Found)**:
```
No tasks found matching criteria:
  - Status: pending
  - Priority: high
  - Tags: work, urgent
```

**Output Success (Empty List)**:
```
No todos found.
Add your first task with: python main.py add "Task title"
```

**Output Error (Invalid Sort Field)**:
```
Error: Invalid sort field 'priority_level'
Valid options: priority, due_date, created_at, title
```

**Output Error (Invalid Date Range)**:
```
Error: Invalid date format for --from-date. Use YYYY-MM-DD
Example: 2025-12-01
```

**Display Features**:
- **Priority Colors**:
  - High: Red bold
  - Medium: Yellow
  - Low: Green
- **Status Colors**:
  - Pending: White
  - In Progress: Yellow
  - Completed: Green
- **Overdue Indicator**: Red bold "OVERDUE!" for tasks past due date
- **Tag Display**: Space-separated with # prefix (e.g., "#work #urgent")
- **Due Date Format**: "MMM DD, YYYY H:MMAM/PM" or "No date"
- **Filter Summary**: Display active filters above table
- **Sort Indicator**: Display current sort field and order below table

**Validation Rules**:
- Status: Must be "pending", "in_progress", or "completed"
- Priority: Must be "high", "medium", or "low"
- Sort-by: Must be "priority", "due_date", "created_at", or "title"
- Order: Must be "asc" or "desc"
- Dates: Must be parseable in YYYY-MM-DD format

**Return Code**:
- 0: Success (tasks found or empty list)
- 1: Validation error

---

### 3. `search` - Find Tasks (New)

**Purpose**: Dedicated search command with combined filtering.

**Signature**:
```bash
python main.py search <keyword> [OPTIONS]
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| keyword | Argument | Yes | - | - | Search term (case-insensitive) |
| status | Option | No | -s, --status | None | Filter: pending, in_progress, completed |
| priority | Option | No | -p, --priority | None | Filter: high, medium, low |
| tags | Option | No | -t, --tags | None | Filter: comma-separated tags |

**Examples**:
```bash
# Search for "meeting" in all tasks
python main.py search "meeting"

# Search for "report" in pending tasks only
python main.py search "report" -s pending

# Search for "review" in high-priority work tasks
python main.py search "review" -p high -t work
```

**Output Success**:
```
Found 2 tasks matching "meeting":

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Title                ┃ Priority ┃ Status   ┃ Tags             ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 3  │ Team standup meeting │ [M] med  │ pending  │ #work #meetings  │
│ 7  │ Client meeting prep  │ [H] high │ pending  │ #work #client    │
└────┴──────────────────────┴──────────┴──────────┴──────────────────┘

Search: "meeting" (case-insensitive, title + description)
Filters: None
```

**Output Error (No Matches)**:
```
No tasks found matching "quarterly" with filters:
  - Status: completed
  - Priority: high
```

**Search Behavior**:
- Case-insensitive substring matching
- Searches in both title AND description fields
- Exact word matching not required (partial matches included)
- Results sorted by creation date (newest first)

**Return Code**:
- 0: Success (tasks found or no matches)
- 1: Validation error

---

### 4. `update` - Modify Task (Extended)

**Purpose**: Update task attributes including new fields (priority, tags, due date, recurrence).

**Signature**:
```bash
python main.py update <todo_id> [OPTIONS]
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| todo_id | Argument | Yes | - | - | Task ID to update |
| title | Option | No | -t, --title | None | New task title |
| description | Option | No | -d, --description | None | New task details |
| status | Option | No | -s, --status | None | New status: pending, in_progress, completed |
| priority | Option | No | -p, --priority | None | New priority: high, medium, low |
| tags | Option | No | --tags | None | New tags (replaces existing, comma-separated) |
| due-date | Option | No | --due-date | None | New due date (YYYY-MM-DD HH:MM) or "none" to clear |
| recurrence | Option | No | -r, --recurrence | None | New recurrence: daily, weekly, monthly, or "none" |

**Examples**:
```bash
# Change priority to high
python main.py update 1 -p high

# Update title and add tags
python main.py update 3 -t "Team standup (updated)" --tags "work,meetings,daily"

# Set due date and recurrence
python main.py update 5 --due-date "2025-12-27 09:00" -r weekly

# Clear due date (removes recurrence too)
python main.py update 7 --due-date none

# Complete a task
python main.py update 2 -s completed
```

**Output Success**:
```
[OK] Todo updated successfully!

  ID: 1
  Title: Quarterly report
  Priority: [H] high (changed)
  Tags: #work #reports
  Due Date: Dec 30, 2025 2:00 PM
  Status: pending
```

**Output Error (No Fields Provided)**:
```
Error: At least one field must be provided to update
Use --help to see available options
```

**Output Error (Task Not Found)**:
```
Error: Todo with ID 99 not found
```

**Output Error (Invalid Status)**:
```
Error: Invalid status 'done'. Must be one of: pending, in_progress, completed
```

**Output Error (Recurrence Without Due Date)**:
```
Error: Cannot set recurrence without a due date
Use --due-date to specify when the task repeats
```

**Special Behaviors**:
- `--tags` replaces all existing tags (not additive)
- `--due-date none` clears due date and removes recurrence
- `--recurrence none` removes recurrence but keeps due date
- `updated_at` timestamp auto-updated
- Validation runs on all modified fields

**Return Code**:
- 0: Success
- 1: Validation error or task not found

---

### 5. `complete` - Mark Task as Done (Unchanged)

**Purpose**: Set task status to "completed". For recurring tasks, auto-creates next instance.

**Signature**:
```bash
python main.py complete <todo_id>
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| todo_id | Argument | Yes | - | - | Task ID to complete |

**Examples**:
```bash
# Complete a one-time task
python main.py complete 1

# Complete a recurring task (auto-creates next instance)
python main.py complete 3
```

**Output Success (One-Time Task)**:
```
[OK] Todo marked as completed!

  ID: 1
  Title: Buy groceries
  Status: completed
```

**Output Success (Recurring Task)**:
```
[OK] Todo marked as completed!

  ID: 3
  Title: Team standup
  Status: completed

[AUTO-CREATE] Next instance created!

  ID: 8
  Title: Team standup
  Due Date: Jan 3, 2026 9:00 AM (next weekly)
  Status: pending
```

**Output Error (Task Not Found)**:
```
Error: Todo with ID 99 not found
```

**Special Behavior**:
- If task has `recurrence_pattern`, creates new instance with:
  - Next due date calculated from pattern (daily +1 day, weekly +7 days, monthly +1 month)
  - Status reset to "pending"
  - New ID, created_at, updated_at
  - All other fields inherited (title, description, priority, tags, recurrence_pattern)
  - `recurrence_parent_id` set to current task's ID

**Return Code**:
- 0: Success
- 1: Task not found

---

### 6. `delete` - Remove Task (Unchanged)

**Purpose**: Permanently delete a task.

**Signature**:
```bash
python main.py delete <todo_id>
```

**Parameters**:

| Name | Type | Required | Flag | Default | Description |
|------|------|----------|------|---------|-------------|
| todo_id | Argument | Yes | - | - | Task ID to delete |

**Examples**:
```bash
python main.py delete 1
```

**Output Success**:
```
[OK] Todo deleted successfully!
```

**Output Error (Task Not Found)**:
```
Error: Todo with ID 99 not found
```

**Special Behavior**:
- For recurring tasks, only deletes current instance (does not affect other instances in series)
- No confirmation prompt (immediate deletion)
- ID is not reused after deletion

**Return Code**:
- 0: Success
- 1: Task not found

---

## Global Options

**Available for all commands**:

| Flag | Description |
|------|-------------|
| --help | Show command help and exit |
| --version | Show application version and exit |

**Examples**:
```bash
python main.py --help          # Show all commands
python main.py add --help      # Show add command help
python main.py --version       # Show version
```

---

## Error Handling

### Common Error Patterns

| Error Type | Exit Code | Message Format |
|------------|-----------|----------------|
| Validation Error | 1 | `Error: {validation_message}` |
| Not Found | 1 | `Error: Todo with ID {id} not found` |
| Invalid Argument | 1 | `Error: Invalid {field} '{value}'. {hint}` |
| Missing Required | 1 | `Error: Missing required argument: {arg}` |
| General Exception | 1 | `Error: {exception_message}` |

### Error Color Scheme

- Errors: Red text (`[red]Error:[/red]`)
- Success: Green text (`[green][OK][/green]`)
- Warnings: Yellow text (`[yellow]Warning:[/yellow]`)
- Info: White text (default)

---

## Output Format Standards

### Table Columns (list/search commands)

| Column | Width | Alignment | Color Logic |
|--------|-------|-----------|-------------|
| ID | 6 | Left | Dim white |
| Title | Auto | Left | Cyan |
| Priority | 10 | Center | Red (high), Yellow (medium), Green (low) |
| Status | 10 | Center | Green (completed), Yellow (in_progress), White (pending) |
| Due Date | 18 | Left | Red bold (overdue), White (future), Dim (none) |
| Tags | Auto | Left | Cyan (#tag format) |
| Created | 16 | Left | Dim white (YYYY-MM-DD HH:MM) |

### Date/Time Formats

| Context | Format | Example |
|---------|--------|---------|
| Input (CLI) | YYYY-MM-DD HH:MM | 2025-12-30 14:00 |
| Input (Date Only) | YYYY-MM-DD | 2025-12-01 |
| Display (Table) | MMM DD, YYYY H:MMAM/PM | Dec 30, 2025 2:00PM |
| Display (Created) | YYYY-MM-DD HH:MM | 2025-12-25 10:30 |

---

## Performance Requirements

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Add task | <100ms | Command completion time |
| List 1000 tasks | <1s | Table rendering time (SC-002) |
| Search 1000 tasks | <1s | Results display time (SC-002) |
| Filter + Sort | <500ms | For 100+ tasks (SC-004) |
| Update task | <100ms | Command completion time |
| Complete (recurring) | <1s | Including next instance creation (SC-006) |

---

## Accessibility

### Terminal Compatibility

- **Minimum Width**: 80 columns
- **Color Support**: ANSI colors (Rich library)
- **No Unicode Required**: ASCII symbols fallback for priority ([H], [M], [L])
- **Screen Readers**: Plain text output mode (future consideration)

### Help Text Clarity

- Every command has `--help` flag
- Help text includes examples
- Error messages include hints for correction
- Consistent terminology across commands

---

## Examples: Complete Workflows

### Workflow 1: Create and Manage High-Priority Work Tasks

```bash
# Add high-priority task with due date
python main.py add "Prepare Q4 report" -p high -t "work,reports" --due-date "2025-12-30 14:00"
# Output: [OK] Todo added successfully! ID: 1

# View all high-priority tasks
python main.py list -p high
# Output: Table with 1 task

# Update to add more tags
python main.py update 1 --tags "work,reports,q4,presentation"
# Output: [OK] Todo updated successfully!

# Complete the task
python main.py complete 1
# Output: [OK] Todo marked as completed!
```

### Workflow 2: Set Up Recurring Weekly Meeting

```bash
# Create recurring weekly task
python main.py add "Team standup" -p medium -t "work,meetings" --due-date "2025-12-27 09:00" -r weekly
# Output: [OK] Todo added successfully! ID: 2

# Complete first instance (auto-creates next)
python main.py complete 2
# Output: [OK] Todo marked as completed!
#         [AUTO-CREATE] Next instance created! ID: 3, Due: Jan 3, 2026 9AM

# View all pending meetings
python main.py list -s pending -t meetings --sort-by due_date
# Output: Table showing ID 3 and other pending meetings
```

### Workflow 3: Search and Filter Complex Queries

```bash
# Add multiple tasks
python main.py add "Code review for PR #123" -p high -t "work,code-review"
python main.py add "Review meeting notes" -p medium -t "work,meetings"
python main.py add "Personal review of goals" -p low -t "personal,review"

# Search for "review" in work tasks only
python main.py search "review" -t work
# Output: Table showing first 2 tasks (work tagged)

# Filter pending work tasks sorted by priority
python main.py list -s pending -t work --sort-by priority --order desc
# Output: Table with high-priority first
```

---

## Contract Compliance Checklist

- [x] All commands have clear signatures
- [x] All parameters have type, required, flag, default, and description
- [x] Examples provided for each command
- [x] Success and error outputs documented
- [x] Validation rules specified
- [x] Return codes defined
- [x] Error handling patterns documented
- [x] Output format standards defined
- [x] Performance requirements specified
- [x] Complete workflows demonstrated

**Status**: Ready for implementation (`/sp.tasks`)
