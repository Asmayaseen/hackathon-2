# Quick Start: Advanced Todo Features

**Feature**: 001-advanced-todo-features
**Status**: Ready for Implementation
**Date**: 2025-12-25

## Overview

This guide demonstrates the advanced features added to the Phase I console todo application:

**Intermediate Features**:
- ✅ Priorities (high/medium/low) with color-coded display
- ✅ Tags (category labels, max 10 per task)
- ✅ Search (keyword matching in title/description)
- ✅ Filter (multi-criteria with AND logic)
- ✅ Sort (by priority/due date/created date/title)

**Advanced Features**:
- ✅ Due Dates (ISO 8601 format with timezone)
- ✅ Time Reminders (console notifications for upcoming tasks)
- ✅ Recurring Tasks (auto-generate daily/weekly/monthly)

## Installation

```bash
cd hackathon-2
uv sync
```

## Basic Usage

### Create Tasks with Priorities

```bash
# High-priority work task
uv run python main.py add "Quarterly report" -p high -t "work,reports"

# Medium-priority personal task with due date
uv run python main.py add "Dentist appointment" -p medium -t "health,personal" --due-date "2025-12-30 14:00"

# Low-priority task
uv run python main.py add "Read book" -p low -t "personal,leisure"
```

**Expected Output**:
```
[OK] Todo added successfully!

  ID: 1
  Title: Quarterly report
  Priority: [H] high
  Tags: #work #reports
  Due Date: No date
  Status: pending
  Recurrence: None
```

### List and Filter Tasks

```bash
# List all tasks (default: sorted by creation date)
uv run python main.py list

# List high-priority tasks only
uv run python main.py list -p high

# List all work tasks
uv run python main.py list -t work

# List pending work tasks (multiple filters)
uv run python main.py list -s pending -t work

# List high-priority pending work tasks (complex filter)
uv run python main.py list -p high -s pending -t work
```

**Expected Output** (list -p high):
```
Showing 2 tasks (filtered by: priority=high)

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID ┃ Title               ┃ Priority ┃ Status   ┃ Tags         ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 1  │ Quarterly report    │ [H] high │ pending  │ #work #reports│
│ 3  │ Team standup        │ [H] high │ pending  │ #work #meeting│
└────┴─────────────────────┴──────────┴──────────┴──────────────┘

Sorted by: created_at (asc)
```

### Search Tasks

```bash
# Search for "meeting" in all tasks
uv run python main.py search "meeting"

# Search for "report" in pending tasks only
uv run python main.py search "report" -s pending

# Search for "review" in high-priority work tasks
uv run python main.py search "review" -p high -t work
```

**Expected Output** (search "meeting"):
```
Found 2 tasks matching "meeting":

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID ┃ Title               ┃ Priority ┃ Status   ┃ Tags         ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 3  │ Team standup meeting│ [M] med  │ pending  │ #work #meetings│
│ 7  │ Client meeting prep │ [H] high │ pending  │ #work #client │
└────┴─────────────────────┴──────────┴──────────┴──────────────┘

Search: "meeting" (case-insensitive, title + description)
Filters: None
```

### Sort Tasks

```bash
# Sort by priority (high to low)
uv run python main.py list --sort-by priority --order desc

# Sort by due date (earliest first)
uv run python main.py list --sort-by due_date

# Sort by creation date (newest first)
uv run python main.py list --sort-by created_at --order desc

# Sort alphabetically by title
uv run python main.py list --sort-by title
```

### Work with Due Dates

```bash
# Add task with due date and time
uv run python main.py add "Submit proposal" -p high -t "work" --due-date "2025-12-31 17:00"

# List tasks created in December 2025
uv run python main.py list --from-date "2025-12-01" --to-date "2025-12-31"

# List tasks sorted by due date
uv run python main.py list --sort-by due_date

# Update task to add due date
uv run python main.py update 1 --due-date "2025-12-28 14:00"

# Clear due date
uv run python main.py update 1 --due-date none
```

### Create Recurring Tasks

```bash
# Daily recurring task
uv run python main.py add "Morning standup" -p medium -t "work,meetings" --due-date "2025-12-27 09:00" -r daily

# Weekly recurring task
uv run python main.py add "Team retrospective" -p medium -t "work,meetings" --due-date "2025-12-27 15:00" -r weekly

# Monthly recurring task
uv run python main.py add "Monthly report" -p high -t "work,reports" --due-date "2025-12-30 17:00" -r monthly

# Complete recurring task (auto-creates next instance)
uv run python main.py complete 1
```

**Expected Output** (complete recurring task):
```
[OK] Todo marked as completed!

  ID: 1
  Title: Morning standup
  Status: completed

[AUTO-CREATE] Next instance created!

  ID: 8
  Title: Morning standup
  Due Date: Dec 28, 2025 9:00 AM (next daily)
  Status: pending
```

### Update Tasks

```bash
# Change priority
uv run python main.py update 1 -p high

# Update title and add tags
uv run python main.py update 3 -t "Team standup (updated)" --tags "work,meetings,daily"

# Update multiple fields
uv run python main.py update 5 -p high --tags "urgent,work" --due-date "2025-12-27 10:00"

# Remove recurrence (keeps due date)
uv run python main.py update 7 -r none
```

## Feature Guide

### Priority Levels

**Three Levels**:
- **high**: Red bold display, urgent tasks requiring immediate attention
- **medium**: Yellow display, normal priority (default for new tasks)
- **low**: Green display, when-possible tasks

**Display**:
- CLI shows `[H]`, `[M]`, `[L]` symbols with color coding
- Color codes: high=red, medium=yellow, low=green

**Sorting**:
```bash
# High-priority tasks first
uv run python main.py list --sort-by priority --order desc
```

### Tags

**Format**:
- Comma-separated: `-t "work,urgent,q4"`
- Maximum 10 tags per task
- Auto-normalized to lowercase alphanumeric + hyphens
- Spaces and special characters replaced with hyphens

**Examples**:
```bash
# Valid tags
-t "work,urgent,q4-review"

# Normalized from "Work, Urgent!, Q4 Review"
# Becomes: ["work", "urgent", "q4-review"]

# Too many tags (error)
-t "1,2,3,4,5,6,7,8,9,10,11"  # Max 10 allowed
```

**Display**:
- Tags shown with # prefix: `#work #urgent #q4`
- Space-separated in table columns

**Filtering**:
```bash
# Single tag
uv run python main.py list -t work

# Multiple tags (AND logic - task must have ALL tags)
uv run python main.py list -t "work,urgent"
```

### Due Dates

**Format**:
- Input: ISO 8601 `YYYY-MM-DD HH:MM`
- Example: `--due-date "2025-12-30 14:00"`
- Timezone: System local timezone (no multi-timezone support)

**Display**:
- Human-readable: "Dec 30, 2025 2:00PM"
- Overdue tasks: Red bold "OVERDUE!" indicator

**Examples**:
```bash
# Add task with due date
uv run python main.py add "Deadline task" --due-date "2025-12-31 23:59"

# Filter by date range (created date)
uv run python main.py list --from-date "2025-12-20" --to-date "2025-12-31"

# Sort by due date (earliest first, null dates last)
uv run python main.py list --sort-by due_date
```

**Overdue Check**:
- Tasks past due date shown in red bold
- Checked on startup and during list operations

### Recurrence Patterns

**Three Patterns**:
- **daily**: Creates next instance tomorrow (due_date + 1 day)
- **weekly**: Creates next instance next week (due_date + 7 days)
- **monthly**: Creates next instance same day next month (due_date + 1 month)

**Requirements**:
- Recurrence REQUIRES due date (validation error if missing)
- Must specify both `--due-date` and `--recurrence/-r`

**Auto-Creation Behavior**:
- Triggered by `complete` command
- New instance inherits: title, description, priority, tags, recurrence_pattern
- New instance resets: status="pending", new ID, new created_at/updated_at
- New instance links: recurrence_parent_id set to completed task's ID

**Examples**:
```bash
# Create weekly recurring task
uv run python main.py add "Weekly sync" -p medium -t "work" --due-date "2025-12-27 10:00" -r weekly

# Complete (auto-creates next instance for 2026-01-03 10:00 AM)
uv run python main.py complete 1

# View next instance
uv run python main.py list
# Shows ID 2 with due date 2026-01-03 10:00 AM

# Remove recurrence from task
uv run python main.py update 1 -r none  # Keeps due date, removes recurrence
```

### Reminders (Console-Based)

**Timing**:
- Checks for tasks due within next 30 minutes
- Triggered on: app startup, list command, add command with due_date

**Display**:
```
[REMINDER] 2 tasks due soon:
  - ID 3: Team standup (due in 15 minutes)
  - ID 7: Client call (due in 28 minutes)
```

**Limitations**:
- Only works while app is running (console app limitation)
- Missed reminders shown on next app startup
- No background daemon (Phase I in-memory only)

**Example**:
```bash
# Add task due in 20 minutes
uv run python main.py add "Quick call" --due-date "$(date -d '+20 minutes' +'%Y-%m-%d %H:%M')"

# List tasks (reminder notification appears)
uv run python main.py list
# Output includes: [REMINDER] 1 task due soon: ...
```

### Filtering (Multi-Criteria)

**Filter Options**:
- `--status/-s`: pending, in_progress, completed
- `--priority/-p`: high, medium, low
- `--tags/-t`: Comma-separated tags (AND logic)
- `--keyword/-k`: Search in title and description
- `--from-date`: Start of date range (YYYY-MM-DD)
- `--to-date`: End of date range (YYYY-MM-DD)

**Logic**:
- AND: Task must match ALL specified criteria
- Example: `-s pending -p high -t work` → pending AND high AND work

**Examples**:
```bash
# Single filter
uv run python main.py list -s pending

# Multiple filters
uv run python main.py list -s pending -p high

# Complex filter
uv run python main.py list -s pending -p high -t "work,urgent" --keyword "report"

# Date range
uv run python main.py list --from-date "2025-12-01" --to-date "2025-12-31"
```

### Sorting

**Sort Fields**:
- `priority`: high → medium → low (or reverse)
- `due_date`: earliest → latest (null dates always last)
- `created_at`: oldest → newest (or reverse)
- `title`: alphabetical A-Z (or reverse)

**Sort Order**:
- `asc`: Ascending (default)
- `desc`: Descending

**Examples**:
```bash
# Sort by priority (high first)
uv run python main.py list --sort-by priority --order desc

# Sort by due date (earliest first, nulls last)
uv run python main.py list --sort-by due_date

# Sort by creation date (newest first)
uv run python main.py list --sort-by created_at --order desc

# Sort alphabetically
uv run python main.py list --sort-by title

# Combine filter and sort
uv run python main.py list -s pending --sort-by priority --order desc
```

## Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage report
uv run pytest --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_todo_item.py

# Specific test class
uv run pytest tests/test_todo_item.py::TestTodoItemPriority

# Verbose output
uv run pytest -v
```

### Type Checking

```bash
# Run mypy strict type checking
uv run mypy src/ --strict

# Check specific file
uv run mypy src/core/todo_item.py --strict
```

### Demo Workflow

```bash
# Run demo script (showcases all features)
uv run python test_cli_workflow_advanced.py
```

## Troubleshooting

### "Invalid date format" error

**Problem**: Due date not in ISO 8601 format

**Solution**: Use `YYYY-MM-DD HH:MM` format
```bash
# Wrong:
--due-date "tomorrow"
--due-date "12/30/2025"

# Correct:
--due-date "2025-12-30 14:00"
```

### "Maximum 10 tags allowed" error

**Problem**: Too many tags specified

**Solution**: Reduce tag count or split into multiple tasks
```bash
# Wrong (11 tags):
-t "work,project,urgent,meeting,team,q4,important,review,presentation,slides,deadline"

# Correct (10 tags max):
-t "work,project,urgent,meeting,team,q4,important,review,presentation,slides"
```

### "Recurring tasks must have a due date" error

**Problem**: Trying to create recurring task without due date

**Solution**: Add `--due-date` when using `--recurrence`
```bash
# Wrong:
uv run python main.py add "Task" -r weekly

# Correct:
uv run python main.py add "Task" --due-date "2025-12-27 09:00" -r weekly
```

### "Invalid priority" error

**Problem**: Priority value not in allowed list

**Solution**: Use only high, medium, or low (case-insensitive)
```bash
# Wrong:
-p urgent
-p critical

# Correct:
-p high
-p medium
-p low
```

### Reminders not showing

**Problem**: App closed when reminder time passed

**Solution**: Reminders only work while app is running
- Check for missed reminders on next app startup
- Run `list` command periodically to see upcoming reminders
- Phase II will add persistent reminder system

### Tags not filtering correctly

**Problem**: Multiple tags use AND logic, not OR

**Understanding**: `-t "work,urgent"` shows ONLY tasks with BOTH tags

**Solution**:
```bash
# To find tasks with "work" OR "urgent", run two commands:
uv run python main.py list -t work
uv run python main.py list -t urgent

# To find tasks with BOTH "work" AND "urgent":
uv run python main.py list -t "work,urgent"
```

## Complete Workflow Examples

### Example 1: Manage High-Priority Work Tasks

```bash
# 1. Add high-priority tasks with due dates
uv run python main.py add "Prepare Q4 report" -p high -t "work,reports" --due-date "2025-12-30 14:00"
uv run python main.py add "Review team proposals" -p high -t "work,review" --due-date "2025-12-27 10:00"
uv run python main.py add "Client presentation" -p high -t "work,client" --due-date "2025-12-28 15:00"

# 2. View all high-priority tasks
uv run python main.py list -p high
# Output: 3 tasks displayed

# 3. Sort by due date to prioritize
uv run python main.py list -p high --sort-by due_date
# Output: Review (Dec 27), Presentation (Dec 28), Report (Dec 30)

# 4. Update tags for better organization
uv run python main.py update 1 --tags "work,reports,q4,presentation"

# 5. Complete tasks as finished
uv run python main.py complete 2
uv run python main.py complete 3
uv run python main.py complete 1
```

### Example 2: Set Up Recurring Weekly Meetings

```bash
# 1. Create recurring weekly tasks
uv run python main.py add "Team standup" -p medium -t "work,meetings" --due-date "2025-12-27 09:00" -r weekly
uv run python main.py add "1-on-1 with manager" -p medium -t "work,meetings" --due-date "2025-12-27 14:00" -r weekly
uv run python main.py add "Department sync" -p low -t "work,meetings" --due-date "2025-12-27 16:00" -r weekly

# 2. View all pending meetings
uv run python main.py list -s pending -t meetings --sort-by due_date
# Output: 3 meetings for Dec 27

# 3. Complete first meeting (auto-creates next instance)
uv run python main.py complete 1
# Output: [OK] Completed + [AUTO-CREATE] Next instance for Jan 3, 2026

# 4. View updated list (shows next instance)
uv run python main.py list -s pending -t meetings --sort-by due_date
# Output: 2 meetings for Dec 27, 1 meeting for Jan 3
```

### Example 3: Search and Filter for Project Review

```bash
# 1. Add multiple project-related tasks
uv run python main.py add "Code review for PR #123" -p high -t "work,code-review"
uv run python main.py add "Review meeting notes" -p medium -t "work,meetings"
uv run python main.py add "Personal review of goals" -p low -t "personal,review"
uv run python main.py add "Quarterly performance review" -p high -t "work,review" --due-date "2025-12-31 10:00"

# 2. Search for all "review" tasks
uv run python main.py search "review"
# Output: 4 tasks containing "review"

# 3. Narrow to work-related reviews only
uv run python main.py search "review" -t work
# Output: 3 work tasks

# 4. Filter pending work reviews sorted by priority
uv run python main.py list -s pending -t work,review --sort-by priority --order desc
# Output: High-priority reviews first

# 5. View reviews due in December 2025
uv run python main.py list -t review --from-date "2025-12-01" --to-date "2025-12-31" --sort-by due_date
# Output: Quarterly review (Dec 31)
```

## Next Steps

After getting familiar with basic usage:

1. **Extend with More Features** - Run `/sp.tasks` to see implementation tasks
2. **Contribute Tests** - Add test coverage for new features
3. **Migrate to Phase II** - Move to full-stack web application with database
4. **Explore AI Features** - Phase III adds OpenAI Agents SDK integration

## Resources

- **Specification**: `specs/001-advanced-todo-features/spec.md`
- **Implementation Plan**: `specs/001-advanced-todo-features/plan.md`
- **Data Model**: `specs/001-advanced-todo-features/data-model.md`
- **CLI Contracts**: `specs/001-advanced-todo-features/contracts/cli-commands.md`
- **Project README**: `README.md`

## Support

For issues or questions:
- Check specification for requirements details
- Review implementation plan for architecture decisions
- Run tests to verify behavior: `uv run pytest -v`
- Check type hints: `uv run mypy src/ --strict`

---

**Status**: Ready for Implementation | **Next**: Run `/sp.tasks` to generate task breakdown
