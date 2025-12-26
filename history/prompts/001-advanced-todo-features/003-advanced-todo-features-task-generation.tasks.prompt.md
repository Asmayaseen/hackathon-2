---
id: 003
title: Advanced Todo Features Task Breakdown
stage: tasks
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5
feature: 001-advanced-todo-features
branch: 001-advanced-todo-features
user: system
command: /sp.tasks
labels: ["task-breakdown", "implementation-tasks", "user-stories", "mvp-planning"]
links:
  spec: specs/001-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-advanced-todo-features/tasks.md
tests:
  - Task format validation (all 127 tasks follow checklist format)
  - User story organization (5 phases for P1-P5)
  - Dependency graph validation
  - Independent test criteria verification
---

## Prompt

/sp.tasks

(No additional arguments provided - executed from specification and planning artifacts)

## Response snapshot

Generated comprehensive task breakdown for Advanced Todo Features following Spec-Driven Development workflow Phase 2 (Task Generation).

### Task Breakdown Generated

**File**: `tasks.md` (627 lines)

**Total Tasks**: 127

**By Phase**:
- **Phase 1 (Setup)**: 4 tasks - Environment verification
- **Phase 2 (Foundation)**: 10 tasks - Core TodoItem model extensions (5 new fields, 2 validators)
- **Phase 3 (US1 - Priorities & Tags)**: 23 tasks - Task organization with filtering
- **Phase 4 (US2 - Search & Filter)**: 20 tasks - Keyword search and multi-criteria filtering
- **Phase 5 (US3 - Sort)**: 18 tasks - Dynamic sorting by multiple fields
- **Phase 6 (US4 - Due Dates & Reminders)**: 19 tasks - Time management with console notifications
- **Phase 7 (US5 - Recurring Tasks)**: 22 tasks - Auto-generation of recurring task instances
- **Phase 8 (Polish)**: 11 tasks - Documentation, integration, final validation

**By Type**:
- Setup/Infrastructure: 14 tasks (11%)
- Model/Business Logic: 28 tasks (22%)
- CLI Implementation: 45 tasks (35%)
- Tests: 40 tasks (31%) - RECOMMENDED but optional per constitution

### Task Format Compliance

✅ **All 127 tasks follow strict checklist format**:
- Checkbox: `- [ ]` prefix
- Task ID: Sequential T001-T127
- [P] marker: 45 tasks parallelizable (35%)
- [Story] label: US1-US5 for user story phases
- File paths: Exact paths specified (src/core/, src/ui/, tests/)

**Examples**:
- `- [ ] T005 [P] Add priority field to TodoItem model in src/core/todo_item.py`
- `- [ ] T019 [P] [US1] Extend add_todo method in src/core/todo_manager.py`
- `- [ ] T050 [US2] Implement search CLI command in src/ui/cli.py`

### User Story Organization

**5 Independent User Stories** (mapped from spec.md):

1. **US1 (P1) - Task Organization** (23 tasks):
   - Goal: Priorities (high/medium/low) + Tags (categories)
   - MVP Scope: Deploy after this story
   - Independent Test: Create/filter tasks by priority and tags
   - Files: todo_item.py, todo_manager.py, cli.py

2. **US2 (P2) - Search & Filter** (20 tasks):
   - Goal: Keyword search + multi-criteria filtering
   - Depends on: US1 (needs priority/tags to filter by)
   - Independent Test: Search "meeting", apply combined filters
   - Files: todo_manager.py (filter_todos method), cli.py (search command)

3. **US3 (P3) - Sort Tasks** (18 tasks):
   - Goal: Sort by priority/due_date/created_at/title
   - Depends on: US2 (sorting enhances filtered results)
   - Independent Test: Sort by each criterion, verify order
   - Files: todo_manager.py (sort_todos method), cli.py (sort options)

4. **US4 (P4) - Due Dates & Reminders** (19 tasks):
   - Goal: ISO 8601 due dates + 30-minute console reminders
   - Independent: Can implement in parallel with US1-US3
   - Independent Test: Set due date, verify reminder notification
   - Files: todo_item.py (due_date field), todo_manager.py (check_reminders), cli.py

5. **US5 (P5) - Recurring Tasks** (22 tasks):
   - Goal: Auto-generate daily/weekly/monthly recurring instances
   - Depends on: US4 (recurring requires due_date field)
   - Independent Test: Complete recurring task, verify auto-create
   - Files: todo_item.py (recurrence fields), todo_manager.py (complete_todo), cli.py

### Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Foundation - BLOCKING)
                       ↓
    ┌──────────────────┴──────────────────┐
    ↓                  ↓                  ↓
  US1 (P1)           US4 (P4)      [Independent tracks]
    ↓                  ↓
  US2 (P2)           US5 (P5)
    ↓              [Requires US4]
  US3 (P3)
[Requires US2]

Phase 8 (Polish - after all user stories)
```

### Execution Strategies

**MVP Approach** (Fastest value delivery):
1. Phase 1 + Phase 2 (Foundation) → 14 tasks
2. **Phase 3 (US1 only)** → 23 tasks
3. **Deploy MVP** with priorities and tags (37 tasks total, ~5 hours)
4. Continue with US2→US3→US4→US5 post-MVP

**Parallel Tracks** (Aggressive):
1. Phase 1 + Phase 2 → 14 tasks
2. **Track 1**: US1 (23 tasks) | **Track 2**: US4 (19 tasks) [Parallel]
3. **Track 1**: US2 (20 tasks) | **Track 2**: US5 (22 tasks) [Parallel]
4. US3 (18 tasks) → Phase 8 (11 tasks)

**Sequential Safe** (No risk):
1. Phase 1 → Phase 2 → US1 → US2 → US3 → US4 → US5 → Phase 8

### Independent Test Criteria

Each user story includes complete test verification:

**US1**:
```bash
uv run python main.py add "Task" -p high -t "work,urgent"
uv run python main.py list -p high -t work
```

**US2**:
```bash
uv run python main.py search "meeting"
uv run python main.py list -s pending -p high -t work --keyword "report"
```

**US3**:
```bash
uv run python main.py list --sort-by priority --order desc
uv run python main.py list --sort-by due_date
```

**US4**:
```bash
uv run python main.py add "Call" --due-date "2025-12-26 14:30"
uv run python main.py list  # Shows reminder if within 30 min
```

**US5**:
```bash
uv run python main.py add "Weekly sync" --due-date "2025-12-27 10:00" -r weekly
uv run python main.py complete 1  # Auto-creates next instance
```

### Key Highlights

**Parallelization Opportunities**:
- Foundation phase: 9/10 tasks marked [P] (can run simultaneously)
- Per user story: ~50% tasks marked [P] (tests, different files)
- After Foundation: 2 independent tracks (US1→US2→US3 | US4→US5)

**Test Coverage**:
- 40 test tasks (31% of total)
- Marked RECOMMENDED but optional (constitution: spec doesn't mandate TDD)
- Extends existing 91 Phase I tests
- Organized by feature area (TestTodoItemPriority, TestTodoManagerSearch, etc.)

**File Modifications**:
- `src/core/todo_item.py`: +5 fields, +2 validators (T005-T012)
- `src/core/todo_manager.py`: +3 methods (filter/sort/check_reminders)
- `src/ui/cli.py`: Extend add/list/update, add search command
- `tests/test_*.py`: +10 new test classes

**Validation**:
- All 30 functional requirements (FR-001 to FR-030) mapped to tasks
- All 5 user stories (P1-P5) have complete task coverage
- All acceptance scenarios testable via task outputs
- MVP scope clearly defined (US1 only = 37 tasks)

### Estimated Effort

**Total**: 15-20 hours for complete implementation

**By Phase**:
- Foundation: 2-3 hours (critical path, blocking)
- Each User Story: 3-4 hours (with tests)
- Polish: 2 hours (documentation, validation)

**MVP (US1 only)**: ~5 hours
- Foundation (2-3h) + US1 (3-4h) = 5-7 hours
- Delivers immediate value: task organization with priorities and tags

### Next Steps

**Ready for Implementation**: `/sp.implement` or manual implementation

**Execution Order**:
1. Start with Phase 1 (Setup): T001-T004 (verify environment)
2. Complete Phase 2 (Foundation): T005-T014 (extend TodoItem model) - BLOCKING
3. Choose execution strategy:
   - **MVP**: Implement US1 only (T015-T037), deploy, iterate
   - **Parallel**: US1 + US4 simultaneously, then US2 + US5
   - **Sequential**: US1 → US2 → US3 → US4 → US5

**Each task includes**:
- Exact file path to modify
- Clear acceptance criteria
- Dependencies (if any)
- Parallelization marker ([P])
- User story mapping ([US1-US5])

## Outcome

- ✅ Impact: Complete task breakdown for implementing all 30 functional requirements across 5 user stories. Enables independent, testable delivery of each feature increment. MVP scope defined for rapid value delivery.
- 🧪 Tests: Format validation PASS (all 127 tasks follow checklist format), Organization validation PASS (5 user story phases), Dependency validation PASS (graph shows correct dependencies), Independent test criteria PASS (each story testable standalone)
- 📁 Files: Created tasks.md (627 lines, 127 tasks organized by user story)
- 🔁 Next prompts: Run `/sp.implement` to begin implementation, OR manually execute tasks starting with T001 (Setup). Recommend MVP approach (Foundation + US1 only) for fastest value delivery.
- 🧠 Reflection: Successfully applied Spec-Driven Development Phase 2 workflow. Organized tasks by user story (not by layer) to enable independent implementation and testing. Clear parallelization markers and dependency graph. Tests marked optional per constitution but recommended for quality. Each user story deliverable as standalone increment.

## Evaluation notes (flywheel)

- Failure modes observed: None. All tasks follow strict checklist format. User stories properly organized from spec.md priorities (P1-P5). Dependencies correctly identified (US2→US1, US3→US2, US5→US4).
- Graders run and results (PASS/FAIL): Format Validation - PASS (127/127 tasks have checkbox + ID + description + file path), Story Organization - PASS (5 phases for 5 user stories), Dependency Graph - PASS (US1/US4 independent, US2→US1, US3→US2, US5→US4), Independent Test Criteria - PASS (each story has bash examples)
- Prompt variant (if applicable): Standard /sp.tasks workflow with user story organization
- Next experiment (smallest change to try): Proceed to implementation (manual or `/sp.implement`). Test MVP approach: implement Foundation + US1 only (37 tasks), verify deliverable value before continuing.
