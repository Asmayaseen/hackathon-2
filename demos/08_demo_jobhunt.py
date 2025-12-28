#!/usr/bin/env python3
"""
Demo: Job Hunting Tracker
==========================
Track applications, interviews, follow-ups, and resume updates.
Features: Application deadlines, interview prep, networking
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
        "[bold cyan]JOB HUNTING TRACKER DEMO[/bold cyan]\n"
        "[dim]Applications, Interviews & Career Development[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    job_tasks = [
        ("Update Resume", "Add recent projects and skills", 1, 16, 0, "high"),
        ("Apply to Google - SWE Role", "Submit application via LinkedIn", 2, 23, 59, "high"),
        ("Apply to Microsoft - Cloud Engineer", "Complete online application form", 2, 23, 59, "high"),
        ("Prepare for Interview - Amazon", "Study system design and algorithms", 3, 18, 0, "high"),
        ("Interview - Meta (Round 1)", "Technical coding interview", 5, 10, 0, "high"),
        ("Follow-up Email - ABC Corp", "Send thank you email after interview", 4, 12, 0, "medium"),
        ("LinkedIn Profile Update", "Optimize profile for recruiters", 7, 20, 0, "medium"),
        ("Weekly Job Applications", "Apply to 5 companies per week", 7, 18, 0, "high"),
    ]

    console.print("[bold]Creating Job Hunt Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority in job_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        recurrence = "weekly" if "Weekly" in title else None
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["jobhunt", "career", "applications"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Job Hunt Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags jobhunt[/cyan]\n"
        "  [cyan]uv run python main.py search \"interview\"[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
