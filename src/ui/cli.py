# T026-T053: CLI implementation with Typer and Rich
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
from pydantic import ValidationError
from src.core.todo_manager import TodoManager

app = typer.Typer(help="Phase I Console Todo Application")
console = Console()
manager = TodoManager()


@app.command()
def add(
    title: str = typer.Argument(..., help="Todo title"),
    description: str = typer.Option("", "--description", "-d", help="Optional description"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority (high/medium/low)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Tags (comma-separated)"),
    due_date: Optional[str] = typer.Option(None, "--due-date", help="Due date (YYYY-MM-DD HH:MM)"),
    recurrence: Optional[str] = typer.Option(None, "--recurrence", "-r", help="Recurrence pattern (daily/weekly/monthly)")
) -> None:
    """Add a new todo item."""
    # T023: Validate priority
    if priority not in ["high", "medium", "low"]:
        console.print(f"[red]Error:[/red] Invalid priority '{priority}'. Must be one of: high, medium, low")
        raise typer.Exit(1)

    # T106: Validate recurrence
    if recurrence and recurrence not in ["daily", "weekly", "monthly"]:
        console.print(f"[red]Error:[/red] Invalid --recurrence '{recurrence}'. Must be one of: daily, weekly, monthly")
        raise typer.Exit(1)

    # T024: Parse tags from comma-separated string
    tag_list: List[str] = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # T083: Parse due_date from ISO 8601 format
    from datetime import datetime as dt
    due_dt: Optional[dt] = None
    if due_date:
        try:
            due_dt = dt.strptime(due_date, "%Y-%m-%d %H:%M")
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid --due-date format. Use YYYY-MM-DD HH:MM")
            raise typer.Exit(1)

    # T107: Validate recurrence requires due_date
    if recurrence and not due_dt:
        console.print(f"[red]Error:[/red] Recurrence pattern requires --due-date")
        raise typer.Exit(1)

    try:
        todo = manager.add_todo(title, description, priority, tag_list, due_dt, recurrence)
        console.print("[green][OK][/green] Todo added successfully!\n")
        console.print(f"  ID: {todo.id}")
        console.print(f"  Title: {todo.title}")
        console.print(f"  Status: {todo.status}")

        # T031: Display priority and tags
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        console.print(f"  Priority: [{priority_color}]{todo.priority}[/{priority_color}]")

        if todo.tags:
            tags_formatted = " ".join([f"#{tag}" for tag in todo.tags])
            console.print(f"  Tags: {tags_formatted}")

        # T089: Display due_date if specified
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d, %Y %I:%M%p")
            console.print(f"  Due: {due_formatted}")

        # T111: Display recurrence_pattern if specified
        if todo.recurrence_pattern:
            console.print(f"  Recurrence: {todo.recurrence_pattern}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e.errors()[0]['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated, AND logic)"),
    keyword: Optional[str] = typer.Option(None, "--keyword", "-k", help="Search by keyword"),
    from_date: Optional[str] = typer.Option(None, "--from-date", help="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = typer.Option(None, "--to-date", help="Filter to date (YYYY-MM-DD)"),
    sort_by: str = typer.Option("created_at", "--sort-by", help="Sort by field (priority/due_date/created_at/title)"),
    order: str = typer.Option("asc", "--order", help="Sort order (asc/desc)")
) -> None:
    """List all todos with optional filtering and sorting."""
    # T068: Validate sort_by parameter
    valid_sort_fields = ["priority", "due_date", "created_at", "title"]
    if sort_by not in valid_sort_fields:
        console.print(f"[red]Error:[/red] Invalid --sort-by '{sort_by}'. Must be one of: {', '.join(valid_sort_fields)}")
        raise typer.Exit(1)

    # Validate order parameter
    if order not in ["asc", "desc"]:
        console.print(f"[red]Error:[/red] Invalid --order '{order}'. Must be 'asc' or 'desc'")
        raise typer.Exit(1)

    # T026: Parse tags filter
    tag_list: Optional[List[str]] = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # T046-T047: Parse date range filters
    from datetime import datetime as dt
    date_from: Optional[dt] = None
    date_to: Optional[dt] = None

    if from_date:
        try:
            date_from = dt.strptime(from_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid --from-date format. Use YYYY-MM-DD")
            raise typer.Exit(1)

    if to_date:
        try:
            # Set to end of day (23:59:59)
            date_to = dt.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid --to-date format. Use YYYY-MM-DD")
            raise typer.Exit(1)

    # T048: Use filter_todos when any filter is specified, otherwise use list_todos
    if keyword or from_date or to_date:
        # Use advanced filtering
        todos = manager.filter_todos(keyword, status, priority, tag_list, date_from, date_to)
    else:
        # Use simple filtering (backward compatibility)
        todos = manager.list_todos(status, priority, tag_list)

    # T069: Apply sorting after filtering
    todos = manager.sort_todos(todos, sort_by, order)

    # T049, T051: Enhanced filter criteria display
    if not todos:
        msg = "No todos found"
        if keyword or status or priority or tags or from_date or to_date:
            filters = []
            if keyword:
                filters.append(f"keyword='{keyword}'")
            if status:
                filters.append(f"status='{status}'")
            if priority:
                filters.append(f"priority='{priority}'")
            if tags:
                filters.append(f"tags='{tags}'")
            if from_date:
                filters.append(f"from={from_date}")
            if to_date:
                filters.append(f"to={to_date}")
            msg += f" with {', '.join(filters)}"
        console.print(msg)
        return

    # T087: Display reminder notifications before table
    reminders = manager.check_reminders()
    if reminders:
        console.print("\n[bold yellow]⏰ REMINDERS[/bold yellow]")
        console.print("[yellow]The following tasks are due within 30 minutes:[/yellow]\n")
        for reminder in reminders:
            due_str = reminder.due_date.strftime("%I:%M%p") if reminder.due_date else "N/A"
            console.print(f"  • [bold]{reminder.title}[/bold] - Due at {due_str}")
        console.print()

    # T085: Add Due Date column
    # T110: Add Recurrence column
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Priority", justify="center", width=8)
    table.add_column("Tags", style="dim", no_wrap=False)
    table.add_column("Due Date", style="dim", no_wrap=False)
    table.add_column("Recurrence", style="dim", justify="center", width=10)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_colors = {
            "completed": "green",
            "in_progress": "yellow",
            "pending": "white"
        }
        status_color = status_colors[todo.status]

        # T029: Priority column with colors
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        priority_display = f"[{priority_color}]{todo.priority[0].upper()}[/{priority_color}]"

        # T030: Tags column
        tags_display = " ".join([f"#{tag}" for tag in todo.tags]) if todo.tags else ""

        # T085-T086: Due Date column with overdue indicator
        from datetime import datetime as dt
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d %I:%M%p")
            # Check if overdue
            if todo.due_date < dt.now() and todo.status != "completed":
                due_display = f"[bold red]{due_formatted} OVERDUE![/bold red]"
            else:
                due_display = due_formatted
        else:
            due_display = ""

        # T110: Recurrence pattern display
        recurrence_display = ""
        if todo.recurrence_pattern:
            # Abbreviate: daily -> D, weekly -> W, monthly -> M
            pattern_abbrev = {
                "daily": "[cyan]D[/cyan]",
                "weekly": "[cyan]W[/cyan]",
                "monthly": "[cyan]M[/cyan]"
            }
            recurrence_display = pattern_abbrev.get(todo.recurrence_pattern, "")

        table.add_row(
            str(todo.id),
            todo.title,
            priority_display,
            tags_display,
            due_display,
            recurrence_display,
            f"[{status_color}]{todo.status}[/{status_color}]",
            todo.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

    # T070: Display sort indicator
    sort_indicator = f"\nSorted by: {sort_by} ({order})"
    console.print(f"[dim]{sort_indicator}[/dim]")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Search keyword"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated, AND logic)")
) -> None:
    """Search todos by keyword (searches title and description)."""
    # Parse tags filter
    tag_list: Optional[List[str]] = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # T050: Search using filter_todos with keyword
    todos = manager.filter_todos(keyword, status, priority, tag_list)

    # T051: Handle empty results
    if not todos:
        msg = f"No todos found matching '{keyword}'"
        if status or priority or tags:
            filters = []
            if status:
                filters.append(f"status='{status}'")
            if priority:
                filters.append(f"priority='{priority}'")
            if tags:
                filters.append(f"tags='{tags}'")
            msg += f" with {', '.join(filters)}"
        console.print(msg)
        return

    # Display results in table
    # T110: Add Recurrence column
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Priority", justify="center", width=8)
    table.add_column("Tags", style="dim", no_wrap=False)
    table.add_column("Due Date", style="dim", no_wrap=False)
    table.add_column("Recurrence", style="dim", justify="center", width=10)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_colors = {
            "completed": "green",
            "in_progress": "yellow",
            "pending": "white"
        }
        status_color = status_colors[todo.status]

        # Priority column with colors
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        priority_display = f"[{priority_color}]{todo.priority[0].upper()}[/{priority_color}]"

        # Tags column
        tags_display = " ".join([f"#{tag}" for tag in todo.tags]) if todo.tags else ""

        # T085-T086: Due Date column with overdue indicator
        from datetime import datetime as dt
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d %I:%M%p")
            # Check if overdue
            if todo.due_date < dt.now() and todo.status != "completed":
                due_display = f"[bold red]{due_formatted} OVERDUE![/bold red]"
            else:
                due_display = due_formatted
        else:
            due_display = ""

        # T110: Recurrence pattern display
        recurrence_display = ""
        if todo.recurrence_pattern:
            # Abbreviate: daily -> D, weekly -> W, monthly -> M
            pattern_abbrev = {
                "daily": "[cyan]D[/cyan]",
                "weekly": "[cyan]W[/cyan]",
                "monthly": "[cyan]M[/cyan]"
            }
            recurrence_display = pattern_abbrev.get(todo.recurrence_pattern, "")

        table.add_row(
            str(todo.id),
            todo.title,
            priority_display,
            tags_display,
            due_display,
            recurrence_display,
            f"[{status_color}]{todo.status}[/{status_color}]",
            todo.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(f"\nFound {len(todos)} task(s) matching '{keyword}':\n")
    console.print(table)


@app.command()
def complete(
    todo_id: int = typer.Argument(..., help="Todo ID")
) -> None:
    """Mark a todo as completed. Creates next instance for recurring tasks."""
    completed, new_instance = manager.complete_todo(todo_id)

    if not completed:
        console.print(f"[red]Error:[/red] Todo #{todo_id} not found")
        raise typer.Exit(1)

    console.print(f"[green][OK][/green] Todo #{todo_id} marked as completed: \"{completed.title}\"")

    # T109: Display auto-create notification for recurring tasks
    if new_instance:
        console.print(f"\n[bold cyan]♻️  Recurring Task:[/bold cyan]")
        console.print(f"  Created next instance #{new_instance.id}")
        console.print(f"  Title: {new_instance.title}")
        console.print(f"  Next due: {new_instance.due_date.strftime('%b %d, %Y %I:%M%p') if new_instance.due_date else 'N/A'}")
        console.print(f"  Pattern: {new_instance.recurrence_pattern}")


@app.command()
def delete(
    todo_id: int = typer.Argument(..., help="Todo ID")
) -> None:
    """Delete a todo."""
    success = manager.delete_todo(todo_id)

    if not success:
        console.print(f"[red]Error:[/red] Todo #{todo_id} not found")
        raise typer.Exit(1)

    console.print(f"[green][OK][/green] Todo #{todo_id} deleted successfully")


@app.command()
def update(
    todo_id: int = typer.Argument(..., help="Todo ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status (pending/in_progress/completed)"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="New priority (high/medium/low)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="New tags (comma-separated, replaces existing)"),
    due_date: Optional[str] = typer.Option(None, "--due-date", help="New due date (YYYY-MM-DD HH:MM or 'none' to clear)"),
    recurrence: Optional[str] = typer.Option(None, "--recurrence", "-r", help="New recurrence pattern (daily/weekly/monthly or 'none' to remove)")
) -> None:
    """Update a todo's fields."""
    # Validate at least one field is provided
    if all(v is None for v in [title, description, status, priority, tags, due_date, recurrence]):
        console.print("[red]Error:[/red] At least one field must be provided (--title, --description, --status, --priority, --tags, --due-date, or --recurrence)")
        raise typer.Exit(1)

    # Validate status if provided
    if status and status not in ["pending", "in_progress", "completed"]:
        console.print(f"[red]Error:[/red] Invalid status '{status}'. Must be one of: pending, in_progress, completed")
        raise typer.Exit(1)

    # T027: Validate priority if provided
    if priority and priority not in ["high", "medium", "low"]:
        console.print(f"[red]Error:[/red] Invalid priority '{priority}'. Must be one of: high, medium, low")
        raise typer.Exit(1)

    # T028: Parse tags from comma-separated string
    tag_list: Optional[List[str]] = None
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # T084: Parse due_date (support "none" to clear)
    from datetime import datetime as dt
    due_dt: Optional[dt] = None
    clear_due = False
    if due_date:
        if due_date.lower() == "none":
            clear_due = True
        else:
            try:
                due_dt = dt.strptime(due_date, "%Y-%m-%d %H:%M")
            except ValueError:
                console.print(f"[red]Error:[/red] Invalid --due-date format. Use YYYY-MM-DD HH:MM or 'none'")
                raise typer.Exit(1)

    # T108: Validate and parse recurrence
    recurrence_pattern: Optional[str] = None
    clear_recurrence = False
    if recurrence:
        if recurrence.lower() == "none":
            clear_recurrence = True
        elif recurrence not in ["daily", "weekly", "monthly"]:
            console.print(f"[red]Error:[/red] Invalid --recurrence '{recurrence}'. Must be one of: daily, weekly, monthly, none")
            raise typer.Exit(1)
        else:
            recurrence_pattern = recurrence

    try:
        todo = manager.update_todo(
            todo_id, title=title, description=description,
            status=status, priority=priority, tags=tag_list,
            due_date=due_dt, clear_due_date=clear_due,
            recurrence_pattern=recurrence_pattern, clear_recurrence=clear_recurrence
        )

        if not todo:
            console.print(f"[red]Error:[/red] Todo #{todo_id} not found")
            raise typer.Exit(1)

        console.print(f"[green][OK][/green] Todo #{todo_id} updated successfully\n")
        console.print(f"  ID: {todo.id}")
        console.print(f"  Title: {todo.title}")
        console.print(f"  Description: {todo.description}")
        console.print(f"  Status: {todo.status}")

        # Display priority
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_color = priority_colors[todo.priority]
        console.print(f"  Priority: [{priority_color}]{todo.priority}[/{priority_color}]")

        # Display tags
        if todo.tags:
            tags_formatted = " ".join([f"#{tag}" for tag in todo.tags])
            console.print(f"  Tags: {tags_formatted}")

        # Display due_date
        if todo.due_date:
            due_formatted = todo.due_date.strftime("%b %d, %Y %I:%M%p")
            console.print(f"  Due: {due_formatted}")

        # T108: Display recurrence pattern
        if todo.recurrence_pattern:
            console.print(f"  Recurrence: {todo.recurrence_pattern}")

        console.print(f"  Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M')}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e.errors()[0]['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
