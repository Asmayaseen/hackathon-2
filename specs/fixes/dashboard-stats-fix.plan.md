# Dashboard Stats Fix - Implementation Plan

**Spec Reference**: `dashboard-stats-fix.spec.md`
**Phase**: Phase 4
**Date**: 2026-02-07

---

## Architecture Overview

```
┌─────────────┐      HTTP       ┌──────────────┐      SQL       ┌──────────┐
│   Browser   │ ────────────▶   │   Backend    │ ───────────▶   │ SQLite   │
│  Dashboard  │                 │  Stats API   │                │    DB    │
└─────────────┘                 └──────────────┘                └──────────┘
      │                                │                              │
      │  GET /api/{user}/stats         │  SELECT ... FROM tasks       │
      │  GET /api/{user}/stats/history │  GROUP BY completed_at       │
      │                                │                              │
      │◀────── JSON response ──────────│◀─────── Query results ───────│
```

---

## Key Design Decisions

### Decision 1: Database Initialization Strategy

**Options Considered:**
1. Manual SQL script execution
2. Automatic on startup (current)
3. Migration tool (Alembic)

**Chosen**: Automatic on startup
**Rationale**: Simplest for Phase 4 local development. Alembic adds complexity unnecessary for hackathon.

**Trade-offs**:
- ✅ Pro: Zero-config for developers
- ✅ Pro: Tables always in sync with models
- ❌ Con: No migration history
- ❌ Con: Difficult to rollback schema changes

### Decision 2: Seed Data Approach

**Options Considered:**
1. Hardcoded in seed script
2. Random faker-generated data
3. Import from JSON fixture

**Chosen**: Hardcoded realistic data
**Rationale**: Deterministic, easy to debug, matches demo scenarios.

**Trade-offs**:
- ✅ Pro: Predictable test data
- ✅ Pro: Can craft specific edge cases (overdue, upcoming, etc.)
- ❌ Con: Not scalable for load testing
- ❌ Con: Requires manual updates

### Decision 3: Environment Variable Handling

**Options Considered:**
1. Require .env file (fail if missing)
2. Default to sqlite:// with warning
3. Use dotenv auto-loading

**Chosen**: Default to local sqlite with warning
**Rationale**: Fail-safe for development, explicit for production.

**Implementation**:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evolution_todo.db")
if not os.getenv("DATABASE_URL"):
    logger.warning("DATABASE_URL not set, using local SQLite")
```

---

## Component Design

### 1. Environment Configuration

**File**: `phase-4/backend/.env`

**Schema**:
```env
# Database
DATABASE_URL=sqlite:///./evolution_todo.db

# Authentication
JWT_SECRET=your-secret-key-change-in-production

# Optional
LOG_LEVEL=INFO
```

**Validation**:
- Check file exists on backend startup
- Warn if JWT_SECRET is default value
- Log final DATABASE_URL (without credentials)

### 2. Database Seeding Script

**File**: `phase-4/backend/seed_data.py`

**Function Signature**:
```python
def seed_database(clear_existing: bool = False):
    """
    Populate database with sample tasks for testing.

    Args:
        clear_existing: If True, delete all existing tasks first

    Creates:
        - 3 test users (alice@test.com, bob@test.com, charlie@test.com)
        - 20 tasks per user with varied:
            - Priorities: 30% high, 30% medium, 20% low, 20% none
            - Status: 40% completed, 60% pending
            - Due dates: 20% overdue, 30% next 7 days, 30% future, 20% none
        - Completion history spread over last 7 days
    """
```

**Data Distribution**:
```python
SAMPLE_TASKS = [
    # Overdue tasks (past due, not completed)
    {"title": "Submit quarterly report", "priority": "high", "due_date": now - 3 days},
    {"title": "Review team budget", "priority": "medium", "due_date": now - 1 day},

    # Upcoming tasks (next 7 days, not completed)
    {"title": "Weekly standup", "priority": "medium", "due_date": now + 1 day},
    {"title": "Client presentation", "priority": "high", "due_date": now + 3 days},

    # Completed tasks (for completion rate)
    {"title": "Update documentation", "priority": "low", "completed": True, "completed_at": now - 2 days},

    # Future tasks (beyond 7 days)
    {"title": "Plan Q2 goals", "priority": "high", "due_date": now + 14 days},

    # No due date tasks
    {"title": "Read industry news", "priority": "low", "due_date": None},
]
```

### 3. Backend Startup Sequence

**File**: `phase-4/backend/main.py`

**Startup Flow**:
```python
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Starting Evolution Todo API...")

    # 1. Load environment
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "sqlite:///./evolution_todo.db")
    logger.info(f"📊 Database: {db_url.split('@')[-1]}")  # Hide credentials

    # 2. Create tables
    try:
        create_db_and_tables()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # 3. Check if seeding needed (optional)
    with Session(engine) as session:
        task_count = session.query(func.count(Task.id)).scalar()
        if task_count == 0:
            logger.warning("⚠️ Database is empty. Run: python seed_data.py")
```

### 4. Stats API Enhancement

**File**: `phase-4/backend/routes/stats.py`

**Already Implemented** ✅

**Response Caching** (Future Enhancement):
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_cached_stats(user_id: str, cache_key: str):
    # Cache stats for 5 minutes
    pass
```

---

## Data Flow

### Stats Retrieval Flow

```
1. User loads dashboard
   └─▶ Frontend: useEffect() triggers API calls

2. Frontend makes parallel requests:
   ├─▶ GET /api/{user_id}/stats
   └─▶ GET /api/{user_id}/stats/completion-history?days=7

3. Backend (stats.py):
   ├─▶ Verify JWT token (middleware)
   ├─▶ SELECT * FROM tasks WHERE user_id = ?
   ├─▶ Aggregate counts (total, completed, pending, overdue, upcoming)
   ├─▶ Group by priority
   └─▶ Return JSON

4. Backend (completion-history):
   ├─▶ Loop last 7 days
   ├─▶ SELECT COUNT(*) WHERE completed=true AND DATE(updated_at) = ?
   └─▶ Return array of {date, completed}

5. Frontend updates state:
   ├─▶ setStats(statsData)
   ├─▶ setCompletionHistory(historyData)
   └─▶ Re-render dashboard with real data
```

---

## Error Handling

### Backend Errors

| Error | Cause | Response | HTTP Code |
|-------|-------|----------|-----------|
| Database connection failed | DATABASE_URL invalid | `{"detail": "Database unavailable"}` | 503 |
| User not found | Invalid user_id | `{"detail": "User not found"}` | 404 |
| Unauthorized | Missing/invalid token | `{"detail": "Unauthorized"}` | 401 |
| Query timeout | Large dataset | `{"detail": "Query timeout"}` | 504 |

### Frontend Fallbacks

```typescript
// If API fails, show graceful fallback
const data = stats || {
  total: 0,
  pending: 0,
  completed: 0,
  overdue: 0,
  upcoming: 0,
  completion_rate: 0,
  priority_distribution: { high: 0, medium: 0, low: 0, none: 0 }
};

// Show user-friendly error message
if (error) {
  return <DashboardError message="Unable to load stats. Please refresh." />;
}
```

---

## Testing Strategy

### Unit Tests (Optional for Phase 4)

```python
# tests/test_stats.py
def test_stats_empty_database():
    """Stats should return zeros for new user"""
    response = client.get("/api/test-user/stats")
    assert response.json()["total"] == 0

def test_stats_with_tasks():
    """Stats should calculate correctly"""
    # Create 10 tasks (4 completed, 6 pending)
    response = client.get("/api/test-user/stats")
    data = response.json()
    assert data["total"] == 10
    assert data["completed"] == 4
    assert data["completion_rate"] == 40.0
```

### Integration Testing

**Manual Test Script**:
```bash
#!/bin/bash
# test-dashboard.sh

echo "1. Starting backend..."
cd phase-4/backend && python -m uvicorn main:app &
sleep 5

echo "2. Seeding database..."
python seed_data.py

echo "3. Testing stats API..."
curl -H "Authorization: Bearer $(cat /tmp/test-token.txt)" \
  http://localhost:8000/api/alice-test-id/stats

echo "4. Starting frontend..."
cd ../frontend && npm run dev &
sleep 10

echo "5. Open browser: http://localhost:3000/dashboard"
```

---

## Performance Considerations

### Database Queries

**Current**:
```sql
-- Single query fetches all tasks
SELECT * FROM tasks WHERE user_id = 'alice'
-- Then aggregates in Python
```

**Optimized** (Future):
```sql
-- Use database aggregation
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN due_date < NOW() AND NOT completed THEN 1 ELSE 0 END) as overdue
FROM tasks
WHERE user_id = 'alice'
```

**Trade-off**: Current approach works fine for < 1000 tasks per user (Phase 4 scope).

---

## Deployment Checklist

- [ ] `.env` file exists with DATABASE_URL
- [ ] Backend starts without errors
- [ ] Tables created in database
- [ ] Seed script executed successfully
- [ ] Stats API returns valid JSON
- [ ] Completion history returns 7 days
- [ ] Frontend dashboard displays all metrics
- [ ] Priority chart renders correctly
- [ ] Completion history chart animates
- [ ] No console errors in browser

---

## Rollback Plan

If dashboard fix fails:

1. **Revert backend changes**:
   ```bash
   git checkout phase-4/backend/routes/stats.py
   ```

2. **Remove seed data**:
   ```bash
   rm phase-4/backend/evolution_todo.db
   ```

3. **Restart services**:
   ```bash
   # Backend will recreate empty DB
   ```

4. **Show user message**:
   "Dashboard temporarily unavailable. Task management still functional."

---

## Future Enhancements (Phase 5+)

1. **Real-time Updates**: WebSocket for live dashboard refresh
2. **Advanced Analytics**: Task velocity, burndown charts, time tracking
3. **Caching Layer**: Redis for stats caching
4. **Database Optimization**: Add indexes, use materialized views
5. **Export Feature**: Download dashboard as PDF report

---

## References

- Spec: `dashboard-stats-fix.spec.md`
- Backend API: `phase-4/backend/routes/stats.py`
- Frontend: `phase-4/frontend/src/app/dashboard/page.tsx`
- Models: `phase-4/backend/models.py`
- Constitution: `.specify/memory/constitution.md` (Principle I: Spec-Driven Development)

---

**Status**: Ready for implementation
**Estimated Effort**: 1-2 hours
**Risk Level**: Low (mostly configuration + data seeding)
