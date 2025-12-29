# Implementation Plan - Phase II: Full-Stack Web Application

## Overview
Transform the Phase I console todo app into a production-ready full-stack web application with multi-user authentication, persistent storage, and modern UI exactly matching https://evolution-todo.vercel.app/

**Objective:** Implement all 5 Basic Level features as a web application with Better Auth + JWT + Neon PostgreSQL.

---

## Architecture

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                               │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │         Next.js 16 Frontend (Port 3000)                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │    │
│  │  │   Auth UI    │  │   Task UI    │  │   Theme      │    │    │
│  │  │  (Signup/    │  │  (CRUD)      │  │   Toggle     │    │    │
│  │  │   Signin)    │  │              │  │              │    │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘    │    │
│  │         │                  │                               │    │
│  │         ▼                  ▼                               │    │
│  │  ┌──────────────────────────────────┐                     │    │
│  │  │      Better Auth Client          │                     │    │
│  │  │  - Issues JWT on login           │                     │    │
│  │  │  - Stores token (httpOnly cookie)│                     │    │
│  │  └──────────────┬───────────────────┘                     │    │
│  │                 │                                          │    │
│  │                 │ JWT Token in Authorization Header       │    │
│  │                 ▼                                          │    │
│  │  ┌──────────────────────────────────┐                     │    │
│  │  │      API Client (lib/api.ts)     │                     │    │
│  │  │  - Attaches JWT to all requests  │                     │    │
│  │  │  - Handles errors                │                     │    │
│  │  └──────────────┬───────────────────┘                     │    │
│  └─────────────────┼──────────────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────────────┘
                     │
                     │ HTTP/JSON (JWT in header)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 CORS Middleware                              │  │
│  │  - Allow origins: localhost:3000, vercel.app                │  │
│  └──────────────────┬───────────────────────────────────────────┘  │
│                     ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              JWT Authentication Middleware                   │  │
│  │  - Verify JWT signature                                      │  │
│  │  - Extract user_id from token                                │  │
│  │  - Return 401 if invalid/expired                             │  │
│  └──────────────────┬───────────────────────────────────────────┘  │
│                     ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Routes                                │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │  │
│  │  │  GET /tasks    │  │  POST /tasks   │  │ PATCH /tasks/ │ │  │
│  │  │  GET /tasks/id │  │  PUT /tasks/id │  │   id/complete │ │  │
│  │  │  DELETE /tasks │  │                │  │               │ │  │
│  │  └────────┬───────┘  └────────┬───────┘  └───────┬───────┘ │  │
│  └───────────┼──────────────────┼─────────────────┼────────────┘  │
│              ▼                  ▼                 ▼                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 SQLModel ORM Layer                           │  │
│  │  - User model                                                │  │
│  │  - Task model                                                │  │
│  │  - Validation                                                │  │
│  └──────────────────┬───────────────────────────────────────────┘  │
│                     │                                               │
│                     │ SQL Queries (Parameterized)                   │
│                     ▼                                               │
└─────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Neon Serverless PostgreSQL                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Tables:                                                     │  │
│  │  ┌─────────────────┐        ┌─────────────────────────┐    │  │
│  │  │     users       │        │        tasks            │    │  │
│  │  ├─────────────────┤        ├─────────────────────────┤    │  │
│  │  │ id (PK)         │◀───────│ user_id (FK)            │    │  │
│  │  │ email (UNIQUE)  │        │ id (PK)                 │    │  │
│  │  │ name            │        │ title                   │    │  │
│  │  │ password_hash   │        │ description             │    │  │
│  │  │ created_at      │        │ completed (bool)        │    │  │
│  │  │ updated_at      │        │ created_at              │    │  │
│  │  └─────────────────┘        │ updated_at              │    │  │
│  │                             └─────────────────────────┘    │  │
│  │                                                             │  │
│  │  Indexes:                                                   │  │
│  │  - users.email (UNIQUE)                                     │  │
│  │  - tasks.user_id, tasks.completed, tasks.created_at        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Signup    │         │   Signin    │         │ API Request │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                        │
       ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Better Auth (Next.js)                    │
│  1. Validate credentials                                    │
│  2. Hash password (bcrypt)                                  │
│  3. Create user in DB (if signup)                           │
│  4. Generate JWT token                                      │
│  5. Store in httpOnly cookie                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ JWT Token
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend stores JWT token                      │
│  - httpOnly cookie (secure)                                 │
│  - Included in all API requests                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Authorization: Bearer <token>
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI JWT Middleware                         │
│  1. Extract token from Authorization header                 │
│  2. Verify signature with JWT_SECRET                        │
│  3. Check expiry                                            │
│  4. Extract user_id from payload                            │
│  5. Attach to request context                               │
│  6. Return 401 if invalid                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ user_id
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              API Route Handler                              │
│  1. Verify user_id in URL matches token user_id             │
│  2. Filter all queries by user_id                           │
│  3. Return only user's data                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Backend Components (FastAPI)

#### 1. **main.py** - Application Entry Point
```python
- FastAPI app initialization
- CORS middleware configuration
- JWT middleware registration
- Router registration
- Database initialization
- Startup/shutdown events
```

#### 2. **models.py** - Database Models
```python
- User model (SQLModel)
  - id, email, name, password_hash, timestamps
- Task model (SQLModel)
  - id, user_id, title, description, completed, timestamps
```

#### 3. **db.py** - Database Connection
```python
- SQLModel engine creation
- Database URL from env
- Connection pooling
- Session management
- create_db_and_tables() function
- get_session() dependency
```

#### 4. **middleware/auth.py** - JWT Middleware
```python
- verify_token() function
  - Decode JWT with JWT_SECRET
  - Validate expiry
  - Extract user_id
  - Raise 401 on error
- HTTPBearer security scheme
```

#### 5. **routes/tasks.py** - Task API Routes
```python
- GET /api/{user_id}/tasks
  - List all user's tasks
  - Filter by status (query param)
  - Sort by created_at desc
- POST /api/{user_id}/tasks
  - Create new task
  - Validate title/description
  - Associate with user_id
- GET /api/{user_id}/tasks/{id}
  - Get single task
  - Verify ownership
- PUT /api/{user_id}/tasks/{id}
  - Update task
  - Verify ownership
- DELETE /api/{user_id}/tasks/{id}
  - Delete task
  - Verify ownership
- PATCH /api/{user_id}/tasks/{id}/complete
  - Toggle completion
  - Verify ownership
```

#### 6. **.env** - Environment Configuration
```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

---

### Frontend Components (Next.js 16)

#### 1. **app/layout.tsx** - Root Layout
```typescript
- ThemeProvider (next-themes)
- Better Auth session provider
- Global styles
- Font configuration (Inter)
```

#### 2. **app/page.tsx** - Landing Page
```typescript
- Hero section
- CTA buttons (Login/Signup)
- Redirect if authenticated
```

#### 3. **app/auth/signin/page.tsx** - Signin Page
```typescript
- Email input
- Password input
- Submit button
- Link to signup
- Better Auth integration
```

#### 4. **app/auth/signup/page.tsx** - Signup Page
```typescript
- Email input
- Name input
- Password input
- Confirm password
- Submit button
- Better Auth integration
```

#### 5. **app/tasks/page.tsx** - Main Tasks Page (Protected)
```typescript
- Require authentication
- TaskForm component
- TaskList component
- Theme toggle in header
```

#### 6. **components/TaskForm.tsx** - Create Task Form
```typescript
- Glassmorphism card
- Title input (floating label)
- Description textarea (floating label)
- Gradient submit button
- Validation
- API integration
```

#### 7. **components/TaskList.tsx** - Task Grid Display
```typescript
- Responsive grid (1-3 columns)
- TaskCard components
- Empty state
- Loading skeleton
```

#### 8. **components/TaskCard.tsx** - Individual Task Card
```typescript
- Glassmorphism design
- Title + description
- Status badge
- Action buttons (Edit, Delete, Complete)
- Hover animations
```

#### 9. **components/StatusBadge.tsx** - Status Indicator
```typescript
- Pending: Amber background
- Complete: Green background with checkmark
- Pill shape
```

#### 10. **components/Header.tsx** - App Header
```typescript
- Fixed position with backdrop-blur
- Logo/brand
- Theme toggle
- User menu (name + logout)
```

#### 11. **components/Sidebar.tsx** - Navigation Sidebar
```typescript
- Navigation items (All/Active/Done)
- Active state styling
- Add task button
```

#### 12. **components/ThemeToggle.tsx** - Dark/Light Toggle
```typescript
- Sun/Moon icon
- Smooth rotation animation
- next-themes integration
```

#### 13. **lib/api.ts** - API Client
```typescript
- Axios/fetch wrapper
- JWT token attachment
- Error handling
- Type-safe API calls
- Functions:
  - getTasks(userId, status?)
  - createTask(userId, data)
  - updateTask(userId, taskId, data)
  - deleteTask(userId, taskId)
  - toggleComplete(userId, taskId, completed)
```

#### 14. **lib/auth.ts** - Better Auth Configuration
```typescript
- betterAuth setup
- JWT configuration
- Database connection
- Callbacks
```

#### 15. **.env.local** - Frontend Environment
```env
BETTER_AUTH_SECRET=same-as-backend-jwt-secret
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://...
```

---

## Data Flow Examples

### Example 1: Create Task
```
1. User enters title "Buy groceries" in TaskForm
2. User clicks Submit
3. Frontend validates (title required)
4. API client calls POST /api/{user_id}/tasks
   Headers: Authorization: Bearer <jwt>
   Body: { title: "Buy groceries", description: "" }
5. Backend JWT middleware verifies token
6. Backend extracts user_id from token
7. Backend creates Task with user_id
8. Database inserts record
9. Backend returns 201 with task object
10. Frontend updates task list (optimistic UI)
11. Success toast shown
```

### Example 2: Toggle Completion
```
1. User clicks checkbox on task card
2. Frontend immediately updates UI (strikethrough)
3. API client calls PATCH /api/{user_id}/tasks/{id}/complete
   Headers: Authorization: Bearer <jwt>
   Body: { completed: true }
4. Backend verifies JWT and user_id
5. Backend updates task.completed
6. Database updates record
7. Backend returns 200 with updated task
8. Frontend confirms state
9. On error: Revert UI to previous state
```

---

## Technical Decisions

### Decision 1: Monorepo Structure
**Choice:** Single repository with /frontend and /backend folders
**Rationale:**
- Simpler for hackathon development
- Claude Code can see entire project context
- Easier to make cross-cutting changes
- Spec-Kit Plus works well with monorepos

**Alternatives Considered:**
- Separate repos: More complex for single developer, harder context sharing

---

### Decision 2: Authentication Strategy
**Choice:** Better Auth (Next.js) + JWT tokens
**Rationale:**
- Better Auth handles user management in frontend
- JWT enables stateless backend (scalable)
- Shared secret allows both to verify tokens
- No session store needed

**Alternatives Considered:**
- NextAuth: More complex setup
- Clerk: External dependency, cost concerns
- Custom auth: More work, error-prone

---

### Decision 3: Database Choice
**Choice:** Neon Serverless PostgreSQL
**Rationale:**
- Free tier sufficient for hackathon
- Auto-scaling, auto-suspend (cost-efficient)
- Standard PostgreSQL (no vendor lock-in)
- Connection pooling built-in

**Alternatives Considered:**
- Supabase: Requires separate auth setup
- PlanetScale: MySQL, less familiar
- Local PostgreSQL: Not cloud-native

---

### Decision 4: ORM Choice
**Choice:** SQLModel
**Rationale:**
- Type-safe Python models
- Built on SQLAlchemy (mature)
- Pydantic integration (FastAPI native)
- Auto-generates API schemas

**Alternatives Considered:**
- Raw SQLAlchemy: More boilerplate
- Django ORM: Overkill for FastAPI
- Prisma (Python): Less mature than SQLModel

---

### Decision 5: Frontend Framework
**Choice:** Next.js 16 (App Router)
**Rationale:**
- Hackathon requirement
- Server components for performance
- Built-in routing
- Vercel deployment (easy)

**No alternatives** - hackathon requirement.

---

### Decision 6: Styling Approach
**Choice:** Tailwind CSS + shadcn/ui
**Rationale:**
- Rapid development
- Glassmorphism easy with Tailwind
- shadcn/ui provides accessible components
- Matches reference UI design

**Alternatives Considered:**
- Styled Components: Slower, more code
- Material UI: Doesn't match design
- Plain CSS: Too slow for hackathon

---

## Security Model

### Authentication Security
1. **Password Hashing**: bcrypt with salt (Better Auth handles this)
2. **JWT Secret**: Minimum 32 characters, stored in env vars
3. **Token Expiry**: 7 days default (configurable)
4. **HTTPS**: Required in production (Vercel enforces)
5. **httpOnly Cookies**: Prevents XSS attacks

### API Security
1. **JWT Validation**: Every request requires valid token
2. **User Isolation**: All queries filtered by user_id from token
3. **User ID Verification**: URL user_id must match token user_id
4. **Input Validation**: Client and server-side validation
5. **SQL Injection Prevention**: Parameterized queries via SQLModel
6. **CORS**: Whitelist only frontend origins

### Data Security
1. **No Password Exposure**: Never return password_hash in API
2. **Unique Email**: Database constraint prevents duplicates
3. **Foreign Key Constraints**: ON DELETE CASCADE for data integrity
4. **Environment Variables**: Secrets never committed to git

---

## Performance Optimization

### Backend Optimizations
1. **Database Indexing**: On user_id, completed, created_at
2. **Connection Pooling**: pool_size=10, max_overflow=20
3. **Query Optimization**: Select only needed fields
4. **Pagination**: LIMIT queries (future enhancement)

### Frontend Optimizations
1. **Optimistic UI**: Instant feedback on mutations
2. **Skeleton Loaders**: Show placeholders while loading
3. **Code Splitting**: Next.js automatic code splitting
4. **Image Optimization**: Next.js Image component (if needed)
5. **Static Generation**: Landing page as static HTML

---

## Error Handling Strategy

### Backend Error Responses
```python
# 400 Bad Request - Validation error
{
  "detail": [
    {"loc": ["body", "title"], "msg": "field required"}
  ]
}

# 401 Unauthorized - Auth error
{
  "detail": "Invalid token"
}

# 403 Forbidden - Permission denied
{
  "detail": "Forbidden - user_id mismatch"
}

# 404 Not Found - Resource not found
{
  "detail": "Task not found or you don't have access"
}

# 500 Internal Server Error
{
  "detail": "Internal server error"
}
```

### Frontend Error Handling
```typescript
// API call with error handling
try {
  const task = await createTask(userId, data);
  toast.success("Task created!");
  return task;
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login
    router.push('/auth/signin');
  } else if (error.response?.status === 400) {
    // Show validation errors
    toast.error(error.response.data.detail);
  } else {
    // Generic error
    toast.error("Failed to create task. Please try again.");
  }
}
```

---

## Deployment Strategy

### Backend Deployment (Railway/Render)
1. Connect GitHub repository
2. Configure environment variables:
   - DATABASE_URL
   - JWT_SECRET
   - CORS_ORIGINS
3. Deploy from main branch
4. Backend URL: https://evolution-todo-api.railway.app

### Frontend Deployment (Vercel)
1. Connect GitHub repository
2. Configure environment variables:
   - BETTER_AUTH_SECRET (same as JWT_SECRET)
   - NEXT_PUBLIC_API_URL (backend URL)
   - DATABASE_URL (Neon connection string)
3. Deploy from main branch
4. Auto-deploy on push
5. Frontend URL: https://evolution-todo.vercel.app

### Database Setup (Neon)
1. Create Neon account (free tier)
2. Create project: "evolution-todo"
3. Copy connection string
4. Add to both backend and frontend .env files
5. Run migrations on first backend deploy

---

## Testing Strategy

### Backend Tests (Pytest)
```python
# tests/test_auth.py
- test_jwt_generation
- test_jwt_validation
- test_expired_token_rejected

# tests/test_tasks_api.py
- test_create_task_success
- test_create_task_requires_auth
- test_get_tasks_only_returns_user_tasks
- test_update_task_verifies_ownership
- test_delete_task_verifies_ownership
- test_toggle_completion
```

### Frontend Tests (Jest + React Testing Library)
```typescript
// tests/TaskForm.test.tsx
- renders form correctly
- validates required fields
- calls API on submit
- shows error on failure

// tests/TaskCard.test.tsx
- renders task data
- handles edit click
- handles delete click
- toggles completion
```

### E2E Tests (Playwright - Optional)
```typescript
// e2e/auth-flow.spec.ts
- can signup with valid credentials
- can signin with valid credentials
- redirects to tasks page after login

// e2e/task-crud.spec.ts
- can create task
- can edit task
- can delete task
- can toggle completion
```

---

## Development Ports

- **Backend (FastAPI)**: http://localhost:8000
- **Frontend (Next.js)**: http://localhost:3000
- **Database (Neon)**: Remote connection string

---

## Risk Analysis

### Risk 1: Better Auth + FastAPI Integration
**Risk**: JWT secret mismatch between Better Auth and FastAPI
**Mitigation**: Use same secret in both .env files, test early
**Likelihood**: Medium
**Impact**: High

### Risk 2: CORS Configuration
**Risk**: Frontend can't call backend due to CORS errors
**Mitigation**: Configure CORS middleware early, test localhost + production URLs
**Likelihood**: Low
**Impact**: High

### Risk 3: Neon Database Connection
**Risk**: Connection string issues, SSL configuration
**Mitigation**: Test connection before coding, use Neon docs
**Likelihood**: Low
**Impact**: Medium

### Risk 4: UI Matching Reference
**Risk**: UI doesn't exactly match https://evolution-todo.vercel.app/
**Mitigation**: Use provided design spec, frequent visual checks
**Likelihood**: Medium
**Impact**: Medium

---

## Success Criteria

### Backend Complete When:
- [x] FastAPI app running on port 8000
- [x] All 6 API endpoints functional
- [x] JWT middleware validates tokens
- [x] Database connection works
- [x] Neon PostgreSQL schema created
- [x] All endpoints return correct responses
- [x] User isolation enforced

### Frontend Complete When:
- [x] Next.js app running on port 3000
- [x] Better Auth signup/signin works
- [x] JWT token stored and sent
- [x] All 5 CRUD features functional
- [x] UI matches design spec (glassmorphism, theme toggle)
- [x] Responsive on mobile/tablet/desktop
- [x] Dark/light theme toggle works

### Integration Complete When:
- [x] Frontend can create/read/update/delete tasks via API
- [x] Authentication flow works end-to-end
- [x] Users see only their own tasks
- [x] All error cases handled gracefully
- [x] Performance targets met (< 1s load, < 500ms ops)

### Deployment Complete When:
- [x] Backend deployed and accessible
- [x] Frontend deployed and accessible
- [x] Environment variables configured
- [x] HTTPS working in production
- [x] Demo video created (90 seconds)

---

## Next Steps: Task Generation

This plan will be broken down into atomic tasks in `tasks.md` with the following organization:

1. **Setup Tasks** (Backend + Frontend initialization)
2. **Database Tasks** (Schema creation, models)
3. **Backend API Tasks** (6 endpoints + JWT middleware)
4. **Frontend Auth Tasks** (Signup/Signin pages)
5. **Frontend UI Tasks** (Task CRUD components)
6. **Integration Tasks** (Connect frontend to backend)
7. **Deployment Tasks** (Deploy to Vercel + Railway)
8. **Testing Tasks** (E2E verification)

**Execution Order**: Backend → Frontend → Integration → Deployment

---

**Status**: Plan Complete ✅
**Next**: Generate tasks.md with atomic, executable tasks
**Then**: Execute with /sp.implement

---

**References:**
- Constitution: `.specify/memory/constitution.md`
- Overview: `specs/overview.md`
- UI Design: `specs/ui/design.md`
- Features: `specs/features/task-crud.md`, `specs/features/authentication.md`
- API: `specs/api/rest-endpoints.md`
- Database: `specs/database/schema.md`
