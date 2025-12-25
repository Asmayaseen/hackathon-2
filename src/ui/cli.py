# T026-T053: CLI implementation with Typer and Rich
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from pydantic import ValidationError
from src.core.todo_manager import TodoManager

app = typer.Typer(help="Phase I Console Todo Application")
console = Console()
manager = TodoManager()


@app.command()
def add(
    title: str = typer.Argument(..., help="Todo title"),
    description: str = typer.Option("", "--description", "-d", help="Optional description")
) -> None:
    """Add a new todo item."""
    try:
        todo = manager.add_todo(title, description)
        console.print("[green][OK][/green] Todo added successfully!\n")
        console.print(f"  ID: {todo.id}")
        console.print(f"  Title: {todo.title}")
        console.print(f"  Status: {todo.status}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e.errors()[0]['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status")
) -> None:
    """List all todos."""
    todos = manager.list_todos(status)

    if not todos:
        msg = "No todos found" if not status else f"No todos found with status '{status}'"
        console.print(msg)
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for todo in todos:
        status_colors = {
            "completed": "green",
            "in_progress": "yellow",
            "pending": "white"
        }
        color = status_colors[todo.status]

        table.add_row(
            str(todo.id),
            todo.title,
            f"[{color}]{todo.status}[/{color}]",
            todo.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)


@app.command()
def complete(
    todo_id: int = typer.Argument(..., help="Todo ID")
) -> None:
    """Mark a todo as completed."""
    todo = manager.complete_todo(todo_id)

    if not todo:
        console.print(f"[red]Error:[/red] Todo #{todo_id} not found")
        raise typer.Exit(1)

    console.print(f"[green][OK][/green] Todo #{todo_id} marked as completed: \"{todo.title}\"")


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
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status (pending/in_progress/completed)")
) -> None:
    """Update a todo's fields."""
    # Validate at least one field is provided
    if title is None and description is None and status is None:
        console.print("[red]Error:[/red] At least one field must be provided (--title, --description, or --status)")
        raise typer.Exit(1)

    # Validate status if provided
    if status and status not in ["pending", "in_progress", "completed"]:
        console.print(f"[red]Error:[/red] Invalid status '{status}'. Must be one of: pending, in_progress, completed")
        raise typer.Exit(1)

    try:
        todo = manager.update_todo(todo_id, title=title, description=description, status=status)

        if not todo:
            console.print(f"[red]Error:[/red] Todo #{todo_id} not found")
            raise typer.Exit(1)

        console.print(f"[green][OK][/green] Todo #{todo_id} updated successfully\n")
        console.print(f"  ID: {todo.id}")
        console.print(f"  Title: {todo.title}")
        console.print(f"  Description: {todo.description}")
        console.print(f"  Status: {todo.status}")
        console.print(f"  Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M')}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e.errors()[0]['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
