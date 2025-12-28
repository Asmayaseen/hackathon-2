#!/usr/bin/env python3
"""
Demo: Language Learning Tracker
================================
Track daily practice, vocabulary, speaking, and fluency goals.
Features: Daily lessons, practice sessions, immersion activities
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
        "[bold cyan]LANGUAGE LEARNING DEMO[/bold cyan]\n"
        "[dim]Duolingo, Vocabulary, Speaking & Immersion[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    language_tasks = [
        ("Duolingo Urdu Lesson", "Complete daily lesson streak", 0, 19, 0, "high", "daily"),
        ("Vocabulary Practice - 10 Words", "Learn and memorize new words", 0, 20, 0, "medium", "daily"),
        ("Watch Urdu News - 15 mins", "Listening comprehension practice", 0, 21, 0, "medium", "daily"),
        ("Speaking Practice - 10 mins", "Record voice practicing phrases", 0, 19, 30, "high", "daily"),
        ("Read Urdu Article", "Read one article for reading practice", 0, 20, 30, "medium", "daily"),
        ("Language Exchange Call", "Practice with native speaker", 7, 18, 0, "high", "weekly"),
        ("Grammar Exercise", "Complete one grammar lesson", 0, 21, 0, "medium", "daily"),
    ]

    console.print("[bold]Creating Language Learning Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority, recurrence in language_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["language", "urdu", "learning"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Language Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags language[/cyan]\n"
        "  [cyan]uv run python main.py list --tags urdu[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
