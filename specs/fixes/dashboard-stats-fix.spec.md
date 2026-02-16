# Dashboard Stats Fix - Feature Specification

**Feature ID**: FIX-DASH-001
**Phase**: Phase 4 (Local Kubernetes)
**Priority**: High
**Status**: Draft
**Date**: 2026-02-07

---

## Problem Statement

The Dashboard page is not displaying statistics correctly. All metrics show as 0 or incorrect values:
- Total Nodes: Not displaying
- Pending Tasks: Not displaying
- Overdue: Not displaying
- Global Completion Status: Shows 0%
- Mission Progress: Empty chart
- Upcoming Actions: Shows 0
- Scheduled: Not working

### Root Cause Analysis

1. **Database Not Initialized**: Backend starts but database tables are not created
   - Missing DATABASE_URL environment variable
   - `create_db_and_tables()` function not executing properly

2. **Field Name Mismatch** (FIXED):
   - Frontend expects: `total`, `pending`, `completed`, `overdue`, `upcoming`
   - Backend was returning: `total_tasks`, `completed_tasks`, etc.
   - ✅ Already fixed in `/phase-4/backend/routes/stats.py`

3. **No Test Data**: Database is empty, so even if APIs work, there's nothing to display

---

## Success Criteria

- [ ] Backend starts with DATABASE_URL configured
- [ ] Database tables are automatically created on startup
- [ ] At least 5-10 sample tasks exist in database for testing
- [ ] Dashboard displays correct statistics:
  - Total Nodes count
  - Pending Tasks count
  - Completed Tasks count
  - Overdue count (tasks past due date)
  - Upcoming count (tasks due in next 7 days)
  - Completion percentage
  - Priority distribution chart
  - 7-day completion history chart

---

## User Stories

### US-DASH-01: View Task Statistics
**As a** user
**I want** to see a summary of my tasks on the dashboard
**So that** I can quickly understand my task status and productivity

**Acceptance Criteria:**
- Total tasks count is displayed
- Pending vs completed breakdown is shown
- Overdue tasks are highlighted in red
- Completion rate is shown as percentage

### US-DASH-02: View Priority Distribution
**As a** user
**I want** to see how my tasks are distributed by priority
**So that** I can understand my workload priorities

**Acceptance Criteria:**
- Priority chart shows: Critical, Standard, Low Trace, Default
- Each priority shows count and percentage
- Visual bars show relative distribution

### US-DASH-03: View Completion History
**As a** user
**I want** to see my task completion trend over the last 7 days
**So that** I can track my productivity over time

**Acceptance Criteria:**
- Bar chart shows last 7 days
- Hover shows exact count for each day
- Visual feedback animates on load

---

## Technical Requirements

### Backend Changes

1. **Environment Configuration** (`phase-4/backend/.env`):
   ```env
   DATABASE_URL=sqlite:///./evolution_todo.db
   JWT_SECRET=your-secret-key-here
   ```

2. **Database Initialization** (No code changes needed):
   - Verify `create_db_and_tables()` is called on startup
   - Ensure all models are imported properly

3. **API Endpoints** (Already implemented):
   ```
   GET /api/{user_id}/stats
   GET /api/{user_id}/stats/completion-history?days=7
   ```

4. **Response Schema**:
   ```json
   {
     "total": 10,
     "completed": 4,
     "pending": 6,
     "overdue": 2,
     "upcoming": 3,
     "completion_rate": 40.0,
     "priority_distribution": {
       "high": 2,
       "medium": 5,
       "low": 2,
       "none": 1
     }
   }
   ```

### Frontend Changes

**No changes needed** - Already implemented correctly.

### Database Seeding

Create seed script to populate test data:

**File**: `phase-4/backend/seed_data.py`

**Requirements**:
- Create 3 test users
- Create 15-20 tasks per user with varied:
  - Priorities (high, medium, low, none)
  - Statuses (completed, pending)
  - Due dates (past, today, future, none)
- Create completion history (spread over last 7 days)

---

## Implementation Plan

### Step 1: Fix Environment Configuration
1. Verify `.env` file exists in `phase-4/backend/`
2. Ensure DATABASE_URL is set
3. Restart backend to trigger table creation

### Step 2: Create Seed Data Script
1. Create `seed_data.py` with sample tasks
2. Run seeding script to populate database
3. Verify data via backend API

### Step 3: Test Dashboard
1. Login to frontend
2. Navigate to dashboard
3. Verify all stats display correctly
4. Test hover interactions
5. Verify charts animate properly

### Step 4: Validate & Document
1. Create test checklist
2. Document any remaining issues
3. Create ADR if architectural changes made

---

## Testing Strategy

### Manual Testing Checklist

**Backend:**
- [ ] Backend starts without errors
- [ ] Database file is created
- [ ] Tables exist in database
- [ ] `/api/{user_id}/stats` returns valid data
- [ ] `/api/{user_id}/stats/completion-history` returns 7 days

**Frontend:**
- [ ] Dashboard loads without errors
- [ ] Total Nodes shows correct count
- [ ] Pending Tasks shows correct count
- [ ] Overdue shows correct count (red badge)
- [ ] Completion percentage is calculated correctly
- [ ] Priority chart displays all 4 categories
- [ ] 7-day history chart displays bars
- [ ] Hover on bars shows exact counts

### API Test Commands

```bash
# Test stats endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/<user_id>/stats

# Test completion history
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/<user_id>/stats/completion-history?days=7
```

---

## Dependencies

- ✅ Backend stats API (already implemented)
- ✅ Frontend dashboard page (already implemented)
- ✅ Field name mapping (already fixed)
- ⏳ DATABASE_URL configuration
- ⏳ Database seeding script
- ⏳ Test data in database

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database not initializing | High | Add startup logging to verify table creation |
| Seed data conflicts with existing data | Medium | Use unique test user IDs |
| Performance with large datasets | Low | Dashboard already uses aggregation queries |

---

## Open Questions

1. Should we keep seed data or clear it for production?
   - **Decision**: Add `--clear` flag to seed script for optional cleanup

2. Should completion history use `completed_at` or `updated_at`?
   - **Current**: Uses `updated_at` (already implemented)
   - **Better**: Should add `completed_at` field in future

---

## References

- Backend Stats API: `phase-4/backend/routes/stats.py`
- Frontend Dashboard: `phase-4/frontend/src/app/dashboard/page.tsx`
- Database Models: `phase-4/backend/models.py`
- Constitution: `.specify/memory/constitution.md`

---

**Next Steps**: Create implementation plan → Create tasks → Execute fixes
