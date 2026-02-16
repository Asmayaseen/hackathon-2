# Dashboard Stats Fix - Implementation Tasks

**Spec**: `dashboard-stats-fix.spec.md`
**Plan**: `dashboard-stats-fix.plan.md`
**Phase**: Phase 4
**Date**: 2026-02-07

---

## Task Breakdown

### ✅ TASK-DASH-001: Fix Backend Field Names
**Status**: COMPLETED
**Priority**: High
**Estimate**: 10 minutes

**Description**:
Update backend stats API to return field names matching frontend expectations.

**Implementation**:
- [x] Update `phase-4/backend/routes/stats.py` line 47-54 (empty data case)
- [x] Update `phase-4/backend/routes/stats.py` line 72-79 (data return)
- [x] Change `total_tasks` → `total`
- [x] Change `completed_tasks` → `completed`
- [x] Add `pending` field (total - completed)
- [x] Change `overdue_count` → `overdue`
- [x] Change `upcoming_count` → `upcoming`

**Test Cases**:
- [x] API returns correct field names
- [x] Frontend receives expected data structure

**Files Modified**:
- `phase-4/backend/routes/stats.py`

---

### ⏳ TASK-DASH-002: Configure Environment Variables
**Status**: PENDING
**Priority**: High
**Estimate**: 5 minutes

**Description**:
Ensure `.env` file exists with proper DATABASE_URL configuration.

**Implementation Steps**:
1. Check if `phase-4/backend/.env` exists
2. If missing, copy from `.env.example`
3. Set DATABASE_URL to `sqlite:///./evolution_todo.db`
4. Set JWT_SECRET to secure random value
5. Verify file is loaded on backend startup

**Acceptance Criteria**:
- [ ] `.env` file exists in `phase-4/backend/`
- [ ] DATABASE_URL is set correctly
- [ ] JWT_SECRET is non-default value
- [ ] Backend logs show environment loaded

**Test Commands**:
```bash
# Check .env exists
ls -la phase-4/backend/.env

# Verify DATABASE_URL
grep DATABASE_URL phase-4/backend/.env

# Test backend startup
cd phase-4/backend && python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"
```

**Files Modified**:
- `phase-4/backend/.env` (create/update)

---

### ⏳ TASK-DASH-003: Create Database Seed Script
**Status**: PENDING
**Priority**: High
**Estimate**: 30 minutes

**Description**:
Create script to populate database with realistic test data.

**Implementation**:
Create `phase-4/backend/seed_data.py` with:

```python
"""
Database seeding script for testing dashboard.
Usage: python seed_data.py [--clear]
"""
import os
import sys
from datetime import datetime, timedelta
from sqlmodel import Session, select
from passlib.context import CryptContext

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import engine
from models import User, Task

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def clear_data():
    """Clear all existing data."""
    with Session(engine) as session:
        session.query(Task).delete()
        session.query(User).delete()
        session.commit()
    print("✅ Cleared existing data")

def seed_users():
    """Create test users."""
    users = [
        {"id": "alice-test-id", "email": "alice@test.com", "name": "Alice Anderson", "password": "password123"},
        {"id": "bob-test-id", "email": "bob@test.com", "name": "Bob Builder", "password": "password123"},
        {"id": "charlie-test-id", "email": "charlie@test.com", "name": "Charlie Chen", "password": "password123"},
    ]

    with Session(engine) as session:
        for user_data in users:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                password_hash=pwd_context.hash(user_data["password"])
            )
            session.add(user)
        session.commit()
    print(f"✅ Created {len(users)} test users")
    return [u["id"] for u in users]

def seed_tasks(user_id: str):
    """Create varied tasks for a user."""
    now = datetime.utcnow()

    tasks = [
        # OVERDUE TASKS (2)
        {"title": "Submit quarterly report", "priority": "high", "completed": False, "due_date": now - timedelta(days=3)},
        {"title": "Review team budget", "priority": "medium", "completed": False, "due_date": now - timedelta(days=1)},

        # UPCOMING TASKS (3 - next 7 days)
        {"title": "Weekly standup meeting", "priority": "medium", "completed": False, "due_date": now + timedelta(days=1)},
        {"title": "Client presentation prep", "priority": "high", "completed": False, "due_date": now + timedelta(days=3)},
        {"title": "Code review session", "priority": "low", "completed": False, "due_date": now + timedelta(days=5)},

        # COMPLETED TASKS (6)
        {"title": "Update project documentation", "priority": "low", "completed": True, "due_date": now - timedelta(days=2), "completed_at": now - timedelta(days=2)},
        {"title": "Fix login bug", "priority": "high", "completed": True, "due_date": now - timedelta(days=4), "completed_at": now - timedelta(days=4)},
        {"title": "Deploy to staging", "priority": "medium", "completed": True, "due_date": now - timedelta(days=5), "completed_at": now - timedelta(days=5)},
        {"title": "Write unit tests", "priority": "medium", "completed": True, "due_date": now - timedelta(days=6), "completed_at": now - timedelta(days=6)},
        {"title": "Refactor API endpoints", "priority": "low", "completed": True, "due_date": now - timedelta(days=7), "completed_at": now - timedelta(days=7)},
        {"title": "Database migration", "priority": "high", "completed": True, "due_date": now - timedelta(days=8), "completed_at": now - timedelta(days=1)},

        # FUTURE TASKS (4 - beyond 7 days)
        {"title": "Plan Q2 OKRs", "priority": "high", "completed": False, "due_date": now + timedelta(days=14)},
        {"title": "Team building event", "priority": "low", "completed": False, "due_date": now + timedelta(days=20)},
        {"title": "Annual performance review", "priority": "medium", "completed": False, "due_date": now + timedelta(days=30)},

        # NO DUE DATE TASKS (3)
        {"title": "Read industry blog posts", "priority": "low", "completed": False, "due_date": None},
        {"title": "Organize project files", "priority": "none", "completed": False, "due_date": None},
        {"title": "Update resume", "priority": "low", "completed": False, "due_date": None},
    ]

    with Session(engine) as session:
        for task_data in tasks:
            task = Task(
                user_id=user_id,
                title=task_data["title"],
                description=f"Test task: {task_data['title']}",
                priority=task_data["priority"],
                completed=task_data["completed"],
                due_date=task_data.get("due_date"),
                updated_at=task_data.get("completed_at", now)
            )
            session.add(task)
        session.commit()
    print(f"✅ Created {len(tasks)} tasks for user {user_id}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument("--clear", action="store_true", help="Clear existing data first")
    args = parser.parse_args()

    print("🌱 Seeding database...")

    if args.clear:
        clear_data()

    # Create users
    user_ids = seed_users()

    # Create tasks for first user (alice)
    seed_tasks(user_ids[0])

    print("✅ Database seeding complete!")
    print(f"   Test user: alice@test.com / password123")
    print(f"   User ID: {user_ids[0]}")
    print(f"   Total tasks: 18 (6 completed, 2 overdue, 3 upcoming)")

if __name__ == "__main__":
    main()
```

**Acceptance Criteria**:
- [ ] Script creates 3 test users
- [ ] Script creates 18 tasks with varied states:
  - 2 overdue (past due, not completed)
  - 3 upcoming (next 7 days, not completed)
  - 6 completed (spread over last 7 days)
  - 4 future (beyond 7 days)
  - 3 no due date
- [ ] Script supports `--clear` flag to wipe existing data
- [ ] Script prints summary on completion

**Test Commands**:
```bash
# Run seeding
cd phase-4/backend
python seed_data.py --clear

# Verify data created
python -c "
from sqlmodel import Session, select
from db import engine
from models import Task
with Session(engine) as session:
    count = len(session.exec(select(Task)).all())
    print(f'Tasks in DB: {count}')
"
```

**Files Created**:
- `phase-4/backend/seed_data.py`

---

### ⏳ TASK-DASH-004: Verify Database Initialization
**Status**: PENDING
**Priority**: High
**Estimate**: 10 minutes

**Description**:
Ensure database tables are created automatically on backend startup.

**Implementation Steps**:
1. Kill existing backend process
2. Delete existing database file (if corrupt)
3. Start backend with proper environment
4. Verify tables created
5. Check startup logs

**Acceptance Criteria**:
- [ ] Backend starts without errors
- [ ] Database file is created
- [ ] All tables exist (users, tasks, user_preferences, etc.)
- [ ] Startup logs show "Database tables created/verified"

**Test Commands**:
```bash
# Clean start
cd phase-4/backend
pkill -f uvicorn
rm evolution_todo.db  # Optional: only if corrupted
source .env  # Or: export $(cat .env | xargs)
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# In another terminal, verify tables
python -c "
import sqlite3
conn = sqlite3.connect('evolution_todo.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
tables = [t[0] for t in cursor.fetchall()]
print('Tables:', tables)
assert 'tasks' in tables
assert 'users' in tables
print('✅ All tables exist')
"
```

**Files Checked**:
- `phase-4/backend/main.py` (startup event)
- `phase-4/backend/db.py` (create_db_and_tables)

---

### ⏳ TASK-DASH-005: End-to-End Dashboard Testing
**Status**: PENDING
**Priority**: High
**Estimate**: 20 minutes

**Description**:
Manually test complete dashboard flow with real data.

**Test Procedure**:

1. **Prepare Environment**:
   ```bash
   # Terminal 1: Backend
   cd phase-4/backend
   python seed_data.py --clear
   python -m uvicorn main:app --port 8000

   # Terminal 2: Frontend
   cd phase-4/frontend
   npm run dev
   ```

2. **Login**:
   - Navigate to http://localhost:3000/auth/signin
   - Email: `alice@test.com`
   - Password: `password123`

3. **Test Dashboard** (http://localhost:3000/dashboard):
   - [ ] Total Nodes shows 18
   - [ ] Pending Tasks shows 12 (18 - 6 completed)
   - [ ] Success Rate shows ~33.3% (6/18)
   - [ ] Overdue badge shows 2 (red)
   - [ ] Priority Matrix displays:
     - Critical (high): 4 tasks
     - Standard (medium): 6 tasks
     - Low Trace (low): 6 tasks
     - Default (none): 2 tasks
   - [ ] Upcoming Actions shows 3 scheduled
   - [ ] 7-day completion chart shows bars
   - [ ] Hover on bars shows tooltips

4. **Test Responsiveness**:
   - [ ] Resize browser window
   - [ ] Test on mobile viewport (DevTools)
   - [ ] Charts remain readable

5. **Console Check**:
   - [ ] No errors in browser console
   - [ ] No errors in backend logs

**Acceptance Criteria**:
- [ ] All metrics display correct values
- [ ] Charts render properly
- [ ] No console errors
- [ ] Page loads within 2 seconds
- [ ] Animations work smoothly

**Screenshot Locations**:
- Save screenshots to `phase-4/docs/dashboard-working.png`

---

### ⏳ TASK-DASH-006: Documentation & Cleanup
**Status**: PENDING
**Priority**: Medium
**Estimate**: 15 minutes

**Description**:
Document the fix and clean up any temporary files.

**Implementation Steps**:
1. Create `DASHBOARD_FIX_SUMMARY.md` with:
   - Problem description
   - Root cause
   - Solution applied
   - Testing results
   - Future improvements

2. Update `phase-4/README.md`:
   - Add section on dashboard testing
   - Document seed data usage
   - Add troubleshooting tips

3. Clean up:
   - Remove any test files
   - Ensure .env is in .gitignore
   - Remove debug console.logs

**Acceptance Criteria**:
- [ ] Summary document created
- [ ] README updated
- [ ] No sensitive data in repo
- [ ] Clean git status

**Files Modified**:
- `phase-4/DASHBOARD_FIX_SUMMARY.md` (new)
- `phase-4/README.md` (update)
- `.gitignore` (verify)

---

## Execution Order

```
TASK-DASH-001 (DONE) → TASK-DASH-002 → TASK-DASH-003 → TASK-DASH-004 → TASK-DASH-005 → TASK-DASH-006
```

**Critical Path**: 001 → 002 → 003 → 004 → 005
**Parallel Possible**: 006 can be done anytime after 005

---

## Progress Tracking

| Task ID | Status | Assignee | Completed |
|---------|--------|----------|-----------|
| TASK-DASH-001 | ✅ DONE | Claude | 2026-02-07 |
| TASK-DASH-002 | ⏳ PENDING | - | - |
| TASK-DASH-003 | ⏳ PENDING | - | - |
| TASK-DASH-004 | ⏳ PENDING | - | - |
| TASK-DASH-005 | ⏳ PENDING | - | - |
| TASK-DASH-006 | ⏳ PENDING | - | - |

**Overall Progress**: 1/6 tasks complete (16.7%)

---

## References

- Spec: `dashboard-stats-fix.spec.md`
- Plan: `dashboard-stats-fix.plan.md`
- Backend Stats API: `phase-4/backend/routes/stats.py`
- Frontend Dashboard: `phase-4/frontend/src/app/dashboard/page.tsx`

---

**Ready to execute!** Start with TASK-DASH-002.
