# Data Model: Dashboard - Task Management Interface

**Feature**: 1-dashboard
**Date**: 2025-12-29

## Entities

### User Session (Frontend Only)

Client-side representation of authenticated user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string (UUID) | Yes | User identifier from backend |
| email | string | Yes | User email address |
| name | string | No | Display name |
| auth_token | string | Yes | JWT token for API authentication |

**Storage**: localStorage (browser)
**Validation**: Token presence required for dashboard access

---

### Task

Todo item belonging to a user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Auto-incrementing primary key |
| user_id | string (UUID) | Yes | Foreign key to User |
| title | string (1-200 chars) | Yes | Task title |
| description | string | No | Optional task description |
| completed | boolean | Yes | Completion status (default: false) |
| created_at | datetime | Yes | Creation timestamp (UTC) |
| updated_at | datetime | Yes | Last update timestamp (UTC) |

**Storage**: Neon PostgreSQL via SQLModel
**Validation**: Title required, max 200 characters

---

### Statistics (Computed)

Aggregated task metrics computed from Task list.

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total task count |
| pending | integer | Tasks where completed = false |
| completed | integer | Tasks where completed = true |
| percentage | number | (completed / total) * 100, or 0 if total = 0 |

**Storage**: Not persisted - computed on each API response
**Source**: Backend `/api/{user_id}/tasks` endpoint returns counts in response

---

## Relationships

```
User (1) ─────────────< Task (many)
          user_id FK

Statistics ─────────────computed from─────────────< Task (many)
```

## State Transitions

### Task Completion State

```
┌─────────┐     toggle      ┌───────────┐
│ Pending │ ◄─────────────► │ Completed │
└─────────┘                 └───────────┘
completed=false             completed=true
```

### Filter States

```
┌─────┐     ┌─────────┐     ┌───────────┐
│ All │ ◄─► │ Pending │ ◄─► │ Completed │
└─────┘     └─────────┘     └───────────┘
status=all  status=pending  status=completed
```

## API Response Formats

### GET /api/{user_id}/tasks Response

```typescript
interface TasksResponse {
  tasks: Task[];
  count: {
    total: number;
    pending: number;
    completed: number;
  };
}
```

### Task Object

```typescript
interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

## Validation Rules

### Task Creation

- Title: Required, 1-200 characters, trimmed
- Description: Optional, no length limit
- completed: Auto-set to false

### Task Update

- Title: Optional, 1-200 characters if provided
- Description: Optional
- completed: Optional boolean

### User Session

- auth_token: Required for all API calls
- user_id: Required for constructing API paths
