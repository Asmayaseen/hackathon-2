#!/usr/bin/env python3
"""Live CLI Demonstration - Shows all commands in action"""

from datetime import datetime, timedelta
from src.core.todo_manager import TodoManager
from src.ui.cli import console
from rich.table import Table

# Initialize manager (this simulates persistent state)
manager = TodoManager()

print("\n" + "=" * 80)
print("LIVE CLI DEMONSTRATION - Phase II Features")
print("=" * 80)

# ============================================================================
# 1. ADD COMMANDS
# ============================================================================
print("\n[1] ADD: Creating tasks with various options...\n")

print("$ python main.py add 'Quarterly Report' --priority high --tags work,reports,urgent --due-date '2025-01-15 17:00'")
task1 = manager.add_todo(
    "Quarterly Report",
    "Prepare Q4 financial summary",
    "high",
    ["work", "reports", "urgent"],
    datetime(2025, 1, 15, 17, 0)
)
console.print(f"[green][OK][/green] Todo #{task1.id} added: {task1.title} [Priority: {task1.priority}] [Due: Jan 15, 2025 05:00PM]")

print("\n$ python main.py add 'Team standup' --priority medium --tags work,meeting --due-date '2025-12-27 10:00' --recurrence daily")
task2 = manager.add_todo(
    "Team standup",
    "Daily team sync meeting",
    "medium",
    ["work", "meeting"],
    datetime(2025, 12, 27, 10, 0),
    "daily"
)
console.print(f"[green][OK][/green] Todo #{task2.id} added: {task2.title} [Recurrence: daily]")

print("\n$ python main.py add 'Buy groceries' --priority low --tags personal,shopping")
task3 = manager.add_todo("Buy groceries", "", "low", ["personal", "shopping"])
console.print(f"[green][OK][/green] Todo #{task3.id} added: {task3.title}")

print("\n$ python main.py add 'Fix bug #456' --priority high --tags work,bug,urgent")
task4 = manager.add_todo("Fix bug #456", "Critical production issue", "high", ["work", "bug", "urgent"])
console.print(f"[green][OK][/green] Todo #{task4.id} added: {task4.title}")

# ============================================================================
# 2. LIST COMMAND
# ============================================================================
print("\n" + "=" * 80)
print("[2] LIST: Show all tasks in table format")
print("=" * 80)
print("\n$ python main.py list\n")

all_tasks = manager.list_todos()
table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID", style="dim", width=6)
table.add_column("Title", style="cyan", no_wrap=False)
table.add_column("Priority", justify="center", width=8)
table.add_column("Tags", style="dim", no_wrap=False)
table.add_column("Status", justify="center")

for todo in all_tasks:
    priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
    priority_color = priority_colors[todo.priority]
    priority_display = f"[{priority_color}]{todo.priority[0].upper()}[/{priority_color}]"

    tags_display = " ".join([f"#{tag}" for tag in todo.tags]) if todo.tags else ""

    status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
    status_color = status_colors[todo.status]

    table.add_row(
        str(todo.id),
        todo.title,
        priority_display,
        tags_display,
        f"[{status_color}]{todo.status}[/{status_color}]"
    )

console.print(table)
console.print(f"\n[dim]Total: {len(all_tasks)} tasks[/dim]")

# ============================================================================
# 3. FILTER BY PRIORITY
# ============================================================================
print("\n" + "=" * 80)
print("[3] FILTER: Show only high-priority tasks")
print("=" * 80)
print("\n$ python main.py list --priority high\n")

high_tasks = manager.list_todos(priority="high")
for task in high_tasks:
    console.print(f"  #{task.id}: {task.title} [{task.priority}] {task.tags}")

# ============================================================================
# 4. FILTER BY TAGS
# ============================================================================
print("\n" + "=" * 80)
print("[4] FILTER: Show work tasks (AND logic)")
print("=" * 80)
print("\n$ python main.py list --tags work,urgent\n")

work_tasks = manager.list_todos(tags=["work", "urgent"])
for task in work_tasks:
    console.print(f"  #{task.id}: {task.title} {task.tags}")

# ============================================================================
# 5. SEARCH COMMAND
# ============================================================================
print("\n" + "=" * 80)
print("[5] SEARCH: Find tasks with keyword 'bug'")
print("=" * 80)
print("\n$ python main.py search 'bug'\n")

bug_tasks = manager.filter_todos(keyword="bug")
for task in bug_tasks:
    console.print(f"  #{task.id}: {task.title} - {task.description}")

# ============================================================================
# 6. SORT BY PRIORITY
# ============================================================================
print("\n" + "=" * 80)
print("[6] SORT: Sort by priority (high to low)")
print("=" * 80)
print("\n$ python main.py list --sort-by priority --order desc\n")

sorted_tasks = manager.sort_todos(all_tasks, "priority", "asc")
for task in sorted_tasks:
    console.print(f"  [{task.priority}] {task.title}")

# ============================================================================
# 7. UPDATE COMMAND
# ============================================================================
print("\n" + "=" * 80)
print("[7] UPDATE: Change task status to in_progress")
print("=" * 80)
print("\n$ python main.py update 1 --status in_progress\n")

updated = manager.update_todo(1, status="in_progress")
if updated:
    console.print(f"[green][OK][/green] Todo #{updated.id} updated: {updated.title} [Status: {updated.status}]")

# ============================================================================
# 8. COMPLETE COMMAND (with recurring task)
# ============================================================================
print("\n" + "=" * 80)
print("[8] COMPLETE: Complete recurring task (auto-creates next instance)")
print("=" * 80)
print("\n$ python main.py complete 2\n")

completed, new_instance = manager.complete_todo(2)
if completed:
    console.print(f"[green][OK][/green] Todo #{completed.id} marked as completed: '{completed.title}'")
    if new_instance:
        console.print(f"\n[bold cyan]RECURRING TASK:[/bold cyan]")
        console.print(f"  Created next instance #{new_instance.id}")
        console.print(f"  Title: {new_instance.title}")
        console.print(f"  Next due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p') if new_instance.due_date else 'N/A'}")
        console.print(f"  Pattern: {new_instance.recurrence_pattern}")

# ============================================================================
# 9. FINAL LIST
# ============================================================================
print("\n" + "=" * 80)
print("[9] FINAL LIST: Show all tasks after updates")
print("=" * 80)
print("\n$ python main.py list\n")

final_tasks = manager.list_todos()
table2 = Table(show_header=True, header_style="bold magenta")
table2.add_column("ID", style="dim", width=6)
table2.add_column("Title", style="cyan", no_wrap=False)
table2.add_column("Priority", justify="center", width=8)
table2.add_column("Status", justify="center")
table2.add_column("Recurrence", style="dim", justify="center")

for todo in final_tasks:
    priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
    priority_color = priority_colors[todo.priority]
    priority_display = f"[{priority_color}]{todo.priority[0].upper()}[/{priority_color}]"

    status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
    status_color = status_colors[todo.status]

    recurrence_display = ""
    if todo.recurrence_pattern:
        pattern_abbrev = {"daily": "D", "weekly": "W", "monthly": "M"}
        recurrence_display = pattern_abbrev.get(todo.recurrence_pattern, "")

    table2.add_row(
        str(todo.id),
        todo.title,
        priority_display,
        f"[{status_color}]{todo.status}[/{status_color}]",
        recurrence_display
    )

console.print(table2)

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
completed_count = len([t for t in final_tasks if t.status == "completed"])
pending_count = len([t for t in final_tasks if t.status == "pending"])
in_progress_count = len([t for t in final_tasks if t.status == "in_progress"])
recurring_count = len([t for t in final_tasks if t.recurrence_pattern])

console.print(f"\nTotal tasks: {len(final_tasks)}")
console.print(f"  - Completed: {completed_count}")
console.print(f"  - In Progress: {in_progress_count}")
console.print(f"  - Pending: {pending_count}")
console.print(f"  - Recurring: {recurring_count}")

print("\n" + "=" * 80)
print("CLI DEMONSTRATION COMPLETE!")
print("=" * 80 + "\n")
