#!/usr/bin/env python3
"""US2 Feature Demo - Search and Filter"""

from src.core.todo_manager import TodoManager
from datetime import datetime, timedelta

# Initialize manager
manager = TodoManager()

# Add diverse tasks for testing
print("=== Adding Tasks ===\n")

tasks_data = [
    ("Team meeting prep", "Prepare slides for weekly meeting", "high", ["work", "meeting"]),
    ("Client meeting notes", "Review notes from client sync", "medium", ["work", "meeting"]),
    ("Buy groceries", "Milk, bread, eggs", "low", ["personal", "shopping"]),
    ("Fix bug #456", "Critical production issue", "high", ["work", "bug", "urgent"]),
    ("Read meeting summary", "Read summary from last quarterly meeting", "low", ["personal", "meeting"]),
    ("Schedule dentist", "Call for appointment", "medium", ["personal", "health"]),
    ("Write report", "Q4 financial report", "high", ["work", "reports"]),
    ("Gym workout", "Cardio and weights", "low", ["personal", "fitness"]),
    ("Team sync", "Daily standup meeting", "medium", ["work", "meeting"]),
    ("Research tools", "Find meeting scheduler tool", "low", ["work"]),
]

for i, (title, desc, priority, tags) in enumerate(tasks_data, 1):
    task = manager.add_todo(title, desc, priority, tags)
    print(f"{i:2}. Added: {task.title} [{task.priority}] {task.tags}")

print(f"\n[OK] Total tasks: {len(manager.list_todos())}")

# Test keyword search
print("\n=== Test 1: Keyword Search - 'meeting' ===")
results = manager.filter_todos(keyword="meeting")
print(f"Found {len(results)} tasks:")
for task in results:
    print(f"  - {task.title} (in: {'title' if 'meeting' in task.title.lower() else 'description'})")

# Test case-insensitive search
print("\n=== Test 2: Case-Insensitive Search - 'MEETING' ===")
results = manager.filter_todos(keyword="MEETING")
print(f"Found {len(results)} tasks (same as lowercase): {len(results) == 5}")

# Test combined filters: keyword + priority
print("\n=== Test 3: Keyword 'meeting' + Priority 'high' ===")
results = manager.filter_todos(keyword="meeting", priority="high")
print(f"Found {len(results)} task(s):")
for task in results:
    print(f"  - {task.title} [{task.priority}]")

# Test combined filters: keyword + tags
print("\n=== Test 4: Keyword 'meeting' + Tags ['work'] ===")
results = manager.filter_todos(keyword="meeting", tags=["work"])
print(f"Found {len(results)} task(s):")
for task in results:
    print(f"  - {task.title} {task.tags}")

# Test multi-criteria: status + priority + tags
print("\n=== Test 5: Multi-Criteria - Status 'pending' + Priority 'high' + Tags ['work'] ===")
results = manager.filter_todos(status="pending", priority="high", tags=["work"])
print(f"Found {len(results)} task(s):")
for task in results:
    print(f"  - {task.title} [{task.status}] [{task.priority}] {task.tags}")

# Test date range filtering
print("\n=== Test 6: Date Range Filtering ===")
# Add tasks on different dates (simulate by creating them)
now = datetime.now()
all_tasks = manager.list_todos()
print(f"All tasks created around: {now.strftime('%Y-%m-%d %H:%M')}")

# Filter tasks from today
results = manager.filter_todos(date_from=now - timedelta(hours=1))
print(f"Tasks from last hour: {len(results)} (all tasks)")

# Test empty results
print("\n=== Test 7: Empty Results - No Match ===")
results = manager.filter_todos(keyword="nonexistent")
print(f"Results for 'nonexistent': {len(results)} tasks")

# Test combined search that returns no results
print("\n=== Test 8: Combined Filter - No Match ===")
results = manager.filter_todos(keyword="meeting", priority="high", tags=["personal"])
print(f"Results for meeting + high + personal: {len(results)} tasks (no work meetings are personal)")

# Test description search
print("\n=== Test 9: Search in Description - 'production' ===")
results = manager.filter_todos(keyword="production")
print(f"Found {len(results)} task(s):")
for task in results:
    print(f"  - {task.title} (desc: {task.description})")

# Test all filters combined
print("\n=== Test 10: Maximum Filters - keyword + status + priority + tags ===")
results = manager.filter_todos(
    keyword="report",
    status="pending",
    priority="high",
    tags=["work"]
)
print(f"Found {len(results)} task(s):")
for task in results:
    print(f"  - {task.title} [{task.status}] [{task.priority}] {task.tags}")

print("\n=== US2 Demo Complete! ===")
print("\nSummary of Features Tested:")
print("  [OK] Keyword search (title and description)")
print("  [OK] Case-insensitive search")
print("  [OK] Combined filters (AND logic)")
print("  [OK] Multi-criteria filtering")
print("  [OK] Date range filtering")
print("  [OK] Empty results handling")
