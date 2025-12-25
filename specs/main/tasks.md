---
description: "Actionable task list for Phase I Console Todo App implementation"
---

# Tasks: Phase I Console Todo App

**Input**: Design documents from `specs/main/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/cli-interface.md, quickstart.md
**Generated**: 2025-12-25
**Status**: Ready for implementation

**Tests**: Tests are OPTIONAL for Phase I as per plan.md and research.md. TDD will only be enforced if explicitly requested during implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each command group.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

This is a **single project** structure:
- `src/core/` - Logic-Agent scope (business logic)
- `src/ui/` - UI-Agent scope (CLI interface)
- `tests/` - Test suite (mirrors src/ structure)
- `.claude/agents/` - Sub-agent instructions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure creation

**⚠️ CRITICAL**: Directory structure must be created FIRST as per user requirements

- [X] T001 Create root project directory structure with src/, tests/, .claude/
- [X] T002 Create Logic-Agent directory structure at src/core/ with __init__.py
- [X] T003 Create UI-Agent directory structure at src/ui/ with __init__.py
- [X] T004 Create tests directory structure with __init__.py
- [X] T005 Create .claude/agents/ folder for sub-agent instructions
- [X] T006 Create Logic-Agent instruction file at .claude/agents/logic-agent.md
- [X] T007 Create UI-Agent instruction file at .claude/agents/ui-agent.md
- [X] T008 Initialize UV project with pyproject.toml configuration
- [X] T009 [P] Add runtime dependencies (pydantic, rich, typer) via UV
- [X] T010 [P] Add dev dependencies (pytest, pytest-cov, mypy) via UV
- [X] T011 [P] Configure mypy strict mode in pyproject.toml
- [X] T012 [P] Configure pytest settings in pyproject.toml
- [X] T013 Configure CLI entry point (todo command) in pyproject.toml

**Checkpoint**: Project structure created with clear separation between Logic-Agent (src/core/) and UI-Agent (src/ui/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core business logic (Logic-Agent scope) that MUST be complete before ANY CLI command can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Agent Scope**: Logic-Agent only (src/core/)

- [X] T014 [P] Create TodoItem Pydantic model in src/core/todo_item.py
- [X] T015 [P] Add TodoItem field validators (title validation) in src/core/todo_item.py
- [X] T016 [P] Add TodoItem type hints and Config in src/core/todo_item.py
- [X] T017 Create TodoManager class with __init__ in src/core/todo_manager.py
- [X] T018 [P] Implement TodoManager.add_todo method in src/core/todo_manager.py
- [X] T019 [P] Implement TodoManager.get_todo method in src/core/todo_manager.py
- [X] T020 [P] Implement TodoManager.list_todos method in src/core/todo_manager.py
- [X] T021 [P] Implement TodoManager.update_todo method in src/core/todo_manager.py
- [X] T022 [P] Implement TodoManager.complete_todo method in src/core/todo_manager.py
- [X] T023 [P] Implement TodoManager.delete_todo method in src/core/todo_manager.py
- [X] T024 Add type hints to all TodoManager methods in src/core/todo_manager.py
- [X] T025 Run mypy --strict on src/core/ to validate type safety

**Checkpoint**: Foundation ready (Logic-Agent complete) - UI-Agent implementation can now begin in parallel for each user story

---

## Phase 3: User Story 1 - Basic Todo Workflow (Priority: P1) 🎯 MVP

**Goal**: Enable users to add new todos, view all todos in a formatted table, and mark todos as completed

**Independent Test**: User can add a todo, see it in the list, and mark it as completed - the core workflow is functional

**Agent Scope**: UI-Agent (src/ui/)

**User Stories Covered**:
- P1: Add todo (core value)
- P1: List todos (core value)
- P1: Complete todo (core workflow)

### Implementation for User Story 1

- [X] T026 Create CLI app skeleton with Typer in src/ui/cli.py
- [X] T027 Create TodoManager instance in src/ui/cli.py
- [X] T028 Create Rich Console instance in src/ui/cli.py
- [X] T029 [P] [US1] Implement 'add' command in src/ui/cli.py
- [X] T030 [P] [US1] Add success message formatting for 'add' command in src/ui/cli.py
- [X] T031 [P] [US1] Add error handling for 'add' command in src/ui/cli.py
- [X] T032 [P] [US1] Implement 'list' command in src/ui/cli.py
- [X] T033 [P] [US1] Create Rich Table formatter for 'list' command in src/ui/cli.py
- [X] T034 [P] [US1] Add status filtering option for 'list' command in src/ui/cli.py
- [X] T035 [P] [US1] Add semantic color coding (green/yellow/white) for 'list' command in src/ui/cli.py
- [X] T036 [P] [US1] Implement 'complete' command in src/ui/cli.py
- [X] T037 [P] [US1] Add success message for 'complete' command in src/ui/cli.py
- [X] T038 [P] [US1] Add error handling for 'complete' command (not found) in src/ui/cli.py
- [X] T039 [US1] Add CLI entry point (if __name__ == "__main__") in src/ui/cli.py
- [X] T040 [US1] Run mypy --strict on src/ui/cli.py to validate type safety
- [X] T041 [US1] Manual testing: Add 3 todos, list them, complete one, list again

**Checkpoint**: At this point, User Story 1 (core workflow) should be fully functional and testable independently. This is the MVP!

---

## Phase 4: User Story 2 - Advanced Todo Management (Priority: P2)

**Goal**: Enable users to delete todos they no longer need and update todo fields for corrections or changes

**Independent Test**: User can delete a todo and verify it's gone, update a todo's title/status and see changes reflected

**Agent Scope**: UI-Agent (src/ui/)

**User Stories Covered**:
- P2: Delete todo (data management)
- P2: Update todo (nice-to-have editing)

### Implementation for User Story 2

- [X] T042 [P] [US2] Implement 'delete' command in src/ui/cli.py
- [X] T043 [P] [US2] Add success message for 'delete' command in src/ui/cli.py
- [X] T044 [P] [US2] Add error handling for 'delete' command (not found) in src/ui/cli.py
- [X] T045 [P] [US2] Implement 'update' command skeleton in src/ui/cli.py
- [X] T046 [P] [US2] Add --title option for 'update' command in src/ui/cli.py
- [X] T047 [P] [US2] Add --description option for 'update' command in src/ui/cli.py
- [X] T048 [P] [US2] Add --status option for 'update' command in src/ui/cli.py
- [X] T049 [US2] Add validation (at least one field required) for 'update' command in src/ui/cli.py
- [X] T050 [US2] Add success message with updated fields for 'update' command in src/ui/cli.py
- [X] T051 [US2] Add error handling for 'update' command (not found, invalid status) in src/ui/cli.py
- [X] T052 [US2] Run mypy --strict on src/ui/cli.py to validate type safety
- [X] T053 [US2] Manual testing: Delete a todo, update a todo's title and status

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. All 5 commands are functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the entire application

- [ ] T054 [P] Add global --help option documentation in src/ui/cli.py
- [ ] T055 [P] Add global --version option in src/ui/cli.py
- [ ] T056 Verify all error messages use Rich formatting ([red]Error:[/red]) in src/ui/cli.py
- [ ] T057 Verify all success messages use Rich formatting ([green]✓[/green]) in src/ui/cli.py
- [ ] T058 [P] Add docstrings to all CLI commands in src/ui/cli.py
- [ ] T059 [P] Add docstrings to all TodoManager methods in src/core/todo_manager.py
- [ ] T060 Run mypy --strict on entire src/ directory to validate full type safety
- [ ] T061 Test all user journeys from contracts/cli-interface.md (3 journeys)
- [ ] T062 Verify project structure matches plan.md specifications
- [ ] T063 [P] Update README.md with installation and usage instructions
- [ ] T064 [P] Verify quickstart.md validation steps all pass
- [ ] T065 Final smoke test: Run all 5 commands in sequence

**Checkpoint**: Application is production-ready for Phase I console deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
  - **T001-T004**: Directory structure creation MUST be done FIRST (sequential)
  - **T005-T007**: Agent instruction files (sequential after T001-T004)
  - **T008**: UV project initialization (after directories exist)
  - **T009-T013**: Dependencies and configuration (can run in parallel after T008)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
  - **T014-T016**: TodoItem model (can run in parallel)
  - **T017**: TodoManager initialization (after T014 completes)
  - **T018-T023**: TodoManager methods (can run in parallel after T017)
  - **T024-T025**: Type validation (after all methods complete)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 and User Story 2 can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2) for MVP-first approach
- **Polish (Phase 5)**: Depends on User Story 1 (MVP) or both User Stories (full feature set)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - **T026-T028**: CLI setup (sequential)
  - **T029-T031**: 'add' command (can run in parallel)
  - **T032-T035**: 'list' command (can run in parallel with T029-T031)
  - **T036-T038**: 'complete' command (can run in parallel with T029-T035)
  - **T039-T041**: Integration and testing (sequential after all commands)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
  - **T042-T044**: 'delete' command (can run in parallel)
  - **T045-T051**: 'update' command (can run in parallel with T042-T044)
  - **T052-T053**: Integration and testing (sequential after all commands)

### Within Each User Story

- CLI setup before command implementation
- Commands can be implemented in parallel (marked with [P])
- Error handling and formatting within same command (sequential)
- Type checking and testing after implementation (sequential)

### Parallel Opportunities

**Setup Phase**:
- T009, T010, T011, T012, T013 (dependencies and configuration)

**Foundational Phase**:
- T014, T015, T016 (TodoItem model components)
- T018, T019, T020, T021, T022, T023 (TodoManager methods)

**User Story 1 Phase**:
- T029-T031 (add command) || T032-T035 (list command) || T036-T038 (complete command)
- All three commands can be built simultaneously by different developers

**User Story 2 Phase**:
- T042-T044 (delete command) || T045-T051 (update command)
- Both commands can be built simultaneously

**Polish Phase**:
- T054, T055, T058, T059, T063, T064 (documentation and docstrings)

---

## Parallel Example: User Story 1 (MVP)

```bash
# After Foundational Phase completes, launch all three core commands in parallel:

# Developer A (or Agent 1):
Task: "Implement 'add' command in src/ui/cli.py"
Task: "Add success message formatting for 'add' command in src/ui/cli.py"
Task: "Add error handling for 'add' command in src/ui/cli.py"

# Developer B (or Agent 2):
Task: "Implement 'list' command in src/ui/cli.py"
Task: "Create Rich Table formatter for 'list' command in src/ui/cli.py"
Task: "Add status filtering option for 'list' command in src/ui/cli.py"
Task: "Add semantic color coding (green/yellow/white) for 'list' command in src/ui/cli.py"

# Developer C (or Agent 3):
Task: "Implement 'complete' command in src/ui/cli.py"
Task: "Add success message for 'complete' command in src/ui/cli.py"
Task: "Add error handling for 'complete' command (not found) in src/ui/cli.py"

# After all complete, integrate and test:
Task: "Add CLI entry point (if __name__ == '__main__') in src/ui/cli.py"
Task: "Run mypy --strict on src/ui/cli.py to validate type safety"
Task: "Manual testing: Add 3 todos, list them, complete one, list again"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯 RECOMMENDED

This is the fastest path to a working todo application:

1. **Complete Phase 1: Setup** (T001-T013)
   - ✅ Directory structure with Logic-Agent/UI-Agent separation
   - ✅ .claude/agents/ folder with sub-agent instructions
   - ✅ UV project configured with all dependencies
2. **Complete Phase 2: Foundational** (T014-T025)
   - ✅ TodoItem model (Logic-Agent)
   - ✅ TodoManager service (Logic-Agent)
   - ✅ Type checking passes
3. **Complete Phase 3: User Story 1** (T026-T041)
   - ✅ Add command (create todos)
   - ✅ List command (view todos)
   - ✅ Complete command (mark done)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Add 3 todos
   - List them in a table
   - Complete one
   - List again and verify colors
5. **Deploy/Demo MVP**: You now have a working todo app!

### Incremental Delivery (Full Feature Set)

Add capabilities one user story at a time:

1. **Complete Setup + Foundational** → Foundation ready (Logic-Agent complete)
2. **Add User Story 1** → Test independently → Deploy/Demo (MVP!)
   - Commands: add, list, complete
   - User can manage basic todo workflow
3. **Add User Story 2** → Test independently → Deploy/Demo
   - Commands: delete, update
   - User can manage advanced todo operations
4. **Add Polish** → Final validation → Production ready
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers or agents:

1. **Team completes Setup + Foundational together** (T001-T025)
2. **Once Foundational is done, split work**:
   - **Logic-Agent**: Already complete from Phase 2
   - **UI-Agent Team A**: User Story 1 commands (T026-T041)
   - **UI-Agent Team B**: User Story 2 commands (T042-T053)
3. **Teams can work in parallel**:
   - Team A delivers MVP (add, list, complete)
   - Team B delivers advanced features (delete, update)
4. **Integrate and Polish** (T054-T065)

---

## Task Summary

**Total Tasks**: 65

**Breakdown by Phase**:
- **Setup (Phase 1)**: 13 tasks (T001-T013)
- **Foundational (Phase 2)**: 12 tasks (T014-T025) - Logic-Agent scope
- **User Story 1 (Phase 3)**: 16 tasks (T026-T041) - UI-Agent scope
- **User Story 2 (Phase 4)**: 12 tasks (T042-T053) - UI-Agent scope
- **Polish (Phase 5)**: 12 tasks (T054-T065)

**Breakdown by Agent**:
- **Logic-Agent (src/core/)**: 12 tasks (T014-T025)
- **UI-Agent (src/ui/)**: 28 tasks (T026-T053)
- **Shared/Setup**: 25 tasks (T001-T013, T054-T065)

**Parallel Opportunities**: 32 tasks marked with [P]

**Independent Test Criteria**:
- **User Story 1 (MVP)**: Add todos, list in table, complete and verify color changes
- **User Story 2**: Delete todos and verify removal, update fields and verify changes

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (41 tasks) = Fully functional core todo app

---

## Notes

- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] label**: Maps task to specific user story (US1, US2) for traceability
- **Agent Separation**: Logic-Agent (src/core/) MUST NOT import from UI-Agent (src/ui/)
- **Directory Structure First**: T001-T007 create the architecture (Logic-Agent vs UI-Agent separation + .claude/agents/)
- **Each user story should be independently testable**: Can test add/list/complete without delete/update
- **Tests are OPTIONAL**: Only include if explicitly requested during implementation (TDD approach)
- **Type Safety**: mypy --strict enforced at multiple checkpoints (T025, T040, T052, T060)
- **Commit after each task or logical group**: Enables easy rollback and progress tracking
- **Stop at any checkpoint to validate story independently**: Validates incremental value delivery
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Tasks Complete**: Ready for `/sp.implement`

**Next Command**: `/sp.implement` to execute tasks in dependency order
