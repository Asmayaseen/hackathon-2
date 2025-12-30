#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify yearly recurrence works correctly.
"""

import sys
import io
# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime
from src.core.todo_manager import TodoManager

def test_yearly_recurrence():
    """Test that yearly recurrence creates next year's instance correctly."""
    tm = TodoManager()

    # Test 1: Regular date (Dec 29, 2025 -> Dec 29, 2026)
    print("Test 1: Regular yearly recurrence (Dec 29, 2025)")
    task1 = tm.add_todo(
        title="Anniversary",
        description="Wedding anniversary celebration",
        priority="high",
        tags=["event", "anniversary"],
        due_date=datetime(2025, 12, 29, 12, 0),
        recurrence_pattern="yearly"
    )
    print(f"  Created task #{task1.id}: {task1.title}")
    print(f"  Due date: {task1.due_date}")
    print(f"  Recurrence: {task1.recurrence_pattern}")

    # Complete the task - should create next year's instance
    completed, next_instance = tm.complete_todo(task1.id)
    print(f"\n  Completed task #{completed.id}")
    if next_instance:
        print(f"  ✓ Next instance created: #{next_instance.id}")
        print(f"  ✓ Next due date: {next_instance.due_date} (should be 2026-12-29 12:00:00)")
        assert next_instance.due_date == datetime(2026, 12, 29, 12, 0), "Next due date should be one year later"
        assert next_instance.recurrence_pattern == "yearly", "Recurrence pattern should be preserved"
        print("  ✓ PASS: Regular yearly recurrence works!")
    else:
        print("  ✗ FAIL: Next instance not created")
        return False

    # Test 2: Leap year edge case (Feb 29, 2024 -> Feb 28, 2025)
    print("\n\nTest 2: Leap year edge case (Feb 29, 2024 -> Feb 28, 2025)")
    task2 = tm.add_todo(
        title="Leap Year Birthday",
        description="Born on Feb 29",
        priority="high",
        tags=["event", "birthday"],
        due_date=datetime(2024, 2, 29, 10, 0),  # Leap year
        recurrence_pattern="yearly"
    )
    print(f"  Created task #{task2.id}: {task2.title}")
    print(f"  Due date: {task2.due_date}")

    completed2, next_instance2 = tm.complete_todo(task2.id)
    print(f"\n  Completed task #{completed2.id}")
    if next_instance2:
        print(f"  ✓ Next instance created: #{next_instance2.id}")
        print(f"  ✓ Next due date: {next_instance2.due_date} (should be 2025-02-28 10:00:00)")
        assert next_instance2.due_date == datetime(2025, 2, 28, 10, 0), "Feb 29 should become Feb 28 in non-leap year"
        print("  ✓ PASS: Leap year edge case handled correctly!")
    else:
        print("  ✗ FAIL: Next instance not created")
        return False

    # Test 3: Feb 28, 2025 -> Feb 28, 2026
    print("\n\nTest 3: Non-leap year Feb 28 (2025 -> 2026)")
    task3 = tm.add_todo(
        title="February Event",
        description="Feb 28 event",
        priority="medium",
        tags=["event"],
        due_date=datetime(2025, 2, 28, 15, 0),
        recurrence_pattern="yearly"
    )
    print(f"  Created task #{task3.id}: {task3.title}")
    print(f"  Due date: {task3.due_date}")

    completed3, next_instance3 = tm.complete_todo(task3.id)
    print(f"\n  Completed task #{completed3.id}")
    if next_instance3:
        print(f"  ✓ Next instance created: #{next_instance3.id}")
        print(f"  ✓ Next due date: {next_instance3.due_date} (should be 2026-02-28 15:00:00)")
        assert next_instance3.due_date == datetime(2026, 2, 28, 15, 0), "Feb 28 should stay Feb 28"
        print("  ✓ PASS: Feb 28 stays Feb 28!")
    else:
        print("  ✗ FAIL: Next instance not created")
        return False

    print("\n\n" + "="*60)
    print("✓ ALL TESTS PASSED! Yearly recurrence works correctly.")
    print("="*60)
    return True

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    try:
        success = test_yearly_recurrence()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
