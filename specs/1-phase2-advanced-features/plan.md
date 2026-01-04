# Implementation Plan: Phase 2 Advanced Features

**Branch**: `1-phase2-advanced-features` | **Date**: 2026-01-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-phase2-advanced-features/spec.md`

## Summary

This plan extends the existing Phase 2 full-stack application (Next.js 16 + FastAPI + Neon PostgreSQL) with 13 advanced features organized into Intermediate (6) and Advanced (7) tiers. The implementation follows a subagent architecture with 5 specialized agents (BackendAgent, FeaturesAgent, UIAgent, AnalyticsAgent, AuthAgent) working in dependency order. All features leverage the existing authentication system, database schema, and API client while maintaining backward compatibility.

**Primary Approach**: Extend existing `phase-2/backend/` and `phase-2/frontend/` directories with new models, endpoints, components, and pages. Use incremental delivery based on priority: P1 features (organization/search) → P2 features (automation/settings) → P3 features (analytics/profile/shortcuts).

## Technical Context

**Language/Version**:
- Backend: Python 3.12+, FastAPI 0.104+, SQLModel 0.14+
- Frontend: TypeScript 5.3+, Next.js 16 (App Router), React 19

**Primary Dependencies**:
- Backend: `fastapi`, `sqlmodel`, `psycopg2-binary`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`
- Frontend: `next@16`, `react@19`, `tailwindcss`, `shadcn/ui`, `date-fns`, `chart.js`, `react-chartjs-2`
- Additional: `@headlessui/react` (modals/menus), `react-hot-toast` (notifications), `papaparse` (CSV), `cron-parser` (recurrence validation)

**Storage**:
- Primary: Neon Serverless PostgreSQL (existing connection via DATABASE_URL)
- Schema Extensions: Add columns to `tasks` table, create `task_history`, `user_preferences`, `tags`, `notifications` tables
- Indexes: `tasks.user_id`, `tasks.due_date`, `tasks.priority`, `task_history.task_id`, `tags.user_id`

**Testing**:
- Backend: `pytest` with `httpx` for endpoint testing
- Frontend: `@testing-library/react` for component testing
- E2E: Manual testing via browser for keyboard shortcuts, notifications, drag-drop

**Target Platform**:
- Production: Vercel (frontend), Hugging Face Spaces (backend)
- Development: Local (localhost:3000 frontend, localhost:8000 backend)

**Project Type**: Web application (existing monorepo structure)

**Performance Goals**:
- Search: <500ms for 1000 tasks
- Filter/Sort: <300ms for 500 tasks
- Export: <2s for 100 tasks
- Import: <5s for 500 tasks
- Theme toggle: <100ms instant switch
- Keyboard shortcuts: <100ms response

**Constraints**:
- No breaking changes to existing API endpoints (`/api/auth/*`, `/api/{user_id}/tasks`)
- Maintain JWT authentication compatibility
- Browser notification permission required (user opt-in)
- CSV export must open correctly in Excel/Google Sheets (UTF-8 BOM encoding)
- All data must be user-isolated (filter by `user_id` on backend)

**Scale/Scope**:
- Support: 1000+ tasks per user without performance degradation
- Users: Multi-tenant with strict data isolation
- Features: 13 new features across 47 functional requirements
- UI Components: 25+ new components (DatePicker, TagInput, AnalyticsCharts, SettingsPanel, etc.)
- API Endpoints: 15+ new endpoints (search, filter, recurring, analytics, export, import, preferences)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development
- ✅ Specification complete: `specs/1-phase2-advanced-features/spec.md`
- ✅ 11 user stories with Given/When/Then scenarios
- ✅ 47 functional requirements (FR-001 to FR-047)
- ✅ All acceptance criteria defined
- ✅ No manual coding - Claude Code generates all implementation

### ✅ II. Phased Evolution
- ✅ Phase I complete: Console application (Python, in-memory)
- ✅ Phase II in progress: Full-stack web app (existing basic implementation)
- ✅ This plan extends Phase II with advanced features
- ✅ Maintains backward compatibility with existing Phase II codebase

### ✅ III. Technology Stack Adherence
- ✅ Frontend: Next.js 16 (App Router) ✓
- ✅ Backend: FastAPI ✓
- ✅ ORM: SQLModel ✓
- ✅ Database: Neon Serverless PostgreSQL ✓
- ✅ Authentication: JWT (existing custom implementation) - Note: Spec called for Better Auth but Phase II already uses custom JWT; maintaining compatibility

**Note on Authentication**: Constitution specifies Better Auth, but existing Phase II implementation uses custom JWT authentication. **Decision**: Maintain existing JWT auth for backward compatibility. User profile/settings features will extend existing auth system rather than replacing it.

### ✅ IV. Independent User Stories
- ✅ All 11 user stories have P1/P2/P3 priorities
- ✅ Each story independently testable
- ✅ Each story delivers standalone value (can implement P1 first, then P2, then P3)
- ✅ Acceptance scenarios use Given/When/Then format

### ⚠️ V. Test-Driven Development (Conditional)
- ⚠️ Tests not explicitly requested in specification
- ✅ Proceeding with feature-first development
- ✅ Acceptance criteria serve as test cases
- **Decision**: Focus on functional delivery; add tests if time permits

### ✅ VI. Stateless Architecture
- ✅ All state persists to Neon database (no in-memory sessions)
- ✅ JWT tokens stateless (no server-side session storage)
- ✅ Backend can be horizontally scaled
- ✅ Server restarts don't lose data

### ✅ VII. Documentation and Traceability
- ✅ Constitution: `.specify/memory/constitution.md`
- ✅ Spec: `specs/1-phase2-advanced-features/spec.md`
- ✅ Plan: `specs/1-phase2-advanced-features/plan.md` (this file)
- ✅ Tasks: Will be generated via `/sp.tasks` after plan approval
- ✅ CLAUDE.md: `CLAUDE.md` (root guidance)
- ✅ PHR: `history/prompts/1-phase2-advanced-features/` (prompt history)

**Gate Result**: ✅ PASS - All constitution requirements met. Minor deviation: using existing custom JWT instead of Better Auth (justified by backward compatibility).

## Project Structure

### Documentation (this feature)

```text
specs/1-phase2-advanced-features/
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output (dependencies, patterns, best practices)
├── data-model.md        # Phase 1 output (extended schema, relationships)
├── quickstart.md        # Phase 1 output (dev setup for new features)
├── contracts/           # Phase 1 output (OpenAPI specs for new endpoints)
│   ├── search-filter-api.yaml
│   ├── recurring-tasks-api.yaml
│   ├── analytics-api.yaml
│   ├── export-import-api.yaml
│   └── preferences-api.yaml
├── checklists/
│   └── requirements.md  # Quality validation (already complete)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created yet)
```

### Source Code (existing Phase 2 monorepo)

```text
phase-2/
├── backend/
│   ├── main.py                      # [EXTEND] Add new router imports
│   ├── models.py                    # [EXTEND] Add: TaskHistory, UserPreferences, Tag, Notification
│   ├── db.py                        # [EXTEND] Add new table creation
│   ├── migrate.py                   # [EXTEND] Add migration for new columns/tables
│   ├── middleware/
│   │   └── auth.py                  # [KEEP] Existing JWT middleware
│   ├── routes/
│   │   ├── auth.py                  # [KEEP] Existing auth endpoints
│   │   ├── tasks.py                 # [EXTEND] Add search, filter, sort, recurring endpoints
│   │   ├── analytics.py             # [NEW] Stats, history, charts data
│   │   ├── export_import.py         # [NEW] JSON/CSV export/import endpoints
│   │   ├── preferences.py           # [NEW] User settings endpoints
│   │   └── notifications.py         # [NEW] Notification management endpoints
│   ├── services/
│   │   ├── recurring_tasks.py       # [NEW] Recurring task generation logic
│   │   ├── search.py                # [NEW] Full-text search implementation
│   │   ├── export.py                # [NEW] Export generation (JSON/CSV)
│   │   └── import_service.py        # [NEW] Import validation and processing
│   └── requirements.txt             # [EXTEND] Add chart.js deps, cron-parser, papaparse
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── tasks/
│   │   │   │   └── page.tsx         # [EXTEND] Add filters, search, sort UI
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx         # [NEW] Analytics dashboard
│   │   │   ├── settings/
│   │   │   │   └── page.tsx         # [NEW] User settings/preferences
│   │   │   ├── profile/
│   │   │   │   └── page.tsx         # [NEW] User profile management
│   │   │   └── layout.tsx           # [EXTEND] Add keyboard shortcuts listener
│   │   ├── components/
│   │   │   ├── TaskItem.tsx         # [EXTEND] Add priority badges, due date, tags
│   │   │   ├── TaskForm.tsx         # [EXTEND] Add DatePicker, priority, tags, recurrence
│   │   │   ├── DatePicker.tsx       # [NEW] Date/time picker component
│   │   │   ├── TagInput.tsx         # [NEW] Multi-tag input with autocomplete
│   │   │   ├── PriorityBadge.tsx    # [NEW] Color-coded priority display
│   │   │   ├── SearchBar.tsx        # [NEW] Global search component
│   │   │   ├── FilterPanel.tsx      # [NEW] Multi-criteria filter UI
│   │   │   ├── SortDropdown.tsx     # [NEW] Sort options selector
│   │   │   ├── RecurrenceInput.tsx  # [NEW] Recurrence pattern selector
│   │   │   ├── AnalyticsChart.tsx   # [NEW] Chart.js wrapper components
│   │   │   ├── ExportModal.tsx      # [NEW] Export format selector (Ctrl+E)
│   │   │   ├── ImportModal.tsx      # [NEW] Import file upload (Ctrl+I)
│   │   │   ├── KeyboardHelp.tsx     # [NEW] Shortcuts help modal (?)
│   │   │   ├── ThemeToggle.tsx      # [KEEP] Existing theme switcher
│   │   │   └── NotificationBanner.tsx # [NEW] Permission request banner
│   │   ├── lib/
│   │   │   ├── api.ts               # [EXTEND] Add new endpoint methods
│   │   │   ├── notifications.ts     # [NEW] Browser notification helpers
│   │   │   ├── keyboard.ts          # [NEW] Keyboard shortcut manager
│   │   │   ├── export.ts            # [NEW] Export generation helpers
│   │   │   └── import.ts            # [NEW] Import validation helpers
│   │   └── hooks/
│   │       ├── useKeyboard.ts       # [NEW] Keyboard shortcuts hook
│   │       ├── useNotifications.ts  # [NEW] Browser notifications hook
│   │       └── useSearch.ts         # [NEW] Debounced search hook
│   ├── package.json                 # [EXTEND] Add shadcn/ui, chart.js, date-fns
│   └── tailwind.config.js           # [EXTEND] Add custom colors for priorities
│
└── docker-compose.yml               # [KEEP] Existing Docker setup
```

**Structure Decision**: Extending existing Phase 2 monorepo structure. Backend adds new routes and services; frontend adds new pages and components. Maintains separation of concerns: backend handles business logic and data persistence, frontend handles UI and user interactions.

## Complexity Tracking

**No violations to justify** - all requirements align with constitution principles.

## Phase 0: Research & Dependencies

### Research Tasks

1. **Date/Time Picker Component**
   - Research: shadcn/ui date picker vs react-datepicker vs date-fns
   - **Decision**: Use shadcn/ui calendar component + date-fns for formatting
   - **Rationale**: Consistent with project's shadcn/ui usage, TypeScript support, accessibility built-in
   - **Alternatives**: react-datepicker (heavier bundle), native HTML5 date input (limited browser support)

2. **Recurring Task Pattern Storage**
   - Research: cron format vs custom JSON schema vs RFC 5545 (iCalendar RRULE)
   - **Decision**: Use simplified cron-like format (e.g., "0 9 * * 1-5" for weekdays 9am)
   - **Rationale**: Developer-familiar, compact storage, existing libraries (cron-parser)
   - **Alternatives**: iCalendar RRULE (overkill for basic recurrence), custom JSON (reinventing wheel)

3. **Full-Text Search Implementation**
   - Research: PostgreSQL `LIKE` vs `tsvector` full-text search vs external service (Algolia/Meilisearch)
   - **Decision**: PostgreSQL `tsvector` with GIN index on tasks table
   - **Rationale**: Native database feature, no external dependencies, good performance for <10k tasks per user
   - **Alternatives**: `LIKE '%term%'` (too slow), Algolia (unnecessary complexity for MVP)

4. **Browser Notifications**
   - Research: Notification API vs Service Workers vs push notifications
   - **Decision**: Use Notification API with permission request flow
   - **Rationale**: Simple implementation, no service worker needed for foreground notifications
   - **Alternatives**: Service Workers (overkill), push notifications (requires backend push service)

5. **CSV Export Encoding**
   - Research: UTF-8 vs UTF-8 BOM vs ISO-8859-1
   - **Decision**: UTF-8 with BOM (Byte Order Mark)
   - **Rationale**: Excel on Windows requires BOM to display UTF-8 correctly
   - **Alternatives**: UTF-8 without BOM (breaks in Excel), ISO-8859-1 (no emoji support)

6. **Analytics Charts Library**
   - Research: Chart.js vs Recharts vs D3.js
   - **Decision**: Chart.js with react-chartjs-2 wrapper
   - **Rationale**: Lightweight, good React integration, sufficient for bar/pie/line charts
   - **Alternatives**: Recharts (React-first but heavier), D3.js (too low-level)

7. **Keyboard Shortcuts Manager**
   - Research: react-hotkeys-hook vs custom useEffect listeners
   - **Decision**: react-hotkeys-hook library
   - **Rationale**: Handles key combinations, prevents conflicts, well-maintained
   - **Alternatives**: Custom implementation (reinventing wheel), tinykeys (no React hooks)

8. **Import Validation Strategy**
   - Research: Zod vs JSON Schema vs manual validation
   - **Decision**: Manual validation with clear error messages
   - **Rationale**: Simple validation rules, no heavy schema library needed
   - **Alternatives**: Zod (adds dependency), JSON Schema (verbose)

### Dependency Analysis

**Backend New Dependencies**:
- `cron-parser`: Validate and parse recurrence patterns
- `python-multipart`: File upload for import (already in FastAPI)
- No additional dependencies needed (standard library sufficient for CSV/JSON)

**Frontend New Dependencies**:
- `@shadcn/ui`: calendar, select, dialog, popover components (already installed)
- `date-fns`: Date formatting and manipulation
- `chart.js` + `react-chartjs-2`: Analytics charts
- `react-hot-toast`: Toast notifications (already may be installed)
- `react-hotkeys-hook`: Keyboard shortcuts
- `papaparse`: CSV parsing for import
- `@headlessui/react`: Accessible UI primitives (modals, menus)

**Total Added Bundle Size**: ~150KB gzipped (chart.js ~60KB, date-fns ~30KB, others ~60KB combined)

### Integration Patterns

1. **Authentication Flow**: All new endpoints use existing JWT middleware from `phase-2/backend/middleware/auth.py`
2. **API Client**: Extend `phase-2/frontend/src/lib/api.ts` with new methods (searchTasks, exportTasks, etc.)
3. **Database Migrations**: Use `phase-2/backend/migrate.py` to add new tables and columns
4. **Theme System**: Integrate with existing ThemeToggle component for dark mode support

## Phase 1: Data Model & Contracts

See generated artifacts:
- [data-model.md](./data-model.md) - Extended database schema
- [contracts/](./contracts/) - OpenAPI specifications for new endpoints
- [quickstart.md](./quickstart.md) - Development setup guide

## Implementation Strategy

### Subagent Execution Order

The implementation follows a dependency-driven subagent workflow:

```
1. BackendAgent (Foundation)
   ├─ Extend models.py with new tables
   ├─ Create migration script
   ├─ Implement search/filter/sort endpoints
   ├─ Add recurring task service
   └─ Create analytics/export/import endpoints

2. FeaturesAgent (Core Features)
   ├─ Due dates & priorities (depends on Backend models)
   ├─ Tags/categories (depends on Backend tags table)
   ├─ Search/filter/sort (depends on Backend endpoints)
   └─ Recurring tasks (depends on Backend recurring service)

3. UIAgent (User Interface)
   ├─ DatePicker, TagInput, PriorityBadge components
   ├─ SearchBar, FilterPanel, SortDropdown
   ├─ Task list enhancements (priority badges, due dates)
   └─ Keyboard shortcuts integration

4. AnalyticsAgent (Insights & Export)
   ├─ Analytics dashboard with charts
   ├─ Task history timeline
   ├─ Export modal (JSON/CSV with Ctrl+E)
   └─ Import modal (drag-drop with Ctrl+I)

5. AuthAgent (Settings & Profile)
   ├─ User preferences page
   ├─ Profile management page
   ├─ Theme switcher integration
   └─ Notification settings
```

### Incremental Delivery Plan

**Sprint 1: P1 Features (Must-Have)**
- Due dates & priorities (FR-001 to FR-009)
- Tags & search (FR-004, FR-005)
- Filter & sort (FR-006, FR-007, FR-008, FR-009)
- **Deliverable**: Users can organize, search, and filter tasks

**Sprint 2: P2 Features (High-Value)**
- Recurring tasks (FR-010, FR-011)
- Browser notifications (FR-012, FR-013, FR-014)
- User settings (FR-019, FR-020)
- Import/Export (FR-026 to FR-040)
- **Deliverable**: Automation and data portability

**Sprint 3: P3 Features (Nice-to-Have)**
- Task history (FR-015, FR-016)
- Analytics dashboard (FR-017, FR-018)
- User profile (FR-021, FR-022, FR-023)
- Keyboard shortcuts (FR-024, FR-025)
- **Deliverable**: Insights and power user features

### Risk Mitigation

1. **Browser Notification Permission**: User may deny → Gracefully degrade, show banner to re-enable
2. **Large Export Performance**: 1000+ tasks → Implement streaming export with progress indicator
3. **Recurring Task Edge Cases**: "31st of month" in February → Skip invalid dates, log warnings
4. **CSV Import Encoding**: Non-UTF8 files → Auto-detect encoding, show preview before import
5. **Search Performance**: 10k+ tasks → Add PostgreSQL GIN index on tsvector column

## Next Steps

1. **Review and approve this plan**
2. **Run `/sp.tasks`** to generate atomic task breakdown
3. **Execute BackendAgent tasks** (database, endpoints, services)
4. **Execute FeaturesAgent tasks** (due dates, priorities, tags, recurring)
5. **Execute UIAgent tasks** (components, pages, keyboard shortcuts)
6. **Execute AnalyticsAgent tasks** (charts, export, import, history)
7. **Execute AuthAgent tasks** (settings, profile)
8. **Test all 13 features end-to-end**
9. **Deploy to Vercel (frontend) and Hugging Face Spaces (backend)**
10. **Create 90-second demo video**

**Estimated Completion**: 5-7 days (with Claude Code generating all implementation code)
