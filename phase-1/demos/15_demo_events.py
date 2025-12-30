#!/usr/bin/env python3
"""
Demo: Events & Special Occasions
=================================
Track birthdays, anniversaries, holidays, and important events.
Features: Event planning, gift shopping, celebrations, reminders
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
        "[bold cyan]EVENTS & OCCASIONS DEMO[/bold cyan]\n"
        "[dim]Birthdays, Anniversaries, Holidays & Celebrations[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    event_tasks = [
        ("Hackathon Phase I Submission", "Submit Phase I deliverables", 7, 23, 59, "high"),
        ("Sister's Birthday", "Plan and celebrate birthday", 10, 18, 0, "high"),
        ("Wedding Anniversary", "Plan special dinner celebration", 15, 19, 0, "high"),
        ("Eid Preparation", "Shopping, decorations, food planning", 20, 10, 0, "high"),
        ("New Year Planning", "Set goals and resolutions for new year", 30, 20, 0, "medium"),
        ("Buy Birthday Gift - Ahmed", "Shop for gift 3 days before birthday", 7, 14, 0, "medium"),
        ("Book Restaurant Reservation", "Reserve table for anniversary dinner", 13, 12, 0, "high"),
        ("Eid Card Shopping", "Buy greeting cards for relatives", 18, 16, 0, "medium"),
    ]

    console.print("[bold]Creating Event Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority in event_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["events", "celebration", "special"],
            due_date=due_date
        )
        console.print(f"[green][OK][/green] {title} - {due_date.strftime('%b %d')}")

    console.print(f"\n[bold cyan]Total Event Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags events[/cyan]\n"
        "  [cyan]uv run python main.py list --sort-by due_date[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
