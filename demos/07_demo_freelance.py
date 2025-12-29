#!/usr/bin/env python3
"""
Demo: Freelance Work Management
================================
Track clients, projects, invoices, and deadlines.
Features: Client meetings, project delivery, invoicing
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
        "[bold cyan]FREELANCE WORK TRACKER DEMO[/bold cyan]\n"
        "[dim]Clients, Projects, Invoices & Deadlines[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    freelance_tasks = [
        ("Client Meeting - Ahmed", "Discuss website redesign project", 2, 11, 0, "high"),
        ("Send Invoice #123", "Invoice for completed logo design", 3, 16, 0, "high"),
        ("Project Delivery - E-commerce Site", "Deploy final version to client server", 5, 23, 59, "high"),
        ("Follow-up Call - Sarah", "Check feedback on delivered project", 4, 14, 0, "medium"),
        ("Portfolio Update", "Add recent projects to portfolio site", 7, 18, 0, "medium"),
        ("Monthly Client Reports", "Send progress reports to all clients", 30, 10, 0, "high"),
    ]

    console.print("[bold]Creating Freelance Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority in freelance_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["freelance", "work", "client"],
            due_date=due_date
        )
        console.print(f"[green][OK][/green] {title} - Due: {due_date.strftime('%b %d')}")

    console.print(f"\n[bold cyan]Total Freelance Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags freelance[/cyan]\n"
        "  [cyan]uv run python main.py list --priority high[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
