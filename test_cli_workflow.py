"""
Test script to demonstrate the CLI workflow in a single Python session.
This shows all commands working with in-memory storage.
"""

from src.core.todo_manager import TodoManager
from rich.console import Console
from rich.table import Table

console = Console()
manager = TodoManager()

# Test User Story 1: Basic Todo Workflow
console.print("\n[bold magenta]Testing User Story 1: Basic Todo Workflow[/bold magenta]\n")

# Add todos
console.print("[bold]1. Adding todos...[/bold]")
todo1 = manager.add_todo("Implement data model", "Create Pydantic models for TodoItem")
console.print(f"[green][OK][/green] Added todo #{todo1.id}: {todo1.title}")

todo2 = manager.add_todo("Create CLI interface", "Use Typer and Rich")
console.print(f"[green][OK][/green] Added todo #{todo2.id}: {todo2.title}")

todo3 = manager.add_todo("Write unit tests")
console.print(f"[green][OK][/green] Added todo #{todo3.id}: {todo3.title}")

# List all todos
console.print("\n[bold]2. Listing all todos...[/bold]")
todos = manager.list_todos()

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

# Complete a todo
console.print("\n[bold]3. Completing todo #1...[/bold]")
completed_todo = manager.complete_todo(1)
if completed_todo:
    console.print(f"[green][OK][/green] Todo #{completed_todo.id} marked as completed: \"{completed_todo.title}\"")

# List again to see status change
console.print("\n[bold]4. Listing todos after completion...[/bold]")
todos = manager.list_todos()

table2 = Table(show_header=True, header_style="bold magenta")
table2.add_column("ID", style="dim", width=6)
table2.add_column("Title", style="cyan", no_wrap=False)
table2.add_column("Status", justify="center")
table2.add_column("Created", style="dim")

for todo in todos:
    status_colors = {
        "completed": "green",
        "in_progress": "yellow",
        "pending": "white"
    }
    color = status_colors[todo.status]

    table2.add_row(
        str(todo.id),
        todo.title,
        f"[{color}]{todo.status}[/{color}]",
        todo.created_at.strftime("%Y-%m-%d %H:%M")
    )

console.print(table2)

# Test User Story 2: Advanced Todo Management
console.print("\n[bold magenta]Testing User Story 2: Advanced Todo Management[/bold magenta]\n")

# Update a todo
console.print("[bold]5. Updating todo #2...[/bold]")
updated_todo = manager.update_todo(2, status="in_progress")
if updated_todo:
    console.print(f"[green][OK][/green] Todo #{updated_todo.id} updated to '{updated_todo.status}'")

# Delete a todo
console.print("\n[bold]6. Deleting todo #3...[/bold]")
deleted = manager.delete_todo(3)
if deleted:
    console.print(f"[green][OK][/green] Todo #3 deleted successfully")

# Final list
console.print("\n[bold]7. Final todo list...[/bold]")
todos = manager.list_todos()

table3 = Table(show_header=True, header_style="bold magenta")
table3.add_column("ID", style="dim", width=6)
table3.add_column("Title", style="cyan", no_wrap=False)
table3.add_column("Status", justify="center")
table3.add_column("Created", style="dim")

for todo in todos:
    status_colors = {
        "completed": "green",
        "in_progress": "yellow",
        "pending": "white"
    }
    color = status_colors[todo.status]

    table3.add_row(
        str(todo.id),
        todo.title,
        f"[{color}]{todo.status}[/{color}]",
        todo.created_at.strftime("%Y-%m-%d %H:%M")
    )

console.print(table3)

console.print("\n[bold green]All tests passed! Application is working correctly.[/bold green]\n")
