#!/usr/bin/env python3
"""US1 Feature Demo - Priorities & Tags"""

from src.core.todo_manager import TodoManager
from src.core.todo_item import TodoItem

# Initialize manager
manager = TodoManager()

# Add tasks with different priorities and tags
print("=== Adding Tasks ===\n")

task1 = manager.add_todo("Quarterly report", "Write Q4 report", "high", ["work", "urgent"])
print(f"[OK] Added: {task1.title} | Priority: {task1.priority} | Tags: {task1.tags}")

task2 = manager.add_todo("Buy groceries", "", "low", ["personal", "shopping"])
print(f"[OK] Added: {task2.title} | Priority: {task2.priority} | Tags: {task2.tags}")

task3 = manager.add_todo("Team meeting", "Weekly sync", "medium", ["work"])
print(f"[OK] Added: {task3.title} | Priority: {task3.priority} | Tags: {task3.tags}")

task4 = manager.add_todo("Fix bug #123", "Critical production bug", "high", ["work", "urgent", "bug"])
print(f"[OK] Added: {task4.title} | Priority: {task4.priority} | Tags: {task4.tags}")

task5 = manager.add_todo("Read book", "", "low", ["personal"])
print(f"[OK] Added: {task5.title} | Priority: {task5.priority} | Tags: {task5.tags}")

# Test filtering
print("\n=== Filter by Priority: high ===")
high_priority = manager.list_todos(priority="high")
for task in high_priority:
    print(f"  #{task.id}: {task.title} [{task.priority}] {task.tags}")

print("\n=== Filter by Tags: work ===")
work_tasks = manager.list_todos(tags=["work"])
for task in work_tasks:
    print(f"  #{task.id}: {task.title} [{task.priority}] {task.tags}")

print("\n=== Filter by Tags: work AND urgent (AND logic) ===")
urgent_work = manager.list_todos(tags=["work", "urgent"])
for task in urgent_work:
    print(f"  #{task.id}: {task.title} [{task.priority}] {task.tags}")

print("\n=== Filter by Priority: medium AND Tags: work ===")
medium_work = manager.list_todos(priority="medium", tags=["work"])
for task in medium_work:
    print(f"  #{task.id}: {task.title} [{task.priority}] {task.tags}")

print("\n=== All Tasks ===")
all_tasks = manager.list_todos()
for task in all_tasks:
    print(f"  #{task.id}: {task.title} | Priority: {task.priority} | Tags: {task.tags}")

# Test update
print("\n=== Update Task #2 Priority ===")
updated = manager.update_todo(2, priority="high")
if updated:
    print(f"[OK] Updated: {updated.title} | Priority: {updated.priority}")

# Test tag normalization
print("\n=== Tag Normalization Test ===")
task6 = manager.add_todo("Test task", "", "medium", ["Work!", "URGENT", "test-tag", "CamelCase"])
print(f"[OK] Input tags: ['Work!', 'URGENT', 'test-tag', 'CamelCase']")
print(f"[OK] Normalized tags: {task6.tags}")

print("\n=== US1 Demo Complete! ===")
