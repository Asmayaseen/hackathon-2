# Implementation Plan: Dashboard - Task Management Interface

**Branch**: `1-dashboard` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-dashboard/spec.md`

## Summary

Build a comprehensive task management dashboard for authenticated users with statistics display (total/pending/completed), progress visualization, task CRUD operations (add, view, edit, delete, complete), status filtering, and glassmorphism dark theme UI. Leverages existing backend API endpoints and extends current frontend components.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.13+ (Backend - existing)
**Primary Dependencies**: Next.js 16+ (App Router), React 19, Tailwind CSS, Axios
**Storage**: Neon PostgreSQL (via existing SQLModel backend)
**Testing**: Manual testing per acceptance scenarios (TDD not required for Phase II)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (monorepo with frontend/ and backend/)
**Performance Goals**: Page load <2s, API response <500ms, filter switch <1s
**Constraints**: JWT auth required, mobile-responsive (320px+), glassmorphism design
**Scale/Scope**: Single user dashboard, ~100 tasks max typical usage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Following specify → plan → tasks → implement workflow |
| II. Phased Evolution | PASS | Phase II feature, building on existing auth/API |
| III. Technology Stack | PASS | Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, JWT |
| IV. Independent User Stories | PASS | 8 prioritized stories with acceptance criteria |
| V. TDD (Conditional) | N/A | Tests not explicitly required in spec |
| VI. Stateless Architecture | PASS | All state persisted to Neon DB, localStorage for auth only |
| VII. Documentation | PASS | Spec, plan, tasks will be created |

**Gate Result**: PASS - No violations, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/1-dashboard/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── dashboard-api.yaml
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app entry (EXISTS)
├── models.py            # SQLModel entities (EXISTS)
├── db.py                # Database connection (EXISTS)
├── routes/
│   ├── auth.py          # Auth endpoints (EXISTS)
│   └── tasks.py         # Task CRUD endpoints (EXISTS)
└── middleware/
    └── auth.py          # JWT verification (EXISTS)

frontend/
├── app/
│   ├── page.tsx         # Landing page (EXISTS)
│   ├── tasks/
│   │   └── page.tsx     # Dashboard page (TO ENHANCE)
│   └── auth/
│       ├── signin/      # Sign in (EXISTS)
│       └── signup/      # Sign up (EXISTS)
├── components/
│   ├── TaskForm.tsx     # Add task form (EXISTS - TO ENHANCE)
│   ├── TaskList.tsx     # Task list (EXISTS - TO ENHANCE)
│   ├── TaskItem.tsx     # Task card (EXISTS - TO ENHANCE)
│   ├── StatsCard.tsx    # Statistics card (NEW)
│   └── ProgressBar.tsx  # Progress indicator (NEW)
├── lib/
│   └── api.ts           # API client (EXISTS)
└── globals.css          # Glassmorphism styles (EXISTS)
```

**Structure Decision**: Web application with existing monorepo structure. Backend API is complete; focus is on frontend dashboard enhancement.

## Complexity Tracking

> No violations - no complexity justification required.

---

## Phase 0: Research & Resolution

### Research Findings

**1. Existing Codebase Analysis**

| Component | Status | Notes |
|-----------|--------|-------|
| Backend API | Complete | All CRUD endpoints implemented in `/backend/routes/tasks.py` |
| Auth Flow | Complete | JWT-based auth in `/backend/routes/auth.py` |
| API Client | Complete | Axios client in `/frontend/lib/api.ts` |
| Task Page | Partial | Basic structure exists, needs enhancement |
| Task Components | Partial | TaskForm, TaskList, TaskItem exist but need styling updates |
| Stats Display | Missing | Need to add StatsCard component |
| Progress Bar | Missing | Need to add ProgressBar component |

**2. API Endpoints Available**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/{user_id}/tasks` | GET | Fetch tasks with filter, returns counts |
| `POST /api/{user_id}/tasks` | POST | Create new task |
| `PUT /api/{user_id}/tasks/{task_id}` | PUT | Update task |
| `DELETE /api/{user_id}/tasks/{task_id}` | DELETE | Delete task |
| `PATCH /api/{user_id}/tasks/{task_id}/complete` | PATCH | Toggle completion |

**3. Design System**

- Theme: Dark (slate-900 background)
- Primary Gradient: Purple (#8B5CF6) to Blue (#3B82F6)
- Glassmorphism: `backdrop-filter: blur(12px)`, semi-transparent backgrounds
- Border radius: xl (rounded-xl) for cards, lg for buttons
- Existing utility classes: `.glass`, `.bg-gradient-primary`

**4. State Management Decision**

- Decision: Local React state with prop drilling
- Rationale: Simple single-page dashboard, no complex state sharing needed
- Alternatives considered: Context API (rejected - overkill), Redux (rejected - unnecessary)

**5. Progress Bar Implementation**

- Decision: CSS-based animated progress bar
- Rationale: Simple, performant, no additional dependencies
- Calculation: `(completed / total) * 100`%

### Unknowns Resolved

All technical context items resolved - no NEEDS CLARIFICATION remaining.

---

## Phase 1: Design & Contracts

### Data Model

Documented in [data-model.md](./data-model.md)

### API Contracts

Documented in [contracts/dashboard-api.yaml](./contracts/dashboard-api.yaml)

### Component Architecture

```text
TasksPage (app/tasks/page.tsx)
├── Header
│   ├── Logo
│   ├── User Info (name/email)
│   └── Logout Button
├── Dashboard Content
│   ├── Page Title & Subtitle
│   ├── Stats Section
│   │   ├── StatsCard (Total)
│   │   ├── StatsCard (Pending)
│   │   ├── StatsCard (Completed)
│   │   └── ProgressBar
│   ├── TaskForm (Add new task)
│   └── TaskList
│       ├── Filter Buttons (All/Pending/Completed)
│       └── TaskItem[] (mapped tasks)
│           ├── Checkbox (toggle complete)
│           ├── Title & Description
│           ├── Edit Button → Edit Mode
│           └── Delete Button → Confirmation
```

### Quickstart

Documented in [quickstart.md](./quickstart.md)

---

## Post-Design Constitution Re-check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Plan follows spec, tasks will reference Task IDs |
| II. Phased Evolution | PASS | Phase II dashboard feature |
| III. Technology Stack | PASS | Using required stack (Next.js, Tailwind) |
| IV. Independent User Stories | PASS | Each story can be implemented/tested independently |
| V. TDD | N/A | Not required per spec |
| VI. Stateless Architecture | PASS | DB-backed, no server session state |
| VII. Documentation | PASS | All artifacts being created |

**Final Gate Result**: PASS - Ready for /sp.tasks

---

## Next Steps

1. Run `/sp.tasks` to generate atomic tasks from this plan
2. Execute `/sp.implement` to build the dashboard
3. Test against acceptance scenarios in spec.md
4. Create PHR for complete workflow
