# Tasks: Dashboard - Task Management Interface

**Input**: Design documents from `/specs/1-dashboard/`
**Prerequisites**: plan.md (complete), spec.md (complete), data-model.md (complete), contracts/dashboard-api.yaml (complete)

**Tests**: Not required per spec (TDD not explicitly requested for Phase II)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (this project)**: `backend/` and `frontend/` at repository root
- Backend API: Complete (no backend tasks needed)
- Focus: Frontend dashboard enhancement

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure and create new component foundations

- [x] T001 Verify backend server running at http://localhost:8000 (existing)
- [x] T002 Verify frontend dev server running at http://localhost:3000 (existing)
- [x] T003 [P] Verify API client works by testing GET /api/{user_id}/tasks endpoint

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared components that multiple user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create StatsCard component in frontend/components/StatsCard.tsx
- [x] T005 [P] Create ProgressBar component in frontend/components/ProgressBar.tsx
- [x] T006 Verify existing glassmorphism styles work in frontend/app/globals.css

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Dashboard Overview (Priority: P1)

**Goal**: Display comprehensive dashboard with header, stats, and user info when authenticated

**Independent Test**: Login and verify dashboard displays task statistics (total, pending, completed), header with user name/email, and logout button

### Implementation for User Story 1

- [x] T007 [US1] Enhance header section in frontend/app/tasks/page.tsx with user name/email display
- [x] T008 [US1] Add logout button functionality in frontend/app/tasks/page.tsx
- [x] T009 [US1] Add Stats section with 3 StatsCard instances (Total, Pending, Completed) in frontend/app/tasks/page.tsx
- [x] T010 [US1] Integrate StatsCard with task counts from API response in frontend/app/tasks/page.tsx
- [x] T011 [US1] Implement empty state message when no tasks exist in frontend/components/TaskList.tsx

**Checkpoint**: User Story 1 complete - dashboard shows stats and header when logged in

---

## Phase 4: User Story 2 - Add New Task (Priority: P1)

**Goal**: Enable quick task creation from dashboard with validation

**Independent Test**: Fill task form with title, optional description, click Add, verify task appears in list

### Implementation for User Story 2

- [x] T012 [US2] Enhance TaskForm with glassmorphism styling in frontend/components/TaskForm.tsx
- [x] T013 [US2] Add form validation for empty title in frontend/components/TaskForm.tsx
- [x] T014 [US2] Display validation error message when title is empty in frontend/components/TaskForm.tsx
- [x] T015 [US2] Trigger task list refresh after successful task creation in frontend/components/TaskForm.tsx

**Checkpoint**: User Story 2 complete - can add tasks with validation

---

## Phase 5: User Story 3 - View and Filter Task List (Priority: P1)

**Goal**: Display scrollable task list with filter buttons (All/Pending/Completed)

**Independent Test**: View tasks, click filter buttons, verify list updates to show correct subset

### Implementation for User Story 3

- [x] T016 [US3] Enhance TaskList with filter button styling in frontend/components/TaskList.tsx
- [x] T017 [US3] Ensure filter state updates task list correctly in frontend/components/TaskList.tsx
- [x] T018 [US3] Update stats bar to reflect current filter context in frontend/components/TaskList.tsx
- [x] T019 [US3] Add scrollable container for task list in frontend/components/TaskList.tsx

**Checkpoint**: User Story 3 complete - can view and filter tasks

---

## Phase 6: User Story 4 - Toggle Task Completion (Priority: P1)

**Goal**: Toggle task completion status via checkbox with visual feedback

**Independent Test**: Click task checkbox, verify status changes visually (strikethrough) and stats update

### Implementation for User Story 4

- [x] T020 [US4] Enhance TaskItem checkbox with proper styling in frontend/components/TaskItem.tsx
- [x] T021 [US4] Add visual strikethrough for completed tasks in frontend/components/TaskItem.tsx
- [x] T022 [US4] Call toggleComplete API on checkbox click in frontend/components/TaskItem.tsx
- [x] T023 [US4] Trigger stats refresh after completion toggle in frontend/components/TaskItem.tsx

**Checkpoint**: User Story 4 complete - can toggle task completion

---

## Phase 7: User Story 5 - Edit Task (Priority: P2)

**Goal**: Enable inline editing of task title and description

**Independent Test**: Click edit button, modify fields, save, verify changes persist

### Implementation for User Story 5

- [x] T024 [US5] Add edit mode state to TaskItem in frontend/components/TaskItem.tsx
- [x] T025 [US5] Create editable input fields for title and description in frontend/components/TaskItem.tsx
- [x] T026 [US5] Add Save and Cancel buttons in edit mode in frontend/components/TaskItem.tsx
- [x] T027 [US5] Call updateTask API on save in frontend/components/TaskItem.tsx
- [x] T028 [US5] Reset to original values on cancel in frontend/components/TaskItem.tsx

**Checkpoint**: User Story 5 complete - can edit tasks

---

## Phase 8: User Story 6 - Delete Task (Priority: P2)

**Goal**: Delete tasks with confirmation dialog

**Independent Test**: Click delete, see confirmation, confirm, verify task removed and stats update

### Implementation for User Story 6

- [x] T029 [US6] Add delete confirmation state to TaskItem in frontend/components/TaskItem.tsx
- [x] T030 [US6] Display confirmation prompt when delete clicked in frontend/components/TaskItem.tsx
- [x] T031 [US6] Call deleteTask API on confirm in frontend/components/TaskItem.tsx
- [x] T032 [US6] Keep task if user cancels deletion in frontend/components/TaskItem.tsx

**Checkpoint**: User Story 6 complete - can delete tasks with confirmation

---

## Phase 9: User Story 7 - Progress Visualization (Priority: P2)

**Goal**: Display animated progress bar showing completion percentage

**Independent Test**: View dashboard with tasks, verify progress bar percentage matches completed/total ratio

### Implementation for User Story 7

- [x] T033 [US7] Integrate ProgressBar component into dashboard in frontend/app/tasks/page.tsx
- [x] T034 [US7] Calculate completion percentage from task counts in frontend/app/tasks/page.tsx
- [x] T035 [US7] Add CSS animation for progress bar fill in frontend/components/ProgressBar.tsx
- [x] T036 [US7] Handle 0 tasks case (show 0% or hide bar) in frontend/components/ProgressBar.tsx

**Checkpoint**: User Story 7 complete - progress bar shows completion rate

---

## Phase 10: User Story 8 - Responsive Design (Priority: P3)

**Goal**: Dashboard works on mobile (320px+), tablet, and desktop

**Independent Test**: View dashboard at different viewport widths, verify layout adapts appropriately

### Implementation for User Story 8

- [x] T037 [US8] Add responsive Tailwind classes to StatsCard grid in frontend/app/tasks/page.tsx
- [x] T038 [US8] Make TaskForm responsive in frontend/components/TaskForm.tsx
- [x] T039 [US8] Make TaskItem responsive in frontend/components/TaskItem.tsx
- [x] T040 [US8] Test and adjust layout at 320px, 640px, 1024px breakpoints

**Checkpoint**: User Story 8 complete - dashboard is responsive

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T041 [P] Verify all glassmorphism styling consistent across components
- [x] T042 [P] Add error states with retry option for API failures in frontend/components/TaskList.tsx
- [x] T043 Add loading states during API calls in frontend/components/TaskList.tsx
- [x] T044 Run quickstart.md validation - test complete user flow
- [x] T045 Verify user isolation - logged-in user only sees their tasks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-10)**: All depend on Foundational completion
  - P1 stories (US1-US4) are highest priority
  - P2 stories (US5-US7) follow P1 completion
  - P3 story (US8) follows P2 completion
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Can Start After |
|-------|----------|------------|-----------------|
| US1 (Dashboard Overview) | P1 | Foundational | Phase 2 |
| US2 (Add Task) | P1 | Foundational | Phase 2 |
| US3 (Filter Tasks) | P1 | Foundational | Phase 2 |
| US4 (Toggle Completion) | P1 | Foundational | Phase 2 |
| US5 (Edit Task) | P2 | US1-US4 | Phase 6 |
| US6 (Delete Task) | P2 | US1-US4 | Phase 6 |
| US7 (Progress Bar) | P2 | US1-US4 | Phase 6 |
| US8 (Responsive) | P3 | US1-US7 | Phase 9 |

### Within Each User Story

- Component enhancements before integration
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational):**
```
T004 (StatsCard) || T005 (ProgressBar) || T006 (verify styles)
```

**P1 Stories (after Foundational):**
```
US1, US2, US3, US4 can be worked in parallel if needed
```

**Polish Phase:**
```
T041 (styling) || T042 (error states)
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006)
3. Complete Phases 3-6: P1 User Stories (T007-T023)
4. **STOP and VALIDATE**: Test all P1 stories independently
5. Deploy/demo MVP with basic CRUD + stats

### Full Implementation

1. Complete MVP (above)
2. Add Phase 7-9: P2 User Stories (T024-T036)
3. Add Phase 10: P3 User Story (T037-T040)
4. Complete Phase 11: Polish (T041-T045)
5. Final validation and demo

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 45 |
| **Setup Tasks** | 3 |
| **Foundational Tasks** | 3 |
| **US1 Tasks** | 5 |
| **US2 Tasks** | 4 |
| **US3 Tasks** | 4 |
| **US4 Tasks** | 4 |
| **US5 Tasks** | 5 |
| **US6 Tasks** | 4 |
| **US7 Tasks** | 4 |
| **US8 Tasks** | 4 |
| **Polish Tasks** | 5 |

**MVP Scope**: Phases 1-6 (T001-T023) - 23 tasks
**Full Scope**: All phases (T001-T045) - 45 tasks

---

## Notes

- Backend API is complete - no backend tasks needed
- Focus is on frontend dashboard enhancement
- Existing components (TaskForm, TaskList, TaskItem) need enhancement, not rewrite
- New components (StatsCard, ProgressBar) need to be created
- All tasks reference exact file paths per plan.md structure
- Commit after each task or logical group
