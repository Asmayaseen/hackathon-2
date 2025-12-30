#!/usr/bin/env python3
"""
Demo: Self-Care & Mental Wellness
==================================
Track meditation, journaling, hobbies, and personal development.
Features: Mindfulness, relaxation, creative activities, me-time
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.core.todo_manager import TodoManager
from rich.console import Console
from rich.panel import Panel

console = Console()
manager = TodoManager()

def main():
    console.print(Panel.fit(
        "[bold cyan]SELF-CARE & WELLNESS DEMO[/bold cyan]\n"
        "[dim]Meditation, Journaling, Hobbies & Me-Time[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    selfcare_tasks = [
        ("Morning Meditation - 10 mins", "Mindfulness and breathing exercises", 0, 6, 30, "high", "daily"),
        ("Gratitude Journaling", "Write 3 things you're grateful for", 0, 22, 0, "medium", "daily"),
        ("Evening Relaxation - 15 mins", "Wind down before sleep", 0, 22, 30, "medium", "daily"),
        ("Read Book for Pleasure", "Read 30 minutes for enjoyment", 0, 21, 0, "medium", "daily"),
        ("Hobby Time - Guitar Practice", "Practice instrument for 20 mins", 0, 19, 0, "low", "daily"),
        ("Digital Detox - 1 Hour", "No phone/laptop for one hour", 0, 20, 0, "medium", "daily"),
        ("Sunday Self-Care Routine", "Face mask, long bath, relaxation", 7, 15, 0, "high", "weekly"),
        ("Weekly Reflection", "Review week and plan improvements", 7, 18, 0, "medium", "weekly"),
    ]

    console.print("[bold]Creating Self-Care Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority, recurrence in selfcare_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["selfcare", "wellness", "mental-health"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Self-Care Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags selfcare[/cyan]\n"
        "  [cyan]uv run python main.py list --tags wellness[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
