#!/usr/bin/env python3
"""
PHASE I - ADVANCED LEVEL DEMONSTRATION
========================================
This demo showcases ALL Advanced Level features required by Hackathon Phase I:
1. Recurring Tasks (daily/weekly/monthly auto-scheduling)
2. Due Dates & Time Reminders (ISO 8601 dates + notifications)

Plus bonus Intermediate features:
- Priorities & Tags
- Search & Filter
- Sort Tasks
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from src.core.todo_manager import TodoManager
from datetime import datetime, timedelta

console = Console()
manager = TodoManager()


def section_header(title: str) -> None:
    """Display section header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    console.print()


def show_tasks_table(tasks: list, title: str = "Tasks") -> None:
    """Display tasks in a Rich table with all advanced features highlighted."""
    if not tasks:
        console.print("[yellow]No tasks to display.[/yellow]\n")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=4, justify="center")
    table.add_column("Title", style="cyan", no_wrap=False, width=25)
    table.add_column("Priority", justify="center", width=8)
    table.add_column("Tags", style="dim", no_wrap=False, width=15)
    table.add_column("Due Date", style="yellow", width=16)
    table.add_column("Recurrence", justify="center", width=10)
    table.add_column("Status", justify="center", width=11)

    for todo in tasks:
        # Priority with color
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_display = f"[{priority_colors[todo.priority]}]{todo.priority.upper()}[/{priority_colors[todo.priority]}]"

        # Tags
        tags_display = " ".join([f"#{tag}" for tag in todo.tags[:2]]) if todo.tags else ""
        if len(todo.tags) > 2:
            tags_display += f" +{len(todo.tags)-2}"

        # Due date with overdue check
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d %I:%M%p")
            if todo.due_date < datetime.now() and todo.status != "completed":
                due_display = f"[bold red]OVERDUE!\n{due_formatted}[/bold red]"
            else:
                due_display = due_formatted
        else:
            due_display = "[dim]-[/dim]"

        # Recurrence pattern
        if todo.recurrence_pattern:
            pattern_map = {
                "daily": "[cyan]Daily (D)[/cyan]",
                "weekly": "[cyan]Weekly (W)[/cyan]",
                "monthly": "[cyan]Monthly (M)[/cyan]"
            }
            recurrence_display = pattern_map.get(todo.recurrence_pattern, "")
        else:
            recurrence_display = "[dim]-[/dim]"

        # Status with color
        status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
        status_display = f"[{status_colors[todo.status]}]{todo.status}[/{status_colors[todo.status]}]"

        table.add_row(
            str(todo.id),
            todo.title[:22] + "..." if len(todo.title) > 22 else todo.title,
            priority_display,
            tags_display,
            due_display,
            recurrence_display,
            status_display
        )

    console.print(table)
    console.print(f"[dim]Total: {len(tasks)} task(s)[/dim]\n")


def main():
    """Run Phase I Advanced Level demonstration."""

    console.print()
    console.print(Panel.fit(
        "[bold green]PHASE I - ADVANCED LEVEL DEMONSTRATION[/bold green]\n"
        "[dim]Showcasing Recurring Tasks + Due Dates & Reminders[/dim]",
        border_style="green"
    ))

    # ========== ADVANCED FEATURE 1: RECURRING TASKS ==========
    section_header("ADVANCED FEATURE 1: Recurring Tasks")

    console.print("[bold]Creating Daily Recurring Task...[/bold]")
    daily_task = manager.add_todo(
        title="Daily Standup Meeting",
        description="Team sync at 9 AM every day",
        priority="high",
        tags=["work", "meeting", "daily"],
        due_date=datetime.now() + timedelta(hours=1),
        recurrence_pattern="daily"
    )
    console.print(f"[green][OK][/green] Created Task #{daily_task.id}: {daily_task.title}")
    console.print(f"  Recurrence: [cyan]{daily_task.recurrence_pattern}[/cyan]")
    console.print(f"  Due: {daily_task.due_date.strftime('%b %d, %Y %I:%M%p')}\n")

    console.print("[bold]Creating Weekly Recurring Task...[/bold]")
    weekly_task = manager.add_todo(
        title="Weekly Team Retrospective",
        description="Friday end-of-week review",
        priority="medium",
        tags=["work", "meeting", "retrospective"],
        due_date=datetime.now() + timedelta(days=2),
        recurrence_pattern="weekly"
    )
    console.print(f"[green][OK][/green] Created Task #{weekly_task.id}: {weekly_task.title}")
    console.print(f"  Recurrence: [cyan]{weekly_task.recurrence_pattern}[/cyan]")
    console.print(f"  Due: {weekly_task.due_date.strftime('%b %d, %Y %I:%M%p')}\n")

    console.print("[bold]Creating Monthly Recurring Task...[/bold]")
    monthly_task = manager.add_todo(
        title="Monthly Budget Review",
        description="Review and update monthly budget",
        priority="high",
        tags=["finance", "personal", "budget"],
        due_date=datetime.now() + timedelta(days=5),
        recurrence_pattern="monthly"
    )
    console.print(f"[green][OK][/green] Created Task #{monthly_task.id}: {monthly_task.title}")
    console.print(f"  Recurrence: [cyan]{monthly_task.recurrence_pattern}[/cyan]")
    console.print(f"  Due: {monthly_task.due_date.strftime('%b %d, %Y %I:%M%p')}\n")

    show_tasks_table(manager.list_todos(), "All Tasks with Recurrence Patterns")

    # Demonstrate auto-creation on completion
    console.print("[bold yellow]Demonstrating Auto-Creation on Completion...[/bold yellow]\n")
    console.print(f"Completing recurring task #{daily_task.id}: {daily_task.title}")

    completed, new_instance = manager.complete_todo(daily_task.id)

    if completed and new_instance:
        console.print(f"\n[green][OK][/green] Task #{completed.id} marked as completed")
        console.print(f"\n[bold cyan]RECURRING TASK - New Instance Auto-Created![/bold cyan]")
        console.print(f"  New ID: #{new_instance.id}")
        console.print(f"  Title: {new_instance.title}")
        console.print(f"  Status: [white]{new_instance.status}[/white]")
        console.print(f"  Next Due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p')}")
        console.print(f"  Pattern: {new_instance.recurrence_pattern}\n")

    show_tasks_table(manager.list_todos(), "After Completing Recurring Task")

    # ========== ADVANCED FEATURE 2: DUE DATES & REMINDERS ==========
    section_header("ADVANCED FEATURE 2: Due Dates & Time Reminders")

    console.print("[bold]Creating Tasks with Various Due Dates...[/bold]\n")

    # Task due soon (should trigger reminder)
    soon_task = manager.add_todo(
        title="Submit Hackathon Phase I",
        description="Complete and submit all Phase I deliverables",
        priority="high",
        tags=["hackathon", "urgent", "deadline"],
        due_date=datetime.now() + timedelta(minutes=25)  # Due in 25 minutes
    )
    console.print(f"[green][OK][/green] Created Task #{soon_task.id}: {soon_task.title}")
    console.print(f"  Due: {soon_task.due_date.strftime('%b %d, %Y %I:%M%p')} [yellow](in 25 minutes)[/yellow]\n")

    # Task due later today
    today_task = manager.add_todo(
        title="Code Review for PR #123",
        description="Review backend API changes",
        priority="medium",
        tags=["work", "code-review"],
        due_date=datetime.now() + timedelta(hours=3)
    )
    console.print(f"[green][OK][/green] Created Task #{today_task.id}: {today_task.title}")
    console.print(f"  Due: {today_task.due_date.strftime('%b %d, %Y %I:%M%p')} [yellow](in 3 hours)[/yellow]\n")

    # Overdue task (for demonstration)
    overdue_task = manager.add_todo(
        title="Update Project Documentation",
        description="Add README sections for new features",
        priority="low",
        tags=["documentation", "work"],
        due_date=datetime.now() - timedelta(hours=2)  # 2 hours overdue
    )
    console.print(f"[green][OK][/green] Created Task #{overdue_task.id}: {overdue_task.title}")
    console.print(f"  Due: {overdue_task.due_date.strftime('%b %d, %Y %I:%M%p')} [bold red](OVERDUE!)[/bold red]\n")

    # Task due next week
    future_task = manager.add_todo(
        title="Prepare Phase II Specification",
        description="Plan full-stack web application architecture",
        priority="medium",
        tags=["hackathon", "planning", "phase-2"],
        due_date=datetime.now() + timedelta(days=7)
    )
    console.print(f"[green][OK][/green] Created Task #{future_task.id}: {future_task.title}")
    console.print(f"  Due: {future_task.due_date.strftime('%b %d, %Y %I:%M%p')} [dim](next week)[/dim]\n")

    show_tasks_table(manager.list_todos(), "All Tasks with Due Dates")

    # Check reminders
    console.print("[bold yellow]Checking for Upcoming Reminders...[/bold yellow]\n")
    reminders = manager.check_reminders()

    if reminders:
        console.print(f"[bold red]WARNING - REMINDERS: {len(reminders)} task(s) due within 30 minutes![/bold red]\n")

        reminder_table = Table(show_header=True, header_style="bold red", box=box.ROUNDED)
        reminder_table.add_column("ID", style="dim", width=4)
        reminder_table.add_column("Task", style="bold yellow")
        reminder_table.add_column("Due At", style="red")
        reminder_table.add_column("Priority", justify="center")

        for task in reminders:
            priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
            reminder_table.add_row(
                str(task.id),
                task.title,
                task.due_date.strftime("%I:%M%p"),
                f"[{priority_colors[task.priority]}]{task.priority.upper()}[/{priority_colors[task.priority]}]"
            )

        console.print(reminder_table)
        console.print()
    else:
        console.print("[green][OK] No upcoming reminders (all clear)[/green]\n")

    # ========== BONUS: INTERMEDIATE FEATURES ==========
    section_header("BONUS: Intermediate Features Showcase")

    console.print("[bold]Priority Filtering (High Priority Only)...[/bold]")
    high_priority = manager.list_todos(priority="high")
    show_tasks_table(high_priority, "High Priority Tasks")

    console.print("[bold]Tag Filtering (Work-related Tasks)...[/bold]")
    work_tasks = manager.list_todos(tags=["work"])
    show_tasks_table(work_tasks, "Work Tasks")

    console.print("[bold]Keyword Search ('hackathon')...[/bold]")
    search_results = manager.filter_todos(keyword="hackathon")
    show_tasks_table(search_results, "Search Results: 'hackathon'")

    console.print("[bold]Sorting by Due Date (Earliest First)...[/bold]")
    sorted_tasks = manager.sort_todos(manager.list_todos(), sort_by="due_date", sort_order="asc")
    show_tasks_table(sorted_tasks, "Tasks Sorted by Due Date")

    # ========== SUMMARY ==========
    section_header("PHASE I - ADVANCED LEVEL SUMMARY")

    all_tasks = manager.list_todos()
    completed_count = len([t for t in all_tasks if t.status == "completed"])
    pending_count = len([t for t in all_tasks if t.status == "pending"])
    recurring_count = len([t for t in all_tasks if t.recurrence_pattern])
    with_due_dates = len([t for t in all_tasks if t.due_date])
    overdue_count = len([t for t in all_tasks if t.due_date and t.due_date < datetime.now() and t.status != "completed"])

    summary_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right", style="bold")

    summary_table.add_row("Total Tasks", str(len(all_tasks)))
    summary_table.add_row("[green]Completed[/green]", str(completed_count))
    summary_table.add_row("Pending", str(pending_count))
    summary_table.add_row("[cyan]Recurring Tasks[/cyan]", str(recurring_count))
    summary_table.add_row("[yellow]Tasks with Due Dates[/yellow]", str(with_due_dates))
    if overdue_count > 0:
        summary_table.add_row("[bold red]Overdue Tasks[/bold red]", str(overdue_count))

    console.print(summary_table)
    console.print()

    console.print(Panel.fit(
        "[bold green]PHASE I - ADVANCED LEVEL COMPLETE![/bold green]\n\n"
        "[dim]Features Demonstrated:[/dim]\n"
        "1. [OK] Recurring Tasks (Daily/Weekly/Monthly)\n"
        "2. [OK] Due Dates & Time Reminders\n"
        "3. [OK] Auto-creation on Completion\n"
        "4. [OK] Overdue Detection\n"
        "5. [OK] Reminder Notifications\n"
        "6. [OK] Priority & Tag Organization\n"
        "7. [OK] Search & Filter\n"
        "8. [OK] Multi-criteria Sorting\n\n"
        "[bold]Status:[/bold] Ready for Hackathon Submission",
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
