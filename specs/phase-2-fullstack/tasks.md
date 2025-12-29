# Tasks - Phase II: Full-Stack Web Application

## Task Organization

Tasks are organized by execution order: **Backend → Frontend → Integration → Deployment**

**Total Tasks**: 45
**Estimated Time**: 15-20 hours

---

## PHASE 1: Backend Setup & Database (Tasks 1-10)

### Task 1.1: Initialize Backend Project
**Priority**: P1 (Critical - Must be first)
**Estimated Time**: 15 minutes
**Dependencies**: None

**Steps:**
```bash
cd backend
uv init
uv add fastapi uvicorn sqlmodel psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Acceptance Criteria:**
- [x] backend/ directory created
- [x] pyproject.toml exists with dependencies
- [x] Virtual environment created

**Files Created:**
- backend/pyproject.toml
- backend/uv.lock

---

### Task 1.2: Create Database Models
**Priority**: P1
**Estimated Time**: 20 minutes
**Dependencies**: Task 1.1

**Create**: `backend/models.py`

**Code:**
```python
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

**Acceptance Criteria:**
- [x] User model has all required fields
- [x] Task model has foreign key to User
- [x] Field validations match spec

**Test:**
```python
from models import User, Task
user = User(id="test", email="test@example.com", name="Test", password_hash="hash")
task = Task(user_id="test", title="Test Task")
```

---

### Task 1.3: Create Database Connection
**Priority**: P1
**Estimated Time**: 15 minutes
**Dependencies**: Task 1.2

**Create**: `backend/db.py`

**Code:**
```python
from sqlmodel import create_engine, Session, SQLModel
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

**Acceptance Criteria:**
- [x] Database engine created
- [x] Connection pooling configured
- [x] Session dependency function works

**Test:**
```python
from db import create_db_and_tables
create_db_and_tables()  # Should create tables
```

---

### Task 1.4: Setup Neon PostgreSQL Database
**Priority**: P1
**Estimated Time**: 10 minutes
**Dependencies**: None (can be done in parallel)

**Steps:**
1. Go to https://neon.tech
2. Sign up (free tier)
3. Create project: "evolution-todo"
4. Copy connection string
5. Create `backend/.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require
   JWT_SECRET=your-random-secret-min-32-characters-here
   CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
   ```

**Acceptance Criteria:**
- [x] Neon account created
- [x] Project "evolution-todo" exists
- [x] Connection string copied
- [x] .env file created with DATABASE_URL

**Test:**
```bash
# Test connection
psql "postgresql://user:pass@host/neondb?sslmode=require" -c "SELECT 1;"
```

---

### Task 1.5: Create JWT Middleware
**Priority**: P1
**Estimated Time**: 25 minutes
**Dependencies**: Task 1.1

**Create**: `backend/middleware/auth.py`

**Code:**
```python
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Acceptance Criteria:**
- [x] verify_token function created
- [x] Returns user_id from valid JWT
- [x] Raises 401 for invalid/expired tokens

**Test:**
```python
# Generate test token
import jwt
token = jwt.encode({"user_id": "test-123"}, JWT_SECRET, algorithm="HS256")
# Verify it works
user_id = await verify_token(token)
assert user_id == "test-123"
```

---

### Task 1.6: Create Main FastAPI App
**Priority**: P1
**Estimated Time**: 20 minutes
**Dependencies**: Task 1.3, Task 1.5

**Create**: `backend/main.py`

**Code:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
import os

app = FastAPI(title="Evolution Todo API", version="1.0.0")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Evolution Todo API", "status": "running"}

# Import and include routers (will be added in next tasks)
# from routes import tasks
# app.include_router(tasks.router)
```

**Acceptance Criteria:**
- [x] FastAPI app created
- [x] CORS configured
- [x] Database initialized on startup
- [x] Root endpoint returns status

**Test:**
```bash
cd backend
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000 - should see {"message": "Evolution Todo API"}
```

---

### Task 1.7: Create GET /api/{user_id}/tasks Endpoint
**Priority**: P1
**Estimated Time**: 30 minutes
**Dependencies**: Task 1.6

**Create**: `backend/routes/tasks.py`

**Code:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from models import Task
from db import get_session
from middleware.auth import verify_token
from typing import Optional

router = APIRouter(prefix="/api", tags=["tasks"])

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    status: Optional[str] = Query("all", regex="^(all|pending|completed)$"),
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Sort by created_at desc (newest first)
    query = query.order_by(Task.created_at.desc())

    tasks = session.exec(query).all()

    # Calculate counts
    total = len(tasks)
    pending = sum(1 for t in tasks if not t.completed)
    completed = total - pending

    return {
        "tasks": tasks,
        "total": total,
        "pending": pending,
        "completed": completed
    }
```

**Acceptance Criteria:**
- [x] Endpoint requires JWT authentication
- [x] Verifies user_id matches token
- [x] Filters tasks by status (query param)
- [x] Sorts by created_at desc
- [x] Returns tasks array + counts

**Test:**
```bash
# Create test token
TOKEN="your-test-jwt-token"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/test-user/tasks
```

---

### Task 1.8: Create POST /api/{user_id}/tasks Endpoint
**Priority**: P1
**Estimated Time**: 25 minutes
**Dependencies**: Task 1.7

**Add to**: `backend/routes/tasks.py`

**Code:**
```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

@router.post("/{user_id}/tasks", status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

**Acceptance Criteria:**
- [x] Validates title (1-200 chars)
- [x] Validates description (max 1000 chars)
- [x] Associates task with user_id
- [x] Returns 201 with created task
- [x] Returns 400 on validation error

**Test:**
```bash
curl -X POST http://localhost:8000/api/test-user/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Test"}'
```

---

### Task 1.9: Create PUT, DELETE, PATCH Endpoints
**Priority**: P1
**Estimated Time**: 40 minutes
**Dependencies**: Task 1.8

**Add to**: `backend/routes/tasks.py`

**Code:**
```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

@router.get("/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.put("/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully", "id": task_id}

class TaskComplete(BaseModel):
    completed: bool

@router.patch("/{user_id}/tasks/{task_id}/complete")
async def toggle_complete(
    user_id: str,
    task_id: int,
    data: TaskComplete,
    auth_user_id: str = Depends(verify_token),
    session: Session = Depends(get_session)
):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = data.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

**Acceptance Criteria:**
- [x] GET /{user_id}/tasks/{id} returns single task
- [x] PUT /{user_id}/tasks/{id} updates task
- [x] DELETE /{user_id}/tasks/{id} deletes task
- [x] PATCH /{user_id}/tasks/{id}/complete toggles completion
- [x] All verify ownership

**Test:**
```bash
# Get single task
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/test-user/tasks/1

# Update task
curl -X PUT http://localhost:8000/api/test-user/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'

# Toggle complete
curl -X PATCH http://localhost:8000/api/test-user/tasks/1/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Delete task
curl -X DELETE http://localhost:8000/api/test-user/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

### Task 1.10: Register Router in Main App
**Priority**: P1
**Estimated Time**: 5 minutes
**Dependencies**: Task 1.9

**Edit**: `backend/main.py`

**Add:**
```python
from routes import tasks

app.include_router(tasks.router)
```

**Acceptance Criteria:**
- [x] Tasks router registered
- [x] All endpoints accessible under /api

**Test:**
```bash
# Restart server
uvicorn main:app --reload --port 8000

# Test root
curl http://localhost:8000/

# Test API docs
curl http://localhost:8000/docs
```

---

## PHASE 2: Frontend Setup (Tasks 11-20)

### Task 2.1: Initialize Next.js Project
**Priority**: P1
**Estimated Time**: 10 minutes
**Dependencies**: None

**Steps:**
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Acceptance Criteria:**
- [X] Next.js 16+ installed
- [X] TypeScript configured
- [X] Tailwind CSS configured
- [X] App Router enabled

**Files Created:**
- frontend/package.json
- frontend/tsconfig.json
- frontend/tailwind.config.ts
- frontend/app/layout.tsx
- frontend/app/page.tsx

---

### Task 2.2: Install Dependencies
**Priority**: P1
**Estimated Time**: 5 minutes
**Dependencies**: Task 2.1

**Steps:**
```bash
cd frontend
npm install better-auth @radix-ui/react-* lucide-react framer-motion next-themes axios
npx shadcn-ui@latest init
```

**Acceptance Criteria:**
- [X] better-auth installed
- [X] shadcn/ui initialized
- [X] Radix UI components available
- [X] Icons (lucide-react) installed
- [X] Animations (framer-motion) installed
- [X] Theme support (next-themes) installed
- [X] HTTP client (axios) installed

---

### Task 2.3: Configure Environment Variables
**Priority**: P1
**Estimated Time**: 5 minutes
**Dependencies**: Task 2.2

**Create**: `frontend/.env.local`

**Content:**
```env
BETTER_AUTH_SECRET=same-as-backend-jwt-secret-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require
```

**Acceptance Criteria:**
- [X] .env.local created
- [X] BETTER_AUTH_SECRET matches backend JWT_SECRET
- [X] NEXT_PUBLIC_API_URL points to backend
- [X] DATABASE_URL for Better Auth database connection

---

### Task 2.4: Setup Better Auth
**Priority**: P1
**Estimated Time**: 20 minutes
**Dependencies**: Task 2.3

**Create**: `frontend/lib/auth.ts`

**Code:**
```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET!,
    expiresIn: "7d",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.user_id = user.id;
        token.email = user.email;
        token.name = user.name;
      }
      return token;
    },
  },
});
```

**Acceptance Criteria:**
- [x] Better Auth configured
- [x] JWT secret set
- [x] Token expiry 7 days
- [x] Callback includes user_id in token

---

### Task 2.5: Create API Client
**Priority**: P1
**Estimated Time**: 30 minutes
**Dependencies**: Task 2.4

**Create**: `frontend/lib/api.ts`

**Code:**
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to all requests
apiClient.interceptors.request.use((config) => {
  // Get token from Better Auth session (will implement in auth tasks)
  const token = localStorage.getItem('auth_token'); // Temporary
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export const api = {
  // Get all tasks
  async getTasks(userId: string, status: 'all' | 'pending' | 'completed' = 'all') {
    const response = await apiClient.get(`/api/${userId}/tasks`, {
      params: { status },
    });
    return response.data;
  },

  // Create task
  async createTask(userId: string, data: { title: string; description?: string }) {
    const response = await apiClient.post(`/api/${userId}/tasks`, data);
    return response.data;
  },

  // Update task
  async updateTask(userId: string, taskId: number, data: { title?: string; description?: string }) {
    const response = await apiClient.put(`/api/${userId}/tasks/${taskId}`, data);
    return response.data;
  },

  // Delete task
  async deleteTask(userId: string, taskId: number) {
    const response = await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  },

  // Toggle completion
  async toggleComplete(userId: string, taskId: number, completed: boolean) {
    const response = await apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`, { completed });
    return response.data;
  },
};
```

**Acceptance Criteria:**
- [X] API client configured with base URL
- [X] JWT token attached to requests
- [X] All 5 API methods implemented
- [X] TypeScript types defined

---

### Task 2.6: Setup Tailwind Theme
**Priority**: P2
**Estimated Time**: 15 minutes
**Dependencies**: Task 2.2

**Edit**: `frontend/tailwind.config.ts`

**Code:**
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        purple: {
          primary: '#8B5CF6',
        },
        blue: {
          secondary: '#3B82F6',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)',
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
export default config;
```

**Acceptance Criteria:**
- [X] Dark mode class strategy
- [X] Custom colors (purple, blue)
- [X] Gradient utility class
- [X] Backdrop blur utilities

---

### Task 2.7: Create Root Layout with Theme Provider
**Priority**: P1
**Estimated Time**: 20 minutes
**Dependencies**: Task 2.6

**Edit**: `frontend/app/layout.tsx`

**Code:**
```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "next-themes";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Evolution Todo",
  description: "Modern task management application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

**Acceptance Criteria:**
- [X] Inter font loaded
- [X] ThemeProvider wraps app
- [X] Default theme is dark
- [X] System theme detection enabled

---

### Task 2.8: Create Authentication Pages (Signin)
**Priority**: P1
**Estimated Time**: 40 minutes
**Dependencies**: Task 2.4

**Create**: `frontend/app/auth/signin/page.tsx`

**Code:**
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function SigninPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Call Better Auth signin
    // (Better Auth implementation will be added)
    try {
      // Placeholder - will implement with Better Auth
      console.log('Signin:', { email, password });
      router.push('/tasks');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="glass max-w-md w-full p-8 rounded-2xl">
        <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-primary bg-clip-text text-transparent">
          Sign In
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 focus:border-purple-primary focus:ring-2 focus:ring-purple-primary/20"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-slate-700 focus:border-purple-primary focus:ring-2 focus:ring-purple-primary/20"
              required
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <button
            type="submit"
            className="w-full py-3 rounded-lg bg-gradient-primary text-white font-semibold hover:scale-105 active:scale-95 transition-transform"
          >
            Sign In
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="text-purple-primary hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
```

**Acceptance Criteria:**
- [X] Email and password inputs
- [X] Form validation
- [X] Error display
- [X] Link to signup page
- [X] Glassmorphism styling
- [X] Gradient button

---

### Task 2.9: Create Signup Page
**Priority**: P1
**Estimated Time**: 45 minutes
**Dependencies**: Task 2.8

**Create**: `frontend/app/auth/signup/page.tsx`

(Similar structure to signin, add name field and password confirmation)

**Acceptance Criteria:**
- [X] Name, email, password, confirm password inputs
- [X] Password match validation
- [X] Form validation
- [X] Link to signin page
- [X] Glassmorphism styling

---

### Task 2.10: Create Protected Tasks Page
**Priority**: P1
**Estimated Time**: 15 minutes
**Dependencies**: Task 2.7

**Create**: `frontend/app/tasks/page.tsx`

**Code:**
```typescript
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function TasksPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check authentication (will implement with Better Auth)
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/auth/signin');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">My Tasks</h1>
        {/* Task components will be added in next phase */}
        <p className="text-slate-400">Task components coming next...</p>
      </div>
    </div>
  );
}
```

**Acceptance Criteria:**
- [X] Redirects to signin if not authenticated
- [X] Protected route logic
- [X] Basic page structure

---

## PHASE 3: Frontend UI Components (Tasks 21-30)

### Task 3.1: Create Header Component
**Priority**: P1
**Estimated Time**: 30 minutes

**Create**: `frontend/components/Header.tsx`

(Fixed header with logo, theme toggle, user menu - exact spec from specs/ui/design.md)

---

### Task 3.2: Create Theme Toggle Component
**Priority**: P2
**Estimated Time**: 20 minutes

**Create**: `frontend/components/ThemeToggle.tsx`

(Sun/Moon icon with rotation animation)

---

### Task 3.3: Create Sidebar Component
**Priority**: P2
**Estimated Time**: 35 minutes

**Create**: `frontend/components/Sidebar.tsx`

(Navigation: All/Active/Done, glassmorphism, active states)

---

### Task 3.4: Create TaskForm Component
**Priority**: P1
**Estimated Time**: 40 minutes

**Create**: `frontend/components/TaskForm.tsx`

(Glassmorphism card, floating labels, gradient button, validation, API integration)

---

### Task 3.5: Create StatusBadge Component
**Priority**: P2
**Estimated Time**: 15 minutes

**Create**: `frontend/components/StatusBadge.tsx`

(Pending: Amber, Complete: Green with checkmark)

---

### Task 3.6: Create TaskCard Component
**Priority**: P1
**Estimated Time**: 45 minutes

**Create**: `frontend/components/TaskCard.tsx`

(Glassmorphism, title/description, status badge, actions, hover effects)

---

### Task 3.7: Create TaskList Component
**Priority**: P1
**Estimated Time**: 35 minutes

**Create**: `frontend/components/TaskList.tsx`

(Responsive grid, TaskCard rendering, empty state, skeleton loaders)

---

### Task 3.8: Integrate Components in Tasks Page
**Priority**: P1
**Estimated Time**: 30 minutes

**Edit**: `frontend/app/tasks/page.tsx`

(Add Header, Sidebar, TaskForm, TaskList with proper layout)

---

### Task 3.9: Implement Optimistic UI Updates
**Priority**: P2
**Estimated Time**: 25 minutes

**Edit**: TaskList and TaskCard components

(Immediate UI updates, revert on API error)

---

### Task 3.10: Add Toast Notifications
**Priority**: P2
**Estimated Time**: 20 minutes

**Install**: `npm install sonner`
**Implement**: Success/error toasts on all mutations

---

## PHASE 4: Integration & Testing (Tasks 31-35)

### Task 4.1: Complete Better Auth Integration
**Priority**: P1
**Estimated Time**: 60 minutes

- Implement actual signup/signin with Better Auth
- Store JWT token properly
- Implement logout
- Session persistence

---

### Task 4.2: Connect Frontend to Backend
**Priority**: P1
**Estimated Time**: 45 minutes

- Test all CRUD operations end-to-end
- Fix CORS issues if any
- Handle all error cases
- Verify JWT authentication works

---

### Task 4.3: Test User Isolation
**Priority**: P1
**Estimated Time**: 30 minutes

- Create 2 test users
- Verify each sees only their tasks
- Test cross-user access attempts (should fail)

---

### Task 4.4: Performance Testing
**Priority**: P2
**Estimated Time**: 20 minutes

- Test task list load time (target < 1s)
- Test CRUD operation times (target < 500ms)
- Optimize if needed

---

### Task 4.5: Accessibility Audit
**Priority**: P2
**Estimated Time**: 30 minutes

- Run Lighthouse accessibility audit
- Fix any issues (target score > 90)
- Test keyboard navigation
- Test screen reader

---

## PHASE 5: Deployment (Tasks 36-40)

### Task 5.1: Deploy Backend to Railway
**Priority**: P1
**Estimated Time**: 30 minutes

1. Create Railway account
2. Connect GitHub repo
3. Configure environment variables
4. Deploy backend
5. Test endpoints

---

### Task 5.2: Deploy Frontend to Vercel
**Priority**: P1
**Estimated Time**: 25 minutes

1. Connect GitHub repo to Vercel
2. Configure environment variables (NEXT_PUBLIC_API_URL with Railway URL)
3. Deploy frontend
4. Test deployment

---

### Task 5.3: Update CORS for Production
**Priority**: P1
**Estimated Time**: 10 minutes

- Add production frontend URL to backend CORS_ORIGINS
- Redeploy backend
- Test production integration

---

### Task 5.4: Create Demo Video
**Priority**: P1
**Estimated Time**: 60 minutes

- Record 90-second demo showing:
  1. Signup/Signin
  2. Create task
  3. Update task
  4. Toggle completion
  5. Delete task
  6. Theme toggle
  7. Responsive design
- Upload to YouTube/Loom

---

### Task 5.5: Prepare Submission
**Priority**: P1
**Estimated Time**: 30 minutes

1. Update README.md with:
   - Setup instructions
   - Deployed URLs
   - Tech stack
   - Features
2. Ensure all specs in /specs folder
3. Push to GitHub (make repo public)
4. Fill submission form: https://forms.gle/KMKEKaFUD6ZX4UtY8

---

## PHASE 6: Polish & Bonus (Tasks 41-45) [OPTIONAL]

### Task 6.1: Add Loading States
**Priority**: P3
**Estimated Time**: 20 minutes

- Spinner on form submit
- Skeleton loaders on initial load
- Loading states on all buttons

---

### Task 6.2: Add Animations
**Priority**: P3
**Estimated Time**: 30 minutes

- Task card entrance (stagger)
- Modal transitions
- Button ripple effects

---

### Task 6.3: Mobile Responsive Testing
**Priority**: P2
**Estimated Time**: 25 minutes

- Test on mobile (Chrome DevTools)
- Fix any layout issues
- Ensure sidebar drawer works

---

### Task 6.4: Error Boundary
**Priority**: P3
**Estimated Time**: 15 minutes

- Add React error boundary
- Graceful error page

---

### Task 6.5: Final Polish
**Priority**: P3
**Estimated Time**: 30 minutes

- Fix any visual bugs
- Ensure exact UI match with reference
- Final QA pass

---

## Execution Summary

**Order**: 1 → 2 → 3 → 4 → 5 → (6 optional)

**Critical Path**: Tasks 1.1-1.10 → 2.1-2.10 → 3.4, 3.6, 3.7, 3.8 → 4.1, 4.2 → 5.1, 5.2, 5.3, 5.4, 5.5

**Estimated Total Time**: 18-22 hours (without optional tasks)

**Ports**:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

**Environment Variables**:
- Backend: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`
- Frontend: `BETTER_AUTH_SECRET`, `NEXT_PUBLIC_API_URL`, `DATABASE_URL`

---

**Status**: Tasks Ready ✅
**Next**: Execute with `/sp.implement backend` to start Phase 1 (Tasks 1.1-1.10)
