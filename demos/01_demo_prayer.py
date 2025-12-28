#!/usr/bin/env python3
"""
Demo: Prayer Schedule Management
================================
Shows how to manage daily prayer times with automatic recurring reminders.
Features: 5 daily prayers, auto-scheduling, priority alerts
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
        "[bold cyan]PRAYER SCHEDULE DEMO[/bold cyan]\n"
        "[dim]Managing 5 Daily Prayers with Auto-Reminders[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Define prayer times for today
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    prayers = [
        ("Fajr Prayer", "Morning prayer before sunrise", base_date.replace(hour=5, minute=30)),
        ("Dhuhr Prayer", "Afternoon prayer at noon", base_date.replace(hour=12, minute=30)),
        ("Asr Prayer", "Late afternoon prayer", base_date.replace(hour=15, minute=45)),
        ("Maghrib Prayer", "Evening prayer at sunset", base_date.replace(hour=17, minute=15)),
        ("Isha Prayer", "Night prayer", base_date.replace(hour=19, minute=0)),
    ]

    console.print("[bold]Creating Daily Prayer Schedule...[/bold]\n")

    for title, desc, due_time in prayers:
        task = manager.add_todo(
            title=title,
            description=desc,
            priority="high",
            tags=["prayer", title.split()[0].lower(), "daily"],
            due_date=due_time,
            recurrence_pattern="daily"
        )
        console.print(f"[green][OK][/green] {title} - {due_time.strftime('%I:%M %p')}")

    console.print(f"\n[bold cyan]Total Prayers Scheduled: {len(prayers)}[/bold cyan]\n")

    # Display prayer table
    table = Table(title="Today's Prayer Schedule", show_header=True, header_style="bold magenta")
    table.add_column("Prayer", style="cyan", width=15)
    table.add_column("Time", style="yellow", width=10)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Recurrence", justify="center", width=10)

    all_tasks = manager.list_todos()
    for task in all_tasks:
        if task.due_date:
            time_str = task.due_date.strftime("%I:%M %p")
            status_color = "green" if task.status == "completed" else "white"
            table.add_row(
                task.title,
                time_str,
                f"[{status_color}]{task.status}[/{status_color}]",
                f"[cyan]{task.recurrence_pattern}[/cyan]" if task.recurrence_pattern else "-"
            )

    console.print(table)
    console.print()

    # Check upcoming reminders
    console.print("[bold yellow]Checking Upcoming Reminders (30-min window)...[/bold yellow]")
    reminders = manager.check_reminders()

    if reminders:
        console.print(f"[bold red]WARNING: {len(reminders)} prayer(s) due soon![/bold red]\n")
        for reminder in reminders:
            console.print(f"  • [bold]{reminder.title}[/bold] at {reminder.due_date.strftime('%I:%M %p')}")
    else:
        console.print("[green][OK] No prayers due in the next 30 minutes[/green]")

    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Usage Commands:[/bold]\n\n"
        "View all prayers:\n"
        "  [cyan]uv run python main.py list --tags prayer[/cyan]\n\n"
        "View specific prayer:\n"
        "  [cyan]uv run python main.py search \"fajr\"[/cyan]\n\n"
        "Complete a prayer (auto-creates tomorrow's):\n"
        "  [cyan]uv run python main.py complete <id>[/cyan]\n\n"
        "Check reminders:\n"
        "  [cyan]uv run python main.py list --sort-by due_date[/cyan]",
        title="How to Use",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
