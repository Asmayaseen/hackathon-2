-- Migration: Phase 2 Advanced Features
-- Date: 2026-01-01
-- Description: Add columns to tasks, create new tables
-- Task: T003
-- Spec: specs/1-phase2-advanced-features/data-model.md

BEGIN TRANSACTION;

-- 1. Extend tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP NULL;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'none' CHECK (priority IN ('high', 'medium', 'low', 'none'));
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(100) NULL;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_offset INTEGER NULL CHECK (reminder_offset > 0 AND reminder_offset <= 10080);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_recurring_id INTEGER NULL REFERENCES tasks(id) ON DELETE SET NULL;

-- 2. Add full-text search
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS idx_tasks_search ON tasks USING gin(search_vector);

-- Create or replace trigger for search vector update
DROP TRIGGER IF EXISTS tasks_search_update ON tasks;
CREATE TRIGGER tasks_search_update BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);

-- 3. Add performance indexes
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_recurring ON tasks(is_recurring) WHERE is_recurring = TRUE;

-- 4. Create task_history table
CREATE TABLE IF NOT EXISTS task_history (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id),
  action VARCHAR(50) NOT NULL CHECK (action IN ('created', 'updated', 'completed', 'uncompleted', 'deleted', 'priority_changed', 'due_date_changed', 'tags_changed')),
  old_value JSON NULL,
  new_value JSON NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_task_id ON task_history(task_id);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON task_history(timestamp DESC);

-- 5. Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
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
CREATE TABLE IF NOT EXISTS tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#6B7280',
  usage_count INTEGER DEFAULT 1 CHECK (usage_count >= 0),
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_tags_user_name ON tags(user_id, name);
CREATE INDEX IF NOT EXISTS idx_tags_usage ON tags(user_id, usage_count DESC);

-- 7. Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id VARCHAR(255) NOT NULL REFERENCES users(id),
  scheduled_time TIMESTAMP NOT NULL,
  sent BOOLEAN DEFAULT FALSE,
  notification_type VARCHAR(20) DEFAULT 'reminder' CHECK (notification_type IN ('due', 'reminder', 'recurring')),
  created_at TIMESTAMP DEFAULT NOW(),
  sent_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_notif_scheduled ON notifications(scheduled_time) WHERE sent = FALSE;
CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id);

-- 8. Create default preferences for existing users
INSERT INTO user_preferences (user_id)
SELECT id FROM users
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
