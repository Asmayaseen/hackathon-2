#!/usr/bin/env python3
"""
Demo: Learning & Skill Development
===================================
Track coding practice, online courses, certifications, and study goals.
Features: Daily practice, course deadlines, skill tracking
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
        "[bold cyan]LEARNING & SKILL DEVELOPMENT DEMO[/bold cyan]\n"
        "[dim]Coding, Courses, Certifications & Practice[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    learning_tasks = [
        ("LeetCode Daily Challenge", "Solve 1 coding problem daily", 0, 20, 0, "high", "daily"),
        ("Python DSA Practice", "Data structures and algorithms", 0, 21, 0, "high", "daily"),
        ("Udemy Course - Module 3", "Complete FastAPI tutorial module", 2, 19, 0, "medium", None),
        ("Read Tech Article", "Read one technical blog post", 0, 22, 0, "medium", "daily"),
        ("AWS Certification Study", "Study for Solutions Architect exam", 0, 18, 0, "high", "daily"),
        ("System Design Practice", "Design scalable systems", 1, 20, 0, "high", "weekly"),
        ("GitHub Contributions", "Contribute to open source", 0, 19, 0, "medium", "daily"),
    ]

    console.print("[bold]Creating Learning Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority, recurrence in learning_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["learning", "coding", "education"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Learning Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags learning[/cyan]\n"
        "  [cyan]uv run python main.py search \"coding\"[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
