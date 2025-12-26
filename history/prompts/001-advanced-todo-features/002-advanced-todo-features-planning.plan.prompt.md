---
id: 002
title: Advanced Todo Features Implementation Planning
stage: plan
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5
feature: 001-advanced-todo-features
branch: 001-advanced-todo-features
user: system
command: /sp.plan
labels: ["planning", "architecture", "data-model", "cli-contracts", "technical-decisions"]
links:
  spec: specs/001-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-advanced-todo-features/plan.md
  - specs/001-advanced-todo-features/research.md
  - specs/001-advanced-todo-features/data-model.md
  - specs/001-advanced-todo-features/contracts/cli-commands.md
tests:
  - Constitution Check validation (all 7 principles passed)
  - Data model validation (5 new fields, 2 new entities, 6 validation rules)
  - CLI contract specification (6 commands, 688 lines)
---

## Prompt

/sp.plan

(No additional arguments provided - executed from specification)

## Response snapshot

Created comprehensive implementation plan for Advanced Todo Features following Spec-Driven Development workflow Phase 1 (Design & Contracts).

### Planning Artifacts Generated

**1. Implementation Plan** (`plan.md` - 840 lines):
- Complete technical context (Python 3.12+, Pydantic/Typer/Rich stack)
- Constitution Check: All 7 principles validated (PASS)
- Project structure with file modification summary (~1500 LOC estimated)
- 7 architectural decisions documented with rationale
- Implementation sequence with 4 phases
- Risk analysis with mitigation strategies
- Non-goals explicitly stated

**2. Research Report** (`research.md` - 203 lines):
- Technical context resolution (language, dependencies, storage, testing)
- 8 key architectural patterns identified from Phase I codebase
- Technology decisions (Literal types, datetime, tags normalization, recurrence)
- Best practices (Pydantic validation, CLI error handling, type hints)
- Integration patterns (model extension, manager methods, CLI commands)
- Performance considerations and risk mitigation

**3. Data Model** (`data-model.md` - 533 lines):
- **TodoItem Extended**: 5 new fields (priority, tags, due_date, recurrence_pattern, recurrence_parent_id)
- **FilterCriteria**: New entity for search/filter parameters
- **SortOptions**: New entity for task ordering preferences
- 6 validation rules with field-level and cross-field validation
- Self-referencing relationship for recurring tasks (parent-child via recurrence_parent_id)
- Migration strategy for Phase II database (PostgreSQL)
- 4 detailed examples with data flow diagrams

**4. CLI Contracts** (`contracts/cli-commands.md` - 688 lines):
- 6 command specifications (add/list/search/update/complete/delete)
- Extended commands: add, list, update with new options
- New command: search with keyword + filters
- Auto-create behavior: complete command for recurring tasks
- 20+ examples with input/output specifications
- Error handling patterns and validation rules
- Performance targets for each operation
- 3 complete workflow demonstrations

### Architecture Highlights

**5 New Fields to TodoItem**:
1. `priority: Literal["high", "medium", "low"] = "medium"` - Type-safe urgency levels
2. `tags: list[str] = []` - Max 10, normalized lowercase alphanumeric + hyphens
3. `due_date: datetime | None = None` - ISO 8601 format with timezone awareness
4. `recurrence_pattern: Literal["daily", "weekly", "monthly"] | None = None` - Auto-repeat schedule
5. `recurrence_parent_id: int | None = None` - Links recurring task instances

**3 New TodoManager Methods**:
1. `filter_todos()` - Multi-criteria filtering with AND logic (keyword, priority, tags, status, date_range)
2. `sort_todos()` - Dynamic sorting by priority/due_date/created_at/title with asc/desc order
3. `check_reminders()` - Return tasks due within next 30 minutes for console notifications

**Extended CLI Commands**:
- `add`: +4 new options (priority, tags, due-date, recurrence)
- `list`: +7 new options (priority, tags, keyword, from-date, to-date, sort-by, order)
- `search`: New command for keyword search with optional filters
- `update`: +4 new options (priority, tags, due-date, recurrence)
- `complete`: Auto-creates next instance for recurring tasks
- `delete`: Unchanged from Phase I

### Key Architectural Decisions

**1. Priority Implementation**: Pydantic Literal type for compile-time type safety
**2. Tags Storage**: list[str] with field_validator for normalization (lowercase, max 10)
**3. Due Date Handling**: Python datetime with system local timezone (ISO 8601 input)
**4. Recurring Tasks**: Parent-child relationship via recurrence_parent_id for instance tracking
**5. Filtering**: Single filter_todos() method with optional parameters (AND logic)
**6. Sorting**: Dynamic sort with special handling for priority order and null due_dates
**7. Reminders**: Hybrid check (startup + list operations) - no background daemon

### Constitution Compliance

✅ **All 7 Principles Validated**:
- I. Spec-Driven Development: Plan generated from complete spec.md
- II. Phased Evolution: Phase I Extension maintaining in-memory storage
- III. Technology Stack Adherence: No new dependencies, maintains Pydantic/Typer/Rich
- IV. Independent User Stories: 5 prioritized stories (P1-P5) independently testable
- V. Test-Driven Development: Optional (tests not explicitly requested)
- VI. Stateless Architecture: Maintains in-memory dict, prepares for Phase II database
- VII. Documentation and Traceability: All artifacts generated (spec/plan/research/data-model/contracts)

### Performance Targets

- Add task: <100ms
- List 1000 tasks: <1 second (SC-002)
- Search 1000 tasks: <1 second (SC-002)
- Filter + Sort 100+ tasks: <500ms (SC-004)
- Reminder check: <5 seconds on startup (SC-005)
- Recurring instance creation: <1 second (SC-006)

All targets achievable with in-memory O(n) filtering and O(n log n) sorting.

### Files to Modify

**7 Core Files** (~1500 LOC total):
1. `src/core/todo_item.py`: +5 fields, +2 validators (57 → ~120 lines)
2. `src/core/todo_manager.py`: +3 methods (139 → ~250 lines)
3. `src/ui/cli.py`: Extend add/list, add search (139 → ~300 lines)
4. `tests/test_todo_item.py`: +4 test classes (193 → ~300 lines)
5. `tests/test_todo_manager.py`: +4 test classes (386 → ~550 lines)
6. `tests/test_cli.py`: Extend tests (267 → ~400 lines)
7. `README.md`: Document new features (~220 → ~350 lines)

**2 New Files**:
- `specs/001-advanced-todo-features/quickstart.md`: User guide (~150 lines)
- `test_cli_workflow_advanced.py`: Demo script (~100 lines)

### Risk Mitigation

**8 Identified Risks with Mitigation**:
1. Due date parsing errors → Clear error messages with format examples
2. Tag input inconsistency → field_validator normalizes (lowercase, trim)
3. Reminder notification spam → Only notify tasks due within 30 minutes
4. Sort field validation → CLI validates against enum before calling
5. Recurring task infinite loops → Create only one instance per completion
6. mypy --strict failures → Incremental validation per task
7. Performance on large lists → Acceptable per spec (<1s for 1000 tasks)
8. In-memory data loss → Documented clearly, Phase II adds persistence

### Next Steps

**Ready for Task Generation**: `/sp.tasks`

Expected output: `tasks.md` with 30-50 atomic tasks organized by user story (P1-P5).

## Outcome

- ✅ Impact: Complete architectural plan for extending Phase I todo app with 5 major feature groups. Defines HOW to implement all 30 functional requirements (FR-001 to FR-030) with type-safe, testable code following Pydantic/Typer/Rich patterns.
- 🧪 Tests: Constitution Check validated (all 7 principles PASS), Data model validated (field constraints, validation rules, relationships), CLI contracts specified (6 commands with examples)
- 📁 Files: Created plan.md (840 lines), research.md (203 lines), data-model.md (533 lines), cli-commands.md (688 lines)
- 🔁 Next prompts: Run `/sp.tasks` to generate task breakdown (30-50 tasks). Then `/sp.implement` or manual implementation referencing Task IDs. No clarifications needed.
- 🧠 Reflection: Successfully applied Spec-Driven Development Phase 1 workflow. Used Task tool with Explore agent to research Phase I codebase patterns (Pydantic validators, Typer CLI, Rich tables). All architectural decisions documented with rationale and consequences. Clean separation between core/ (business logic) and ui/ (CLI) enables Phase II migration.

## Evaluation notes (flywheel)

- Failure modes observed: None. Research agent provided comprehensive codebase analysis (91 tests, 17 test classes, all patterns documented). All planning artifacts generated following SDD templates.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 7 principles validated), Data Model Validation - PASS (5 fields, 6 rules, self-referencing relationship), CLI Contracts - PASS (6 commands, performance targets specified)
- Prompt variant (if applicable): Standard /sp.plan workflow with automatic research phase
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to test plan completeness for task generation. Verify that all 30 functional requirements map to atomic tasks.
