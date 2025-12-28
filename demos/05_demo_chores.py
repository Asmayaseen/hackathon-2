#!/usr/bin/env python3
"""
Demo: Home Chores & Household Management
=========================================
Track cleaning, laundry, groceries, and home maintenance tasks.
Features: Recurring chores, shopping lists, home organization
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
        "[bold cyan]HOME CHORES TRACKER DEMO[/bold cyan]\n"
        "[dim]Cleaning, Laundry, Shopping & Maintenance[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    # Daily Chores
    console.print("[bold]1. Daily Household Chores...[/bold]\n")

    daily_chores = [
        ("Make Bed", "Organize bedroom after waking up", 7, 0, "low"),
        ("Kitchen Cleaning", "Wash dishes and clean counters", 9, 0, "medium"),
        ("Take Out Trash", "Empty all trash bins", 20, 0, "medium"),
        ("Wipe Dining Table", "Clean after meals", 21, 0, "low"),
    ]

    for title, desc, hour, minute, priority in daily_chores:
        due_time = base_date.replace(hour=hour, minute=minute)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["chores", "daily", "cleaning"],
            due_date=due_time,
            recurrence_pattern="daily"
        )
        console.print(f"[green][OK][/green] {title} - {due_time.strftime('%I:%M %p')}")

    console.print()

    # Weekly Chores
    console.print("[bold]2. Weekly Cleaning Schedule...[/bold]\n")

    weekly_chores = [
        ("Laundry Day", "Wash, dry, and fold clothes", 1, "high"),
        ("Vacuum Living Room", "Deep clean carpets and floors", 2, "medium"),
        ("Bathroom Deep Clean", "Scrub toilet, shower, sink", 3, "high"),
        ("Change Bed Sheets", "Replace with fresh linens", 1, "medium"),
        ("Dust Furniture", "Wipe all surfaces and shelves", 4, "low"),
        ("Mop Kitchen Floor", "Clean and sanitize floor", 5, "medium"),
    ]

    for title, desc, days_ahead, priority in weekly_chores:
        due_date = base_date + timedelta(days=days_ahead, hours=10, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["chores", "weekly", "cleaning"],
            due_date=due_date,
            recurrence_pattern="weekly"
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Shopping & Groceries
    console.print("[bold]3. Shopping & Grocery Lists...[/bold]\n")

    shopping = [
        ("Grocery Shopping", "Weekly grocery run - fruits, vegetables, essentials", 7, "high"),
        ("Buy Cleaning Supplies", "Detergent, soap, disinfectant", 14, "medium"),
        ("Pharmacy Run", "Pick up medications and vitamins", 7, "high"),
    ]

    for title, desc, days_ahead, priority in shopping:
        due_date = base_date + timedelta(days=days_ahead, hours=11, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["chores", "shopping", "errands"],
            due_date=due_date,
            recurrence_pattern="weekly"
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Monthly Maintenance
    console.print("[bold]4. Monthly Home Maintenance...[/bold]\n")

    maintenance = [
        ("Pay Electricity Bill", "Monthly utility payment", 30, "high"),
        ("Pay Internet Bill", "Broadband service payment", 30, "high"),
        ("AC Filter Cleaning", "Clean or replace AC filters", 30, "medium"),
        ("Check Smoke Detectors", "Test batteries and functionality", 30, "low"),
    ]

    for title, desc, days_ahead, priority in maintenance:
        due_date = base_date + timedelta(days=days_ahead, hours=16, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["chores", "maintenance", "monthly"],
            due_date=due_date,
            recurrence_pattern="monthly"
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Display chores table
    table = Table(title="Household Chores Schedule", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Chore", style="white", width=28)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Frequency", justify="center", width=10)

    all_tasks = manager.list_todos()
    for task in all_tasks:
        task_type = "Daily" if task.recurrence_pattern == "daily" else ("Weekly" if task.recurrence_pattern == "weekly" else "Monthly")
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_display = f"[{priority_colors[task.priority]}]{task.priority.upper()}[/{priority_colors[task.priority]}]"

        table.add_row(
            task_type,
            task.title[:26] + "..." if len(task.title) > 26 else task.title,
            priority_display,
            f"[cyan]{task.recurrence_pattern.upper() if task.recurrence_pattern else 'ONCE'}[/cyan]"
        )

    console.print(table)
    console.print()

    # Statistics
    total = len(all_tasks)
    daily_count = len([t for t in all_tasks if t.recurrence_pattern == "daily"])
    weekly_count = len([t for t in all_tasks if t.recurrence_pattern == "weekly"])
    monthly_count = len([t for t in all_tasks if t.recurrence_pattern == "monthly"])

    console.print(f"[bold cyan]Chores Summary:[/bold cyan]")
    console.print(f"  Total Tasks: {total}")
    console.print(f"  Daily Chores: {daily_count}")
    console.print(f"  Weekly Chores: {weekly_count}")
    console.print(f"  Monthly Maintenance: {monthly_count}")
    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Usage Commands:[/bold]\n\n"
        "View all chores:\n"
        "  [cyan]uv run python main.py list --tags chores[/cyan]\n\n"
        "View cleaning tasks only:\n"
        "  [cyan]uv run python main.py list --tags cleaning[/cyan]\n\n"
        "View shopping list:\n"
        "  [cyan]uv run python main.py search \"shopping\"[/cyan]\n\n"
        "Mark chore complete:\n"
        "  [cyan]uv run python main.py complete <id>[/cyan]",
        title="How to Use",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
