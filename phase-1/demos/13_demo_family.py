#!/usr/bin/env python3
"""
Demo: Family & Relationship Management
=======================================
Track family time, kids' activities, important dates, and bonding.
Features: Quality time, events, celebrations, responsibilities
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
        "[bold cyan]FAMILY & RELATIONSHIPS DEMO[/bold cyan]\n"
        "[dim]Quality Time, Events & Family Responsibilities[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    family_tasks = [
        ("Family Dinner Together", "Quality time with all members", 0, 19, 0, "high", "daily"),
        ("Kids Homework Help", "Help children with school assignments", 0, 17, 0, "medium", "daily"),
        ("Bedtime Story for Kids", "Read story before sleep", 0, 21, 0, "medium", "daily"),
        ("Weekly Family Game Night", "Board games or video games together", 7, 20, 0, "high", "weekly"),
        ("Call Parents", "Check in with parents/in-laws", 3, 18, 0, "high", None),
        ("Date Night Planning", "Plan romantic evening with spouse", 7, 19, 0, "medium", "weekly"),
        ("Kids Sports Practice", "Take kids to football/cricket practice", 3, 16, 0, "medium", "weekly"),
        ("Family Outing - Park Visit", "Weekend outdoor activity", 7, 10, 0, "medium", "weekly"),
    ]

    console.print("[bold]Creating Family Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority, recurrence in family_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["family", "relationships", "kids"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Family Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags family[/cyan]\n"
        "  [cyan]uv run python main.py list --tags kids[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
