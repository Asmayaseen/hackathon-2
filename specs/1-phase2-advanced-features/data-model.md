# Phase 1: Data Model & Schema Design

**Feature**: Phase 2 Advanced Features
**Date**: 2026-01-01
**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (Pydantic + SQLAlchemy)

## Overview

This document defines the database schema extensions required for all 13 advanced features. The design extends the existing `users` and `tasks` tables while adding 4 new tables: `task_history`, `user_preferences`, `tags`, and `notifications`.

**Design Principles**:
- Extend existing tables (backward compatible)
- User-scoped data (all queries filter by `user_id`)
- JSON columns for flexible data (tags, history metadata)
- Indexes for performance (search, filtering, sorting)

---

## Table 1: `tasks` (Extended)

**Purpose**: Core task entity with advanced feature columns added

### Existing Columns (Keep)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| `user_id` | VARCHAR(255) | NOT NULL, FK→users.id | Owner of task |
| `title` | VARCHAR(200) | NOT NULL | Task title |
| `description` | TEXT | NULLABLE | Task description |
| `completed` | BOOLEAN | DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW(), ON UPDATE NOW() | Last update timestamp |

### New Columns (Add via Migration)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `due_date` | TIMESTAMP | NULLABLE | When task is due |
| `priority` | VARCHAR(10) | DEFAULT 'none', CHECK IN ('high', 'medium', 'low', 'none') | Priority level |
| `tags` | JSON | DEFAULT '[]' | Array of tag strings |
| `recurrence_pattern` | VARCHAR(100) | NULLABLE | Cron-style pattern (e.g., "0 9 * * 1-5") |
| `reminder_offset` | INTEGER | NULLABLE | Minutes before due_date to send reminder |
| `is_recurring` | BOOLEAN | DEFAULT FALSE | Whether task is recurring |
| `parent_recurring_id` | INTEGER | NULLABLE, FK→tasks.id | Original recurring task (for instances) |
| `search_vector` | TSVECTOR | GENERATED | Full-text search vector (auto-updated) |

### Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_recurring ON tasks(is_recurring) WHERE is_recurring = TRUE;
CREATE INDEX idx_tasks_search ON tasks USING gin(search_vector);
```

### Validation Rules
- `title`: 1-200 characters, not empty
- `description`: Max 1000 characters
- `priority`: Must be one of: high, medium, low, none
- `tags`: Array of strings, each tag 1-50 characters, max 10 tags
- `recurrence_pattern`: If not null, must be valid cron syntax
- `reminder_offset`: If not null, must be positive integer (1-10080 minutes = 1 week)
- `due_date`: If not null, must be valid timestamp

### State Transitions
```
[New Task]
   ├─> completed = FALSE (default)
   ├─> [User marks complete] → completed = TRUE
   ├─> [User marks incomplete] → completed = FALSE
   └─> [Recurring task completed] → Generate next instance, keep original

[Due Date States]
   ├─> No due date (due_date = NULL)
   ├─> Future due date (due_date > NOW())
   ├─> Due today (DATE(due_date) = CURRENT_DATE)
   └─> Overdue (due_date < NOW() AND completed = FALSE)
```

### Example Row
```sql
INSERT INTO tasks VALUES (
  id: 123,
  user_id: 'user_abc123',
  title: 'Weekly standup meeting',
  description: 'Sync with team on progress',
  completed: FALSE,
  created_at: '2026-01-01 08:00:00',
  updated_at: '2026-01-01 08:00:00',
  due_date: '2026-01-06 09:00:00',
  priority: 'high',
  tags: '["work", "meeting", "recurring"]',
  recurrence_pattern: '0 9 * * 1',  -- Every Monday at 9am
  reminder_offset: 15,  -- 15 minutes before
  is_recurring: TRUE,
  parent_recurring_id: NULL,
  search_vector: to_tsvector('english', 'Weekly standup meeting Sync with team on progress work meeting recurring')
);
```

---

## Table 2: `task_history` (New)

**Purpose**: Audit log of all task modifications

### Schema
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique history entry ID |
| `task_id` | INTEGER | NOT NULL, FK→tasks.id ON DELETE CASCADE | Task being modified |
| `user_id` | VARCHAR(255) | NOT NULL, FK→users.id | User who made change |
| `action` | VARCHAR(50) | NOT NULL, CHECK IN ('created', 'updated', 'completed', 'uncompleted', 'deleted', 'priority_changed', 'due_date_changed', 'tags_changed') | Type of change |
| `old_value` | JSON | NULLABLE | Previous value (for updates) |
| `new_value` | JSON | NULLABLE | New value (for updates) |
| `timestamp` | TIMESTAMP | DEFAULT NOW() | When change occurred |

### Indexes
```sql
CREATE INDEX idx_history_task_id ON task_history(task_id);
CREATE INDEX idx_history_user_id ON task_history(user_id);
CREATE INDEX idx_history_timestamp ON task_history(timestamp DESC);
```

### Triggers
```sql
-- Auto-create history entry on task insert
CREATE TRIGGER task_created_history
AFTER INSERT ON tasks
FOR EACH ROW
INSERT INTO task_history (task_id, user_id, action, new_value, timestamp)
VALUES (NEW.id, NEW.user_id, 'created', json_build_object('title', NEW.title), NOW());

-- Auto-create history entry on task update
CREATE TRIGGER task_updated_history
AFTER UPDATE ON tasks
FOR EACH ROW
WHEN (OLD.* IS DISTINCT FROM NEW.*)
INSERT INTO task_history (task_id, user_id, action, old_value, new_value, timestamp)
VALUES (NEW.id, NEW.user_id,
  CASE
    WHEN OLD.completed != NEW.completed THEN
      CASE WHEN NEW.completed THEN 'completed' ELSE 'uncompleted' END
    WHEN OLD.priority != NEW.priority THEN 'priority_changed'
    WHEN OLD.due_date != NEW.due_date THEN 'due_date_changed'
    WHEN OLD.tags != NEW.tags THEN 'tags_changed'
    ELSE 'updated'
  END,
  json_build_object('old', to_json(OLD.*)),
  json_build_object('new', to_json(NEW.*)),
  NOW()
);
```

### Example Row
```sql
INSERT INTO task_history VALUES (
  id: 456,
  task_id: 123,
  user_id: 'user_abc123',
  action: 'priority_changed',
  old_value: '{"priority": "medium"}',
  new_value: '{"priority": "high"}',
  timestamp: '2026-01-01 10:30:00'
);
```

---

## Table 3: `user_preferences` (New)

**Purpose**: User-specific settings and preferences

### Schema
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | VARCHAR(255) | PRIMARY KEY, FK→users.id ON DELETE CASCADE | User identifier |
| `theme` | VARCHAR(10) | DEFAULT 'light', CHECK IN ('light', 'dark') | UI theme preference |
| `notifications_enabled` | BOOLEAN | DEFAULT TRUE | Master notification toggle |
| `notification_sound` | BOOLEAN | DEFAULT TRUE | Play sound with notifications |
| `default_priority` | VARCHAR(10) | DEFAULT 'none', CHECK IN ('high', 'medium', 'low', 'none') | Default priority for new tasks |
| `default_view` | VARCHAR(20) | DEFAULT 'all', CHECK IN ('all', 'today', 'week', 'month') | Default task list view |
| `language` | VARCHAR(10) | DEFAULT 'en', CHECK IN ('en', 'ur') | UI language (English/Urdu) |
| `timezone` | VARCHAR(50) | DEFAULT 'UTC' | User's timezone (IANA format) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When preferences created |
| `updated_at` | TIMESTAMP | DEFAULT NOW(), ON UPDATE NOW() | Last preference update |

### Indexes
```sql
-- Primary key index on user_id (automatic)
CREATE INDEX idx_prefs_theme ON user_preferences(theme); -- For analytics
```

### Default Values
When user signs up, create default preferences:
```sql
INSERT INTO user_preferences (user_id) VALUES ('user_abc123')
ON CONFLICT (user_id) DO NOTHING; -- Idempotent
```

### Example Row
```sql
INSERT INTO user_preferences VALUES (
  user_id: 'user_abc123',
  theme: 'dark',
  notifications_enabled: TRUE,
  notification_sound: FALSE,
  default_priority: 'medium',
  default_view: 'today',
  language: 'en',
  timezone: 'America/New_York',
  created_at: '2026-01-01 08:00:00',
  updated_at: '2026-01-01 12:00:00'
);
```

---

## Table 4: `tags` (New)

**Purpose**: Tag management and autocomplete

### Schema
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique tag ID |
| `user_id` | VARCHAR(255) | NOT NULL, FK→users.id ON DELETE CASCADE | Tag owner |
| `name` | VARCHAR(50) | NOT NULL | Tag name (e.g., "work") |
| `color` | VARCHAR(7) | DEFAULT '#6B7280' | Hex color code for UI |
| `usage_count` | INTEGER | DEFAULT 1 | Number of tasks using this tag |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When tag first created |
| `last_used_at` | TIMESTAMP | DEFAULT NOW() | When tag last used |

### Indexes
```sql
CREATE UNIQUE INDEX idx_tags_user_name ON tags(user_id, name); -- One tag per user
CREATE INDEX idx_tags_usage ON tags(user_id, usage_count DESC); -- For autocomplete ranking
```

### Constraints
- `name`: 1-50 characters, case-insensitive unique per user
- `color`: Must be valid hex code (#RRGGBB)
- `usage_count`: Non-negative integer

### Auto-Update Logic
```sql
-- When task created/updated with tags, update tag usage_count
-- (Implemented in backend service, not trigger for flexibility)
```

### Example Row
```sql
INSERT INTO tags VALUES (
  id: 789,
  user_id: 'user_abc123',
  name: 'work',
  color: '#EF4444', -- Red
  usage_count: 42,
  created_at: '2026-01-01 08:00:00',
  last_used_at: '2026-01-01 12:00:00'
);
```

---

## Table 5: `notifications` (New)

**Purpose**: Scheduled notification reminders

### Schema
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique notification ID |
| `task_id` | INTEGER | NOT NULL, FK→tasks.id ON DELETE CASCADE | Task to remind about |
| `user_id` | VARCHAR(255) | NOT NULL, FK→users.id | Notification recipient |
| `scheduled_time` | TIMESTAMP | NOT NULL | When to send notification |
| `sent` | BOOLEAN | DEFAULT FALSE | Whether notification sent |
| `notification_type` | VARCHAR(20) | DEFAULT 'reminder', CHECK IN ('due', 'reminder', 'recurring') | Type of notification |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When notification scheduled |
| `sent_at` | TIMESTAMP | NULLABLE | When notification actually sent |

### Indexes
```sql
CREATE INDEX idx_notif_scheduled ON notifications(scheduled_time) WHERE sent = FALSE; -- For cron job
CREATE INDEX idx_notif_user ON notifications(user_id);
CREATE INDEX idx_notif_task ON notifications(task_id);
```

### Example Row
```sql
INSERT INTO notifications VALUES (
  id: 101,
  task_id: 123,
  user_id: 'user_abc123',
  scheduled_time: '2026-01-06 08:45:00', -- 15 min before due_date
  sent: FALSE,
  notification_type: 'reminder',
  created_at: '2026-01-01 08:00:00',
  sent_at: NULL
);
```

---

## Relationships Diagram

```
users (existing)
  ├─ 1:N → tasks (user_id)
  ├─ 1:N → task_history (user_id)
  ├─ 1:1 → user_preferences (user_id)
  ├─ 1:N → tags (user_id)
  └─ 1:N → notifications (user_id)

tasks (extended)
  ├─ 1:N → task_history (task_id)
  ├─ 1:N → notifications (task_id)
  └─ 1:N → tasks (parent_recurring_id) -- Self-referential for recurring instances
```

---

## Migration Script

### File: `phase-2/backend/migrations/002_phase2_advanced.sql`

```sql
-- Migration: Phase 2 Advanced Features
-- Date: 2026-01-01
-- Description: Add columns to tasks, create new tables

BEGIN TRANSACTION;

-- 1. Extend tasks table
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP NULL;
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'none' CHECK (priority IN ('high', 'medium', 'low', 'none'));
ALTER TABLE tasks ADD COLUMN tags JSON DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(100) NULL;
ALTER TABLE tasks ADD COLUMN reminder_offset INTEGER NULL CHECK (reminder_offset > 0 AND reminder_offset <= 10080);
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN parent_recurring_id INTEGER NULL REFERENCES tasks(id) ON DELETE SET NULL;

-- 2. Add full-text search
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

CREATE INDEX idx_tasks_search ON tasks USING gin(search_vector);

CREATE TRIGGER tasks_search_update BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);

-- 3. Add performance indexes
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_recurring ON tasks(is_recurring) WHERE is_recurring = TRUE;

-- 4. Create task_history table
CREATE TABLE task_history (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id),
  action VARCHAR(50) NOT NULL CHECK (action IN ('created', 'updated', 'completed', 'uncompleted', 'deleted', 'priority_changed', 'due_date_changed', 'tags_changed')),
  old_value JSON NULL,
  new_value JSON NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_history_task_id ON task_history(task_id);
CREATE INDEX idx_history_timestamp ON task_history(timestamp DESC);

-- 5. Create user_preferences table
CREATE TABLE user_preferences (
  user_id VARCHAR(255) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  theme VARCHAR(10) DEFAULT 'light' CHECK (theme IN ('light', 'dark')),
  notifications_enabled BOOLEAN DEFAULT TRUE,
  notification_sound BOOLEAN DEFAULT TRUE,
  default_priority VARCHAR(10) DEFAULT 'none' CHECK (default_priority IN ('high', 'medium', 'low', 'none')),
  default_view VARCHAR(20) DEFAULT 'all' CHECK (default_view IN ('all', 'today', 'week', 'month')),
  language VARCHAR(10) DEFAULT 'en' CHECK (language IN ('en', 'ur')),
  timezone VARCHAR(50) DEFAULT 'UTC',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Create tags table
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#6B7280',
  usage_count INTEGER DEFAULT 1 CHECK (usage_count >= 0),
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_tags_user_name ON tags(user_id, name);
CREATE INDEX idx_tags_usage ON tags(user_id, usage_count DESC);

-- 7. Create notifications table
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id),
  scheduled_time TIMESTAMP NOT NULL,
  sent BOOLEAN DEFAULT FALSE,
  notification_type VARCHAR(20) DEFAULT 'reminder' CHECK (notification_type IN ('due', 'reminder', 'recurring')),
  created_at TIMESTAMP DEFAULT NOW(),
  sent_at TIMESTAMP NULL
);

CREATE INDEX idx_notif_scheduled ON notifications(scheduled_time) WHERE sent = FALSE;
CREATE INDEX idx_notif_user ON notifications(user_id);

-- 8. Create default preferences for existing users
INSERT INTO user_preferences (user_id)
SELECT id FROM users
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
```

---

## SQLModel Python Models

### File: `phase-2/backend/models.py` (additions)

```python
from sqlmodel import Field, SQLModel, Column, JSON
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"

# Extended Task model
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # New fields
    due_date: Optional[datetime] = None
    priority: Priority = Field(default=Priority.NONE)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    recurrence_pattern: Optional[str] = None
    reminder_offset: Optional[int] = None
    is_recurring: bool = Field(default=False)
    parent_recurring_id: Optional[int] = Field(default=None, foreign_key="tasks.id")

class TaskHistory(SQLModel, table=True):
    __tablename__ = "task_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(foreign_key="users.id")
    action: str
    old_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserPreferences(SQLModel, table=True):
    __tablename__ = "user_preferences"

    user_id: str = Field(primary_key=True, foreign_key="users.id")
    theme: Theme = Field(default=Theme.LIGHT)
    notifications_enabled: bool = Field(default=True)
    notification_sound: bool = Field(default=True)
    default_priority: Priority = Field(default=Priority.NONE)
    default_view: str = Field(default="all")
    language: str = Field(default="en")
    timezone: str = Field(default="UTC")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    name: str = Field(max_length=50)
    color: str = Field(default="#6B7280", max_length=7)
    usage_count: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(foreign_key="users.id")
    scheduled_time: datetime
    sent: bool = Field(default=False)
    notification_type: str = Field(default="reminder")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
```

---

## Data Integrity Rules

1. **User Isolation**: All queries MUST filter by `user_id` to prevent data leaks
2. **Cascading Deletes**: When user deleted, all related data deleted (CASCADE)
3. **Task History**: Immutable - never update/delete history entries (audit trail)
4. **Tag Consistency**: When task deleted, decrement tag usage_count (backend logic)
5. **Notification Cleanup**: Delete sent notifications older than 30 days (cron job)
6. **Recurring Tasks**: Original recurring task never deleted (only mark inactive)

---

## Performance Considerations

- **Search**: GIN index on `search_vector` enables <10ms searches up to 10k tasks
- **Filtering**: Indexes on `priority`, `due_date`, `completed` enable fast WHERE clauses
- **Sorting**: Composite indexes may be needed for common sorts (e.g., `(user_id, due_date)`)
- **History**: Partition by month if history grows large (>100k entries)
- **Tags**: Usage_count index enables fast autocomplete ranking

---

## Next Steps

1. Review this data model with user
2. Run migration script on development database
3. Update SQLModel models in `phase-2/backend/models.py`
4. Generate API contracts (OpenAPI specs) in Phase 1
5. Create quickstart guide for developers

**Estimated Migration Time**: 5-10 minutes on production (Neon serverless handles concurrency)
