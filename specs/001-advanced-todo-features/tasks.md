# Tasks: Advanced Todo Features

**Input**: Design documents from `/specs/001-advanced-todo-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-commands.md

**Tests**: Tests are RECOMMENDED but OPTIONAL per constitution (spec does not mandate TDD). Phase I has 91 existing tests - extending test coverage is advised for quality assurance.

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: Always `- [ ]` at start
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5) - only for user story phases
- **File path**: Always include exact file path in description

## Path Conventions

Single project structure:
- Core business logic: `src/core/`
- CLI interface: `src/ui/`
- Tests: `tests/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and dependencies

- [ ] T001 Verify Python 3.12+ and UV package manager installed
- [ ] T002 Run `uv sync` to ensure all dependencies (Pydantic 2.0+, Typer 0.15+, Rich 13.7+) are installed
- [ ] T003 Verify existing Phase I codebase structure (src/core/, src/ui/, tests/)
- [ ] T004 Run existing tests to establish baseline (`uv run pytest` should show 91 passing tests)

**Checkpoint**: Environment verified - ready to extend Phase I codebase

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model extensions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Add `priority` field to TodoItem model in src/core/todo_item.py (Literal["high", "medium", "low"], default="medium")
- [ ] T006 [P] Add `tags` field to TodoItem model in src/core/todo_item.py (list[str], default_factory=list)
- [ ] T007 [P] Add `due_date` field to TodoItem model in src/core/todo_item.py (datetime | None, default=None)
- [ ] T008 [P] Add `recurrence_pattern` field to TodoItem model in src/core/todo_item.py (Literal["daily", "weekly", "monthly"] | None, default=None)
- [ ] T009 [P] Add `recurrence_parent_id` field to TodoItem model in src/core/todo_item.py (int | None, default=None)
- [ ] T010 Implement `validate_tags` field validator in src/core/todo_item.py (max 10 tags, lowercase, alphanumeric + hyphens)
- [ ] T011 Implement `validate_recurrence` field validator in src/core/todo_item.py (recurrence requires due_date)
- [ ] T012 Update TodoItem ConfigDict json_schema_extra with example including all new fields
- [ ] T013 Run `uv run mypy src/core/todo_item.py --strict` to verify type safety
- [ ] T014 Update existing TodoItem tests to use new field defaults (tests/test_todo_item.py)

**Checkpoint**: Foundation ready - TodoItem model extended with all new fields, validation working

---

## Phase 3: User Story 1 - Task Organization (Priorities & Tags) (Priority: P1) 🎯 MVP

**Goal**: Enable users to organize tasks by assigning priority levels (high/medium/low) and category tags for filtering and grouping.

**Independent Test**: Create tasks with different priorities and tags, then filter by priority or tags. Tasks display with priority indicators and tag labels.

**Acceptance Criteria**:
1. Can create task with priority="high" and tags=["work", "urgent"]
2. Can list only high-priority tasks (`list -p high`)
3. Can filter by single tag (`list -t work`)
4. Can filter by multiple tags with AND logic (`list -t "work,urgent"`)
5. Can update task priority and tags

### Tests for User Story 1 (RECOMMENDED for Quality Assurance)

- [ ] T015 [P] [US1] Add TestTodoItemPriority class in tests/test_todo_item.py (test default="medium", valid values, invalid values)
- [ ] T016 [P] [US1] Add TestTodoItemTags class in tests/test_todo_item.py (test tag normalization, max 10 tags, empty tags)
- [ ] T017 [P] [US1] Add TestTodoManagerFilterByPriority class in tests/test_todo_manager.py (test filtering by high/medium/low)
- [ ] T018 [P] [US1] Add TestTodoManagerFilterByTags class in tests/test_todo_manager.py (test single tag, multiple tags AND logic)

### Implementation for User Story 1

- [ ] T019 [P] [US1] Extend `add_todo` method in src/core/todo_manager.py to accept priority and tags parameters
- [ ] T020 [P] [US1] Extend `update_todo` method in src/core/todo_manager.py to accept priority and tags parameters
- [ ] T021 [US1] Implement priority-based filtering in `list_todos` method in src/core/todo_manager.py (add optional priority parameter)
- [ ] T022 [US1] Implement tag-based filtering in `list_todos` method in src/core/todo_manager.py (add optional tags parameter with AND logic)
- [ ] T023 [US1] Extend `add` CLI command in src/ui/cli.py with `--priority/-p` option (validate high/medium/low)
- [ ] T024 [US1] Extend `add` CLI command in src/ui/cli.py with `--tags/-t` option (comma-separated input)
- [ ] T025 [US1] Extend `list` CLI command in src/ui/cli.py with `--priority/-p` filter option
- [ ] T026 [US1] Extend `list` CLI command in src/ui/cli.py with `--tags/-t` filter option (parse comma-separated, apply AND logic)
- [ ] T027 [US1] Extend `update` CLI command in src/ui/cli.py with `--priority` option
- [ ] T028 [US1] Extend `update` CLI command in src/ui/cli.py with `--tags` option (replaces existing tags)
- [ ] T029 [US1] Add Priority column to Rich table in src/ui/cli.py list command (color: high=red, medium=yellow, low=green)
- [ ] T030 [US1] Add Tags column to Rich table in src/ui/cli.py list command (display with #tag format)
- [ ] T031 [US1] Update `add` command output in src/ui/cli.py to display priority and tags
- [ ] T032 [P] [US1] Add TestCliAddWithPriority class in tests/test_cli.py (test --priority option, validation)
- [ ] T033 [P] [US1] Add TestCliAddWithTags class in tests/test_cli.py (test --tags option, comma-separated parsing)
- [ ] T034 [P] [US1] Add TestCliListFilterByPriority class in tests/test_cli.py (test -p high/medium/low)
- [ ] T035 [P] [US1] Add TestCliListFilterByTags class in tests/test_cli.py (test -t single and multiple tags)
- [ ] T036 [US1] Run `uv run mypy src/ --strict` to verify type safety for US1 changes
- [ ] T037 [US1] Run US1-specific tests: `uv run pytest tests/test_todo_item.py::TestTodoItemPriority tests/test_todo_item.py::TestTodoItemTags -v`

**Checkpoint**: User Story 1 complete - users can organize tasks with priorities and tags, filter by both criteria

---

## Phase 4: User Story 2 - Search and Filter Tasks (Priority: P2)

**Goal**: Enable users to search tasks by keyword and apply multi-criteria filters (status, priority, tags, date range) to quickly find specific tasks.

**Independent Test**: Create 20+ tasks with varied attributes, search for keyword "meeting", apply combined filters (status + priority + tags), verify results match all criteria.

**Acceptance Criteria**:
1. Can search for "meeting" and get all tasks with keyword in title or description
2. Can filter by date range (--from-date, --to-date)
3. Can combine multiple filters (AND logic) - e.g., status=pending + priority=high + tags=work
4. Search is case-insensitive
5. Empty results show clear "No tasks found" message with filter criteria

### Tests for User Story 2 (RECOMMENDED)

- [ ] T038 [P] [US2] Add TestTodoManagerSearch class in tests/test_todo_manager.py (test keyword search in title/description, case-insensitive)
- [ ] T039 [P] [US2] Add TestTodoManagerFilterMultiCriteria class in tests/test_todo_manager.py (test combining status + priority + tags + date range)
- [ ] T040 [P] [US2] Add TestTodoManagerFilterByDateRange class in tests/test_todo_manager.py (test --from-date and --to-date filtering)

### Implementation for User Story 2

- [ ] T041 [US2] Implement `filter_todos` method in src/core/todo_manager.py (keyword, status, priority, tags, date_from, date_to parameters)
- [ ] T042 [US2] Implement keyword search logic in `filter_todos` (case-insensitive substring match in title and description)
- [ ] T043 [US2] Implement date range filtering logic in `filter_todos` (filter by created_at between dates)
- [ ] T044 [US2] Implement AND logic for combining all filter criteria in `filter_todos`
- [ ] T045 [US2] Extend `list` CLI command in src/ui/cli.py with `--keyword/-k` option
- [ ] T046 [US2] Extend `list` CLI command in src/ui/cli.py with `--from-date` option (YYYY-MM-DD format)
- [ ] T047 [US2] Extend `list` CLI command in src/ui/cli.py with `--to-date` option (YYYY-MM-DD format)
- [ ] T048 [US2] Update `list` CLI command to call `filter_todos` method instead of `list_todos` when filters specified
- [ ] T049 [US2] Add filter criteria summary display in `list` command output (show active filters above table)
- [ ] T050 [US2] Implement `search` CLI command in src/ui/cli.py (keyword argument + optional status/priority/tags filters)
- [ ] T051 [US2] Handle empty results in `list` and `search` commands - display "No tasks found" with filter criteria
- [ ] T052 [P] [US2] Add TestCliSearch class in tests/test_cli.py (test search command with keyword and filters)
- [ ] T053 [P] [US2] Add TestCliListWithKeyword class in tests/test_cli.py (test --keyword option)
- [ ] T054 [P] [US2] Add TestCliListWithDateRange class in tests/test_cli.py (test --from-date and --to-date options)
- [ ] T055 [P] [US2] Add TestCliListCombinedFilters class in tests/test_cli.py (test multiple filters together)
- [ ] T056 [US2] Run `uv run mypy src/ --strict` to verify type safety for US2 changes
- [ ] T057 [US2] Run US2-specific tests: `uv run pytest tests/test_todo_manager.py::TestTodoManagerSearch tests/test_cli.py::TestCliSearch -v`

**Checkpoint**: User Story 2 complete - users can search by keyword and apply complex multi-criteria filters

---

## Phase 5: User Story 3 - Sort Tasks (Priority: P3)

**Goal**: Enable users to sort task lists by different criteria (priority, due_date, created_at, title) in ascending or descending order.

**Independent Test**: Create tasks with varied priorities, due dates, and titles. Sort by each criterion and verify correct order (e.g., priority: high→medium→low, due_date: earliest→latest with nulls last).

**Acceptance Criteria**:
1. Can sort by priority (high first when desc, low first when asc)
2. Can sort by due_date (earliest first, null dates always last)
3. Can sort by created_at (newest or oldest first)
4. Can sort by title (A-Z or Z-A)
5. Can specify sort order (asc or desc)

### Tests for User Story 3 (RECOMMENDED)

- [ ] T058 [P] [US3] Add TestTodoManagerSortByPriority class in tests/test_todo_manager.py (test priority order high→medium→low)
- [ ] T059 [P] [US3] Add TestTodoManagerSortByDueDate class in tests/test_todo_manager.py (test earliest first, null dates last)
- [ ] T060 [P] [US3] Add TestTodoManagerSortByCreatedAt class in tests/test_todo_manager.py (test newest/oldest first)
- [ ] T061 [P] [US3] Add TestTodoManagerSortByTitle class in tests/test_todo_manager.py (test alphabetical A-Z and Z-A)

### Implementation for User Story 3

- [ ] T062 [US3] Implement `sort_todos` method in src/core/todo_manager.py (sort_by, sort_order parameters)
- [ ] T063 [US3] Implement priority sorting logic in `sort_todos` (high=0, medium=1, low=2 mapping)
- [ ] T064 [US3] Implement due_date sorting logic in `sort_todos` (use datetime.max for null dates)
- [ ] T065 [US3] Implement created_at and title sorting logic in `sort_todos` (use getattr for dynamic field access)
- [ ] T066 [US3] Extend `list` CLI command in src/ui/cli.py with `--sort-by` option (priority/due_date/created_at/title, default=created_at)
- [ ] T067 [US3] Extend `list` CLI command in src/ui/cli.py with `--order` option (asc/desc, default=asc)
- [ ] T068 [US3] Validate sort_by parameter against allowed fields in `list` CLI command
- [ ] T069 [US3] Update `list` CLI command to call `sort_todos` after filtering
- [ ] T070 [US3] Add sort indicator display in `list` command output (show "Sorted by: field (order)" below table)
- [ ] T071 [P] [US3] Add TestCliListSortByPriority class in tests/test_cli.py (test --sort-by priority with --order asc/desc)
- [ ] T072 [P] [US3] Add TestCliListSortByDueDate class in tests/test_cli.py (test --sort-by due_date)
- [ ] T073 [P] [US3] Add TestCliListSortByTitle class in tests/test_cli.py (test --sort-by title)
- [ ] T074 [US3] Run `uv run mypy src/ --strict` to verify type safety for US3 changes
- [ ] T075 [US3] Run US3-specific tests: `uv run pytest tests/test_todo_manager.py::TestTodoManagerSort* -v`

**Checkpoint**: User Story 3 complete - users can sort tasks by multiple criteria with flexible ordering

---

## Phase 6: User Story 4 - Due Dates and Reminders (Priority: P4)

**Goal**: Enable users to set due dates with times for tasks and receive console-based reminder notifications for tasks due within 30 minutes.

**Independent Test**: Create task with due date 25 minutes in future, run list command, verify reminder notification appears. Create task with past due date, verify "OVERDUE" indicator.

**Acceptance Criteria**:
1. Can add task with due_date in ISO 8601 format (YYYY-MM-DD HH:MM)
2. Due dates display in human-readable format (MMM DD, YYYY H:MMAM/PM)
3. Overdue tasks marked with red bold "OVERDUE!" indicator
4. Console notifications appear for tasks due within 30 minutes
5. Reminders checked on app startup and during list operations

### Tests for User Story 4 (RECOMMENDED)

- [ ] T076 [P] [US4] Add TestTodoItemDueDates class in tests/test_todo_item.py (test due_date field, datetime parsing)
- [ ] T077 [P] [US4] Add TestTodoManagerReminders class in tests/test_todo_manager.py (test check_reminders method, 30-minute window)
- [ ] T078 [P] [US4] Add TestTodoManagerOverdue class in tests/test_todo_manager.py (test overdue detection logic)

### Implementation for User Story 4

- [ ] T079 [US4] Extend `add_todo` method in src/core/todo_manager.py to accept due_date parameter
- [ ] T080 [US4] Extend `update_todo` method in src/core/todo_manager.py to accept due_date parameter
- [ ] T081 [US4] Implement `check_reminders` method in src/core/todo_manager.py (return tasks due within 30 minutes)
- [ ] T082 [US4] Extend `add` CLI command in src/ui/cli.py with `--due-date` option (YYYY-MM-DD HH:MM format)
- [ ] T083 [US4] Implement date parsing logic in `add` CLI command (strptime with ISO 8601 format, error handling)
- [ ] T084 [US4] Extend `update` CLI command in src/ui/cli.py with `--due-date` option (support "none" to clear)
- [ ] T085 [US4] Add Due Date column to Rich table in src/ui/cli.py list command (human-readable format)
- [ ] T086 [US4] Implement overdue indicator logic in `list` CLI command (red bold for past due dates)
- [ ] T087 [US4] Implement reminder notification display in `list` CLI command (call check_reminders, display before table)
- [ ] T088 [US4] Add reminder check to app startup in src/ui/cli.py (check on first command execution)
- [ ] T089 [US4] Update `add` command output to display due_date if specified
- [ ] T090 [P] [US4] Add TestCliAddWithDueDate class in tests/test_cli.py (test --due-date option, format validation)
- [ ] T091 [P] [US4] Add TestCliListReminders class in tests/test_cli.py (test reminder notifications displayed)
- [ ] T092 [P] [US4] Add TestCliListOverdue class in tests/test_cli.py (test overdue indicator displayed)
- [ ] T093 [US4] Run `uv run mypy src/ --strict` to verify type safety for US4 changes
- [ ] T094 [US4] Run US4-specific tests: `uv run pytest tests/test_todo_manager.py::TestTodoManagerReminders -v`

**Checkpoint**: User Story 4 complete - users can set due dates and receive timely console reminders

---

## Phase 7: User Story 5 - Recurring Tasks (Priority: P5)

**Goal**: Enable users to create tasks that automatically repeat on a schedule (daily/weekly/monthly), auto-generating new instances when marked complete.

**Independent Test**: Create weekly recurring task with due date, mark complete, verify new instance auto-created with next week's due date and status reset to pending.

**Acceptance Criteria**:
1. Can add task with recurrence pattern (daily/weekly/monthly) and due_date
2. Validation enforces: recurrence requires due_date
3. Completing recurring task auto-creates next instance with calculated due_date
4. New instance inherits: title, description, priority, tags, recurrence_pattern
5. New instance resets: status=pending, new id/created_at/updated_at, sets recurrence_parent_id

### Tests for User Story 5 (RECOMMENDED)

- [ ] T095 [P] [US5] Add TestTodoItemRecurrence class in tests/test_todo_item.py (test recurrence_pattern field, validation requires due_date)
- [ ] T096 [P] [US5] Add TestTodoManagerRecurring class in tests/test_todo_manager.py (test auto-create on complete, due_date calculation)
- [ ] T097 [P] [US5] Add TestTodoManagerRecurringDaily class in tests/test_todo_manager.py (test daily recurrence: due_date + 1 day)
- [ ] T098 [P] [US5] Add TestTodoManagerRecurringWeekly class in tests/test_todo_manager.py (test weekly recurrence: due_date + 7 days)
- [ ] T099 [P] [US5] Add TestTodoManagerRecurringMonthly class in tests/test_todo_manager.py (test monthly recurrence: same day next month)

### Implementation for User Story 5

- [ ] T100 [US5] Extend `add_todo` method in src/core/todo_manager.py to accept recurrence_pattern parameter
- [ ] T101 [US5] Extend `update_todo` method in src/core/todo_manager.py to accept recurrence_pattern parameter
- [ ] T102 [US5] Extend `complete_todo` method in src/core/todo_manager.py to check for recurrence_pattern
- [ ] T103 [US5] Implement recurrence logic in `complete_todo`: calculate next due_date based on pattern (daily/weekly/monthly)
- [ ] T104 [US5] Implement auto-create logic in `complete_todo`: create new TodoItem with inherited fields and reset fields
- [ ] T105 [US5] Set recurrence_parent_id in new instance to link back to completed task
- [ ] T106 [US5] Extend `add` CLI command in src/ui/cli.py with `--recurrence/-r` option (daily/weekly/monthly)
- [ ] T107 [US5] Add validation in `add` CLI command: recurrence requires --due-date
- [ ] T108 [US5] Extend `update` CLI command in src/ui/cli.py with `--recurrence/-r` option (support "none" to remove)
- [ ] T109 [US5] Update `complete` CLI command output to display auto-create notification with next instance details
- [ ] T110 [US5] Add Recurrence column to Rich table in src/ui/cli.py list command (show pattern or "None")
- [ ] T111 [US5] Update `add` command output to display recurrence_pattern if specified
- [ ] T112 [P] [US5] Add TestCliAddWithRecurrence class in tests/test_cli.py (test --recurrence option, validation)
- [ ] T113 [P] [US5] Add TestCliCompleteRecurring class in tests/test_cli.py (test auto-create notification displayed)
- [ ] T114 [P] [US5] Add TestCliListRecurrence class in tests/test_cli.py (test recurrence column displayed)
- [ ] T115 [US5] Run `uv run mypy src/ --strict` to verify type safety for US5 changes
- [ ] T116 [US5] Run US5-specific tests: `uv run pytest tests/test_todo_manager.py::TestTodoManagerRecurring* -v`

**Checkpoint**: User Story 5 complete - users can create recurring tasks with automatic instance generation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality assurance

- [ ] T117 [P] Update README.md with new features documentation (priorities, tags, search, filter, sort, due dates, reminders, recurring tasks)
- [ ] T118 [P] Update README.md with usage examples for all new CLI options
- [ ] T119 [P] Create demo workflow script in test_cli_workflow_advanced.py showcasing all features
- [ ] T120 Update CLI help text for all commands with new options (`--help` flag descriptions)
- [ ] T121 Run full test suite: `uv run pytest -v` (expect 91+ tests passing)
- [ ] T122 Run type checking: `uv run mypy src/ --strict` (expect 0 errors)
- [ ] T123 Run test coverage report: `uv run pytest --cov=src --cov-report=term-missing` (verify new features covered)
- [ ] T124 Manual acceptance testing: Execute all 25+ acceptance scenarios from spec.md
- [ ] T125 Performance validation: Create 1000 tasks, verify search/filter <1s, sort <500ms (SC-002, SC-004)
- [ ] T126 Create quickstart guide with common workflows (already exists at specs/001-advanced-todo-features/quickstart.md - verify examples work)
- [ ] T127 Final verification: Run demo workflow and ensure all features work end-to-end

**Checkpoint**: All features implemented, tested, documented - ready for production use

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation)
                       ↓
    ┌──────────────────┴──────────────────┐
    ↓                  ↓                  ↓
  US1 (P1)           US4 (P4)         [Independent]
    ↓                  ↓
  US2 (P2)           US5 (P5)
    ↓               [Depends on US4]
  US3 (P3)
 [Depends on US2]
```

**Dependency Rules**:
- **US1 (Priorities & Tags)**: Independent - can start after Foundation
- **US2 (Search & Filter)**: Depends on US1 (needs priority and tags to filter by)
- **US3 (Sort)**: Depends on US2 (sorting works best with filtering capability)
- **US4 (Due Dates & Reminders)**: Independent - can start after Foundation
- **US5 (Recurring Tasks)**: Depends on US4 (recurring tasks require due_date field)

### Parallel Execution Opportunities

**After Phase 2 (Foundation) completes**, these can run in parallel:
- **Track 1**: US1 → US2 → US3 (Organization → Search → Sort)
- **Track 2**: US4 → US5 (Due Dates → Recurring Tasks)

**Within each User Story**, tasks marked [P] can run in parallel:
- Model tests can run parallel to manager tests
- CLI tests can run parallel to model/manager tests
- Different CLI commands can be extended in parallel

### Suggested Execution Order

**MVP Approach** (Minimum Viable Product):
1. Phase 1 + Phase 2 (Setup + Foundation)
2. **Phase 3 (US1)** ← Deploy MVP here with just priorities and tags
3. Phase 4 (US2) → Enhanced search capabilities
4. Phase 5 (US3) → Better task viewing
5. Phase 6 (US4) + Phase 7 (US5) → Time management features

**Aggressive Parallel** (Two tracks):
1. Phase 1 + Phase 2
2. **Track 1**: Phase 3 (US1) + **Track 2**: Phase 6 (US4) [Parallel]
3. **Track 1**: Phase 4 (US2) + **Track 2**: Phase 7 (US5) [Parallel]
4. Phase 5 (US3)
5. Phase 8 (Polish)

**Sequential Safe** (No risk):
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

## Independent Test Criteria Per User Story

### US1 (Priorities & Tags)
**How to test independently**:
```bash
# Create tasks with priorities and tags
uv run python main.py add "Task 1" -p high -t "work,urgent"
uv run python main.py add "Task 2" -p medium -t "work"
uv run python main.py add "Task 3" -p low -t "personal"

# Filter by priority
uv run python main.py list -p high  # Should show only Task 1

# Filter by tags
uv run python main.py list -t work  # Should show Task 1 and Task 2
uv run python main.py list -t "work,urgent"  # Should show only Task 1 (AND logic)
```

**Success**: Can create, filter, and update tasks by priority and tags without needing any other user stories.

### US2 (Search & Filter)
**How to test independently** (requires US1 data):
```bash
# Create tasks with varied attributes
uv run python main.py add "Meeting notes" -p high -t "work"
uv run python main.py add "Team meeting" -p medium -t "work,meetings"
uv run python main.py add "Personal meeting" -p low -t "personal"

# Search by keyword
uv run python main.py search "meeting"  # Should show all 3 tasks

# Combined filters
uv run python main.py list -s pending -p high -t work --keyword "meeting"  # Should show first task only
```

**Success**: Can search by keyword and apply complex multi-criteria filters to find specific tasks.

### US3 (Sort)
**How to test independently** (requires US1 for priority sorting):
```bash
# Create tasks with different priorities and titles
uv run python main.py add "Zebra task" -p low
uv run python main.py add "Alpha task" -p high
uv run python main.py add "Beta task" -p medium

# Sort by priority
uv run python main.py list --sort-by priority --order desc  # Alpha, Beta, Zebra

# Sort by title
uv run python main.py list --sort-by title  # Alpha, Beta, Zebra
```

**Success**: Can sort tasks by different criteria with correct ordering.

### US4 (Due Dates & Reminders)
**How to test independently**:
```bash
# Create task with future due date (25 minutes from now)
uv run python main.py add "Quick call" --due-date "2025-12-26 $(date -d '+25 minutes' +'%H:%M')"

# List tasks - should see reminder notification
uv run python main.py list
# Output includes: [REMINDER] 1 task due soon: ID X - Quick call (due in 25 minutes)

# Create overdue task
uv run python main.py add "Past task" --due-date "2025-12-25 10:00"
uv run python main.py list  # Should show OVERDUE indicator
```

**Success**: Can set due dates, receive reminders, and see overdue indicators without needing priorities/tags.

### US5 (Recurring Tasks)
**How to test independently** (requires US4 due_date field):
```bash
# Create weekly recurring task
uv run python main.py add "Weekly sync" --due-date "2025-12-27 10:00" -r weekly

# Complete task
uv run python main.py complete 1
# Output: [OK] Completed + [AUTO-CREATE] Next instance created for Jan 3, 2026 10:00 AM

# Verify new instance
uv run python main.py list  # Should show new instance with ID 2, status=pending
```

**Success**: Completing recurring task auto-generates next instance with correct due date and inherited attributes.

---

## Task Summary

**Total Tasks**: 127

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundation): 10 tasks
- Phase 3 (US1 - Priorities & Tags): 23 tasks
- Phase 4 (US2 - Search & Filter): 20 tasks
- Phase 5 (US3 - Sort): 18 tasks
- Phase 6 (US4 - Due Dates & Reminders): 19 tasks
- Phase 7 (US5 - Recurring Tasks): 22 tasks
- Phase 8 (Polish): 11 tasks

**By Type**:
- Setup/Infrastructure: 14 tasks
- Model/Business Logic: 28 tasks
- CLI Implementation: 45 tasks
- Tests: 40 tasks (RECOMMENDED but optional)

**Parallelization**:
- Foundation phase: 9 tasks can run in parallel ([P] marker)
- Per user story: 50% of tasks can run in parallel (tests, different files)
- After Foundation: 2 independent tracks (US1→US2→US3 and US4→US5)

**Estimated Effort**:
- Foundation: 2-3 hours (critical path)
- Each User Story: 3-4 hours (with tests)
- Total: 15-20 hours for complete implementation

**MVP Scope** (User Story 1 only):
- Phase 1 + Phase 2 + Phase 3 = 37 tasks
- Delivers: Task organization with priorities and tags
- Can be completed in ~5 hours
- Provides immediate user value

---

## Validation Checklist

- [x] All tasks follow checklist format (`- [ ] [ID] [P?] [Story?] Description`)
- [x] All implementation tasks include exact file paths
- [x] User stories organized in priority order (P1 → P2 → P3 → P4 → P5)
- [x] Each user story has clear independent test criteria
- [x] Dependencies documented (US2 depends on US1, US3 on US2, US5 on US4)
- [x] Parallel execution opportunities identified ([P] markers)
- [x] MVP scope defined (User Story 1)
- [x] Tests marked as RECOMMENDED but optional (per constitution)
- [x] All 30 functional requirements (FR-001 to FR-030) covered
- [x] All 5 user stories mapped to task phases
- [x] Foundation phase includes blocking prerequisites only
- [x] Polish phase includes cross-cutting concerns

**Status**: ✅ **Tasks ready for implementation** - Each user story can be independently implemented and tested

**Next Command**: `/sp.implement` or manual implementation starting with Phase 1 (Setup)
