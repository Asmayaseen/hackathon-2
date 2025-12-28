#!/usr/bin/env python3
"""
Demo: Fitness & Health Tracker
===============================
Track workouts, water intake, sleep, and health goals.
Features: Daily habits, workout schedules, health monitoring
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
        "[bold cyan]FITNESS & HEALTH TRACKER DEMO[/bold cyan]\n"
        "[dim]Workouts, Nutrition, Sleep & Wellness Goals[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    # Daily Health Habits
    console.print("[bold]1. Daily Health Habits...[/bold]\n")

    daily_habits = [
        ("Morning Walk - 30 mins", "Cardio exercise before breakfast", 6, 0, "medium"),
        ("8 Glasses of Water", "Track daily water intake goal", 8, 0, "high"),
        ("Healthy Breakfast", "Protein-rich meal with fruits", 8, 30, "high"),
        ("Lunch - Balanced Meal", "Include vegetables and protein", 13, 0, "medium"),
        ("Evening Workout", "Gym or home workout session", 18, 0, "high"),
        ("Sleep by 11 PM", "Get 7-8 hours of quality sleep", 23, 0, "high"),
    ]

    for title, desc, hour, minute, priority in daily_habits:
        due_time = base_date.replace(hour=hour, minute=minute)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["fitness", "daily", "health"],
            due_date=due_time,
            recurrence_pattern="daily"
        )
        console.print(f"[green][OK][/green] {title} - {due_time.strftime('%I:%M %p')}")

    console.print()

    # Weekly Workout Plan
    console.print("[bold]2. Weekly Workout Schedule...[/bold]\n")

    workouts = [
        ("Monday - Chest & Triceps", "Bench press, push-ups, dips", 1),
        ("Tuesday - Back & Biceps", "Pull-ups, rows, curls", 2),
        ("Wednesday - Legs & Core", "Squats, lunges, planks", 3),
        ("Thursday - Shoulders", "Military press, lateral raises", 4),
        ("Friday - Full Body HIIT", "High-intensity interval training", 5),
        ("Saturday - Yoga & Stretching", "Flexibility and recovery", 6),
    ]

    for title, desc, days_ahead in workouts:
        due_date = base_date + timedelta(days=days_ahead, hours=18, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority="high",
            tags=["fitness", "workout", title.split()[0].lower()],
            due_date=due_date,
            recurrence_pattern="weekly"
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Health Goals
    console.print("[bold]3. Monthly Health Goals...[/bold]\n")

    goals = [
        ("Weight Check - Monthly", "Track weight progress", 30, "medium"),
        ("Meal Prep Sunday", "Prepare healthy meals for the week", 7, "high"),
        ("Doctor Checkup", "Regular health screening", 30, "high"),
    ]

    for title, desc, days_ahead, priority in goals:
        due_date = base_date + timedelta(days=days_ahead, hours=10, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["fitness", "health", "monthly"],
            due_date=due_date,
            recurrence_pattern="monthly" if days_ahead == 30 else "weekly"
        )
        console.print(f"[green][OK][/green] {title}")

    console.print()

    # Display fitness table
    table = Table(title="Fitness & Health Schedule", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", width=12)
    table.add_column("Task", style="white", width=28)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Frequency", justify="center", width=10)

    all_tasks = manager.list_todos()
    for task in all_tasks:
        category = "Workout" if "workout" in task.tags else ("Habit" if "daily" in task.tags else "Goal")
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_display = f"[{priority_colors[task.priority]}]{task.priority.upper()}[/{priority_colors[task.priority]}]"
        frequency = task.recurrence_pattern.upper() if task.recurrence_pattern else "ONCE"

        table.add_row(
            category,
            task.title[:26] + "..." if len(task.title) > 26 else task.title,
            priority_display,
            f"[cyan]{frequency}[/cyan]"
        )

    console.print(table)
    console.print()

    # Statistics
    total = len(all_tasks)
    daily_count = len([t for t in all_tasks if t.recurrence_pattern == "daily"])
    workout_count = len([t for t in all_tasks if "workout" in task.tags])

    console.print(f"[bold cyan]Fitness Summary:[/bold cyan]")
    console.print(f"  Total Tasks: {total}")
    console.print(f"  Daily Habits: {daily_count}")
    console.print(f"  Weekly Workouts: {len(workouts)}")
    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Usage Commands:[/bold]\n\n"
        "View all fitness tasks:\n"
        "  [cyan]uv run python main.py list --tags fitness[/cyan]\n\n"
        "View daily habits only:\n"
        "  [cyan]uv run python main.py list --tags daily[/cyan]\n\n"
        "View workout schedule:\n"
        "  [cyan]uv run python main.py search \"workout\"[/cyan]\n\n"
        "Mark habit complete:\n"
        "  [cyan]uv run python main.py complete <id>[/cyan]",
        title="How to Use",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
