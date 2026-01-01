# API Contracts Summary - Phase 2 Advanced Features

**Base URL**: `http://localhost:8000` (development) | `https://asma-yaseen-evolution-todo-api.hf.space` (production)
**Authentication**: JWT Bearer token in `Authorization` header
**Content-Type**: `application/json`

## 1. Search & Filter API

### `GET /api/{user_id}/tasks/search`

Search and filter tasks with multiple criteria

**Query Parameters**:
- `query` (string, optional): Full-text search term
- `status` (string, optional): "pending" | "completed" | "all"
- `priority` (string, optional): "high" | "medium" | "low" | "none"
- `tags` (string[], optional): Filter by tags (comma-separated)
- `due_before` (ISO date, optional): Tasks due before this date
- `due_after` (ISO date, optional): Tasks due after this date
- `sort` (string, optional): "due_date" | "priority" | "title" | "created_at"
- `order` (string, optional): "asc" | "desc"
- `limit` (int, optional): Max results (default 50)
- `offset` (int, optional): Pagination offset

**Response 200**:
```json
{
  "tasks": [
    {
      "id": 123,
      "title": "Weekly standup",
      "description": "Team sync",
      "completed": false,
      "priority": "high",
      "due_date": "2026-01-06T09:00:00Z",
      "tags": ["work", "meeting"],
      "recurrence_pattern": "0 9 * * 1",
      "is_recurring": true,
      "created_at": "2026-01-01T08:00:00Z",
      "updated_at": "2026-01-01T08:00:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

## 2. Recurring Tasks API

### `POST /api/{user_id}/tasks/{task_id}/complete-recurring`

Mark recurring task complete and generate next instance

**Request Body**: (none)

**Response 200**:
```json
{
  "completed_task": { "id": 123, "completed": true },
  "next_instance": {
    "id": 124,
    "title": "Weekly standup",
    "due_date": "2026-01-13T09:00:00Z",
    "parent_recurring_id": 123
  }
}
```

### `PUT /api/{user_id}/tasks/{task_id}/recurrence`

Update recurrence pattern

**Request Body**:
```json
{
  "recurrence_pattern": "0 9 * * 1-5",
  "reminder_offset": 15
}
```

---

## 3. Analytics API

### `GET /api/{user_id}/analytics/stats`

Get user's task statistics

**Query Parameters**:
- `period` (string, optional): "today" | "week" | "month" | "all" (default "all")

**Response 200**:
```json
{
  "total_tasks": 156,
  "completed_tasks": 89,
  "pending_tasks": 67,
  "completion_rate": 0.57,
  "by_priority": {
    "high": 23,
    "medium": 45,
    "low": 31,
    "none": 57
  },
  "by_status": {
    "completed": 89,
    "pending": 67
  },
  "overdue_tasks": 5,
  "due_today": 8,
  "weekly_activity": [
    { "date": "2025-12-29", "completed": 12 },
    { "date": "2025-12-30", "completed": 15 },
    { "date": "2025-12-31", "completed": 8 },
    { "date": "2026-01-01", "completed": 3 }
  ]
}
```

### `GET /api/{user_id}/tasks/{task_id}/history`

Get task history timeline

**Response 200**:
```json
{
  "history": [
    {
      "id": 456,
      "action": "created",
      "timestamp": "2026-01-01T08:00:00Z",
      "new_value": { "title": "Weekly standup" }
    },
    {
      "id": 457,
      "action": "priority_changed",
      "timestamp": "2026-01-01T10:30:00Z",
      "old_value": { "priority": "medium" },
      "new_value": { "priority": "high" }
    },
    {
      "id": 458,
      "action": "completed",
      "timestamp": "2026-01-01T12:00:00Z"
    }
  ]
}
```

---

## 4. Export/Import API

### `GET /api/{user_id}/export`

Export all tasks

**Query Parameters**:
- `format` (string, required): "json" | "csv"

**Response 200 (JSON)**:
```json
{
  "metadata": {
    "export_date": "2026-01-01T14:00:00Z",
    "app_version": "2.0.0",
    "user_id": "user_abc123",
    "total_tasks": 156
  },
  "tasks": [ /* all tasks */ ]
}
```

**Response 200 (CSV)**:
```csv
Title,Description,Status,Priority,Due Date,Tags,Created,Updated
"Weekly standup","Team sync","pending","high","2026-01-06 09:00:00","work,meeting","2026-01-01 08:00:00","2026-01-01 08:00:00"
```

### `POST /api/{user_id}/import`

Import tasks from file

**Request Body** (multipart/form-data):
- `file` (file): JSON or CSV file
- `merge_strategy` (string): "skip" | "import_new" | "update" (default "skip")

**Response 200**:
```json
{
  "imported": 42,
  "skipped": 5,
  "errors": [
    { "line": 10, "field": "due_date", "message": "Invalid date format" }
  ]
}
```

---

## 5. User Preferences API

### `GET /api/{user_id}/preferences`

Get user preferences

**Response 200**:
```json
{
  "theme": "dark",
  "notifications_enabled": true,
  "notification_sound": false,
  "default_priority": "medium",
  "default_view": "today",
  "language": "en",
  "timezone": "America/New_York"
}
```

### `PATCH /api/{user_id}/preferences`

Update preferences

**Request Body**:
```json
{
  "theme": "dark",
  "notifications_enabled": false
}
```

---

## 6. Tags API

### `GET /api/{user_id}/tags/autocomplete`

Get tag suggestions

**Query Parameters**:
- `query` (string, required): Partial tag name
- `limit` (int, optional): Max results (default 10)

**Response 200**:
```json
{
  "suggestions": [
    { "name": "work", "usage_count": 42, "color": "#EF4444" },
    { "name": "workout", "usage_count": 18, "color": "#10B981" }
  ]
}
```

---

## 7. Notifications API

### `POST /api/{user_id}/tasks/{task_id}/schedule-reminder`

Schedule notification reminder

**Request Body**:
```json
{
  "reminder_offset": 15,
  "notification_type": "reminder"
}
```

**Response 201**:
```json
{
  "notification_id": 101,
  "scheduled_time": "2026-01-06T08:45:00Z"
}
```

### `GET /api/{user_id}/notifications/pending`

Get pending notifications

**Response 200**:
```json
{
  "notifications": [
    {
      "id": 101,
      "task_id": 123,
      "scheduled_time": "2026-01-06T08:45:00Z",
      "notification_type": "reminder"
    }
  ]
}
```

---

## Error Responses

All endpoints return standard error format:

**400 Bad Request**:
```json
{
  "error": "validation_error",
  "message": "Invalid priority value",
  "details": { "field": "priority", "allowed": ["high", "medium", "low", "none"] }
}
```

**401 Unauthorized**:
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

**404 Not Found**:
```json
{
  "error": "not_found",
  "message": "Task not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- **Search/Filter**: 100 requests/minute per user
- **Export**: 5 requests/hour per user
- **Import**: 3 requests/hour per user
- **Other endpoints**: 200 requests/minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1735804800
```

---

## Testing Examples

### Search tasks with multiple filters
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/user_abc123/tasks/search?query=meeting&priority=high&sort=due_date"
```

### Export tasks as CSV
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/user_abc123/export?format=csv" > tasks.csv
```

### Update theme preference
```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark"}' \
  "http://localhost:8000/api/user_abc123/preferences"
```

---

**Next Steps**: Implement these endpoints in `phase-2/backend/routes/` following the contracts above.
