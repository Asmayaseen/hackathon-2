#!/usr/bin/env python3
"""
Demo: Ramzan 30-Day Tracker
============================
Track Sehri, Iftar, Taraweeh, Quran reading for the holy month.
Features: Daily recurring tasks, specific timings, spiritual goals
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.core.todo_manager import TodoManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
manager = TodoManager()

def main():
    console.print(Panel.fit(
        "[bold cyan]RAMZAN 30-DAY TRACKER DEMO[/bold cyan]\n"
        "[dim]Sehri, Iftar, Taraweeh & Spiritual Goals[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    # Daily Ramzan Routine
    console.print("[bold]Creating Ramzan Daily Routine...[/bold]\n")

    ramzan_tasks = [
        ("Sehri Time", "Pre-dawn meal before fasting", base_date.replace(hour=4, minute=30), "high", "daily"),
        ("Fajr Prayer", "Morning prayer", base_date.replace(hour=5, minute=0), "high", "daily"),
        ("Quran Reading - 1 Juz", "Read one Juz (para) daily", base_date.replace(hour=10, minute=0), "high", "daily"),
        ("Dhuhr Prayer", "Afternoon prayer", base_date.replace(hour=13, minute=0), "high", "daily"),
        ("Asr Prayer", "Late afternoon prayer", base_date.replace(hour=16, minute=30), "high", "daily"),
        ("Iftar Preparation", "Prepare breaking fast meal", base_date.replace(hour=17, minute=30), "medium", "daily"),
        ("Iftar Time", "Break fast at sunset", base_date.replace(hour=18, minute=0), "high", "daily"),
        ("Maghrib Prayer", "Evening prayer after Iftar", base_date.replace(hour=18, minute=10), "high", "daily"),
        ("Isha Prayer", "Night prayer", base_date.replace(hour=19, minute=30), "high", "daily"),
        ("Taraweeh Prayer", "Special Ramzan night prayer", base_date.replace(hour=20, minute=0), "high", "daily"),
    ]

    for title, desc, due_time, priority, recurrence in ramzan_tasks:
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["ramzan", title.split()[0].lower(), "spiritual"],
            due_date=due_time,
            recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title} - {due_time.strftime('%I:%M %p')}")

    console.print()

    # Weekly Ramzan Goals
    console.print("[bold]Adding Weekly Spiritual Goals...[/bold]\n")

    weekly_goals = [
        ("Charity/Sadaqah Distribution", "Give charity to the needy", "medium"),
        ("Visit Relatives", "Strengthen family bonds", "medium"),
        ("Zakat Calculation", "Calculate and distribute Zakat", "high"),
    ]

    for title, desc, priority in weekly_goals:
        due_date = base_date + timedelta(days=7, hours=20, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["ramzan", "spiritual", "weekly"],
            due_date=due_date,
            recurrence_pattern="weekly"
        )
        console.print(f"[green][OK][/green] {title} - Weekly Goal")

    console.print()

    # Special Last 10 Days
    console.print("[bold]Special: Last 10 Days of Ramzan...[/bold]\n")

    last_10_days = [
        ("Laylatul Qadr Search", "Seek the Night of Power", base_date + timedelta(days=20, hours=21, minutes=0), "high"),
        ("Itikaf Preparation", "Prepare for mosque retreat", base_date + timedelta(days=20, hours=10, minutes=0), "medium"),
        ("Eid Shopping", "Buy Eid gifts and clothes", base_date + timedelta(days=25, hours=14, minutes=0), "medium"),
    ]

    for title, desc, due_time, priority in last_10_days:
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["ramzan", "special", "last-10-days"],
            due_date=due_time
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Display Ramzan schedule table
    table = Table(title="Ramzan Daily Schedule", show_header=True, header_style="bold magenta")
    table.add_column("Time", style="yellow", width=10)
    table.add_column("Activity", style="cyan", width=25)
    table.add_column("Type", justify="center", width=12)
    table.add_column("Recurrence", justify="center", width=10)

    all_tasks = manager.list_todos(tags=["ramzan"])
    sorted_tasks = sorted(all_tasks, key=lambda x: x.due_date if x.due_date else datetime.max)

    for task in sorted_tasks:
        time_str = task.due_date.strftime("%I:%M %p") if task.due_date else "-"
        task_type = "Prayer" if "prayer" in task.title.lower() else ("Meal" if any(x in task.title.lower() for x in ["sehri", "iftar"]) else "Goal")
        recurrence = f"[cyan]{task.recurrence_pattern}[/cyan]" if task.recurrence_pattern else "-"

        table.add_row(
            time_str,
            task.title[:23] + "..." if len(task.title) > 23 else task.title,
            task_type,
            recurrence
        )

    console.print(table)
    console.print()

    # Statistics
    total = len(all_tasks)
    daily_count = len([t for t in all_tasks if t.recurrence_pattern == "daily"])
    prayer_count = len([t for t in all_tasks if "prayer" in t.title.lower()])

    console.print(f"[bold cyan]Ramzan Tasks Summary:[/bold cyan]")
    console.print(f"  Total Tasks: {total}")
    console.print(f"  Daily Recurring: {daily_count}")
    console.print(f"  Prayers: {prayer_count}")
    console.print(f"  Special Goals: {total - daily_count}")
    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Usage Commands:[/bold]\n\n"
        "View all Ramzan tasks:\n"
        "  [cyan]uv run python main.py list --tags ramzan[/cyan]\n\n"
        "View daily routine only:\n"
        "  [cyan]uv run python main.py list --tags ramzan,daily[/cyan]\n\n"
        "Check what's coming up:\n"
        "  [cyan]uv run python main.py list --sort-by due_date[/cyan]\n\n"
        "Mark task complete (auto-creates tomorrow's):\n"
        "  [cyan]uv run python main.py complete <id>[/cyan]",
        title="How to Use",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
