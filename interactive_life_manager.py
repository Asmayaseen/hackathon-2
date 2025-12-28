#!/usr/bin/env python3
"""
Interactive Life Manager - 15 Category Selector
================================================
Transform todo app into comprehensive life management system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.todo_manager import TodoManager
from src.core.presets import LifePresets
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()


def print_header():
    """Display Life Manager header."""
    console.print()
    console.print(Panel.fit(
        "[bold green]LIFE MANAGER - 15 CATEGORIES[/bold green]\n"
        "[dim]Your Complete Personal Organization System[/dim]",
        border_style="green"
    ))
    console.print()


def load_category(tm: TodoManager, category_key: str) -> int:
    """Load all tasks for a specific category."""
    tasks = LifePresets.get_category_tasks(category_key)
    count = 0

    for task_data in tasks:
        # Set smart due dates for tasks
        due_date = None
        if task_data.get("recurrence_pattern") == "daily":
            due_date = LifePresets.get_smart_due_date(hours_offset=2)
        elif task_data.get("recurrence_pattern") == "weekly":
            due_date = LifePresets.get_smart_due_date(hours_offset=24)
        elif task_data.get("recurrence_pattern") == "monthly":
            due_date = LifePresets.get_smart_due_date(hours_offset=24 * 7)
        else:
            due_date = LifePresets.get_smart_due_date(hours_offset=6)

        tm.add_todo(
            title=task_data["title"],
            description=task_data.get("description", ""),
            priority=task_data.get("priority", "medium"),
            tags=task_data.get("tags", []),
            due_date=due_date,
            recurrence_pattern=task_data.get("recurrence_pattern")
        )
        count += 1

    return count


def load_all_categories(tm: TodoManager) -> int:
    """Load all 15 categories at once."""
    total = 0
    for category_key in LifePresets.get_all_category_keys():
        total += load_category(tm, category_key)
    return total


def show_stats(tm: TodoManager) -> None:
    """Show category-wise completion statistics."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]CATEGORY-WISE PROGRESS[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    stats_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    stats_table.add_column("Category", style="cyan", width=20)
    stats_table.add_column("Total", justify="center", width=8)
    stats_table.add_column("Completed", justify="center", width=10)
    stats_table.add_column("Pending", justify="center", width=8)
    stats_table.add_column("Progress", justify="center", width=12)

    all_tasks = tm.list_todos()

    for category_key, category_name in LifePresets.CATEGORY_NAMES.items():
        # Get tasks for this category
        category_tasks = [t for t in all_tasks if category_key in [tag.lower() for tag in t.tags]]

        if category_tasks:
            total = len(category_tasks)
            completed = len([t for t in category_tasks if t.status == "completed"])
            pending = total - completed
            progress = (completed / total * 100) if total > 0 else 0

            progress_bar = f"{progress:.0f}%"
            if progress >= 75:
                progress_display = f"[green]{progress_bar}[/green]"
            elif progress >= 50:
                progress_display = f"[yellow]{progress_bar}[/yellow]"
            else:
                progress_display = f"[red]{progress_bar}[/red]"

            stats_table.add_row(
                category_name,
                str(total),
                f"[green]{completed}[/green]",
                f"[yellow]{pending}[/yellow]",
                progress_display
            )

    console.print(stats_table)

    # Overall summary
    total_tasks = len(all_tasks)
    total_completed = len([t for t in all_tasks if t.status == "completed"])
    total_pending = total_tasks - total_completed
    overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0

    console.print()
    console.print(f"[bold]Overall Progress:[/bold] {total_completed}/{total_tasks} tasks completed ([cyan]{overall_progress:.1f}%[/cyan])")
    console.print()


def print_tasks_formatted(tm: TodoManager) -> None:
    """Display all tasks in formatted table."""
    tasks = tm.list_todos()

    if not tasks:
        console.print("[yellow]No tasks found. Load a category first![/yellow]\n")
        return

    table = Table(title="All Tasks", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=4, justify="center")
    table.add_column("Title", style="cyan", width=30)
    table.add_column("Category", style="yellow", width=12)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Recurrence", justify="center", width=10)

    for task in tasks[:50]:  # Show first 50 tasks
        # Determine category from tags
        category = "general"
        for tag in task.tags:
            if tag.lower() in LifePresets.ALL_CATEGORIES:
                category = tag.lower()
                break

        category_name = LifePresets.CATEGORY_NAMES.get(category, category.title())

        # Priority display
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority_display = f"[{priority_colors[task.priority]}]{task.priority.upper()}[/{priority_colors[task.priority]}]"

        # Status display
        status_colors = {"completed": "green", "in_progress": "yellow", "pending": "white"}
        status_display = f"[{status_colors[task.status]}]{task.status}[/{status_colors[task.status]}]"

        # Recurrence
        recurrence = task.recurrence_pattern.upper() if task.recurrence_pattern else "-"

        table.add_row(
            str(task.id),
            task.title[:28] + "..." if len(task.title) > 28 else task.title,
            category_name[:10] + "..." if len(category_name) > 10 else category_name,
            priority_display,
            status_display,
            f"[cyan]{recurrence}[/cyan]" if recurrence != "-" else "[dim]-[/dim]"
        )

    console.print(table)

    if len(tasks) > 50:
        console.print(f"\n[dim]Showing first 50 of {len(tasks)} tasks[/dim]")

    console.print()


def show_category_menu() -> None:
    """Display the 15 category selection menu."""
    table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
    table.add_column("Option", style="bold cyan", justify="center", width=6)
    table.add_column("Category", style="white", width=25)
    table.add_column("Description", style="dim", width=35)

    categories = [
        ("1", "Prayer Schedule", "5 daily prayers with reminders"),
        ("2", "School Management", "Classes, homework, exams"),
        ("3", "Ramzan Tracker", "Sehri, Iftar, Taraweeh, Quran"),
        ("4", "Fitness & Health", "Workouts, nutrition, wellness"),
        ("5", "Home Chores", "Cleaning, laundry, shopping"),
        ("6", "Meal Planning", "Daily meals and meal prep"),
        ("7", "Freelance Work", "Clients, invoices, projects"),
        ("8", "Job Hunting", "Applications, interviews"),
        ("9", "Content Creation", "YouTube, blogging, social media"),
        ("10", "Finance", "Bills, budgets, savings"),
        ("11", "Learning & Coding", "LeetCode, courses, practice"),
        ("12", "Language Learning", "Duolingo, vocabulary, speaking"),
        ("13", "Family & Kids", "Quality time, events, bonding"),
        ("14", "Self-Care", "Meditation, journaling, hobbies"),
        ("15", "Events & Occasions", "Birthdays, celebrations"),
    ]

    for option, name, desc in categories:
        table.add_row(option, name, desc)

    table.add_row("", "", "")
    table.add_row("0", "[bold green]Load ALL Categories[/bold green]", "[bold]126 tasks across 15 areas[/bold]")
    table.add_row("", "", "")
    table.add_row("S", "Show Stats", "Category-wise progress dashboard")
    table.add_row("L", "List Tasks", "View all loaded tasks")
    table.add_row("Q", "Quit", "Exit Life Manager")

    console.print(table)


def main():
    """Main interactive Life Manager loop."""
    tm = TodoManager()

    print_header()

    # Category key mapping
    category_map = {
        "1": "prayer",
        "2": "school",
        "3": "ramzan",
        "4": "fitness",
        "5": "chores",
        "6": "meal",
        "7": "freelance",
        "8": "jobhunt",
        "9": "content",
        "10": "finance",
        "11": "learning",
        "12": "language",
        "13": "family",
        "14": "selfcare",
        "15": "events",
    }

    while True:
        show_category_menu()
        console.print()

        choice = Prompt.ask(
            "[bold cyan]Select a category[/bold cyan]",
            default="Q"
        ).strip().upper()

        if choice == "Q":
            console.print("\n[bold cyan]Thank you for using Life Manager![/bold cyan]\n")
            break

        elif choice == "0":
            console.print("\n[bold yellow]Loading ALL 15 categories...[/bold yellow]\n")
            count = load_all_categories(tm)
            console.print(f"\n[bold green][OK] Successfully loaded {count} tasks across 15 categories![/bold green]\n")
            console.print("[dim]Tip: Use 'L' to list all tasks or 'S' to see progress dashboard[/dim]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")

        elif choice in category_map:
            category_key = category_map[choice]
            category_name = LifePresets.CATEGORY_NAMES[category_key]

            console.print(f"\n[bold yellow]Loading {category_name}...[/bold yellow]\n")
            count = load_category(tm, category_key)
            console.print(f"\n[bold green][OK] Successfully loaded {count} {category_name} tasks![/bold green]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")

        elif choice == "S":
            show_stats(tm)
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")

        elif choice == "L":
            console.print()
            print_tasks_formatted(tm)
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")

        else:
            console.print("\n[bold red]Invalid choice! Please select a valid option.[/bold red]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye![/bold cyan]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
