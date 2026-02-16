# REST API Endpoints Specification

**Spec ID**: API-REST-001
**Created**: 2025-12-29
**Updated**: 2026-02-10
**Status**: Implemented (Phase II - V)
**Base URL**: `http://localhost:8000` (dev) | Deployed backend URL (prod)

---

## Global Conventions

| Convention | Detail |
|---|---|
| Content-Type | `application/json` (unless noted) |
| Authentication | `Authorization: Bearer <JWT>` on all protected endpoints |
| User Isolation | URL `{user_id}` MUST match JWT `user_id` or response is 403 |
| Error Format | `{"detail": "<message>"}` |
| Timestamps | ISO 8601 UTC (`2025-12-29T10:00:00Z`) |
| JWT Algorithm | HS256, 7-day expiry |
| CORS | Enabled for frontend origin |

---

## 1. Authentication

**Source**: `routes/auth.py`
**Prefix**: `/api/auth`
**Auth Required**: No

---

### POST /api/auth/signup

Register a new user account.

| Field | Value |
|---|---|
| Auth | No |
| Status | 200 |

**Request Body**:

| Field | Type | Required | Constraints |
|---|---|---|---|
| `name` | string | Yes | 1-255 chars |
| `email` | string (email) | Yes | Valid email, unique |
| `password` | string | Yes | 8-255 chars |

**Response (200)**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "name": "John"
  }
}
```

**Errors**:

| Status | Condition | Detail |
|---|---|---|
| 400 | Email already exists | `"Email already registered"` |
| 422 | Validation error | Pydantic error (short password, invalid email) |

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"secure123"}'
```

---

### POST /api/auth/signin

Authenticate existing user and receive JWT.

| Field | Value |
|---|---|
| Auth | No |
| Status | 200 |

**Request Body**:

| Field | Type | Required |
|---|---|---|
| `email` | string (email) | Yes |
| `password` | string | Yes |

**Response (200)**: Same schema as signup.

**Errors**:

| Status | Condition | Detail |
|---|---|---|
| 401 | Wrong email or password | `"Invalid email or password"` |

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"secure123"}'
```

---

### GET /api/auth/me

Get current authenticated user info. **(Stub — not implemented in Phase 2)**

---

## 2. Tasks

**Source**: `routes/tasks.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes (all endpoints)

---

### GET /api/{user_id}/tasks

List all tasks with optional filtering and sorting.

**Query Parameters**:

| Param | Alias | Type | Default | Values |
|---|---|---|---|---|
| `status` | status_filter | string | — | `all`, `pending`, `completed` |
| `priority` | priority_filter | string | — | `all`, `high`, `medium`, `low`, `none` |
| `due` | due_filter | string | — | `all`, `today`, `overdue`, `week` |
| `sort` | sort_by | string | `created_at` | `created_at`, `due_date`, `priority`, `title` |
| `order` | sort_order | string | `desc` | `asc`, `desc` |

**Response (200)**:

```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "uuid",
      "title": "Buy groceries",
      "description": "Milk, eggs",
      "completed": false,
      "created_at": "2025-12-29T10:00:00Z",
      "updated_at": "2025-12-29T10:00:00Z",
      "due_date": "2025-12-31T14:00:00Z",
      "priority": "high",
      "tags": ["shopping"],
      "recurrence_pattern": null,
      "reminder_offset": null,
      "is_recurring": false,
      "parent_recurring_id": null
    }
  ],
  "count": {
    "total": 10,
    "pending": 7,
    "completed": 3
  }
}
```

**Errors**:

| Status | Detail |
|---|---|
| 403 | `"Cannot access other users' tasks"` |

**Example curl**:

```bash
curl http://localhost:8000/api/USER_ID/tasks?status=pending&sort=due_date&order=asc \
  -H "Authorization: Bearer TOKEN"
```

---

### POST /api/{user_id}/tasks

Create a new task.

| Field | Value |
|---|---|
| Auth | Yes |
| Status | 201 Created |

**Request Body**:

| Field | Type | Required | Constraints |
|---|---|---|---|
| `title` | string | Yes | 1-200 chars |
| `description` | string | No | — |
| `due_date` | datetime (ISO 8601) | No | Must not be in the past |
| `priority` | string | No | `high`, `medium`, `low`, `none` (default: `none`) |
| `tags` | array[string] | No | Default: `[]` |
| `recurrence_pattern` | string | No | `daily`, `weekly`, `monthly`, `yearly` |
| `reminder_offset` | integer | No | Minutes before due_date |

**Response (201)**: `TaskResponse` object.

**Errors**:

| Status | Detail |
|---|---|
| 400 | `"Invalid priority. Must be one of: high, medium, low, none"` |
| 400 | `"Due date cannot be in the past"` |
| 403 | `"Cannot create tasks for other users"` |

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/USER_ID/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","priority":"high","due_date":"2026-03-01T14:00:00Z"}'
```

---

### GET /api/{user_id}/tasks/{task_id}

Get a single task by ID.

**Response (200)**: `TaskResponse` object.

**Errors**:

| Status | Detail |
|---|---|
| 403 | `"Cannot access other users' tasks"` |
| 404 | `"Task not found"` |

**Example curl**:

```bash
curl http://localhost:8000/api/USER_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

---

### PUT /api/{user_id}/tasks/{task_id}

Update a task. All fields optional.

**Request Body**:

| Field | Type | Required |
|---|---|---|
| `title` | string | No (1-200 chars if provided) |
| `description` | string | No |
| `completed` | boolean | No |
| `due_date` | datetime | No |
| `priority` | string | No |
| `tags` | array[string] | No |
| `recurrence_pattern` | string | No |
| `reminder_offset` | integer | No |

**Response (200)**: Updated `TaskResponse` object.

**Errors**:

| Status | Detail |
|---|---|
| 400 | `"Invalid priority..."` or `"Due date cannot be in the past"` |
| 403 | `"Cannot update other users' tasks"` |
| 404 | `"Task not found"` |

**Example curl**:

```bash
curl -X PUT http://localhost:8000/api/USER_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title","priority":"medium"}'
```

---

### DELETE /api/{user_id}/tasks/{task_id}

Delete a task permanently.

| Field | Value |
|---|---|
| Auth | Yes |
| Status | 204 No Content |

**Response**: Empty body.

**Errors**:

| Status | Detail |
|---|---|
| 403 | `"Cannot delete other users' tasks"` |
| 404 | `"Task not found"` |

**Example curl**:

```bash
curl -X DELETE http://localhost:8000/api/USER_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

---

### PATCH /api/{user_id}/tasks/{task_id}/complete

Toggle task completion status (pending ↔ completed).

**Response (200)**: `TaskResponse` with toggled `completed` field.

**Errors**:

| Status | Detail |
|---|---|
| 403 | `"Cannot update other users' tasks"` |
| 404 | `"Task not found"` |

**Example curl**:

```bash
curl -X PATCH http://localhost:8000/api/USER_ID/tasks/1/complete \
  -H "Authorization: Bearer TOKEN"
```

---

## 3. Search

**Source**: `routes/search.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### GET /api/{user_id}/search

Case-insensitive search across task titles, descriptions, and tags.

**Query Parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | Yes (min 1 char) | Search query |
| `status` | string | No | `all`, `pending`, `completed` |

**Response (200)**:

```json
{
  "tasks": [TaskResponse],
  "count": { "total": 3, "pending": 2, "completed": 1 },
  "query": "groceries"
}
```

**Example curl**:

```bash
curl "http://localhost:8000/api/USER_ID/search?q=groceries&status=pending" \
  -H "Authorization: Bearer TOKEN"
```

---

## 4. Statistics

**Source**: `routes/stats.py`
**Auth Required**: Yes

---

### GET /api/{user_id}/stats

Dashboard aggregation statistics.

**Response (200)**:

```json
{
  "total_tasks": 15,
  "completed_tasks": 8,
  "completion_rate": 53.33,
  "priority_distribution": { "high": 3, "medium": 5, "low": 4, "none": 3 },
  "overdue_count": 2,
  "upcoming_count": 4,
  "active_count": 7
}
```

**Example curl**:

```bash
curl http://localhost:8000/api/USER_ID/stats \
  -H "Authorization: Bearer TOKEN"
```

---

### GET /api/{user_id}/stats/completion-history

Completion history over last N days.

**Query Parameters**:

| Param | Type | Default |
|---|---|---|
| `days` | integer | 7 |

**Response (200)**:

```json
{
  "history": [
    { "date": "2025-12-29", "completed": 3 },
    { "date": "2025-12-28", "completed": 1 }
  ]
}
```

---

## 5. History (Audit Log)

**Source**: `routes/history.py`
**Auth Required**: Yes

---

### GET /api/{user_id}/history

Retrieve task modification history.

**Query Parameters**:

| Param | Type | Default | Constraint |
|---|---|---|---|
| `task_id` | integer | — | Optional: filter by task |
| `limit` | integer | 50 | max 100 |
| `offset` | integer | 0 | — |

**Response (200)**:

```json
{
  "history": [
    {
      "id": 1,
      "task_id": 5,
      "user_id": "uuid",
      "action": "updated",
      "old_value": { "title": "Old" },
      "new_value": { "title": "New" },
      "timestamp": "2025-12-29T10:00:00Z"
    }
  ],
  "count": 1,
  "offset": 0,
  "limit": 50
}
```

**Example curl**:

```bash
curl "http://localhost:8000/api/USER_ID/history?limit=10&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

---

## 6. Notifications

**Source**: `routes/notifications.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### GET /api/{user_id}/notifications

Retrieve user notifications (reminders).

**Query Parameters**:

| Param | Alias | Type | Default |
|---|---|---|---|
| `unread` | unread_only | boolean | `true` |
| `limit` | — | integer | 20 (max 50) |

**Response (200)**:

```json
{
  "notifications": [
    {
      "id": 1,
      "task_id": 5,
      "user_id": "uuid",
      "scheduled_time": "2025-12-31T13:30:00Z",
      "sent": false,
      "notification_type": "reminder",
      "created_at": "2025-12-29T10:00:00Z",
      "sent_at": null
    }
  ],
  "count": 1
}
```

---

### PATCH /api/{user_id}/notifications/{notification_id}/read

Mark a notification as read/sent.

**Response (200)**:

```json
{ "id": 1, "sent": true, "sent_at": "2025-12-29T11:00:00Z" }
```

**Errors**:

| Status | Detail |
|---|---|
| 404 | `"Notification not found"` |

---

## 7. Preferences

**Source**: `routes/preferences.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### GET /api/{user_id}/preferences

Get user preferences. Creates default if none exist.

**Response (200)**:

```json
{
  "user_id": "uuid",
  "theme": "light",
  "notifications_enabled": true,
  "notification_sound": true,
  "default_priority": "none",
  "default_view": "all",
  "language": "en",
  "timezone": "UTC"
}
```

---

### PUT /api/{user_id}/preferences

Update user preferences. All fields optional.

**Request Body**:

| Field | Type | Values |
|---|---|---|
| `theme` | string | `light`, `dark` |
| `notifications_enabled` | boolean | — |
| `notification_sound` | boolean | — |
| `default_priority` | string | `high`, `medium`, `low`, `none` |
| `default_view` | string | `all`, `pending`, `completed` |
| `language` | string | `en`, `ur` |
| `timezone` | string | IANA timezone |

**Example curl**:

```bash
curl -X PUT http://localhost:8000/api/USER_ID/preferences \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark","language":"en"}'
```

---

## 8. Bulk Operations

**Source**: `routes/bulk.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### POST /api/{user_id}/tasks/bulk

Bulk update or delete tasks.

**Request Body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `task_ids` | array[int] | Yes (min 1) | IDs to operate on |
| `completed` | boolean | No | Set completion status |
| `priority` | string | No | Set priority |
| `delete` | boolean | No (default false) | If true, delete the tasks |

**Response (200)**:

```json
{
  "action": "updated",
  "affected": 3,
  "missing_ids": []
}
```

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/USER_ID/tasks/bulk \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_ids":[1,2,3],"completed":true}'
```

---

## 9. Recurrence

**Source**: `routes/recurrence.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### POST /api/{user_id}/tasks/{task_id}/complete

Complete a task and auto-create next instance if recurring.

If the task has `is_recurring=true` and a `recurrence_pattern`, a new task is created with the next due date based on the pattern (daily/weekly/monthly/yearly).

**Response (200)**: Completed `TaskResponse`. If recurring, a new sibling task is also created in the database.

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/USER_ID/tasks/5/complete \
  -H "Authorization: Bearer TOKEN"
```

---

## 10. Export / Import

**Source**: `routes/export_import.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### GET /api/{user_id}/export/json

Export all user tasks as a downloadable JSON file.

**Response**: `application/json` file download (`Content-Disposition: attachment`).

**Example curl**:

```bash
curl http://localhost:8000/api/USER_ID/export/json \
  -H "Authorization: Bearer TOKEN" -o tasks.json
```

---

### GET /api/{user_id}/export/csv

Export all user tasks as a downloadable CSV file.

**Response**: `text/csv` file download.

**Example curl**:

```bash
curl http://localhost:8000/api/USER_ID/export/csv \
  -H "Authorization: Bearer TOKEN" -o tasks.csv
```

---

## 11. Chat (Phase III+)

**Source**: `routes/chat.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### POST /api/{user_id}/chat

Stateless conversational endpoint. AI agent processes natural language using MCP tools.

**Request Body**:

| Field | Type | Required | Description |
|---|---|---|---|
| `conversation_id` | integer | No | Omit to create new conversation |
| `message` | string | Yes | Natural language input |

**Response (200)**:

```json
{
  "conversation_id": 1,
  "response": "I've created a task 'Buy groceries' for you!",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": { "title": "Buy groceries" },
      "result": { "task_id": 5, "status": "created" }
    }
  ]
}
```

**Errors**:

| Status | Detail |
|---|---|
| 403 | `"Cannot access another user's chat"` |
| 404 | `"Conversation not found"` |

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/USER_ID/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}'
```

---

## 12. ChatKit (Phase III+)

**Source**: `routes/chatkit.py`
**Prefix**: `/api/chatkit`
**Auth Required**: Yes

---

### POST /api/chatkit/session

Create a ChatKit session with client secret for frontend integration.

**Request Body**:

| Field | Type | Required |
|---|---|---|
| `user_id` | string | Yes |

**Response (200)**:

```json
{
  "client_secret": "random-secure-token",
  "server_url": "http://localhost:8000/api/chatkit"
}
```

---

### POST /api/chatkit/respond

ChatKit respond endpoint. Streams AI response events via SSE.

**Request Body** (raw JSON, not Pydantic):

| Field | Type | Required |
|---|---|---|
| `thread_id` | string | No |
| `message` | string | Yes |

**Response**: `text/event-stream` (Server-Sent Events).

```
data: {"type": "TextContent", "data": {"text": "I've added..."}}

data: {"type": "ToolCall", "data": {"tool": "add_task", ...}}
```

---

### GET /api/chatkit/threads

List all ChatKit threads (conversations) for authenticated user.

---

## 13. Voice (Phase III+)

**Source**: `routes/voice.py`
**Prefix**: `/api/{user_id}`
**Auth Required**: Yes

---

### POST /api/{user_id}/transcribe

Transcribe audio to text using Whisper API (OpenAI or Groq).

**Request**: `multipart/form-data`

| Field | Type | Required |
|---|---|---|
| `audio` | File (webm/mp3/wav) | Yes |

**Response (200)**:

```json
{
  "text": "Add a task to buy groceries",
  "language": "en"
}
```

**Errors**:

| Status | Detail |
|---|---|
| 400 | `"Audio file is required"` |
| 403 | `"Cannot transcribe for another user"` |

**Example curl**:

```bash
curl -X POST http://localhost:8000/api/USER_ID/transcribe \
  -H "Authorization: Bearer TOKEN" \
  -F "audio=@recording.webm"
```

---

## 14. Dapr Events (Phase V)

**Source**: `routes/events.py`
**Auth Required**: No (called by Dapr sidecar)

---

### GET /dapr/subscribe

Dapr subscription configuration. Called automatically by Dapr sidecar on startup.

**Response (200)**:

```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/api/events/task-events"
  },
  {
    "pubsubname": "kafka-pubsub",
    "topic": "reminders",
    "route": "/api/events/reminders"
  }
]
```

---

### POST /api/events/task-events

Receive task events from Dapr Pub/Sub (CloudEvents format).

**Payload** (from Dapr):

| Field | Type |
|---|---|
| `event_type` | string (`created`, `updated`, `completed`, `deleted`) |
| `task_id` | integer |
| `task_data` | object |
| `user_id` | string |
| `timestamp` | string (ISO 8601) |

**Response (200)**: `{"status": "SUCCESS"}`

---

### POST /api/events/reminders

Receive reminder events from Dapr Pub/Sub.

**Payload**:

| Field | Type |
|---|---|
| `task_id` | integer |
| `title` | string |
| `due_at` | string (ISO 8601) |
| `remind_at` | string (ISO 8601) |
| `user_id` | string |

**Response (200)**: `{"status": "SUCCESS"}`

---

## 15. Cron Handlers (Phase V)

**Source**: `routes/cron_handlers.py`
**Prefix**: `/api/cron`
**Auth Required**: No (called by Dapr cron binding)

---

### POST /api/cron/reminder-cron

**Triggered by**: Dapr cron binding (every 5 minutes).

Scans for tasks due within 15min/30min/1hr/24hr windows. Creates notification records and publishes reminder events via Dapr pub/sub.

**Response (200)**:

```json
{
  "status": "success",
  "triggered_at": "2025-12-29T10:05:00Z",
  "reminders_sent": 3
}
```

---

### POST /api/cron/recurring-task-cron

**Triggered by**: Dapr cron binding (every hour).

Scans for completed recurring tasks and creates next occurrence if missing.

**Response (200)**:

```json
{
  "status": "success",
  "triggered_at": "2025-12-29T11:00:00Z",
  "tasks_created": 2
}
```

---

## 16. Notification Service (Phase V — separate microservice)

**Source**: `phase-5/notification-service/main.py`
**Base URL**: `http://notification-service:8001`
**Auth Required**: No (internal service)

---

### GET /health

Health check.

**Response**: `{"status": "healthy", "service": "notification-service"}`

---

### GET /dapr/subscribe

Dapr subscription for `reminders` topic.

---

### POST /api/notifications/reminders

Receive and process reminder events from Kafka via Dapr.

---

## Common Response Models

### TaskResponse

```json
{
  "id": 1,
  "user_id": "uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs",
  "completed": false,
  "created_at": "2025-12-29T10:00:00Z",
  "updated_at": "2025-12-29T10:00:00Z",
  "due_date": "2025-12-31T14:00:00Z",
  "priority": "high",
  "tags": ["shopping"],
  "recurrence_pattern": "weekly",
  "reminder_offset": 30,
  "is_recurring": true,
  "parent_recurring_id": null
}
```

### AuthResponse

```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "user": { "id": "uuid", "email": "john@example.com", "name": "John" }
}
```

---

## Error Code Reference

| Status | Meaning | Common Triggers |
|---|---|---|
| 400 | Bad Request | Validation failure, duplicate email, invalid priority, past due date |
| 401 | Unauthorized | Missing / expired / invalid JWT |
| 403 | Forbidden | URL `user_id` != JWT `user_id` |
| 404 | Not Found | Task / conversation / notification does not exist |
| 422 | Unprocessable Entity | Pydantic schema validation (malformed body) |
| 500 | Internal Server Error | Database or server failure |

---

## Route File Index

| File | Prefix | Phase | Endpoints |
|---|---|---|---|
| `routes/auth.py` | `/api/auth` | II | signup, signin, me |
| `routes/tasks.py` | `/api/{user_id}` | II | CRUD + complete |
| `routes/search.py` | `/api/{user_id}` | II | search |
| `routes/stats.py` | `/api/{user_id}` | II | stats, completion-history |
| `routes/history.py` | `/api/{user_id}` | II | history |
| `routes/notifications.py` | `/api/{user_id}` | II | notifications, mark-read |
| `routes/preferences.py` | `/api/{user_id}` | II | preferences get/put |
| `routes/bulk.py` | `/api/{user_id}` | II | bulk operations |
| `routes/recurrence.py` | `/api/{user_id}` | II | complete-with-recurrence |
| `routes/export_import.py` | `/api/{user_id}` | II | export json/csv |
| `routes/chat.py` | `/api/{user_id}` | III | chat endpoint |
| `routes/chatkit.py` | `/api/chatkit` | III | session, respond, threads |
| `routes/voice.py` | `/api/{user_id}` | III | transcribe |
| `routes/events.py` | `/api/events` | V | dapr subscriptions |
| `routes/cron_handlers.py` | `/api/cron` | V | reminder-cron, recurring-cron |

---

## Related Specs

- `specs/features/task-crud.md` — Task CRUD feature details
- `specs/features/authentication.md` — Auth flow and JWT lifecycle
- `specs/api/mcp-tools.md` — MCP tool specs for AI agent
- `specs/database/schema.md` — Table definitions
- `specs/phase-3-chatbot/spec.md` — Chat and ChatKit architecture

---

## Revision History

| Date | Change | Author |
|---|---|---|
| 2025-12-29 | Initial draft | spec-kit |
| 2026-02-10 | Complete rewrite: scanned all 15 route files across phase-2 through phase-5; documented 30+ endpoints with schemas, curls, and error tables | claude-code |
