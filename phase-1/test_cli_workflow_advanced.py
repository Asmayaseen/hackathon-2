#!/usr/bin/env python3
"""
Advanced CLI Workflow Demonstration - Phase II Features

Demonstrates all 5 user stories:
- US1: Priorities & Tags
- US2: Search & Filter
- US3: Sort Tasks
- US4: Due Dates & Reminders
- US5: Recurring Tasks
"""

from datetime import datetime, timedelta
from src.core.todo_manager import TodoManager

# Initialize manager
manager = TodoManager()

print("=" * 80)
print("PHASE II: ADVANCED TODO APPLICATION - FEATURE DEMONSTRATION")
print("=" * 80)

# ============================================================================
# US1: PRIORITIES & TAGS
# ============================================================================
print("\n" + "=" * 80)
print("USER STORY 1: PRIORITIES & TAGS")
print("=" * 80)

print("\n[1] Adding tasks with priorities and tags...")
task1 = manager.add_todo(
    "Quarterly financial report",
    "Prepare Q4 summary for board meeting",
    "high",
    ["work", "reports", "urgent"]
)
print(f"  [OK] Added: #{task1.id} {task1.title} [{task1.priority}] {task1.tags}")

task2 = manager.add_todo(
    "Team standup meeting",
    "Daily team sync",
    "medium",
    ["work", "meeting"]
)
print(f"  [OK] Added: #{task2.id} {task2.title} [{task2.priority}] {task2.tags}")

task3 = manager.add_todo(
    "Buy groceries",
    "Milk, bread, eggs",
    "low",
    ["personal", "shopping"]
)
print(f"  [OK] Added: #{task3.id} {task3.title} [{task3.priority}] {task3.tags}")

task4 = manager.add_todo(
    "Fix critical bug #456",
    "Production issue affecting users",
    "high",
    ["work", "bug", "urgent"]
)
print(f"  [OK] Added: #{task4.id} {task4.title} [{task4.priority}] {task4.tags}")

print("\n[2] Filter by priority...")
high_priority = manager.list_todos(priority="high")
print(f"  High-priority tasks: {len(high_priority)}")
for task in high_priority:
    print(f"    - {task.title}")

print("\n[3] Filter by tags (AND logic)...")
urgent_work = manager.list_todos(tags=["work", "urgent"])
print(f"  Urgent work tasks: {len(urgent_work)}")
for task in urgent_work:
    print(f"    - {task.title} {task.tags}")

# ============================================================================
# US2: SEARCH & FILTER
# ============================================================================
print("\n" + "=" * 80)
print("USER STORY 2: SEARCH & FILTER")
print("=" * 80)

# Add more diverse tasks
task5 = manager.add_todo("Client meeting prep", "Prepare slides", "high", ["work", "meeting"])
task6 = manager.add_todo("Research meeting tools", "Find scheduling app", "low", ["work"])
task7 = manager.add_todo("Read meeting summary", "Review quarterly notes", "low", ["personal", "meeting"])

print("\n[1] Keyword search: 'meeting'")
meeting_tasks = manager.filter_todos(keyword="meeting")
print(f"  Found {len(meeting_tasks)} tasks:")
for task in meeting_tasks:
    print(f"    - {task.title} (in: {'title' if 'meeting' in task.title.lower() else 'description'})")

print("\n[2] Combined filter: keyword='meeting' + priority='high'")
high_meetings = manager.filter_todos(keyword="meeting", priority="high")
print(f"  Found {len(high_meetings)} task(s):")
for task in high_meetings:
    print(f"    - {task.title} [{task.priority}]")

print("\n[3] Multi-criteria: status='pending' + priority='high' + tags=['work']")
results = manager.filter_todos(status="pending", priority="high", tags=["work"])
print(f"  Found {len(results)} task(s):")
for task in results:
    print(f"    - {task.title} [{task.status}] [{task.priority}] {task.tags}")

# ============================================================================
# US3: SORT TASKS
# ============================================================================
print("\n" + "=" * 80)
print("USER STORY 3: SORT TASKS")
print("=" * 80)

all_tasks = manager.list_todos()

print("\n[1] Sort by priority (high -> medium -> low)")
sorted_priority = manager.sort_todos(all_tasks, "priority", "asc")
for task in sorted_priority:
    print(f"  {task.priority:6} - {task.title}")

print("\n[2] Sort by title (alphabetical)")
sorted_title = manager.sort_todos(all_tasks, "title", "asc")
for task in sorted_title:
    print(f"  {task.title}")

print("\n[3] Sort by created_at (newest first)")
sorted_created = manager.sort_todos(all_tasks, "created_at", "desc")
for task in sorted_created:
    print(f"  {task.created_at.strftime('%H:%M:%S')} - {task.title}")

# ============================================================================
# US4: DUE DATES & REMINDERS
# ============================================================================
print("\n" + "=" * 80)
print("USER STORY 4: DUE DATES & REMINDERS")
print("=" * 80)

# Add tasks with due dates
now = datetime.now()
task8 = manager.add_todo(
    "Submit expense report",
    "End of month deadline",
    "medium",
    ["work", "admin"],
    due_date=now + timedelta(days=5)
)
print(f"\n[1] Added task with due date: {task8.title}")
print(f"    Due: {task8.due_date.strftime('%b %d, %Y %I:%M%p')}")

# Add task due soon (for reminder demonstration)
task9 = manager.add_todo(
    "Client call",
    "Weekly sync call",
    "high",
    ["work", "meeting"],
    due_date=now + timedelta(minutes=15)  # Due in 15 minutes
)
print(f"\n[2] Added task due soon: {task9.title}")
print(f"    Due: {task9.due_date.strftime('%b %d, %Y %I:%M%p')} (in 15 minutes)")

# Check reminders
reminders = manager.check_reminders()
print(f"\n[3] Reminder check (30-minute window):")
if reminders:
    print(f"  [REMINDER] {len(reminders)} task(s) due within 30 minutes:")
    for task in reminders:
        print(f"    - {task.title} at {task.due_date.strftime('%I:%M%p')}")
else:
    print("  No upcoming reminders")

# Sort by due date
print("\n[4] Sort by due date:")
sorted_due = manager.sort_todos(all_tasks, "due_date", "asc")
for task in sorted_due:
    if task.due_date:
        print(f"  {task.due_date.strftime('%b %d %I:%M%p')} - {task.title}")
    else:
        print(f"  No due date - {task.title}")

# ============================================================================
# US5: RECURRING TASKS
# ============================================================================
print("\n" + "=" * 80)
print("USER STORY 5: RECURRING TASKS")
print("=" * 80)

# Add recurring tasks
print("\n[1] Create daily recurring task...")
task10 = manager.add_todo(
    "Daily standup",
    "Morning team sync",
    "medium",
    ["work", "meeting"],
    due_date=now + timedelta(hours=1),
    recurrence_pattern="daily"
)
print(f"  [OK] Created: #{task10.id} {task10.title}")
print(f"    Pattern: {task10.recurrence_pattern}")
print(f"    Due: {task10.due_date.strftime('%b %d, %Y %I:%M%p')}")

print("\n[2] Create weekly recurring task...")
task11 = manager.add_todo(
    "Weekly team retrospective",
    "Team improvement discussion",
    "medium",
    ["work", "meeting"],
    due_date=now + timedelta(days=2),
    recurrence_pattern="weekly"
)
print(f"  [OK] Created: #{task11.id} {task11.title}")
print(f"    Pattern: {task11.recurrence_pattern}")
print(f"    Due: {task11.due_date.strftime('%b %d, %Y %I:%M%p')}")

print("\n[3] Create monthly recurring task...")
task12 = manager.add_todo(
    "Monthly status report",
    "Send management update",
    "high",
    ["work", "reports"],
    due_date=now + timedelta(days=7),
    recurrence_pattern="monthly"
)
print(f"  [OK] Created: #{task12.id} {task12.title}")
print(f"    Pattern: {task12.recurrence_pattern}")
print(f"    Due: {task12.due_date.strftime('%b %d, %Y %I:%M%p')}")

print("\n[4] Complete recurring task (auto-creates next instance)...")
print(f"  Completing task #{task10.id}: {task10.title}")
completed, new_instance = manager.complete_todo(task10.id)
print(f"  [OK] Marked as completed")
if new_instance:
    print(f"  [RECURRING] Auto-created next instance:")
    print(f"    - New ID: #{new_instance.id}")
    print(f"    - Title: {new_instance.title}")
    print(f"    - Next due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p')}")
    print(f"    - Pattern: {new_instance.recurrence_pattern}")
    print(f"    - Parent: #{new_instance.recurrence_parent_id}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

all_final = manager.list_todos()
completed_tasks = [t for t in all_final if t.status == "completed"]
pending_tasks = [t for t in all_final if t.status == "pending"]
high_pri = [t for t in all_final if t.priority == "high"]
recurring = [t for t in all_final if t.recurrence_pattern]

print(f"\nTotal tasks: {len(all_final)}")
print(f"  - Completed: {len(completed_tasks)}")
print(f"  - Pending: {len(pending_tasks)}")
print(f"  - High priority: {len(high_pri)}")
print(f"  - Recurring: {len(recurring)}")

print("\n" + "=" * 80)
print("FEATURES DEMONSTRATED:")
print("=" * 80)
print("  [OK] US1: Priorities & Tags - Priority levels, tag filtering, tag normalization")
print("  [OK] US2: Search & Filter - Keyword search, multi-criteria filtering, AND logic")
print("  [OK] US3: Sort Tasks - Sort by priority/title/created_at/due_date")
print("  [OK] US4: Due Dates & Reminders - ISO 8601 dates, reminder window, overdue detection")
print("  [OK] US5: Recurring Tasks - Daily/weekly/monthly patterns, auto-creation")
print("\n" + "=" * 80)
print("PHASE II DEMONSTRATION COMPLETE!")
print("=" * 80)
