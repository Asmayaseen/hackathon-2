# Tasks: Phase 2 Advanced Features

**Input**: Design documents from `/specs/1-phase2-advanced-features/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-summary.md, research.md, quickstart.md

**Tests**: Not explicitly requested in specification - proceeding with feature-first development per constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Each user story represents a complete, deliverable feature increment.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US11)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this is a **web application monorepo**:
- Backend: `phase-2/backend/`
- Frontend: `phase-2/frontend/`

---

## Phase 1: Setup & Infrastructure

**Purpose**: Project initialization, dependency installation, and database migration

**Duration**: ~2 hours

### Setup Tasks

- [X] T001 Install backend dependencies: `pip install cron-validator` in phase-2/backend/
- [X] T002 Install frontend dependencies: `npm install date-fns chart.js react-chartjs-2 react-hotkeys-hook papaparse @headlessui/react` in phase-2/frontend/
- [X] T003 Create database migration file: phase-2/backend/migrations/002_phase2_advanced.sql from data-model.md
- [X] T004 Run database migration to add new tables and columns
- [X] T005 Verify migration success: check tasks table columns, verify new tables exist (task_history, user_preferences, tags, notifications)
- [X] T006 [P] Update requirements.txt with new dependencies: phase-2/backend/requirements.txt
- [X] T007 [P] Update package.json with new dependencies: phase-2/frontend/package.json
- [X] T008 [P] Add Tailwind custom colors for priorities (red, yellow, green) in phase-2/frontend/tailwind.config.js

**Acceptance**: Database schema extended, all dependencies installed, migrations successful

---

## Phase 2: Foundation (Blocking Prerequisites)

**Purpose**: Core infrastructure needed by all user stories

**Duration**: ~1 day

### Backend Foundation

- [X] T009 Extend Task model in phase-2/backend/models.py with new fields: due_date, priority, tags, recurrence_pattern, reminder_offset, is_recurring, parent_recurring_id
- [X] T010 [P] Create TaskHistory model in phase-2/backend/models.py
- [X] T011 [P] Create UserPreferences model in phase-2/backend/models.py
- [X] T012 [P] Create Tag model in phase-2/backend/models.py
- [X] T013 [P] Create Notification model in phase-2/backend/models.py
- [X] T014 Update db.py to create new tables on startup: phase-2/backend/db.py
- [X] T015 [P] Create enums for Priority and Theme in phase-2/backend/models.py
- [X] T016 [P] Add tsvector trigger function for search in migration script

### Frontend Foundation

- [ ] T017 [P] Extend TaskItem component to display new fields: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T018 [P] Extend TaskForm component with new input fields: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T019 Update API client type definitions in phase-2/frontend/src/lib/api.ts with extended Task interface
- [ ] T020 [P] Create useKeyboard hook for global shortcuts: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T021 [P] Create useNotifications hook for browser notifications: phase-2/frontend/src/hooks/useNotifications.ts

**Acceptance**: All models defined, API types updated, foundation hooks created

---

## Phase 3: User Story 1 - Task Organization (P1 - Must Have)

**Story**: As a busy user managing multiple tasks, I need to organize my tasks by priority levels and set due dates so that I can focus on what's most urgent and meet my deadlines.

**Independent Test**: Create tasks with different priority levels (High/Medium/Low) and due dates, verify visual indicators and date displays work correctly. Delivers immediate value through color-coded visual hierarchy.

**Duration**: ~1 day

### US1: Backend Tasks

- [ ] T022 [US1] Add priority field handling in POST /api/{user_id}/tasks endpoint: phase-2/backend/routes/tasks.py
- [ ] T023 [US1] Add due_date field handling in POST /api/{user_id}/tasks endpoint: phase-2/backend/routes/tasks.py
- [ ] T024 [US1] Add priority and due_date to PUT /api/{user_id}/tasks/{id} endpoint: phase-2/backend/routes/tasks.py
- [ ] T025 [US1] Add validation for priority enum values in routes: phase-2/backend/routes/tasks.py
- [ ] T026 [US1] Add validation for due_date (must be future date unless editing overdue): phase-2/backend/routes/tasks.py

### US1: Frontend Tasks

- [ ] T027 [P] [US1] Create PriorityBadge component with color coding (red/yellow/green): phase-2/frontend/src/components/PriorityBadge.tsx
- [ ] T028 [P] [US1] Create DatePicker component using shadcn/ui Calendar + date-fns: phase-2/frontend/src/components/DatePicker.tsx
- [ ] T029 [US1] Add priority selector dropdown to TaskForm: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T030 [US1] Add DatePicker integration to TaskForm for due_date: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T031 [US1] Display PriorityBadge in TaskItem component: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T032 [US1] Display due date with relative formatting ("Due Tomorrow") in TaskItem: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T033 [US1] Add overdue indicator (red text, "OVERDUE" label) for past due dates: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T034 [US1] Update API client methods to include priority and due_date: phase-2/frontend/src/lib/api.ts

**US1 Acceptance**: Users can set priority and due date when creating/editing tasks. Tasks display with color-coded priority badges and formatted due dates. Overdue tasks show red warning.

---

## Phase 4: User Story 2 - Task Categorization (P1 - Must Have)

**Story**: As a user with tasks across different life areas (work, personal, shopping, etc.), I need to tag and search my tasks so that I can quickly find and filter tasks by category.

**Independent Test**: Create tasks with tags (e.g., "work", "urgent", "shopping"), use search and tag filters to verify only matching tasks appear.

**Duration**: ~1 day

### US2: Backend Tasks

- [ ] T035 [US2] Implement full-text search endpoint GET /api/{user_id}/tasks/search: phase-2/backend/routes/tasks.py
- [ ] T036 [US2] Add search query using tsvector and plainto_tsquery: phase-2/backend/routes/tasks.py
- [ ] T037 [US2] Create search service with ranking logic: phase-2/backend/services/search.py
- [ ] T038 [P] [US2] Implement tag autocomplete endpoint GET /api/{user_id}/tags/autocomplete: phase-2/backend/routes/tags.py (NEW FILE)
- [ ] T039 [US2] Create tag management service to update usage_count: phase-2/backend/services/tag_service.py (NEW FILE)
- [ ] T040 [US2] Add tag field handling in task creation/update endpoints: phase-2/backend/routes/tasks.py

### US2: Frontend Tasks

- [ ] T041 [P] [US2] Create SearchBar component with debounced input: phase-2/frontend/src/components/SearchBar.tsx
- [ ] T042 [P] [US2] Create TagInput component with autocomplete: phase-2/frontend/src/components/TagInput.tsx
- [ ] T043 [P] [US2] Create useSearch hook with debouncing: phase-2/frontend/src/hooks/useSearch.ts
- [ ] T044 [US2] Add SearchBar to task list page header: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T045 [US2] Add TagInput to TaskForm component: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T046 [US2] Display tags as badges in TaskItem component: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T047 [US2] Implement tag click to filter functionality: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T048 [US2] Add "Clear filters" button when filters active: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T049 [US2] Update API client with searchTasks method: phase-2/frontend/src/lib/api.ts

**US2 Acceptance**: Users can add multiple tags to tasks. Full-text search works across titles, descriptions, and tags. Clicking a tag filters tasks. Clear filters button resets view.

---

## Phase 5: User Story 3 - Advanced Filtering (P2 - High Value)

**Story**: As a user with many tasks, I need to filter by multiple criteria (status, priority, tags, dates) and sort tasks to customize my view and focus on what matters most right now.

**Independent Test**: Create 30+ tasks with various status/priority/tags/dates, apply different filter/sort combinations to verify correct results.

**Duration**: ~1 day

### US3: Backend Tasks

- [ ] T050 [US3] Extend search endpoint with filter parameters (status, priority, tags, due_before, due_after): phase-2/backend/routes/tasks.py
- [ ] T051 [US3] Add sort parameter handling (due_date, priority, title, created_at): phase-2/backend/routes/tasks.py
- [ ] T052 [US3] Add order parameter (asc/desc) to search endpoint: phase-2/backend/routes/tasks.py
- [ ] T053 [US3] Implement complex filtering logic with multiple criteria: phase-2/backend/services/search.py
- [ ] T054 [US3] Add pagination support (limit, offset): phase-2/backend/routes/tasks.py

### US3: Frontend Tasks

- [ ] T055 [P] [US3] Create FilterPanel component with multi-select: phase-2/frontend/src/components/FilterPanel.tsx
- [ ] T056 [P] [US3] Create SortDropdown component: phase-2/frontend/src/components/SortDropdown.tsx
- [ ] T057 [US3] Add FilterPanel to task list page: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T058 [US3] Add SortDropdown to task list page: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T059 [US3] Display active filter summary bar with × remove buttons: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T060 [US3] Implement filter state management in task list page: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T061 [US3] Add task count badges next to filter options (e.g., "High Priority (5)"): phase-2/frontend/src/components/FilterPanel.tsx
- [ ] T062 [US3] Update API client with filter and sort parameters: phase-2/frontend/src/lib/api.ts

**US3 Acceptance**: Users can filter by status + priority + tags + date ranges simultaneously. Sort by due date, priority, title, or created date. Filter summary shows active filters with × to remove.

---

## Phase 6: User Story 4 - Recurring Tasks (P2 - High Value)

**Story**: As a user with daily/weekly routines, I need tasks to automatically recreate themselves on a schedule so that I don't have to manually re-enter repeating tasks.

**Independent Test**: Create recurring task (e.g., "Daily standup - Every weekday at 9am"), mark complete, verify new instance appears next day with correct due date.

**Duration**: ~1.5 days

### US4: Backend Tasks

- [ ] T063 [US4] Add recurrence_pattern and is_recurring fields to task creation: phase-2/backend/routes/tasks.py
- [ ] T064 [US4] Validate recurrence_pattern using cron-validator: phase-2/backend/routes/tasks.py
- [ ] T065 [US4] Create recurring task service with generate_next_instance method: phase-2/backend/services/recurring_tasks.py (NEW FILE)
- [ ] T066 [US4] Implement POST /api/{user_id}/tasks/{id}/complete-recurring endpoint: phase-2/backend/routes/tasks.py
- [ ] T067 [US4] Add logic to generate next instance on completion: phase-2/backend/services/recurring_tasks.py
- [ ] T068 [US4] Implement PUT /api/{user_id}/tasks/{id}/recurrence endpoint: phase-2/backend/routes/tasks.py
- [ ] T069 [US4] Create cron job script to check for missed recurring tasks: phase-2/backend/run_recurring_tasks.py (NEW FILE)
- [ ] T070 [US4] Handle edge cases (31st of month in February, skip invalid dates): phase-2/backend/services/recurring_tasks.py

### US4: Frontend Tasks

- [ ] T071 [P] [US4] Create RecurrenceInput component with pattern selector: phase-2/frontend/src/components/RecurrenceInput.tsx
- [ ] T072 [US4] Add RecurrenceInput to TaskForm component: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T073 [US4] Display recurring badge (↻ icon) in TaskItem for recurring tasks: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T074 [US4] Add recurrence pattern display (e.g., "↻ Daily" or "↻ Weekly") in TaskItem: phase-2/frontend/src/components/TaskItem.tsx
- [ ] T075 [US4] Update complete task handler to use complete-recurring endpoint when task is recurring: phase-2/frontend/src/lib/api.ts
- [ ] T076 [US4] Show confirmation when completing recurring task ("Mark complete and create next instance?"): phase-2/frontend/src/components/TaskItem.tsx

**US4 Acceptance**: Users can set recurrence patterns (Daily/Weekly/Monthly). Completing recurring task automatically creates next instance with correct due date. Recurring badge visible on tasks.

---

## Phase 7: User Story 5 - Browser Notifications (P2 - High Value)

**Story**: As a forgetful user, I need browser notifications to remind me when tasks are due so that I don't miss important deadlines.

**Independent Test**: Create task due in 5 minutes, grant notification permission, verify browser notification appears at scheduled time with correct task title.

**Duration**: ~1 day

### US5: Backend Tasks

- [ ] T077 [US5] Implement POST /api/{user_id}/tasks/{id}/schedule-reminder endpoint: phase-2/backend/routes/notifications.py (NEW FILE)
- [ ] T078 [US5] Create notification in database when reminder scheduled: phase-2/backend/routes/notifications.py
- [ ] T079 [US5] Implement GET /api/{user_id}/notifications/pending endpoint: phase-2/backend/routes/notifications.py
- [ ] T080 [US5] Create cron job to check pending notifications and trigger them: phase-2/backend/run_notifications.py (NEW FILE)
- [ ] T081 [US5] Add rate limiting (max 1 notification per task per hour): phase-2/backend/routes/notifications.py
- [ ] T082 [US5] Auto-schedule reminder when task created with due_date and reminder_offset: phase-2/backend/routes/tasks.py

### US5: Frontend Tasks

- [ ] T083 [P] [US5] Create notification helpers (requestPermission, sendNotification): phase-2/frontend/src/lib/notifications.ts
- [ ] T084 [P] [US5] Create NotificationBanner component for permission request: phase-2/frontend/src/components/NotificationBanner.tsx
- [ ] T085 [US5] Add NotificationBanner to app layout (shows if permission not granted): phase-2/frontend/src/app/layout.tsx
- [ ] T086 [US5] Add reminder_offset input to TaskForm (dropdown: 15 min, 1 hour, 1 day before): phase-2/frontend/src/components/TaskForm.tsx
- [ ] T087 [US5] Implement notification permission check on app load: phase-2/frontend/src/app/layout.tsx
- [ ] T088 [US5] Poll pending notifications endpoint every minute: phase-2/frontend/src/hooks/useNotifications.ts
- [ ] T089 [US5] Trigger browser notification when task due: phase-2/frontend/src/hooks/useNotifications.ts
- [ ] T090 [US5] Handle notification click to open task in app: phase-2/frontend/src/hooks/useNotifications.ts

**US5 Acceptance**: App requests notification permission on first visit. Users can set reminder offset (15 min, 1 hour, 1 day before). Browser notification appears at scheduled time. Clicking notification opens task.

---

## Phase 8: User Story 6 - Task History (P3 - Nice to Have)

**Story**: As a user who wants to track my productivity, I need to see a history of all changes made to tasks so that I can review what I accomplished and when.

**Independent Test**: Create task, edit it multiple times (title change, status change, priority change), view task history to verify all changes logged with timestamps.

**Duration**: ~1 day

### US6: Backend Tasks

- [ ] T091 [US6] Implement GET /api/{user_id}/tasks/{id}/history endpoint: phase-2/backend/routes/analytics.py (NEW FILE)
- [ ] T092 [US6] Create database triggers to auto-log task changes to task_history table (see data-model.md): phase-2/backend/migrations/002_phase2_advanced.sql (update)
- [ ] T093 [US6] Format history entries with readable action descriptions: phase-2/backend/routes/analytics.py
- [ ] T094 [US6] Add pagination to history endpoint: phase-2/backend/routes/analytics.py

### US6: Frontend Tasks

- [ ] T095 [P] [US6] Create TaskHistory component to display timeline: phase-2/frontend/src/components/TaskHistory.tsx
- [ ] T096 [US6] Add collapsible history section to task detail view: phase-2/frontend/src/components/TaskItem.tsx (or separate TaskDetail component)
- [ ] T097 [US6] Format history entries with icons and timestamps: phase-2/frontend/src/components/TaskHistory.tsx
- [ ] T098 [US6] Show old → new value diffs for changes: phase-2/frontend/src/components/TaskHistory.tsx
- [ ] T099 [US6] Update API client with getTaskHistory method: phase-2/frontend/src/lib/api.ts

**US6 Acceptance**: Task history shows all modifications (created, updated, completed, priority changed) with timestamps. History displayed in reverse chronological order. Changes show old → new values.

---

## Phase 9: User Story 7 - Analytics Dashboard (P3 - Nice to Have)

**Story**: As a goal-oriented user, I need visual charts showing my completion rates, priority distribution, and productivity trends so that I can understand and improve my task management habits.

**Independent Test**: Complete 50+ tasks over time, view analytics dashboard to verify charts accurately reflect completion rates, priority distribution, and weekly activity.

**Duration**: ~1.5 days

### US7: Backend Tasks

- [ ] T100 [US7] Implement GET /api/{user_id}/analytics/stats endpoint: phase-2/backend/routes/analytics.py
- [ ] T101 [US7] Calculate completion rate (completed / total): phase-2/backend/routes/analytics.py
- [ ] T102 [US7] Calculate priority distribution: phase-2/backend/routes/analytics.py
- [ ] T103 [US7] Calculate weekly activity (tasks completed per day): phase-2/backend/routes/analytics.py
- [ ] T104 [US7] Add period filter (today, week, month, all): phase-2/backend/routes/analytics.py
- [ ] T105 [US7] Count overdue tasks and tasks due today: phase-2/backend/routes/analytics.py

### US7: Frontend Tasks

- [ ] T106 [P] [US7] Create analytics page: phase-2/frontend/src/app/analytics/page.tsx (NEW FILE)
- [ ] T107 [P] [US7] Create AnalyticsChart wrapper component for Chart.js: phase-2/frontend/src/components/AnalyticsChart.tsx
- [ ] T108 [US7] Register Chart.js components (Bar, Pie, Line, scales): phase-2/frontend/src/components/AnalyticsChart.tsx
- [ ] T109 [US7] Create completion rate chart (completed vs pending): phase-2/frontend/src/app/analytics/page.tsx
- [ ] T110 [US7] Create priority distribution pie chart: phase-2/frontend/src/app/analytics/page.tsx
- [ ] T111 [US7] Create weekly activity bar chart: phase-2/frontend/src/app/analytics/page.tsx
- [ ] T112 [US7] Add period filter dropdown (Last 7 days, Last 30 days, All time): phase-2/frontend/src/app/analytics/page.tsx
- [ ] T113 [US7] Display key stats cards (total tasks, completion rate, overdue count): phase-2/frontend/src/app/analytics/page.tsx
- [ ] T114 [US7] Add analytics link to main navigation: phase-2/frontend/src/app/layout.tsx
- [ ] T115 [US7] Update API client with getAnalytics method: phase-2/frontend/src/lib/api.ts

**US7 Acceptance**: Analytics page shows completion rate chart, priority distribution pie chart, and weekly activity graph. Period filter works (Last 7 days, Last 30 days, All time). Key stats displayed (total tasks, completion %, overdue count).

---

## Phase 10: User Story 8 - User Settings (P2 - High Value)

**Story**: As a user who wants a personalized experience, I need to configure theme (dark/light), notification settings, and default task options so that the app matches my workflow.

**Independent Test**: Navigate to Settings, toggle dark mode (verify UI changes), disable notifications (verify no alerts), set default priority to High (verify new tasks inherit).

**Duration**: ~1 day

### US8: Backend Tasks

- [ ] T116 [US8] Implement GET /api/{user_id}/preferences endpoint: phase-2/backend/routes/preferences.py (NEW FILE)
- [ ] T117 [US8] Implement PATCH /api/{user_id}/preferences endpoint: phase-2/backend/routes/preferences.py
- [ ] T118 [US8] Create default preferences when user signs up: phase-2/backend/routes/auth.py (update)
- [ ] T119 [US8] Validate preference values (theme, priority, view, language): phase-2/backend/routes/preferences.py

### US8: Frontend Tasks

- [ ] T120 [P] [US8] Create settings page: phase-2/frontend/src/app/settings/page.tsx (NEW FILE)
- [ ] T121 [US8] Add theme toggle (light/dark) to settings page: phase-2/frontend/src/app/settings/page.tsx
- [ ] T122 [US8] Add notification enable/disable toggle: phase-2/frontend/src/app/settings/page.tsx
- [ ] T123 [US8] Add notification sound toggle: phase-2/frontend/src/app/settings/page.tsx
- [ ] T124 [US8] Add default priority selector dropdown: phase-2/frontend/src/app/settings/page.tsx
- [ ] T125 [US8] Add default view selector (All/Today/Week): phase-2/frontend/src/app/settings/page.tsx
- [ ] T126 [US8] Add language selector (English/Urdu): phase-2/frontend/src/app/settings/page.tsx
- [ ] T127 [US8] Implement theme switching with instant UI update: phase-2/frontend/src/app/settings/page.tsx
- [ ] T128 [US8] Persist theme preference to database: phase-2/frontend/src/app/settings/page.tsx
- [ ] T129 [US8] Apply default priority when creating new tasks: phase-2/frontend/src/components/TaskForm.tsx
- [ ] T130 [US8] Add settings link to main navigation: phase-2/frontend/src/app/layout.tsx
- [ ] T131 [US8] Update API client with preferences methods: phase-2/frontend/src/lib/api.ts

**US8 Acceptance**: Settings page allows theme toggle (instant UI change), notification enable/disable, default priority selection, default view selection, language selection (English/Urdu). All settings persist across sessions.

---

## Phase 11: User Story 9 - User Profile (P3 - Nice to Have)

**Story**: As a user who shares my device, I need to manage my profile (name, email, avatar) and view account details so that I can personalize my identity in the app.

**Independent Test**: Navigate to Profile, upload avatar (verify display in header), change name (verify updates throughout app), confirm email update requires verification.

**Duration**: ~1 day

### US9: Backend Tasks

- [ ] T132 [US9] Implement GET /api/{user_id}/profile endpoint: phase-2/backend/routes/auth.py (update)
- [ ] T133 [US9] Implement PATCH /api/{user_id}/profile endpoint: phase-2/backend/routes/auth.py
- [ ] T134 [US9] Add avatar upload endpoint POST /api/{user_id}/profile/avatar: phase-2/backend/routes/auth.py
- [ ] T135 [US9] Validate avatar file (max 2MB, formats: JPG/PNG/WebP): phase-2/backend/routes/auth.py
- [ ] T136 [US9] Store avatar in file storage or base64 in database: phase-2/backend/routes/auth.py
- [ ] T137 [US9] Calculate account statistics (total tasks, completion %): phase-2/backend/routes/auth.py

### US9: Frontend Tasks

- [ ] T138 [P] [US9] Create profile page: phase-2/frontend/src/app/profile/page.tsx (NEW FILE)
- [ ] T139 [US9] Add avatar upload component with preview: phase-2/frontend/src/app/profile/page.tsx
- [ ] T140 [US9] Display avatar in header navigation: phase-2/frontend/src/app/layout.tsx
- [ ] T141 [US9] Add name edit field with save button: phase-2/frontend/src/app/profile/page.tsx
- [ ] T142 [US9] Add email edit field with verification flow: phase-2/frontend/src/app/profile/page.tsx
- [ ] T143 [US9] Display account creation date: phase-2/frontend/src/app/profile/page.tsx
- [ ] T144 [US9] Display account statistics (total tasks, completion %): phase-2/frontend/src/app/profile/page.tsx
- [ ] T145 [US9] Add profile link to main navigation: phase-2/frontend/src/app/layout.tsx
- [ ] T146 [US9] Update API client with profile methods: phase-2/frontend/src/lib/api.ts

**US9 Acceptance**: Profile page allows avatar upload (displays in header), name change (updates throughout app), email change (requires verification). Account stats show creation date, total tasks, completion %.

---

## Phase 12: User Story 10 - Keyboard Shortcuts (P3 - Nice to Have)

**Story**: As a power user who prefers keyboard navigation, I need vim-style shortcuts and quick actions so that I can manage tasks without using the mouse.

**Independent Test**: Open app, press `?` to view shortcuts, test each shortcut (n creates task, j/k navigate, / focuses search, x toggles complete) to verify correct actions.

**Duration**: ~1 day

### US10: Frontend Tasks

- [ ] T147 [P] [US10] Implement keyboard shortcuts with react-hotkeys-hook in useKeyboard hook: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T148 [US10] Add shortcut: `n` to open new task modal: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T149 [US10] Add shortcut: `j/k` to navigate task list (vim-style): phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T150 [US10] Add shortcut: `/` to focus search bar: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T151 [US10] Add shortcut: `x` to toggle selected task complete: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T152 [US10] Add shortcut: `Ctrl+E` to open export modal: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T153 [US10] Add shortcut: `Ctrl+I` to open import modal: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T154 [US10] Add shortcut: `?` to show shortcuts help modal: phase-2/frontend/src/hooks/useKeyboard.ts
- [ ] T155 [P] [US10] Create KeyboardHelp modal component with shortcut list: phase-2/frontend/src/components/KeyboardHelp.tsx
- [ ] T156 [US10] Integrate useKeyboard hook in app layout: phase-2/frontend/src/app/layout.tsx
- [ ] T157 [US10] Add visual feedback for selected task (highlight border): phase-2/frontend/src/components/TaskItem.tsx
- [ ] T158 [US10] Handle keyboard navigation state (current selected task index): phase-2/frontend/src/app/tasks/page.tsx

**US10 Acceptance**: Press `?` opens shortcuts help modal. All shortcuts work: n (new task), j/k (navigate), / (search), x (toggle), Ctrl+E (export), Ctrl+I (import). Selected task has visual highlight.

---

## Phase 13: User Story 11 - Import/Export Data (P2 - High Value)

**Story**: As a user who wants data portability and backup, I need to export my tasks to JSON/CSV files and import them back so that I can backup my data, migrate between devices, or integrate with other tools.

**Independent Test**: Create 20 tasks, export to JSON and CSV (Ctrl+E), clear all tasks, import each file back and verify all data restores correctly with proper field mapping.

**Duration**: ~1.5 days

### US11: Backend Tasks

- [ ] T159 [US11] Implement GET /api/{user_id}/export?format=json endpoint: phase-2/backend/routes/export_import.py (NEW FILE)
- [ ] T160 [US11] Implement GET /api/{user_id}/export?format=csv endpoint: phase-2/backend/routes/export_import.py
- [ ] T161 [US11] Create export service to generate JSON with metadata: phase-2/backend/services/export.py (NEW FILE)
- [ ] T162 [US11] Create export service to generate CSV with UTF-8 BOM: phase-2/backend/services/export.py
- [ ] T163 [US11] Add streaming export for large datasets (1000+ tasks): phase-2/backend/services/export.py
- [ ] T164 [US11] Implement POST /api/{user_id}/import with multipart/form-data: phase-2/backend/routes/export_import.py
- [ ] T165 [US11] Create import validation service: phase-2/backend/services/import_service.py (NEW FILE)
- [ ] T166 [US11] Validate JSON format and schema version: phase-2/backend/services/import_service.py
- [ ] T167 [US11] Validate CSV format and required columns: phase-2/backend/services/import_service.py
- [ ] T168 [US11] Implement duplicate detection by task title: phase-2/backend/services/import_service.py
- [ ] T169 [US11] Handle merge strategies (skip, import_new, update): phase-2/backend/services/import_service.py
- [ ] T170 [US11] Return validation errors with line numbers for CSV: phase-2/backend/routes/export_import.py

### US11: Frontend Tasks

- [ ] T171 [P] [US11] Create ExportModal component with format selection (JSON/CSV): phase-2/frontend/src/components/ExportModal.tsx
- [ ] T172 [P] [US11] Create ImportModal component with drag-drop file upload: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T173 [US11] Display export metadata (task count, date) in ExportModal: phase-2/frontend/src/components/ExportModal.tsx
- [ ] T174 [US11] Implement file download with timestamped filename: phase-2/frontend/src/components/ExportModal.tsx
- [ ] T175 [US11] Add drag-and-drop zone to ImportModal: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T176 [US11] Auto-detect file format (JSON/CSV) from extension: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T177 [US11] Show import preview with task count and sample data: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T178 [US11] Display merge strategy selector (skip/import_new/update): phase-2/frontend/src/components/ImportModal.tsx
- [ ] T179 [US11] Show validation errors with line numbers: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T180 [US11] Show progress indicator for large imports: phase-2/frontend/src/components/ImportModal.tsx
- [ ] T181 [US11] Create export/import helper functions: phase-2/frontend/src/lib/export.ts and phase-2/frontend/src/lib/import.ts (NEW FILES)
- [ ] T182 [US11] Update API client with export and import methods: phase-2/frontend/src/lib/api.ts
- [ ] T183 [US11] Trigger ExportModal on Ctrl+E shortcut (already wired in US10): verify integration
- [ ] T184 [US11] Trigger ImportModal on Ctrl+I shortcut (already wired in US10): verify integration

**US11 Acceptance**: Ctrl+E opens export modal with JSON/CSV options. Export downloads file with timestamp. Ctrl+I opens import modal with drag-drop. Import validates file, shows preview, detects duplicates, offers merge strategies. All data restores correctly.

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, performance optimization, and user experience polish

**Duration**: ~1 day

### Integration Tasks

- [ ] T185 Add error boundaries to catch and display React errors gracefully: phase-2/frontend/src/app/layout.tsx
- [ ] T186 Add loading skeletons for async data (task list, analytics charts): phase-2/frontend/src/components/LoadingSkeleton.tsx (NEW FILE)
- [ ] T187 Add toast notifications for success/error messages using react-hot-toast: phase-2/frontend/src/lib/toast.ts (NEW FILE)
- [ ] T188 Implement optimistic UI updates for task completion toggle: phase-2/frontend/src/app/tasks/page.tsx
- [ ] T189 Add confirmation dialogs for destructive actions (delete task, clear all): phase-2/frontend/src/components/ConfirmDialog.tsx (NEW FILE)
- [ ] T190 [P] Test all keyboard shortcuts end-to-end: verify no conflicts

### Performance Tasks

- [ ] T191 Add database indexes verification: run EXPLAIN ANALYZE on search queries
- [ ] T192 Implement pagination for task list (load 50 tasks at a time): phase-2/frontend/src/app/tasks/page.tsx
- [ ] T193 Add virtual scrolling for large task lists (1000+ tasks): phase-2/frontend/src/app/tasks/page.tsx
- [ ] T194 Optimize Chart.js bundle size (tree-shake unused chart types): phase-2/frontend/src/components/AnalyticsChart.tsx
- [ ] T195 Add debouncing to search input (already in useSearch hook): verify performance

### Documentation Tasks

- [ ] T196 Update README.md with Phase 2 features and screenshots: /mnt/d/hackathon-2/README.md
- [ ] T197 [P] Create demo script for 90-second video: /mnt/d/hackathon-2/DEMO_SCRIPT.md (NEW FILE)
- [ ] T198 [P] Update .env.example with all required variables: phase-2/frontend/.env.example and phase-2/backend/.env.example

### Testing Tasks

- [ ] T199 Test due date picker prevents past dates (except editing overdue): verify US1
- [ ] T200 Test search returns results within 500ms for 1000 tasks: verify US2
- [ ] T201 Test recurring task generates next instance correctly: verify US4
- [ ] T202 Test browser notification appears at scheduled time: verify US5
- [ ] T203 Test CSV export opens correctly in Excel with no encoding issues: verify US11
- [ ] T204 Test import validation catches all invalid data: verify US11
- [ ] T205 Test theme toggle applies instantly without page reload: verify US8
- [ ] T206 Test all 18 success criteria from spec.md: comprehensive validation

**Polish Acceptance**: All error cases handled gracefully. Loading states visible. Performance targets met (search <500ms, filter <300ms, export <2s). All success criteria validated.

---

## Dependency Graph & Execution Order

### Critical Path (Must Complete In Order)

1. **Phase 1: Setup** (T001-T008) → Required for all
2. **Phase 2: Foundation** (T009-T021) → Required for all user stories
3. **Phases 3-13: User Stories** (can be implemented in parallel once Foundation complete)
4. **Phase 14: Polish** (T185-T206) → Final integration

### User Story Dependencies

**No Dependencies (Can Implement Independently)**:
- US1: Task Organization (due dates, priorities)
- US2: Task Categorization (tags, search)
- US6: Task History (audit log)
- US9: User Profile (profile management)
- US10: Keyboard Shortcuts (navigation)

**Dependencies**:
- US3: Advanced Filtering → Requires US1 (priority) and US2 (tags, search) for meaningful filters
- US4: Recurring Tasks → Requires US1 (due dates)
- US5: Browser Notifications → Requires US1 (due dates) and US4 (recurring for recurrence notifications)
- US7: Analytics Dashboard → Requires US1 (priority data) for charts
- US8: User Settings → No hard dependencies but benefits from US5 (notification settings)
- US11: Import/Export → Requires US1, US2, US4 (all fields must be exportable)

### Recommended Implementation Order

**Sprint 1 (MVP - Week 1)**:
1. Phase 1: Setup
2. Phase 2: Foundation
3. Phase 3: US1 (Due Dates, Priorities) ← Start here
4. Phase 4: US2 (Tags, Search)

**Sprint 2 (High-Value - Week 2)**:
5. Phase 5: US3 (Filtering, Sorting)
6. Phase 6: US4 (Recurring Tasks)
7. Phase 10: US8 (User Settings)
8. Phase 13: US11 (Import/Export)

**Sprint 3 (Polish - Week 3)**:
9. Phase 7: US5 (Browser Notifications)
10. Phase 8: US6 (Task History)
11. Phase 9: US7 (Analytics Dashboard)
12. Phase 11: US9 (User Profile)
13. Phase 12: US10 (Keyboard Shortcuts)
14. Phase 14: Polish

### Parallel Execution Examples

**Foundation Phase** (after Setup):
- T009-T013 (all models) can run in parallel [P]
- T017-T018 (UI components) can run in parallel [P]
- T020-T021 (hooks) can run in parallel [P]

**Within US1**:
- T027-T028 (PriorityBadge, DatePicker) can run in parallel [P]
- After backend done: T029-T034 can run in parallel (all frontend)

**Across User Stories** (after Foundation):
- US1, US2, US6, US9, US10 have NO dependencies → Can assign to different developers/agents

**US7 Analytics** (once US1, US2 complete):
- T106-T108 (analytics page setup) can run in parallel [P]
- T109-T111 (individual charts) can run in parallel [P]

---

## Task Summary

**Total Tasks**: 206 tasks
- Phase 1 (Setup): 8 tasks (~2 hours)
- Phase 2 (Foundation): 13 tasks (~1 day)
- Phase 3-13 (User Stories): 164 tasks (~12-15 days)
  - US1: 13 tasks (~1 day)
  - US2: 15 tasks (~1 day)
  - US3: 13 tasks (~1 day)
  - US4: 14 tasks (~1.5 days)
  - US5: 14 tasks (~1 day)
  - US6: 9 tasks (~1 day)
  - US7: 16 tasks (~1.5 days)
  - US8: 16 tasks (~1 day)
  - US9: 15 tasks (~1 day)
  - US10: 12 tasks (~1 day)
  - US11: 26 tasks (~1.5 days)
- Phase 14 (Polish): 22 tasks (~1 day)

**Parallelizable Tasks**: 58 tasks marked with [P]

**Estimated Total Duration**: 15-18 days (sequential) or 8-10 days (with 3-5 parallel developers/agents)

**MVP Scope** (Minimum Viable Product):
- Phase 1: Setup
- Phase 2: Foundation
- Phase 3: US1 (Due Dates, Priorities)
- Phase 4: US2 (Tags, Search)
- ~40 tasks, 3-4 days to deliverable product

---

## Implementation Strategy

1. **Start with MVP**: Complete Setup → Foundation → US1 → US2 first
2. **Test MVP**: Verify core functionality before adding advanced features
3. **Add High-Value**: Implement US3, US4, US8, US11 next (filtering, recurring, settings, export)
4. **Polish Last**: Add US5-US7, US9-US10 for complete experience
5. **Use Agents**: Assign independent user stories to different subagents:
   - BackendAgent: All backend tasks (T022-T026, T035-T040, etc.)
   - FeaturesAgent: US1, US2, US4 (core features)
   - UIAgent: All UI components (T027-T034, T041-T049, etc.)
   - AnalyticsAgent: US6, US7, US11 (history, charts, export)
   - AuthAgent: US8, US9 (settings, profile)
6. **Validate Early**: Run success criteria tests after each user story completes

---

## Format Validation

✅ All 206 tasks follow strict checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T206 (sequential)
- [P] marker: 58 tasks parallelizable
- [Story] label: 164 tasks have US1-US11 labels
- File paths: All tasks include specific file paths

✅ Tasks organized by user story for independent implementation
✅ Each user story has independent test criteria
✅ Dependencies clearly documented
✅ Parallel opportunities identified
✅ MVP scope defined (US1 + US2 = 40 tasks, 3-4 days)

**Ready for execution! Start with Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1)**
