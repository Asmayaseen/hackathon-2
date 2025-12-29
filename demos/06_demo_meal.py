#!/usr/bin/env python3
"""
Demo: Meal Planning & Nutrition
================================
Plan meals, track cooking, and manage grocery shopping.
Features: Daily meals, meal prep, nutrition goals
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
        "[bold cyan]MEAL PLANNING DEMO[/bold cyan]\n"
        "[dim]Daily Meals, Cooking & Nutrition Tracking[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    meals = [
        ("Breakfast Preparation", "Healthy breakfast - eggs, toast, fruit", 7, 30, "high", "daily"),
        ("Pack Lunch", "Prepare lunch box for work/school", 8, 0, "medium", "daily"),
        ("Dinner Cooking", "Evening meal preparation", 17, 0, "high", "daily"),
        ("Meal Prep Sunday", "Prep meals for entire week", 7, 10, 0, "high", "weekly"),
        ("Grocery Shopping", "Buy fresh ingredients", 7, 9, 0, "high", "weekly"),
    ]

    console.print("[bold]Creating Meal Schedule...[/bold]\n")
    for title, desc, *time_parts, priority, recurrence in meals:
        if len(time_parts) == 2:
            hour, minute = time_parts
            due_time = base_date.replace(hour=hour, minute=minute)
        else:
            days_ahead, hour, minute = time_parts
            due_time = base_date + timedelta(days=days_ahead, hours=hour, minutes=minute)

        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["meal", "cooking", "nutrition"],
            due_date=due_time, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Meal Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags meal[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
