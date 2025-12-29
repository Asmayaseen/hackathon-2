# Database Schema Specification - Phase II

## Overview
PostgreSQL database schema for Evolution Todo application, hosted on Neon Serverless. Designed for multi-user task management with authentication support.

## Database Provider

**Platform:** Neon Serverless PostgreSQL
**Website:** https://neon.tech
**Plan:** Free tier (sufficient for Phase II)

**Benefits:**
- Serverless (auto-scaling, auto-sleeping)
- PostgreSQL 15+ compatibility
- Free tier: 512MB storage, 3GB data transfer
- Connection pooling built-in
- Branching for dev/staging/production

---

## Tables

### Table 1: users
Managed by Better Auth, stores user accounts.

**Purpose:** User authentication and account management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000") |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email (lowercase, unique) |
| name | VARCHAR(255) | NOT NULL | User's display name |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password (bcrypt/argon2) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last updated timestamp |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Notes:**
- Better Auth may add additional columns (email_verified, etc.)
- Never query password_hash in application code (only for auth)
- Email is case-insensitive (store as lowercase)

---

### Table 2: tasks
Stores user tasks.

**Purpose:** Todo items with CRUD operations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing task ID |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY → users(id) | Owner's user ID |
| title | VARCHAR(200) | NOT NULL | Task title (1-200 characters) |
| description | TEXT | NULL | Optional task description (max 1000 chars in app validation) |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Foreign Key:**
```sql
CONSTRAINT fk_tasks_user
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;
```

**Indexes:**
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

**Notes:**
- ON DELETE CASCADE: When user is deleted, all their tasks are deleted
- Composite index (user_id, completed) for filtered queries
- created_at index for sorting by date

---

## SQL Schema (Complete)

```sql
-- Create users table (Better Auth manages this, but schema for reference)
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_tasks_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Auto-update updated_at on tasks UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## SQLModel Models (Python)

### User Model
```python
# backend/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Model
```python
# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Database Connection

### Environment Variable
```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

**Neon Connection String Example:**
```
postgresql://username:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### SQLModel Connection (FastAPI)
```python
# backend/db.py
from sqlmodel import create_engine, Session, SQLModel
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Max 10 connections
    max_overflow=20  # Allow 20 overflow connections
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Initialize Database (Startup)
```python
# backend/main.py
from fastapi import FastAPI
from db import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

---

## Queries and Patterns

### Common Queries

#### 1. Get All User Tasks
```python
from sqlmodel import Session, select

def get_user_tasks(session: Session, user_id: str, status: str = "all"):
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Sort by created_at descending (newest first)
    query = query.order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    return tasks
```

#### 2. Create Task
```python
def create_task(session: Session, user_id: str, title: str, description: str = None):
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

#### 3. Update Task
```python
from datetime import datetime

def update_task(session: Session, task_id: int, user_id: str, title: str = None, description: str = None):
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise ValueError("Task not found or unauthorized")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

#### 4. Delete Task
```python
def delete_task(session: Session, task_id: int, user_id: str):
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise ValueError("Task not found or unauthorized")

    session.delete(task)
    session.commit()
    return True
```

#### 5. Toggle Completion
```python
from datetime import datetime

def toggle_task_completion(session: Session, task_id: int, user_id: str, completed: bool):
    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise ValueError("Task not found or unauthorized")

    task.completed = completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

---

## Data Integrity

### Referential Integrity
- **Foreign Key Constraint**: tasks.user_id → users.id
- **ON DELETE CASCADE**: When user is deleted, all tasks are auto-deleted
- Prevents orphaned tasks

### Data Validation
**Database Level:**
- NOT NULL constraints on required fields
- VARCHAR length limits
- DEFAULT values for booleans and timestamps

**Application Level (SQLModel):**
- min_length, max_length on strings
- Field validation
- Type checking

### Concurrency
- PostgreSQL handles concurrent writes with MVCC (Multi-Version Concurrency Control)
- No explicit locking needed for basic CRUD operations
- updated_at trigger ensures last-write-wins

---

## Migrations (Future Enhancement)

**Out of Scope for Phase II**, but recommended for production:

Use Alembic for schema migrations:
```bash
# Install
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add tasks table"

# Apply migration
alembic upgrade head
```

**Phase II Approach:** Use SQLModel.metadata.create_all() on startup (simpler for hackathon)

---

## Sample Data (For Testing)

```sql
-- Insert test user
INSERT INTO users (id, email, name, password_hash)
VALUES (
    'test-user-123',
    'test@example.com',
    'Test User',
    '$2b$12$hashed_password_here'  -- Use bcrypt hash
);

-- Insert test tasks
INSERT INTO tasks (user_id, title, description, completed) VALUES
('test-user-123', 'Buy groceries', 'Milk, eggs, bread', false),
('test-user-123', 'Write report', 'Quarterly report for Q4', false),
('test-user-123', 'Call mom', null, true),
('test-user-123', 'Fix bug #42', 'Authentication timeout issue', false),
('test-user-123', 'Learn FastAPI', 'Complete tutorial and build API', true);
```

---

## Database Performance

### Expected Query Performance
- **SELECT tasks by user_id**: < 50ms (with index)
- **INSERT task**: < 20ms
- **UPDATE task**: < 30ms
- **DELETE task**: < 20ms

### Optimization Tips
1. **Indexes are critical**: Ensure idx_tasks_user_id and idx_tasks_user_completed exist
2. **Connection pooling**: Use pool_size=10 to reuse connections
3. **Avoid N+1 queries**: Use SQLModel relationships if needed
4. **LIMIT queries**: For pagination, always use LIMIT to avoid full table scans

### Neon-Specific Optimizations
- **Auto-suspend**: Database sleeps after inactivity (free tier), first query after wake may be slower (~1-2s)
- **Connection pooling**: Neon provides built-in pooling at connection string level
- **Branching**: Use Neon branches for dev/test to avoid polluting production data

---

## Backup and Recovery

**Neon Free Tier:**
- 7-day point-in-time recovery
- Automatic daily backups
- Restore via Neon dashboard

**Production Recommendations:**
- Enable point-in-time recovery
- Set up automated backups
- Test restore procedure

---

## Security Considerations

### SQL Injection Prevention
- ✅ Use SQLModel/SQLAlchemy (parameterized queries)
- ❌ Never use f-strings or string concatenation for queries

**Bad Example:**
```python
# NEVER DO THIS
query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"  # Vulnerable to SQL injection
```

**Good Example:**
```python
# ALWAYS DO THIS
query = select(Task).where(Task.user_id == user_id)  # Safe, parameterized
```

### Password Storage
- ✅ Always hash passwords with bcrypt/argon2
- ❌ Never store plain-text passwords
- ✅ Use password_hash column (Better Auth handles this)

### Connection Security
- ✅ Always use SSL: `?sslmode=require` in connection string
- ✅ Store DATABASE_URL in environment variables, never in code
- ✅ Use different credentials for dev/prod

---

## Testing Checklist

### Schema Tests
- [ ] Tables exist: users, tasks
- [ ] Foreign key constraint works (tasks.user_id → users.id)
- [ ] ON DELETE CASCADE works (delete user → tasks deleted)
- [ ] Unique constraint on users.email
- [ ] Default values: tasks.completed = false

### Query Tests
- [ ] Create task → task in database
- [ ] Get tasks filtered by user_id → only that user's tasks
- [ ] Update task → updated_at timestamp changes
- [ ] Delete task → task removed from database
- [ ] Toggle completion → completed field updates

### Performance Tests
- [ ] Query 100 tasks by user_id → < 100ms
- [ ] Create 100 tasks → < 5s total
- [ ] Concurrent updates don't corrupt data

---

## Success Metrics

✅ **Database complete when:**
- Schema created successfully on Neon
- SQLModel models match database schema
- All queries work correctly
- Indexes improve query performance
- Foreign key constraints enforced
- Triggers update updated_at automatically
- Connection pooling configured
- No SQL injection vulnerabilities

---

## Out of Scope (Phase II)

❌ **Not included:**
- Database migrations (Alembic)
- Full-text search (PostgreSQL FTS)
- Database replication
- Custom indices for advanced queries
- Stored procedures
- Database-level validation beyond constraints

**Focus:** Basic schema with proper relationships and indexes. Advanced features in later phases.

---

## Neon Setup Instructions

### 1. Create Neon Account
- Visit https://neon.tech
- Sign up (free tier, no credit card required)

### 2. Create Project
- Click "Create Project"
- Name: "evolution-todo"
- Region: Choose closest to your location
- PostgreSQL version: 15+

### 3. Get Connection String
- Go to project dashboard
- Copy connection string
- Format: `postgresql://user:pass@host/db?sslmode=require`

### 4. Set Environment Variable
```bash
# .env (backend)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
```

### 5. Initialize Database
```bash
# Run FastAPI app (will create tables on startup)
cd backend
uvicorn main:app --reload
```

### 6. Verify Schema
- Go to Neon dashboard → SQL Editor
- Run: `SELECT * FROM pg_tables WHERE schemaname = 'public';`
- Should see: users, tasks

---

**References:**
- Neon Docs: https://neon.tech/docs
- SQLModel Docs: https://sqlmodel.tiangolo.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Overview: `/specs/overview.md`
- Task CRUD: `/specs/features/task-crud.md`
- API Endpoints: `/specs/api/rest-endpoints.md`
- Authentication: `/specs/features/authentication.md`
