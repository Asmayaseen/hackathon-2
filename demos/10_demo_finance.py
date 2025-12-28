#!/usr/bin/env python3
"""
Demo: Personal Finance Management
==================================
Track bills, budgets, investments, and savings goals.
Features: Monthly bills, budget reviews, financial planning
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
        "[bold cyan]FINANCE MANAGEMENT DEMO[/bold cyan]\n"
        "[dim]Bills, Budgets, Savings & Investments[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    finance_tasks = [
        ("Pay Electricity Bill", "Monthly utility payment", 28, 12, 0, "high", "monthly"),
        ("Pay Internet Bill", "Broadband subscription", 28, 12, 0, "high", "monthly"),
        ("Pay Rent", "Monthly house rent payment", 28, 10, 0, "high", "monthly"),
        ("Review Monthly Budget", "Analyze expenses vs income", 30, 18, 0, "medium", "monthly"),
        ("Investment Review", "Check stock portfolio performance", 30, 20, 0, "medium", "monthly"),
        ("Transfer to Savings", "Move 20% salary to savings account", 30, 14, 0, "high", "monthly"),
        ("Credit Card Payment", "Pay full balance to avoid interest", 28, 16, 0, "high", "monthly"),
    ]

    console.print("[bold]Creating Finance Tasks...[/bold]\n")
    for title, desc, days, hour, minute, priority, recurrence in finance_tasks:
        due_date = base_date + timedelta(days=days, hours=hour, minutes=minute)
        task = manager.add_todo(
            title=title, description=desc, priority=priority,
            tags=["finance", "bills", "money"],
            due_date=due_date, recurrence_pattern=recurrence
        )
        console.print(f"[green][OK][/green] {title}")

    console.print(f"\n[bold cyan]Total Finance Tasks: {len(manager.list_todos())}[/bold cyan]\n")

    console.print(Panel(
        "[bold]Usage:[/bold]\n"
        "  [cyan]uv run python main.py list --tags finance[/cyan]\n"
        "  [cyan]uv run python main.py list --priority high[/cyan]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
