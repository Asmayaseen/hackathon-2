#!/usr/bin/env python3
"""
COMPREHENSIVE DEMO - All 5 Core Features Working
Demonstrates: Add, View, Update, Delete, Mark Complete
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.core.todo_manager import TodoManager
from datetime import datetime, timedelta

console = Console()
manager = TodoManager()


def show_section(title):
    """Display section header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    console.print()


def display_all_tasks():
    """Display all current tasks in a table."""
    tasks = manager.list_todos()

    if not tasks:
        console.print("[yellow]No tasks in the system.[/yellow]\n")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6, justify="center")
    table.add_column("Title", style="cyan")
    table.add_column("Description", style="white", no_wrap=False)
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Tags", style="dim")

    for todo in tasks:
        # Priority with color
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        priority_display = f"[{priority_color}]{todo.priority}[/{priority_color}]"

        # Status with color
        status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
        status_color = status_colors[todo.status]
        status_display = f"[{status_color}]{todo.status}[/{status_color}]"

        # Tags
        tags_display = ", ".join([f"#{tag}" for tag in todo.tags]) if todo.tags else ""

        table.add_row(
            str(todo.id),
            todo.title,
            todo.description[:40] + "..." if len(todo.description) > 40 else todo.description,
            priority_display,
            status_display,
            tags_display
        )

    console.print(table)
    console.print(f"[dim]Total tasks: {len(tasks)}[/dim]\n")


def main():
    """Run comprehensive demonstration of all features."""

    console.print()
    console.print(Panel.fit(
        "[bold green]PHASE II TODO APPLICATION - COMPREHENSIVE DEMO[/bold green]\n"
        "[dim]Demonstrating All 5 Core Features[/dim]",
        border_style="green"
    ))

    # ========== FEATURE 1: ADD TASKS ==========
    show_section("FEATURE 1: ADD TASKS")

    console.print("[bold]Adding 5 different tasks...[/bold]\n")

    # Task 1: Simple task
    task1 = manager.add_todo(
        title="Complete project documentation",
        description="Write comprehensive README and API docs",
        priority="high",
        tags=["work", "documentation"]
    )
    console.print(f"[green][OK][/green] Added Task #{task1.id}: {task1.title}")
    console.print(f"  Priority: [red]{task1.priority}[/red] | Tags: {', '.join(['#'+t for t in task1.tags])}\n")

    # Task 2: With due date
    task2 = manager.add_todo(
        title="Review pull requests",
        description="Review and merge pending PRs from team",
        priority="medium",
        tags=["work", "code-review"],
        due_date=datetime.now() + timedelta(hours=2)
    )
    console.print(f"[green][OK][/green] Added Task #{task2.id}: {task2.title}")
    console.print(f"  Priority: [yellow]{task2.priority}[/yellow] | Due: {task2.due_date.strftime('%b %d %I:%M%p')}\n")

    # Task 3: Recurring task
    task3 = manager.add_todo(
        title="Daily standup meeting",
        description="Team sync at 9 AM",
        priority="medium",
        tags=["work", "meeting"],
        due_date=datetime.now() + timedelta(days=1, hours=-15),
        recurrence_pattern="daily"
    )
    console.print(f"[green][OK][/green] Added Task #{task3.id}: {task3.title}")
    console.print(f"  Recurrence: [cyan]{task3.recurrence_pattern}[/cyan] | Due: {task3.due_date.strftime('%b %d %I:%M%p')}\n")

    # Task 4: Low priority
    task4 = manager.add_todo(
        title="Organize workspace",
        description="Clean desk and organize cables",
        priority="low",
        tags=["personal", "home"]
    )
    console.print(f"[green][OK][/green] Added Task #{task4.id}: {task4.title}")
    console.print(f"  Priority: [green]{task4.priority}[/green]\n")

    # Task 5: High priority
    task5 = manager.add_todo(
        title="Fix critical production bug",
        description="Database connection timeout in prod",
        priority="high",
        tags=["work", "urgent", "bug-fix"]
    )
    console.print(f"[green][OK][/green] Added Task #{task5.id}: {task5.title}")
    console.print(f"  Priority: [red]{task5.priority}[/red] | Tags: {', '.join(['#'+t for t in task5.tags])}\n")

    console.print("[bold green]SUCCESS: Successfully added 5 tasks![/bold green]")


    # ========== FEATURE 2: VIEW/LIST TASKS ==========
    show_section("FEATURE 2: VIEW/LIST TASKS")

    console.print("[bold]Viewing all tasks in the system...[/bold]\n")
    display_all_tasks()

    console.print("[bold]Filtering by priority (high only)...[/bold]\n")
    high_priority_tasks = manager.list_todos(priority="high")
    console.print(f"Found {len(high_priority_tasks)} high-priority tasks:")
    for task in high_priority_tasks:
        console.print(f"  • [red]#{task.id}[/red] - {task.title}")
    console.print()

    console.print("[bold]Filtering by tags (work)...[/bold]\n")
    work_tasks = manager.list_todos(tags=["work"])
    console.print(f"Found {len(work_tasks)} tasks tagged with 'work':")
    for task in work_tasks:
        console.print(f"  • [cyan]#{task.id}[/cyan] - {task.title}")
    console.print()


    # ========== FEATURE 3: UPDATE TASKS ==========
    show_section("FEATURE 3: UPDATE TASKS")

    console.print(f"[bold]Updating Task #{task1.id}...[/bold]\n")
    console.print(f"[dim]Before: {task1.title} | Status: {task1.status} | Priority: {task1.priority}[/dim]")

    updated_task = manager.update_todo(
        task1.id,
        status="in_progress",
        description="Updated: Writing README, API docs, and setup guide"
    )

    console.print(f"[green]After: {updated_task.title} | Status: {updated_task.status} | Priority: {updated_task.priority}[/green]")
    console.print(f"[green]Description: {updated_task.description}[/green]\n")

    console.print(f"[bold]Updating Task #{task4.id} priority...[/bold]\n")
    console.print(f"[dim]Before: {task4.title} | Priority: {task4.priority}[/dim]")

    updated_task4 = manager.update_todo(task4.id, priority="medium")

    console.print(f"[yellow]After: {updated_task4.title} | Priority: {updated_task4.priority}[/yellow]\n")

    console.print("[bold green]SUCCESS: Successfully updated 2 tasks![/bold green]")


    # ========== FEATURE 4: MARK COMPLETE ==========
    show_section("FEATURE 4: MARK COMPLETE")

    console.print(f"[bold]Marking Task #{task4.id} as completed...[/bold]\n")
    completed, new_instance = manager.complete_todo(task4.id)

    if completed:
        console.print(f"[green][DONE] Task #{completed.id} marked as completed![/green]")
        console.print(f"  Title: {completed.title}")
        console.print(f"  Status: [green]{completed.status}[/green]\n")

    console.print(f"[bold]Marking recurring Task #{task3.id} as completed...[/bold]\n")
    console.print(f"[dim]This is a recurring task with pattern: {task3.recurrence_pattern}[/dim]")

    completed_rec, new_instance = manager.complete_todo(task3.id)

    if completed_rec:
        console.print(f"[green][DONE] Task #{completed_rec.id} marked as completed![/green]")
        console.print(f"  Title: {completed_rec.title}")
        console.print(f"  Status: [green]{completed_rec.status}[/green]\n")

        if new_instance:
            console.print(f"[bold cyan]RECURRING TASK - Auto-created next instance![/bold cyan]")
            console.print(f"  New ID: #{new_instance.id}")
            console.print(f"  Title: {new_instance.title}")
            console.print(f"  Status: [white]{new_instance.status}[/white]")
            console.print(f"  Next Due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p')}")
            console.print(f"  Pattern: {new_instance.recurrence_pattern}\n")

    console.print("[bold green]SUCCESS: Completed 2 tasks (1 recurring)![/bold green]")


    # ========== FEATURE 5: DELETE TASKS ==========
    show_section("FEATURE 5: DELETE TASKS")

    console.print(f"[bold]Deleting Task #{task5.id}...[/bold]\n")
    console.print(f"[dim]Task to delete: {task5.title}[/dim]")

    success = manager.delete_todo(task5.id)

    if success:
        console.print(f"[green][DELETED] Task #{task5.id} deleted successfully![/green]\n")
    else:
        console.print(f"[red][FAIL] Failed to delete task #{task5.id}[/red]\n")

    console.print("[bold green]SUCCESS: Successfully deleted 1 task![/bold green]")


    # ========== FINAL STATE ==========
    show_section("FINAL STATE - ALL TASKS")

    console.print("[bold]Current state after all operations...[/bold]\n")
    display_all_tasks()

    # Statistics
    all_tasks = manager.list_todos()
    completed_count = len([t for t in all_tasks if t.status == "completed"])
    in_progress_count = len([t for t in all_tasks if t.status == "in_progress"])
    pending_count = len([t for t in all_tasks if t.status == "pending"])

    console.print(Panel.fit(
        f"[bold]Summary Statistics[/bold]\n\n"
        f"Total Tasks: [cyan]{len(all_tasks)}[/cyan]\n"
        f"Completed: [green]{completed_count}[/green]\n"
        f"In Progress: [yellow]{in_progress_count}[/yellow]\n"
        f"Pending: [white]{pending_count}[/white]",
        border_style="green"
    ))

    console.print()
    console.print(Panel.fit(
        "[bold green]SUCCESS: ALL 5 FEATURES DEMONSTRATED![/bold green]\n\n"
        "[dim]Features tested:[/dim]\n"
        "1. [OK] Add Tasks (5 tasks added)\n"
        "2. [OK] View/List Tasks (with filters)\n"
        "3. [OK] Update Tasks (2 tasks updated)\n"
        "4. [OK] Mark Complete (2 tasks completed, including recurring)\n"
        "5. [OK] Delete Tasks (1 task deleted)",
        border_style="bold green"
    ))
    console.print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
