# Feature Specification: Advanced Todo Features

**Feature Branch**: `001-advanced-todo-features`
**Created**: 2025-12-25
**Status**: Draft
**Input**: User description: "Extend the Phase I console todo application with Intermediate and Advanced features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Organization with Priorities and Tags (Priority: P1)

As a todo app user, I want to organize my tasks by assigning priority levels and category tags, so that I can focus on what's most important and group related tasks together.

**Why this priority**: This is the foundation for effective task management. Without organization capabilities, users struggle to identify critical tasks among a long list. This delivers immediate value by enabling users to categorize and prioritize their work.

**Independent Test**: Can be fully tested by creating tasks with different priority levels (high/medium/low) and multiple tags (work/home/personal), then listing tasks filtered by specific priorities or tags. Delivers value immediately as users can organize existing tasks.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I specify priority as "high" and tags as "work,urgent", **Then** the task is created with high priority and both tags assigned
2. **Given** I have tasks with different priorities, **When** I list all high-priority tasks, **Then** only high-priority tasks are displayed
3. **Given** I have tasks with different tags, **When** I filter by "work" tag, **Then** only tasks tagged with "work" are shown
4. **Given** I have an existing task, **When** I update its priority from "low" to "high", **Then** the priority is updated and reflected in filtered views
5. **Given** I have tasks with multiple tags, **When** I filter by multiple tags "work,urgent", **Then** only tasks with both tags are displayed

---

### User Story 2 - Search and Filter Tasks (Priority: P2)

As a todo app user, I want to search tasks by keyword and filter by various criteria (status, priority, tags, date), so that I can quickly find specific tasks without scrolling through long lists.

**Why this priority**: Once users have organized tasks (P1), they need efficient retrieval. Search and filter capabilities significantly improve usability for users managing dozens of tasks.

**Independent Test**: Can be tested by creating 20+ tasks with varied attributes, then searching for specific keywords and applying different filter combinations. Delivers value for users with growing task lists.

**Acceptance Scenarios**:

1. **Given** I have tasks with various titles and descriptions, **When** I search for "meeting", **Then** all tasks containing "meeting" in title or description are displayed
2. **Given** I have tasks created on different dates, **When** I filter by date range (last 7 days), **Then** only tasks created within that period are shown
3. **Given** I have tasks with mixed attributes, **When** I apply combined filters (status: pending, priority: high, tag: work), **Then** only tasks matching all criteria are displayed
4. **Given** I search for a keyword, **When** no tasks match, **Then** an appropriate "no results" message is displayed
5. **Given** I have tasks with similar names, **When** I search with partial keywords, **Then** case-insensitive partial matching returns relevant results

---

### User Story 3 - Sort Tasks (Priority: P3)

As a todo app user, I want to sort my task list by different criteria (due date, priority, created date, alphabetically), so that I can view tasks in the order most relevant to my current needs.

**Why this priority**: Sorting enhances the viewing experience built on organization (P1) and search (P2). It's less critical than filtering but improves task visibility and planning.

**Independent Test**: Can be tested by creating tasks with varied creation dates, due dates, priorities, and titles, then sorting by each criterion and verifying the order. Delivers value for users who want flexible task viewing.

**Acceptance Scenarios**:

1. **Given** I have tasks with different priorities, **When** I sort by priority (high to low), **Then** tasks are displayed with high-priority first, then medium, then low
2. **Given** I have tasks with due dates, **When** I sort by due date (earliest first), **Then** tasks are ordered chronologically by due date, with tasks without due dates at the end
3. **Given** I have tasks created at different times, **When** I sort by creation date (newest first), **Then** most recently created tasks appear first
4. **Given** I have tasks with various titles, **When** I sort alphabetically, **Then** tasks are ordered A-Z by title
5. **Given** I apply a sort order, **When** I add a new task, **Then** the list automatically re-sorts to maintain the selected order

---

### User Story 4 - Due Dates and Reminders (Priority: P4)

As a todo app user, I want to set due dates and times for tasks with console-based reminders, so that I never miss important deadlines.

**Why this priority**: Time management is critical but requires the foundational features (P1-P3) to be useful. Due dates enable deadline-driven workflows.

**Independent Test**: Can be tested by creating tasks with various due dates/times, waiting for reminder times to trigger, and verifying console notifications appear. Delivers value for users with time-sensitive tasks.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I specify a due date and time (e.g., "2025-12-30 14:00"), **Then** the task stores the due date and reminder is scheduled
2. **Given** I have tasks with due dates, **When** I view the task list, **Then** due dates are displayed in a human-readable format
3. **Given** a task's reminder time arrives, **When** the application is running, **Then** a console notification displays with the task title and "Due soon!" message
4. **Given** I have tasks with approaching due dates, **When** I list tasks sorted by due date, **Then** overdue tasks are highlighted/marked distinctly
5. **Given** I have a task with a due date, **When** I complete the task, **Then** the reminder is cancelled and no notification triggers

---

### User Story 5 - Recurring Tasks (Priority: P5)

As a todo app user, I want to create tasks that automatically repeat on a schedule (daily, weekly, monthly), so that I don't have to manually recreate routine tasks.

**Why this priority**: This is an advanced automation feature that builds on all previous capabilities. It provides the most value for users with established routines, making it appropriate for final implementation.

**Independent Test**: Can be tested by creating a recurring task (e.g., "Daily standup"), marking it complete, and verifying a new instance is automatically created with the next due date. Delivers value for users managing routine activities.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I specify recurrence as "daily", **Then** the task is marked as recurring with daily frequency
2. **Given** I have a daily recurring task, **When** I complete it, **Then** a new instance is auto-created with tomorrow's due date and status reset to "pending"
3. **Given** I have a weekly recurring task, **When** I complete it on Monday, **Then** a new instance is created with next Monday's date
4. **Given** I have a monthly recurring task, **When** I complete it on the 15th, **Then** a new instance is created for the 15th of next month
5. **Given** I have a recurring task, **When** I delete it, **Then** both the current instance and the recurrence pattern are removed (or I'm prompted to choose)

---

### Edge Cases

- **Empty task lists**: What happens when filtering/searching returns no results? Display clear "No tasks found" message with current filter criteria.
- **Invalid priority values**: How does system handle priority values other than high/medium/low? Reject with validation error specifying allowed values.
- **Tag formatting**: What happens when user enters tags with special characters or spaces? Sanitize tags to lowercase alphanumeric with hyphens.
- **Date parsing**: How does system handle invalid date formats (e.g., "tomorrow", "next week")? Accept ISO format (YYYY-MM-DD HH:MM) and reject others with format guidance.
- **Overlapping filters**: What happens when multiple conflicting filters are applied? Apply filters as AND logic (task must match all criteria).
- **Recurring task completion timing**: If a weekly task is completed early (e.g., Friday instead of Monday), should next instance be scheduled from completion date or original schedule? Use original schedule (next Monday) to maintain consistency.
- **Reminder system when app is closed**: What happens if reminder time passes while app is not running? Check for missed reminders on app startup and display them immediately.
- **Maximum tags per task**: How many tags can a single task have? Allow up to 10 tags per task to prevent abuse while supporting flexible categorization.
- **Past due dates**: Can users set due dates in the past? Allow (useful for logging completed tasks) but mark as overdue immediately.

## Requirements *(mandatory)*

### Functional Requirements

#### Priority and Tag Management (P1)

- **FR-001**: System MUST support three priority levels: "high", "medium", "low" (default: "medium")
- **FR-002**: System MUST allow users to assign multiple tags to a single task (comma-separated input)
- **FR-003**: System MUST validate priority values and reject invalid entries with clear error messages
- **FR-004**: System MUST store tags as lowercase alphanumeric strings with hyphens allowed
- **FR-005**: System MUST display priority with visual indicators in list view (e.g., [H], [M], [L] or color codes)

#### Search and Filter (P2)

- **FR-006**: System MUST provide case-insensitive keyword search across task titles and descriptions
- **FR-007**: System MUST support filtering by status (pending/in_progress/completed)
- **FR-008**: System MUST support filtering by priority level (high/medium/low)
- **FR-009**: System MUST support filtering by tags (single or multiple tags with AND logic)
- **FR-010**: System MUST support filtering by date range (created date)
- **FR-011**: System MUST allow combining multiple filter criteria (AND logic)
- **FR-012**: System MUST display current filter criteria when results are shown

#### Sorting (P3)

- **FR-013**: System MUST support sorting by priority (high → medium → low)
- **FR-014**: System MUST support sorting by due date (earliest → latest, null dates last)
- **FR-015**: System MUST support sorting by creation date (newest → oldest or oldest → newest)
- **FR-016**: System MUST support alphabetical sorting by title (A-Z or Z-A)
- **FR-017**: System MUST maintain sort order when new tasks are added

#### Due Dates and Reminders (P4)

- **FR-018**: System MUST accept due dates in ISO 8601 format (YYYY-MM-DD HH:MM)
- **FR-019**: System MUST store due dates as datetime objects with timezone awareness
- **FR-020**: System MUST display due dates in human-readable format (e.g., "Dec 30, 2025 2:00 PM")
- **FR-021**: System MUST check for upcoming/overdue tasks on app startup and during list operations
- **FR-022**: System MUST display console notifications for tasks due within next 30 minutes
- **FR-023**: System MUST mark overdue tasks with distinct visual indicator
- **FR-024**: System MUST cancel reminders when tasks are completed or deleted

#### Recurring Tasks (P5)

- **FR-025**: System MUST support three recurrence frequencies: "daily", "weekly", "monthly"
- **FR-026**: System MUST automatically create new task instance when recurring task is completed
- **FR-027**: System MUST calculate next due date based on recurrence pattern and original schedule
- **FR-028**: System MUST reset new instance status to "pending" and preserve all other attributes (title, description, priority, tags)
- **FR-029**: System MUST allow users to delete single instance or entire recurrence series
- **FR-030**: System MUST prevent creating recurring tasks without due dates (required for recurrence calculation)

### Key Entities

- **TodoItem (Enhanced)**: Represents a task with:
  - Existing attributes: id, title, description, status, created_at, updated_at
  - New attributes: priority (high/medium/low), tags (list of strings), due_date (optional datetime), recurrence_pattern (optional: daily/weekly/monthly), recurrence_parent_id (optional: links to original recurring task)

- **Filter Criteria**: Represents search/filter parameters:
  - keyword (optional string for text search)
  - status (optional: pending/in_progress/completed)
  - priority (optional: high/medium/low)
  - tags (optional list of tag strings)
  - date_from, date_to (optional datetime range)

- **Sort Options**: Represents sorting configuration:
  - sort_by (field name: priority/due_date/created_at/title)
  - sort_order (asc/desc)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add priority and at least one tag when creating a task in under 10 seconds
- **SC-002**: Search results return in under 1 second for task lists up to 1000 items
- **SC-003**: Users can apply and clear multiple filters (priority + tags + date) in under 15 seconds
- **SC-004**: Sorting 100+ tasks by any criterion completes instantly (under 500ms) with results displayed
- **SC-005**: Console reminders appear within 5 seconds of scheduled reminder time when app is running
- **SC-006**: Recurring task instances are created automatically within 1 second of marking previous instance complete
- **SC-007**: 95% of search/filter operations return expected results on first attempt (user doesn't need to retry)
- **SC-008**: Task list with all new attributes (priority, tags, due dates) displays clearly without horizontal scrolling in 80-column terminal
- **SC-009**: Users can distinguish between task priorities at a glance through visual indicators (colors or symbols)
- **SC-010**: Overdue tasks are immediately identifiable in any list view

### Validation Criteria

- **SC-011**: All Pydantic models pass mypy --strict type checking with zero errors
- **SC-012**: Invalid input (wrong priority, malformed date, empty tags) produces clear, actionable error messages
- **SC-013**: All CLI commands maintain consistent parameter patterns (e.g., --priority, --tags, --due-date)

## Assumptions

1. **Console Environment**: Users run the application in a terminal with at least 80-column width and support for ANSI colors (for Rich library formatting)
2. **Reminder Mechanism**: Since this is a console app with in-memory storage, reminders work only while app is running. Missed reminders (when app was closed) are shown on next startup.
3. **Timezone**: All dates/times use system local timezone (no multi-timezone support required for Phase I)
4. **Tag Limits**: Maximum 10 tags per task is sufficient for personal task management
5. **Recurrence Limits**: Only simple recurrence patterns (daily/weekly/monthly) are needed; no complex patterns (e.g., "every 2nd Tuesday") for Phase I
6. **Date Input Format**: Users are comfortable with ISO 8601 format (YYYY-MM-DD HH:MM); no natural language parsing ("tomorrow", "next week") required
7. **Performance**: With in-memory storage, all operations on lists up to 1000 tasks will perform adequately without optimization
8. **Single User**: Phase I remains single-user; no multi-user or concurrent access considerations

## Scope Boundaries

### In Scope
- All Intermediate Level features: priorities, tags, search, filter, sort
- All Advanced Level features: due dates, time-based reminders, recurring tasks
- CLI commands for all new capabilities
- Rich terminal formatting for enhanced display
- Pydantic model extensions with validation
- In-memory storage of all new attributes

### Out of Scope
- Persistent storage (database) - deferred to Phase II
- Natural language date parsing ("tomorrow", "in 2 days") - ISO format only
- Complex recurrence patterns (bi-weekly, nth weekday of month)
- Reminder delivery via email/SMS - console-only
- Mobile or web interface - CLI only
- Multi-timezone support - local timezone only
- Task dependencies or subtasks
- Collaboration or task sharing
- Undo/redo functionality
- Import/export to external formats (CSV, JSON)
- Calendar integration
- Background daemon for reminders when app is closed (show on next startup instead)
