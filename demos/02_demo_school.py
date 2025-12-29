#!/usr/bin/env python3
"""
Demo: School & Academic Management
===================================
Track homework, classes, exams, and projects with priorities and deadlines.
Features: Recurring classes, assignment deadlines, exam preparation
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
        "[bold cyan]SCHOOL MANAGEMENT DEMO[/bold cyan]\n"
        "[dim]Track Classes, Homework, Exams & Projects[/dim]",
        border_style="cyan"
    ))
    console.print()

    base_date = datetime.now()

    # Recurring Classes (Weekly)
    console.print("[bold]1. Creating Weekly Class Schedule...[/bold]\n")

    classes = [
        ("Physics Class", "Room 301, Prof. Ahmed", "monday", 9, 0),
        ("Math Class", "Room 205, Ms. Sarah", "tuesday", 10, 30),
        ("Chemistry Lab", "Lab Building, Dr. Khan", "wednesday", 14, 0),
        ("English Literature", "Room 102, Mr. Ali", "thursday", 11, 0),
    ]

    for title, desc, day, hour, minute in classes:
        due_date = base_date.replace(hour=hour, minute=minute) + timedelta(days=1)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority="medium",
            tags=["school", "class", title.split()[0].lower()],
            due_date=due_date,
            recurrence_pattern="weekly"
        )
        console.print(f"[green][OK][/green] {title} - {day.capitalize()} {hour:02d}:{minute:02d}")

    console.print()

    # Homework & Assignments
    console.print("[bold]2. Adding Homework & Assignments...[/bold]\n")

    homework = [
        ("Math Homework - Chapter 5", "Complete exercises 1-20, due Friday", "high", "math", 2),
        ("Physics Lab Report", "Write report on pendulum experiment", "high", "physics", 3),
        ("English Essay - Shakespeare", "1000 words on Hamlet", "medium", "english", 5),
        ("Chemistry Problem Set", "Problems 1-15 from textbook", "medium", "chemistry", 4),
    ]

    for title, desc, priority, subject, days_ahead in homework:
        due_date = base_date + timedelta(days=days_ahead, hours=23, minutes=59)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority=priority,
            tags=["school", "homework", subject],
            due_date=due_date
        )
        console.print(f"[green][OK][/green] {title} - Due: {due_date.strftime('%b %d')}")

    console.print()

    # Upcoming Exams
    console.print("[bold]3. Scheduling Exam Preparation...[/bold]\n")

    exams = [
        ("Math Midterm Exam", "Chapters 1-5, Algebra & Geometry", 7),
        ("Physics Final Exam", "Full syllabus, lab work included", 14),
        ("Chemistry Quiz", "Organic chemistry basics", 3),
    ]

    for title, desc, days_ahead in exams:
        due_date = base_date + timedelta(days=days_ahead, hours=9, minutes=0)
        task = manager.add_todo(
            title=title,
            description=desc,
            priority="high",
            tags=["school", "exam", title.split()[0].lower()],
            due_date=due_date
        )
        console.print(f"[green][OK][/green] {title} - {due_date.strftime('%b %d at %I:%M %p')}")

    console.print()

    # Display summary table
    table = Table(title="School Tasks Overview", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Task", style="white", width=30)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Due Date", style="yellow", width=15)

    all_tasks = manager.list_todos()
    for task in all_tasks:
        task_type = "Class" if "class" in task.tags else ("Exam" if "exam" in task.tags else "Homework")
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_display = f"[{priority_colors[task.priority]}]{task.priority.upper()}[/{priority_colors[task.priority]}]"

        due_display = task.due_date.strftime("%b %d %I:%M%p") if task.due_date else "-"

        table.add_row(
            task_type,
            task.title[:28] + "..." if len(task.title) > 28 else task.title,
            priority_display,
            due_display
        )

    console.print(table)
    console.print()

    # Statistics
    total = len(all_tasks)
    homework_count = len([t for t in all_tasks if "homework" in t.tags])
    exam_count = len([t for t in all_tasks if "exam" in t.tags])
    class_count = len([t for t in all_tasks if "class" in t.tags])

    console.print(f"[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Total Tasks: {total}")
    console.print(f"  Classes: {class_count} (recurring weekly)")
    console.print(f"  Homework: {homework_count}")
    console.print(f"  Exams: {exam_count}")
    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Usage Commands:[/bold]\n\n"
        "View all homework:\n"
        "  [cyan]uv run python main.py list --tags homework[/cyan]\n\n"
        "View high priority (urgent assignments):\n"
        "  [cyan]uv run python main.py list --priority high[/cyan]\n\n"
        "Find math-related tasks:\n"
        "  [cyan]uv run python main.py search \"math\"[/cyan]\n\n"
        "Sort by deadline:\n"
        "  [cyan]uv run python main.py list --sort-by due_date[/cyan]",
        title="How to Use",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
