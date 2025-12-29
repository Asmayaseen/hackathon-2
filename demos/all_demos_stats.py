#!/usr/bin/env python3
"""
All Demos Statistics Dashboard
===============================
Shows overview of all 15 life category demos with task counts and features.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def main():
    console.print()
    console.print(Panel.fit(
        "[bold green]15 LIFE CATEGORIES - DEMO OVERVIEW[/bold green]\n"
        "[dim]Comprehensive Todo Application Use Cases[/dim]",
        border_style="green"
    ))
    console.print()

    # Define all demos with their categories and features
    demos = [
        {
            "id": "01",
            "category": "Prayer Schedule",
            "file": "01_demo_prayer.py",
            "tasks": 5,
            "key_feature": "5 Daily Prayers + Auto-Recurrence",
            "tags": "prayer, fajr, dhuhr, asr, maghrib, isha"
        },
        {
            "id": "02",
            "category": "School Management",
            "file": "02_demo_school.py",
            "tasks": 11,
            "key_feature": "Classes + Homework + Exams",
            "tags": "school, homework, class, exam"
        },
        {
            "id": "03",
            "category": "Ramzan Tracker",
            "file": "03_demo_ramzan.py",
            "tasks": 13,
            "key_feature": "30-Day Sehri/Iftar/Taraweeh",
            "tags": "ramzan, spiritual, sehri, iftar"
        },
        {
            "id": "04",
            "category": "Fitness & Health",
            "file": "04_demo_fitness.py",
            "tasks": 12,
            "key_feature": "Workouts + Nutrition + Sleep",
            "tags": "fitness, workout, health, gym"
        },
        {
            "id": "05",
            "category": "Home Chores",
            "file": "05_demo_chores.py",
            "tasks": 14,
            "key_feature": "Cleaning + Laundry + Shopping",
            "tags": "chores, cleaning, laundry"
        },
        {
            "id": "06",
            "category": "Meal Planning",
            "file": "06_demo_meal.py",
            "tasks": 5,
            "key_feature": "Daily Meals + Meal Prep",
            "tags": "meal, cooking, nutrition"
        },
        {
            "id": "07",
            "category": "Freelance Work",
            "file": "07_demo_freelance.py",
            "tasks": 6,
            "key_feature": "Clients + Invoices + Projects",
            "tags": "freelance, client, invoice"
        },
        {
            "id": "08",
            "category": "Job Hunting",
            "file": "08_demo_jobhunt.py",
            "tasks": 8,
            "key_feature": "Applications + Interviews",
            "tags": "jobhunt, interview, resume"
        },
        {
            "id": "09",
            "category": "Content Creation",
            "file": "09_demo_content.py",
            "tasks": 7,
            "key_feature": "YouTube + Blog + Social Media",
            "tags": "content, youtube, blog"
        },
        {
            "id": "10",
            "category": "Finance",
            "file": "10_demo_finance.py",
            "tasks": 7,
            "key_feature": "Bills + Budget + Savings",
            "tags": "finance, bills, money"
        },
        {
            "id": "11",
            "category": "Learning & Coding",
            "file": "11_demo_learning.py",
            "tasks": 7,
            "key_feature": "LeetCode + Courses + Practice",
            "tags": "learning, coding, education"
        },
        {
            "id": "12",
            "category": "Language Learning",
            "file": "12_demo_language.py",
            "tasks": 7,
            "key_feature": "Duolingo + Vocabulary + Speaking",
            "tags": "language, urdu, duolingo"
        },
        {
            "id": "13",
            "category": "Family & Kids",
            "file": "13_demo_family.py",
            "tasks": 8,
            "key_feature": "Quality Time + Events + Bonding",
            "tags": "family, kids, relationships"
        },
        {
            "id": "14",
            "category": "Self-Care",
            "file": "14_demo_selfcare.py",
            "tasks": 8,
            "key_feature": "Meditation + Journaling + Hobbies",
            "tags": "selfcare, wellness, meditation"
        },
        {
            "id": "15",
            "category": "Events",
            "file": "15_demo_events.py",
            "tasks": 8,
            "key_feature": "Birthdays + Celebrations + Planning",
            "tags": "events, celebration, special"
        },
    ]

    # Create overview table
    table = Table(
        title="[bold cyan]15 Real-World Use Cases[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )
    table.add_column("ID", style="dim", width=4, justify="center")
    table.add_column("Category", style="cyan", width=20)
    table.add_column("Tasks", justify="center", width=6)
    table.add_column("Key Features", style="yellow", width=30)

    total_tasks = 0
    for demo in demos:
        total_tasks += demo["tasks"]
        table.add_row(
            demo["id"],
            demo["category"],
            str(demo["tasks"]),
            demo["key_feature"]
        )

    console.print(table)
    console.print()

    # Statistics summary
    stats_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
    stats_table.add_column("Metric", style="bold cyan")
    stats_table.add_column("Value", justify="right", style="bold green")

    stats_table.add_row("Total Demo Categories", "15")
    stats_table.add_row("Total Example Tasks", str(total_tasks))
    stats_table.add_row("Avg Tasks per Category", f"{total_tasks / len(demos):.1f}")
    stats_table.add_row("Daily Recurring Features", "Present in 10+ demos")
    stats_table.add_row("Weekly Recurring Features", "Present in 8+ demos")
    stats_table.add_row("Monthly Recurring Features", "Present in 5+ demos")

    console.print(stats_table)
    console.print()

    # Usage instructions
    console.print(Panel(
        "[bold]Quick Start - Run Any Demo:[/bold]\n\n"
        "Prayer Schedule:\n"
        "  [cyan]uv run python demos/01_demo_prayer.py[/cyan]\n\n"
        "School Management:\n"
        "  [cyan]uv run python demos/02_demo_school.py[/cyan]\n\n"
        "Ramzan 30-Day Tracker:\n"
        "  [cyan]uv run python demos/03_demo_ramzan.py[/cyan]\n\n"
        "Fitness & Health:\n"
        "  [cyan]uv run python demos/04_demo_fitness.py[/cyan]\n\n"
        "All demos follow the same pattern:\n"
        "  [cyan]uv run python demos/<number>_demo_<category>.py[/cyan]\n\n"
        "[dim]Each demo creates realistic tasks with priorities, tags, due dates, and recurrence patterns.[/dim]",
        title="How to Use Demos",
        border_style="green"
    ))
    console.print()

    # Feature highlights
    console.print(Panel.fit(
        "[bold yellow]Advanced Features Demonstrated:[/bold yellow]\n\n"
        "[OK] Recurring Tasks (Daily/Weekly/Monthly)\n"
        "[OK] Due Dates & Time Reminders (30-min window)\n"
        "[OK] Priority Levels (High/Medium/Low)\n"
        "[OK] Multi-Tag Organization\n"
        "[OK] Search & Filter by Keywords\n"
        "[OK] Sort by Priority/Due Date/Created Date\n"
        "[OK] Auto-completion Creates Next Instance\n"
        "[OK] Overdue Detection & Highlighting",
        border_style="yellow"
    ))
    console.print()

if __name__ == "__main__":
    main()
