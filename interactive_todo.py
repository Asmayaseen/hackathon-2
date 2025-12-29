#!/usr/bin/env python3
"""Interactive Todo Application - Rich Library Menu System"""

from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from src.core.todo_manager import TodoManager

console = Console()
manager = TodoManager()


def clear_screen():
    """Clear the console screen."""
    console.clear()


def show_header():
    """Display application header."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Phase II Advanced Todo Application[/bold cyan]\n"
        "[dim]Interactive Menu - Manage Your Tasks[/dim]",
        border_style="cyan"
    ))
    console.print()


def display_tasks_table(tasks, title="All Tasks"):
    """Display tasks in a Rich table."""
    if not tasks:
        console.print(f"[yellow]No tasks found.[/yellow]\n")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6, justify="center")
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Tags", style="dim", no_wrap=False)
    table.add_column("Due Date", style="dim", no_wrap=False, width=18)
    table.add_column("Recur", justify="center", width=6)
    table.add_column("Status", justify="center", width=12)

    for todo in tasks:
        # Priority with color
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        priority_display = f"[{priority_color}]{todo.priority.upper()}[/{priority_color}]"

        # Tags
        tags_display = " ".join([f"#{tag}" for tag in todo.tags[:3]]) if todo.tags else ""
        if len(todo.tags) > 3:
            tags_display += f" +{len(todo.tags)-3}"

        # Due date with overdue check
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d %I:%M%p")
            if todo.due_date < datetime.now() and todo.status != "completed":
                due_display = f"[bold red]{due_formatted}![/bold red]"
            else:
                due_display = due_formatted
        else:
            due_display = "[dim]-[/dim]"

        # Recurrence
        recurrence_display = ""
        if todo.recurrence_pattern:
            pattern_abbrev = {"daily": "[cyan]D[/cyan]", "weekly": "[cyan]W[/cyan]", "monthly": "[cyan]M[/cyan]"}
            recurrence_display = pattern_abbrev.get(todo.recurrence_pattern, "")

        # Status with color
        status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
        status_color = status_colors[todo.status]
        status_display = f"[{status_color}]{todo.status}[/{status_color}]"

        table.add_row(
            str(todo.id),
            todo.title[:40] + "..." if len(todo.title) > 40 else todo.title,
            priority_display,
            tags_display,
            due_display,
            recurrence_display,
            status_display
        )

    console.print(table)
    console.print(f"[dim]Total: {len(tasks)} task(s)[/dim]\n")


def add_task():
    """Add a new task interactively."""
    console.print("[bold green]Add New Task[/bold green]\n", style="bold")

    title = Prompt.ask("[cyan]Task title[/cyan]")
    if not title.strip():
        console.print("[red]Error: Title cannot be empty![/red]\n")
        return

    description = Prompt.ask("[cyan]Description[/cyan] (optional)", default="")

    priority = Prompt.ask(
        "[cyan]Priority[/cyan]",
        choices=["high", "medium", "low"],
        default="medium"
    )

    tags_input = Prompt.ask("[cyan]Tags[/cyan] (comma-separated, optional)", default="")
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []

    has_due_date = Confirm.ask("[cyan]Add due date?[/cyan]", default=False)
    due_date = None
    if has_due_date:
        due_date_str = Prompt.ask("[cyan]Due date[/cyan] (YYYY-MM-DD HH:MM)")
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            console.print("[red]Invalid date format! Using no due date.[/red]")
            due_date = None

    recurrence = None
    if due_date and Confirm.ask("[cyan]Make this recurring?[/cyan]", default=False):
        recurrence = Prompt.ask(
            "[cyan]Recurrence pattern[/cyan]",
            choices=["daily", "weekly", "monthly"]
        )

    try:
        task = manager.add_todo(title, description, priority, tags, due_date, recurrence)
        console.print(f"\n[green]✓ Task #{task.id} added successfully![/green]")
        console.print(f"  Title: {task.title}")
        console.print(f"  Priority: [{priority_colors[task.priority]}]{task.priority}[/{priority_colors[task.priority]}]")
        if tags:
            console.print(f"  Tags: {', '.join(['#'+t for t in task.tags])}")
        if due_date:
            console.print(f"  Due: {due_date.strftime('%b %d, %Y %I:%M%p')}")
        if recurrence:
            console.print(f"  Recurrence: {recurrence}")
        console.print()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]\n")


priority_colors = {"high": "red", "medium": "yellow", "low": "green"}


def list_tasks():
    """List all tasks with optional filters."""
    console.print("[bold green]List Tasks[/bold green]\n", style="bold")

    if Confirm.ask("[cyan]Apply filters?[/cyan]", default=False):
        filter_status = None
        if Confirm.ask("  Filter by status?", default=False):
            filter_status = Prompt.ask("  Status", choices=["pending", "in_progress", "completed"])

        filter_priority = None
        if Confirm.ask("  Filter by priority?", default=False):
            filter_priority = Prompt.ask("  Priority", choices=["high", "medium", "low"])

        filter_tags = None
        if Confirm.ask("  Filter by tags?", default=False):
            tags_input = Prompt.ask("  Tags (comma-separated)")
            filter_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        tasks = manager.list_todos(status=filter_status, priority=filter_priority, tags=filter_tags)
        title = "Filtered Tasks"
    else:
        tasks = manager.list_todos()
        title = "All Tasks"

    # Sort options
    if tasks and Confirm.ask("[cyan]Sort tasks?[/cyan]", default=False):
        sort_by = Prompt.ask(
            "  Sort by",
            choices=["priority", "due_date", "created_at", "title"],
            default="created_at"
        )
        sort_order = Prompt.ask("  Order", choices=["asc", "desc"], default="asc")
        tasks = manager.sort_todos(tasks, sort_by, sort_order)
        title += f" (sorted by {sort_by} {sort_order})"

    console.print()
    display_tasks_table(tasks, title)


def search_tasks():
    """Search tasks by keyword."""
    console.print("[bold green]Search Tasks[/bold green]\n", style="bold")

    keyword = Prompt.ask("[cyan]Search keyword[/cyan]")

    tasks = manager.filter_todos(keyword=keyword)

    console.print()
    display_tasks_table(tasks, f"Search Results for '{keyword}'")


def update_task():
    """Update an existing task."""
    console.print("[bold green]Update Task[/bold green]\n", style="bold")

    # Show current tasks
    all_tasks = manager.list_todos()
    if not all_tasks:
        console.print("[yellow]No tasks to update![/yellow]\n")
        return

    display_tasks_table(all_tasks, "Current Tasks")

    try:
        task_id = int(Prompt.ask("[cyan]Enter task ID to update[/cyan]"))
    except ValueError:
        console.print("[red]Invalid ID![/red]\n")
        return

    task = manager.get_todo(task_id)
    if not task:
        console.print(f"[red]Task #{task_id} not found![/red]\n")
        return

    console.print(f"\n[dim]Current task: {task.title}[/dim]")
    console.print(f"[dim]Status: {task.status} | Priority: {task.priority}[/dim]\n")

    # Ask what to update
    if Confirm.ask("Update title?", default=False):
        title = Prompt.ask("  New title", default=task.title)
    else:
        title = None

    if Confirm.ask("Update status?", default=False):
        status = Prompt.ask("  New status", choices=["pending", "in_progress", "completed"])
    else:
        status = None

    if Confirm.ask("Update priority?", default=False):
        priority = Prompt.ask("  New priority", choices=["high", "medium", "low"])
    else:
        priority = None

    if Confirm.ask("Update tags?", default=False):
        tags_input = Prompt.ask("  New tags (comma-separated)")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
    else:
        tags = None

    try:
        updated = manager.update_todo(task_id, title=title, status=status, priority=priority, tags=tags)
        if updated:
            console.print(f"\n[green]✓ Task #{task_id} updated successfully![/green]\n")
        else:
            console.print(f"[red]Failed to update task #{task_id}[/red]\n")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]\n")


def complete_task():
    """Mark a task as completed."""
    console.print("[bold green]Complete Task[/bold green]\n", style="bold")

    # Show pending tasks
    pending = manager.list_todos(status="pending") + manager.list_todos(status="in_progress")
    if not pending:
        console.print("[yellow]No pending tasks to complete![/yellow]\n")
        return

    display_tasks_table(pending, "Pending Tasks")

    try:
        task_id = int(Prompt.ask("[cyan]Enter task ID to complete[/cyan]"))
    except ValueError:
        console.print("[red]Invalid ID![/red]\n")
        return

    completed, new_instance = manager.complete_todo(task_id)

    if completed:
        console.print(f"\n[green]✓ Task #{task_id} marked as completed![/green]")
        console.print(f"  Title: {completed.title}\n")

        if new_instance:
            console.print("[bold cyan]♻  Recurring Task - Next Instance Created:[/bold cyan]")
            console.print(f"  New ID: #{new_instance.id}")
            console.print(f"  Title: {new_instance.title}")
            console.print(f"  Next due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p') if new_instance.due_date else 'N/A'}")
            console.print(f"  Pattern: {new_instance.recurrence_pattern}\n")
    else:
        console.print(f"[red]Task #{task_id} not found![/red]\n")


def delete_task():
    """Delete a task."""
    console.print("[bold green]Delete Task[/bold green]\n", style="bold")

    all_tasks = manager.list_todos()
    if not all_tasks:
        console.print("[yellow]No tasks to delete![/yellow]\n")
        return

    display_tasks_table(all_tasks, "All Tasks")

    try:
        task_id = int(Prompt.ask("[cyan]Enter task ID to delete[/cyan]"))
    except ValueError:
        console.print("[red]Invalid ID![/red]\n")
        return

    task = manager.get_todo(task_id)
    if not task:
        console.print(f"[red]Task #{task_id} not found![/red]\n")
        return

    if Confirm.ask(f"[red]Delete task '{task.title}'?[/red]", default=False):
        if manager.delete_todo(task_id):
            console.print(f"\n[green]✓ Task #{task_id} deleted successfully![/green]\n")
        else:
            console.print(f"[red]Failed to delete task #{task_id}[/red]\n")
    else:
        console.print("[dim]Delete cancelled.[/dim]\n")


def check_reminders():
    """Check for upcoming reminders."""
    console.print("[bold green]Reminder Check[/bold green]\n", style="bold")

    reminders = manager.check_reminders()

    if reminders:
        console.print(f"[bold yellow]⚠ {len(reminders)} task(s) due within 30 minutes![/bold yellow]\n")
        for task in reminders:
            due_time = task.due_date.strftime("%I:%M%p") if task.due_date else "N/A"
            console.print(f"  • [bold]{task.title}[/bold] - Due at {due_time}")
        console.print()
    else:
        console.print("[green]✓ No upcoming reminders.[/green]\n")


def show_statistics():
    """Show task statistics."""
    console.print("[bold green]Task Statistics[/bold green]\n", style="bold")

    all_tasks = manager.list_todos()

    if not all_tasks:
        console.print("[yellow]No tasks yet![/yellow]\n")
        return

    completed = len([t for t in all_tasks if t.status == "completed"])
    in_progress = len([t for t in all_tasks if t.status == "in_progress"])
    pending = len([t for t in all_tasks if t.status == "pending"])
    high_priority = len([t for t in all_tasks if t.priority == "high"])
    recurring = len([t for t in all_tasks if t.recurrence_pattern])
    overdue = len([t for t in all_tasks if t.due_date and t.due_date < datetime.now() and t.status != "completed"])

    stats_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Count", justify="right", style="bold")

    stats_table.add_row("Total Tasks", str(len(all_tasks)))
    stats_table.add_row("[green]Completed[/green]", str(completed))
    stats_table.add_row("[yellow]In Progress[/yellow]", str(in_progress))
    stats_table.add_row("Pending", str(pending))
    stats_table.add_row("[red]High Priority[/red]", str(high_priority))
    stats_table.add_row("[cyan]Recurring[/cyan]", str(recurring))
    if overdue > 0:
        stats_table.add_row("[bold red]Overdue[/bold red]", str(overdue))

    console.print(stats_table)
    console.print()


def main_menu():
    """Display main menu and handle user choices."""
    while True:
        clear_screen()
        show_header()

        # Create menu
        menu = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
        menu.add_column("Option", style="bold cyan", justify="center", width=8)
        menu.add_column("Action", style="white")

        menu.add_row("1", "➕ Add New Task")
        menu.add_row("2", "📋 List All Tasks")
        menu.add_row("3", "🔍 Search Tasks")
        menu.add_row("4", "✏️  Update Task")
        menu.add_row("5", "✅ Complete Task")
        menu.add_row("6", "🗑️  Delete Task")
        menu.add_row("7", "⏰ Check Reminders")
        menu.add_row("8", "📊 View Statistics")
        menu.add_row("0", "🚪 Exit")

        console.print(menu)
        console.print()

        choice = Prompt.ask(
            "[bold cyan]Select an option[/bold cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            default="2"
        )

        console.print()

        if choice == "1":
            add_task()
        elif choice == "2":
            list_tasks()
        elif choice == "3":
            search_tasks()
        elif choice == "4":
            update_task()
        elif choice == "5":
            complete_task()
        elif choice == "6":
            delete_task()
        elif choice == "7":
            check_reminders()
        elif choice == "8":
            show_statistics()
        elif choice == "0":
            console.print("[bold cyan]Thank you for using Todo App! 👋[/bold cyan]\n")
            break

        if choice != "0":
            console.print()
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]\n")
