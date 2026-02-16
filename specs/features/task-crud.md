# Feature Specification: Task CRUD Operations

**Feature ID**: FEAT-CRUD-001
**Created**: 2025-12-29
**Updated**: 2026-02-10
**Status**: Implemented (Phase II - V)
**Phases**: II (Web CRUD), III (Chat CRUD via MCP), IV (Containerized), V (Event-Driven)

---

## Overview

Task CRUD is the foundational feature of the Evolution Todo application. It enables authenticated users to create, read, update, delete, and complete todo items through both the web UI and the AI chatbot interface. All operations are scoped to the authenticated user; cross-user access is forbidden. Starting from Phase V, every mutation publishes a domain event for downstream services (notifications, recurring-task engine, audit log).

### Scope

- **In Scope**: Create, Read (single + list), Update, Delete, Toggle Complete, Filtering, Sorting, Priority, Tags, Due Dates, Recurrence pattern storage.
- **Out of Scope**: Real-time collaborative editing, file attachments, sub-tasks/checklists.

### Dependencies

| Dependency | Owner | Purpose |
|---|---|---|
| Better Auth (Frontend) | Frontend | Issues JWT on login |
| JWT Middleware (Backend) | Backend | Validates token, extracts `user_id` |
| Neon PostgreSQL | Infrastructure | Persistent storage |
| MCP Server (Phase III+) | Backend | Exposes CRUD as AI-agent tools |
| Dapr Pub/Sub (Phase V) | Infrastructure | Event publishing |

---

## User Stories

### US-CRUD-01: Create Task (Priority: P1)

As an authenticated user, I want to create a new task with a title so that I can track what I need to do.

**Acceptance Scenarios**:

```gherkin
Scenario: Successful task creation with title only
  Given I am authenticated and on the tasks page
  When I enter a title "Buy groceries" and click Add
  Then a task is created with status "pending"
  And the task appears at the top of my task list
  And the pending count increases by 1

Scenario: Task creation with all optional fields
  Given I am authenticated and on the tasks page
  When I enter title "Weekly standup", description "Team sync meeting"
  And I set priority to "high", due date to tomorrow, recurrence to "weekly"
  Then the task is created with all fields persisted
  And a priority badge "high" is displayed on the task

Scenario: Task creation with empty title rejected
  Given I am on the tasks page
  When I submit the form with an empty title
  Then I see validation error "Title is required"
  And no task is created

Scenario: Task creation with title exceeding 200 characters rejected
  Given I am on the tasks page
  When I submit a title longer than 200 characters
  Then I see validation error about maximum length
  And no task is created
```

---

### US-CRUD-02: View Tasks (Priority: P1)

As an authenticated user, I want to view all my tasks so I can see what needs to be done.

**Acceptance Scenarios**:

```gherkin
Scenario: View all tasks
  Given I am authenticated and have 5 tasks
  When I visit the tasks page
  Then I see all 5 tasks with title, status indicator, priority badge, and created date
  And I see count summary (total, pending, completed)

Scenario: View tasks with status filter
  Given I have 3 pending and 2 completed tasks
  When I filter by "pending"
  Then I see only 3 pending tasks

Scenario: View tasks with priority filter
  Given I have tasks with mixed priorities
  When I filter by priority "high"
  Then I see only high-priority tasks

Scenario: View tasks with due date filter
  Given I have tasks with various due dates
  When I filter by "overdue"
  Then I see only tasks past their due date that are not completed

Scenario: View tasks sorted by different criteria
  Given I have multiple tasks
  When I sort by "due_date" ascending
  Then tasks are ordered by earliest due date first
  And tasks without due dates appear last

Scenario: Empty state
  Given I have no tasks
  When I visit the tasks page
  Then I see an empty state message encouraging me to create tasks
```

---

### US-CRUD-03: Update Task (Priority: P1)

As an authenticated user, I want to edit my tasks so I can correct mistakes or update details.

**Acceptance Scenarios**:

```gherkin
Scenario: Update task title
  Given I have a task with title "Buy groceries"
  When I edit the title to "Buy groceries and fruits"
  Then the title is updated and displayed immediately
  And updated_at timestamp is refreshed

Scenario: Update task description
  Given I have a task without a description
  When I add description "Milk, eggs, bread"
  Then the description is saved and visible

Scenario: Update task priority
  Given I have a task with priority "none"
  When I change priority to "high"
  Then the priority badge updates to "high"

Scenario: Update task due date
  Given I have a task without a due date
  When I set due date to next Friday
  Then the due date is saved and displayed on the task

Scenario: Cancel edit discards changes
  Given I am editing a task
  When I click cancel
  Then changes are discarded and original values are restored
```

---

### US-CRUD-04: Delete Task (Priority: P1)

As an authenticated user, I want to delete tasks I no longer need.

**Acceptance Scenarios**:

```gherkin
Scenario: Delete a task
  Given I have a task "Old meeting notes"
  When I click delete and confirm
  Then the task is permanently removed from the database
  And the task disappears from my list
  And task counts are updated

Scenario: Cancel delete keeps the task
  Given I click delete on a task
  When the confirmation dialog appears and I click cancel
  Then the task remains in my list unchanged
```

---

### US-CRUD-05: Toggle Task Completion (Priority: P1)

As an authenticated user, I want to mark tasks as complete to track my progress.

**Acceptance Scenarios**:

```gherkin
Scenario: Mark task as complete
  Given I have a pending task
  When I click the completion checkbox
  Then the task is marked as completed with visual indication (strikethrough, green check)
  And pending count decreases, completed count increases

Scenario: Mark task as incomplete (undo)
  Given I have a completed task
  When I click the completion checkbox again
  Then the task returns to pending status
  And counts update accordingly

Scenario: Complete a recurring task
  Given I have a recurring task with pattern "weekly"
  When I mark it as complete
  Then the task is marked complete
  And (Phase V) a task-completed event is published for the recurring-task engine
```

---

### US-CRUD-06: User Isolation (Priority: P1)

As a user, I want my tasks to be private so no other user can see or modify them.

**Acceptance Scenarios**:

```gherkin
Scenario: User can only see own tasks
  Given User A has 3 tasks and User B has 2 tasks
  When User A logs in and views tasks
  Then User A sees only their 3 tasks

Scenario: Cross-user API access forbidden
  Given I am authenticated as User A
  When I call GET /api/{User_B_id}/tasks
  Then I receive 403 Forbidden
```

---

## Functional Requirements

| ID | Requirement | Phase |
|---|---|---|
| FR-CRUD-01 | System MUST allow authenticated users to create tasks with title (1-200 chars, required) and description (optional, max 1000 chars) | II |
| FR-CRUD-02 | System MUST allow authenticated users to list their own tasks with counts (total, pending, completed) | II |
| FR-CRUD-03 | System MUST allow authenticated users to retrieve a single task by ID | II |
| FR-CRUD-04 | System MUST allow authenticated users to update title, description, priority, due_date, tags, recurrence_pattern of their own tasks | II |
| FR-CRUD-05 | System MUST allow authenticated users to delete their own tasks permanently | II |
| FR-CRUD-06 | System MUST allow authenticated users to toggle task completion status | II |
| FR-CRUD-07 | System MUST filter tasks by status (all, pending, completed) | II |
| FR-CRUD-08 | System MUST filter tasks by priority (all, high, medium, low, none) | II |
| FR-CRUD-09 | System MUST filter tasks by due date (all, today, overdue, week) | II |
| FR-CRUD-10 | System MUST sort tasks by created_at, due_date, priority, or title in asc/desc order | II |
| FR-CRUD-11 | System MUST enforce user isolation: all endpoints verify JWT user_id matches URL user_id | II |
| FR-CRUD-12 | System MUST support priority levels: high, medium, low, none (default: none) | II |
| FR-CRUD-13 | System MUST support tags as a JSON array of strings on each task | II |
| FR-CRUD-14 | System MUST support optional due_date as ISO 8601 datetime | II |
| FR-CRUD-15 | System MUST support optional recurrence_pattern (daily, weekly, monthly, yearly) | II |
| FR-CRUD-16 | System MUST reject due dates in the past on task creation | II |
| FR-CRUD-17 | System MUST expose CRUD operations as MCP tools (add_task, list_tasks, update_task, delete_task, complete_task) for AI agent | III |
| FR-CRUD-18 | System MUST publish domain events (created, updated, completed, deleted) to Dapr pub/sub on every mutation | V |

---

## Validation Rules

| Field | Rule | Error Message |
|---|---|---|
| `title` | Required, 1-200 characters, trimmed | "Title is required" / "Title must be between 1 and 200 characters" |
| `description` | Optional, max 1000 characters | "Description must be under 1000 characters" |
| `priority` | Must be one of: high, medium, low, none | "Invalid priority. Must be one of: high, medium, low, none" |
| `due_date` | Optional, ISO 8601 format, must not be in the past (on create) | "Due date cannot be in the past" |
| `tags` | Optional, JSON array of strings, max 10 tags | "Maximum 10 tags allowed" |
| `recurrence_pattern` | Optional, one of: daily, weekly, monthly, yearly | "Invalid recurrence pattern" |
| `user_id` (URL) | Must match authenticated JWT user_id | "Cannot access other users' tasks" (403) |

---

## Error Handling

| HTTP Status | Condition | Response Body |
|---|---|---|
| `400 Bad Request` | Validation failure (empty title, invalid priority, past due date) | `{"detail": "<specific message>"}` |
| `401 Unauthorized` | Missing or invalid JWT token | `{"detail": "Not authenticated"}` |
| `403 Forbidden` | URL user_id does not match JWT user_id | `{"detail": "Cannot access other users' tasks"}` |
| `404 Not Found` | Task ID does not exist or belongs to another user | `{"detail": "Task not found"}` |
| `500 Internal Server Error` | Database or server failure | `{"detail": "Internal server error"}` |

---

## API Contract

**Base URL**: `http://localhost:8000` (dev) | Deployed backend URL (prod)
**Authentication**: All endpoints require `Authorization: Bearer <JWT>` header.

| Method | Endpoint | Request Body | Response | Status |
|---|---|---|---|---|
| `GET` | `/api/{user_id}/tasks` | Query: `status`, `priority`, `due`, `sort`, `order` | `{ tasks: Task[], count: { total, pending, completed } }` | 200 |
| `POST` | `/api/{user_id}/tasks` | `TaskCreate` (title, description?, due_date?, priority?, tags?, recurrence_pattern?) | `TaskResponse` | 201 |
| `GET` | `/api/{user_id}/tasks/{id}` | - | `TaskResponse` | 200 |
| `PUT` | `/api/{user_id}/tasks/{id}` | `TaskUpdate` (all fields optional) | `TaskResponse` | 200 |
| `DELETE` | `/api/{user_id}/tasks/{id}` | - | `{"message": "Task deleted"}` | 200 |
| `PATCH` | `/api/{user_id}/tasks/{id}/complete` | - | `TaskResponse` (toggled) | 200 |

### Task Entity Schema

```json
{
  "id": 1,
  "user_id": "uuid-string",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-29T10:00:00Z",
  "updated_at": "2025-12-29T10:00:00Z",
  "due_date": "2025-12-31T14:00:00Z",
  "priority": "high",
  "tags": ["shopping", "personal"],
  "recurrence_pattern": "weekly",
  "reminder_offset": 30,
  "is_recurring": true,
  "parent_recurring_id": null
}
```

See also: `specs/database/schema.md` for full table definitions.

---

## UI Expectations

### Desktop (>768px)

- **Task Form**: Full-width input bar with title field, expandable description textarea, advanced options (priority selector, date picker, recurrence dropdown). Submit button with loading state.
- **Task List**: Card-based layout. Each card shows: completion checkbox, title (strikethrough when complete), priority badge (color-coded), due date (if set), description preview, edit/delete action buttons.
- **Filters Bar**: Horizontal row of filter chips (status, priority, due date). Sort dropdown on the right.
- **Stats Summary**: Three stat cards at top showing total, pending, and completed counts.

### Mobile (<768px)

- **Task Form**: Stacked layout. Title input takes full width. Advanced options collapse into a toggle button.
- **Task List**: Single-column card list. Swipe or tap for edit/delete actions.
- **Filters**: Collapsible filter section to save vertical space.
- **Stats**: Horizontal scrollable row or stacked compact cards.

### Theme Support

- Light and dark themes via `next-themes`.
- Dark theme: glassmorphism cards with backdrop-blur, cyan/purple accent glow effects.
- Light theme: clean white cards with subtle shadows.

See also: `specs/ui/design.md` for full design system.

---

## Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-CRUD-01 | CRUD API response time | < 500ms (p95) |
| NFR-CRUD-02 | Page load time (tasks page) | < 2 seconds |
| NFR-CRUD-03 | Concurrent user support | 50+ simultaneous users |
| NFR-CRUD-04 | Data persistence | All data survives server restart (Neon PostgreSQL) |
| NFR-CRUD-05 | User isolation | Enforced at API layer; no data leaks between users |
| NFR-CRUD-06 | Accessibility | Form inputs labeled, keyboard navigable, focus indicators |
| NFR-CRUD-07 | Mobile responsive | Fully functional on screens >= 320px |

---

## Acceptance Criteria Summary (Gherkin)

```gherkin
Feature: Task CRUD Operations

  Background:
    Given the user is authenticated with a valid JWT token
    And the backend is connected to Neon PostgreSQL

  # --- CREATE ---
  Scenario: Create task with valid title
    When the user sends POST /api/{user_id}/tasks with title "Buy milk"
    Then the response status is 201
    And the response body contains the created task with id, title, completed=false

  Scenario: Create task with empty title rejected
    When the user sends POST /api/{user_id}/tasks with title ""
    Then the response status is 400

  Scenario: Create task with past due date rejected
    When the user sends POST /api/{user_id}/tasks with due_date in the past
    Then the response status is 400
    And the detail says "Due date cannot be in the past"

  # --- READ ---
  Scenario: List tasks returns only user's tasks
    Given User A has 3 tasks and User B has 2 tasks
    When User A sends GET /api/{user_A_id}/tasks
    Then the response contains exactly 3 tasks

  Scenario: Filter tasks by status
    Given the user has 2 pending and 1 completed task
    When the user sends GET /api/{user_id}/tasks?status=pending
    Then the response contains exactly 2 tasks

  Scenario: Sort tasks by due date ascending
    When the user sends GET /api/{user_id}/tasks?sort=due_date&order=asc
    Then tasks are ordered by earliest due_date first

  # --- UPDATE ---
  Scenario: Update task title
    Given the user has a task with id 1
    When the user sends PUT /api/{user_id}/tasks/1 with title "Updated title"
    Then the response contains title "Updated title"
    And updated_at is refreshed

  Scenario: Update another user's task forbidden
    When User A sends PUT /api/{user_B_id}/tasks/1
    Then the response status is 403

  # --- DELETE ---
  Scenario: Delete task
    Given the user has a task with id 1
    When the user sends DELETE /api/{user_id}/tasks/1
    Then the response status is 200
    And GET /api/{user_id}/tasks/1 returns 404

  # --- COMPLETE ---
  Scenario: Toggle task completion
    Given the user has a pending task with id 1
    When the user sends PATCH /api/{user_id}/tasks/1/complete
    Then the task completed field is true
    When the user sends PATCH /api/{user_id}/tasks/1/complete again
    Then the task completed field is false

  # --- ISOLATION ---
  Scenario: Cross-user access denied
    When User A sends GET /api/{user_B_id}/tasks
    Then the response status is 403
    And the detail says "Cannot access other users' tasks"
```

---

## Related Specs

- `specs/database/schema.md` - Table definitions and indexes
- `specs/ui/design.md` - Visual design system and component specs
- `specs/phase-2-fullstack/spec.md` - Phase II full feature specification
- `specs/phase-3-chatbot/spec.md` - MCP tool definitions for chat-based CRUD
- `specs/features/phase-v-integration.md` - Event-driven CRUD extensions

---

## Revision History

| Date | Change | Author |
|---|---|---|
| 2025-12-29 | Initial draft aligned with Phase II implementation | spec-kit |
| 2026-02-10 | Formalized from existing code and specs; added Gherkin acceptance criteria, validation rules, error taxonomy, and Phase III-V references | claude-code |
