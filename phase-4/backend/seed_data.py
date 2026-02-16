"""
Database seeding script for testing dashboard.

Usage:
    python seed_data.py          # Add sample data
    python seed_data.py --clear  # Clear all data first

Creates 3 test users with varied tasks for dashboard testing.
"""
import os
import sys
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment first
load_dotenv()

from sqlmodel import Session, select

# Import after loading env
from db import engine
from models import User, Task


def hash_password(password: str) -> str:
    """Hash password using SHA256 (matching auth.py)."""
    return hashlib.sha256(password.encode()).hexdigest()


def clear_data():
    """Clear all existing tasks and users."""
    print("🗑️  Clearing existing data...")
    with Session(engine) as session:
        # Delete tasks first (foreign key constraint)
        tasks = session.exec(select(Task)).all()
        for task in tasks:
            session.delete(task)

        # Then delete users
        users = session.exec(select(User)).all()
        for user in users:
            session.delete(user)

        session.commit()
    print("✅ Cleared all existing data")


def seed_users():
    """Create test users."""
    print("👥 Creating test users...")

    users_data = [
        {
            "id": "alice-test-id",
            "email": "alice@test.com",
            "name": "Alice Anderson",
            "password": "password123"
        },
        {
            "id": "bob-test-id",
            "email": "bob@test.com",
            "name": "Bob Builder",
            "password": "password123"
        },
        {
            "id": "charlie-test-id",
            "email": "charlie@test.com",
            "name": "Charlie Chen",
            "password": "password123"
        },
    ]

    with Session(engine) as session:
        for user_data in users_data:
            # Check if user already exists
            existing = session.get(User, user_data["id"])
            if existing:
                print(f"   ⏭️  User {user_data['email']} already exists, skipping")
                continue

            user = User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                password_hash=pwd_context.hash(user_data["password"])
            )
            session.add(user)

        session.commit()

    print(f"✅ Created {len(users_data)} test users")
    return [u["id"] for u in users_data]


def seed_tasks(user_id: str):
    """Create varied tasks for a user."""
    print(f"📋 Creating tasks for user: {user_id}")

    now = datetime.utcnow()

    tasks_data = [
        # ============ OVERDUE TASKS (2) ============
        {
            "title": "Submit quarterly report",
            "description": "Q4 2025 performance report for management review",
            "priority": "high",
            "completed": False,
            "due_date": now - timedelta(days=3)
        },
        {
            "title": "Review team budget allocation",
            "description": "Analyze and approve budget requests from team leads",
            "priority": "medium",
            "completed": False,
            "due_date": now - timedelta(days=1)
        },

        # ============ UPCOMING TASKS (3 - next 7 days) ============
        {
            "title": "Weekly standup meeting",
            "description": "Monday morning sync with engineering team",
            "priority": "medium",
            "completed": False,
            "due_date": now + timedelta(days=1)
        },
        {
            "title": "Client presentation preparation",
            "description": "Finalize slides for ABC Corp product demo",
            "priority": "high",
            "completed": False,
            "due_date": now + timedelta(days=3)
        },
        {
            "title": "Code review session",
            "description": "Review PRs for authentication module",
            "priority": "low",
            "completed": False,
            "due_date": now + timedelta(days=5)
        },

        # ============ COMPLETED TASKS (6 - spread over last 7 days) ============
        {
            "title": "Update project documentation",
            "description": "Add API endpoint docs to README",
            "priority": "low",
            "completed": True,
            "due_date": now - timedelta(days=2),
            "updated_at": now - timedelta(days=2)
        },
        {
            "title": "Fix critical login bug",
            "description": "Resolve JWT token expiration issue",
            "priority": "high",
            "completed": True,
            "due_date": now - timedelta(days=4),
            "updated_at": now - timedelta(days=4)
        },
        {
            "title": "Deploy v2.1 to staging",
            "description": "Push latest changes to staging environment",
            "priority": "medium",
            "completed": True,
            "due_date": now - timedelta(days=5),
            "updated_at": now - timedelta(days=5)
        },
        {
            "title": "Write unit tests for auth module",
            "description": "Achieve 80% test coverage",
            "priority": "medium",
            "completed": True,
            "due_date": now - timedelta(days=6),
            "updated_at": now - timedelta(days=6)
        },
        {
            "title": "Refactor API endpoints",
            "description": "Clean up legacy REST endpoints",
            "priority": "low",
            "completed": True,
            "due_date": now - timedelta(days=7),
            "updated_at": now - timedelta(days=7)
        },
        {
            "title": "Database migration to PostgreSQL",
            "description": "Migrate from SQLite to Neon PostgreSQL",
            "priority": "high",
            "completed": True,
            "due_date": now - timedelta(days=8),
            "updated_at": now - timedelta(days=1)
        },

        # ============ FUTURE TASKS (4 - beyond 7 days) ============
        {
            "title": "Plan Q2 2026 OKRs",
            "description": "Define quarterly objectives and key results",
            "priority": "high",
            "completed": False,
            "due_date": now + timedelta(days=14)
        },
        {
            "title": "Organize team building event",
            "description": "Plan offsite activity for engineering team",
            "priority": "low",
            "completed": False,
            "due_date": now + timedelta(days=20)
        },
        {
            "title": "Annual performance review",
            "description": "Complete self-assessment and peer reviews",
            "priority": "medium",
            "completed": False,
            "due_date": now + timedelta(days=30)
        },
        {
            "title": "Tech conference attendance",
            "description": "Register for DevOps Summit 2026",
            "priority": "low",
            "completed": False,
            "due_date": now + timedelta(days=45)
        },

        # ============ NO DUE DATE TASKS (3) ============
        {
            "title": "Read industry blog posts",
            "description": "Stay updated with latest tech trends",
            "priority": "low",
            "completed": False,
            "due_date": None
        },
        {
            "title": "Organize project files",
            "description": "Clean up shared drive and archive old docs",
            "priority": "none",
            "completed": False,
            "due_date": None
        },
        {
            "title": "Update resume and LinkedIn",
            "description": "Add recent projects and achievements",
            "priority": "low",
            "completed": False,
            "due_date": None
        },
    ]

    with Session(engine) as session:
        for task_data in tasks_data:
            task = Task(
                user_id=user_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                priority=task_data["priority"],
                completed=task_data["completed"],
                due_date=task_data.get("due_date"),
                updated_at=task_data.get("updated_at", now)
            )
            session.add(task)

        session.commit()

    print(f"✅ Created {len(tasks_data)} tasks")
    return len(tasks_data)


def print_summary(user_ids):
    """Print summary of seeded data."""
    print("\n" + "="*60)
    print("🎉 DATABASE SEEDING COMPLETE!")
    print("="*60)

    with Session(engine) as session:
        for user_id in user_ids:
            user = session.get(User, user_id)
            if not user:
                continue

            tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
            completed = sum(1 for t in tasks if t.completed)
            pending = len(tasks) - completed

            now = datetime.utcnow()
            overdue = sum(1 for t in tasks if not t.completed and t.due_date and t.due_date < now)
            upcoming = sum(1 for t in tasks if not t.completed and t.due_date and now <= t.due_date <= now + timedelta(days=7))

            print(f"\n📊 User: {user.email}")
            print(f"   Password: password123")
            print(f"   User ID: {user_id}")
            print(f"   Total Tasks: {len(tasks)}")
            print(f"   ├─ ✅ Completed: {completed}")
            print(f"   ├─ ⏳ Pending: {pending}")
            print(f"   ├─ 🚨 Overdue: {overdue}")
            print(f"   └─ 📅 Upcoming (7 days): {upcoming}")

    print("\n🚀 Test Dashboard:")
    print("   1. Start backend: cd phase-4/backend && uvicorn main:app")
    print("   2. Start frontend: cd phase-4/frontend && npm run dev")
    print("   3. Login: http://localhost:3000/auth/signin")
    print("   4. View Dashboard: http://localhost:3000/dashboard")
    print("="*60 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument("--clear", action="store_true", help="Clear existing data first")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("🌱 DASHBOARD DATA SEEDING")
    print("="*60 + "\n")

    # Clear existing data if requested
    if args.clear:
        clear_data()
        print()

    # Create users
    user_ids = seed_users()
    print()

    # Create tasks for first user (Alice)
    if user_ids:
        seed_tasks(user_ids[0])

    # Print summary
    print_summary(user_ids)


if __name__ == "__main__":
    main()
