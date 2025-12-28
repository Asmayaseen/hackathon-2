#!/usr/bin/env python3
"""
Demo: Content Creation & Social Media
======================================
Track video editing, blog posts, social media scheduling.
Features: Content calendar, publishing deadlines, engagement
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
        "[bold cyan]CONTENT CREATION DEMO[/bold cyan]\n"
        "[dim]YouTube, Blogging & Social Media Management[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    content_tasks = [
        ("YouTube Video - Tech Tutorial", "Edit and upload Python tutorial video", 3, 20, 0, "high"),
        ("Blog Post Draft", "Write article on AI trends 2025", 4, 18, 0, "medium"),
        ("Instagram Reel Creation", "Create 30-sec coding tips reel", 1, 15, 0, "medium"),
        ("Tweet Thread - Weekly Tips", "Write 10-tweet thread on productivity", 2, 12, 0, "low"),
        ("TikTok Video Upload", "Upload quick coding hack video", 2, 16, 0, "medium"),
        ("Weekly Content Planning", "Plan next week's content calendar", 7, 10, 0, "high"),
        ("Respond to Comments", "Engage with audience comments", 1, 20, 0, "low"),
    ]

    console.print("[bold]Creating Content Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority in content_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        recurrence = "weekly" if "Weekly" in title else ("daily" if "daily" in title.lower() else None)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["content", "social-media", "creative"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Content Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags content[/cyan]\n"
        "  [cyan]uv run python main.py list --priority high[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
