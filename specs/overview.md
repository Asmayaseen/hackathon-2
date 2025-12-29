# Phase II: Evolution Todo - Full-Stack Web Application

## Project Overview

Evolution Todo is progressing from a console-based application (Phase I) to a modern, multi-user web application with persistent storage and authentication. This phase transforms the in-memory Python todo manager into a production-ready full-stack application.

## Phase II Objectives

Transform the Phase I console app into a web application by:
1. Building a responsive Next.js frontend with modern UI
2. Creating a FastAPI backend with RESTful API
3. Implementing persistent storage with Neon PostgreSQL
4. Adding multi-user support with Better Auth authentication
5. Securing the API with JWT tokens

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS 4.x + shadcn/ui components
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Theme**: next-themes (dark/light mode)
- **Authentication**: Better Auth (client-side)

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT token validation
- **CORS**: Enabled for Next.js frontend

### Development Tools
- **Spec-Driven**: Claude Code + Spec-Kit Plus
- **Package Manager (Frontend)**: npm/yarn
- **Package Manager (Backend)**: uv
- **Version Control**: Git

## Current Phase Status

**Phase**: II (Full-Stack Web Application)
**Points**: 150
**Deadline**: Sunday, Dec 14, 2025

**Progress:**
- ✅ Monorepo structure created
- ✅ UI Design specification completed
- ⏳ Feature specifications in progress
- ⏳ API specifications in progress
- ⏳ Database schema specification in progress
- ⏳ Authentication specification in progress

## Feature Set (Phase II Scope)

### Basic Level Features (5 Core Features)
All features from Phase I, now in web interface:

1. **Add Task** - Create new todo items with title and description
2. **Delete Task** - Remove tasks permanently
3. **Update Task** - Modify task title and description
4. **View Task List** - Display all tasks in responsive grid
5. **Mark as Complete** - Toggle task completion status

### Authentication Features
- **User Signup** - New user registration
- **User Signin** - Existing user login
- **Session Management** - Persistent login with JWT
- **User Isolation** - Each user sees only their tasks

## Architecture

### Monorepo Structure
```
hackathon-2/
├── frontend/           # Next.js 16 application
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   ├── lib/           # Utilities and API client
│   └── public/        # Static assets
├── backend/           # FastAPI application
│   ├── main.py        # FastAPI app entry
│   ├── models.py      # SQLModel database models
│   ├── routes/        # API route handlers
│   └── db.py          # Database connection
├── specs/             # All specifications
│   ├── overview.md    # This file
│   ├── ui/            # UI design specs
│   ├── features/      # Feature specs
│   ├── api/           # API endpoint specs
│   └── database/      # Database schema specs
├── .spec-kit/         # Spec-Kit configuration
└── CLAUDE.md          # Root agent instructions
```

### API Architecture
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Next.js        │──────▶│  FastAPI        │──────▶│  Neon DB        │
│  Frontend       │  JWT  │  Backend        │ SQL   │  (PostgreSQL)   │
│                 │◀──────│                 │◀──────│                 │
└─────────────────┘  JSON └─────────────────┘ Data  └─────────────────┘
     │                                                       ▲
     │                                                       │
     ▼                                                       │
┌─────────────────┐                                         │
│  Better Auth    │─────────────────────────────────────────┘
│  (User Auth)    │         User sessions & JWT tokens
└─────────────────┘
```

### Data Flow
1. **User Authentication**: Better Auth issues JWT token on login
2. **API Request**: Frontend includes JWT in Authorization header
3. **Token Validation**: Backend verifies JWT and extracts user_id
4. **Data Isolation**: Backend filters all queries by user_id
5. **Response**: Backend returns only user's own tasks

## API Endpoints (6 Total)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/{user_id}/tasks | List all user's tasks | JWT Required |
| POST | /api/{user_id}/tasks | Create new task | JWT Required |
| GET | /api/{user_id}/tasks/{id} | Get task details | JWT Required |
| PUT | /api/{user_id}/tasks/{id} | Update task | JWT Required |
| DELETE | /api/{user_id}/tasks/{id} | Delete task | JWT Required |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion | JWT Required |

## Database Schema

### Users Table (Managed by Better Auth)
- `id` - Primary key (string)
- `email` - Unique email (string)
- `name` - User's name (string)
- `password_hash` - Hashed password (string)
- `created_at` - Timestamp

### Tasks Table
- `id` - Primary key (integer, auto-increment)
- `user_id` - Foreign key → users.id (string)
- `title` - Task title (string, 1-200 chars, required)
- `description` - Task description (text, optional, max 1000 chars)
- `completed` - Boolean (default: false)
- `created_at` - Timestamp (auto-generated)
- `updated_at` - Timestamp (auto-updated on change)

**Indexes:**
- `tasks.user_id` (for filtering by user)
- `tasks.completed` (for status filtering)

## UI Design Highlights

### Theme
- **Primary Color**: Purple (#8B5CF6)
- **Secondary Color**: Blue (#3B82F6)
- **Gradient**: Linear gradient (135deg, #8B5CF6 → #3B82F6)
- **Dark/Light Mode**: Toggle with smooth transitions

### Visual Effects
- **Glassmorphism**: backdrop-blur cards with transparency
- **Animations**: Hover scale (1.02-1.05), smooth transitions
- **Shadows**: Layered shadows for depth
- **Responsive**: Mobile-first, works on all screen sizes

### Key Components
1. **Header**: Fixed with backdrop-blur, theme toggle, user menu
2. **Sidebar**: Navigation (All/Active/Done tasks)
3. **Task Form**: Glassmorphism card with gradient submit button
4. **Task Cards**: Grid layout, hover effects, status badges
5. **Status Badges**: Color-coded (Pending: Amber, Complete: Green)

## Security Model

### Authentication Flow
1. User signs up/signs in via Better Auth
2. Better Auth creates session and issues JWT token
3. Frontend stores JWT securely (httpOnly cookie recommended)
4. Frontend includes JWT in every API request header:
   ```
   Authorization: Bearer <jwt-token>
   ```
5. Backend validates JWT signature and expiry
6. Backend extracts user_id from JWT payload
7. Backend enforces user_id match with URL parameter

### Security Measures
- **JWT Tokens**: Stateless authentication, auto-expiry (7 days default)
- **User Isolation**: All queries filtered by authenticated user_id
- **HTTPS**: Required in production (Vercel handles this)
- **CORS**: Configured to allow only frontend origin
- **Input Validation**: Client and server-side validation
- **SQL Injection Prevention**: Parameterized queries via SQLModel
- **XSS Prevention**: Input sanitization, CSP headers

## Non-Functional Requirements

### Performance
- Task list loads in < 1 second
- CRUD operations complete in < 500ms
- Optimistic UI updates appear instantly
- Responsive on 3G connections

### Scalability
- Stateless backend (can scale horizontally)
- Database connection pooling
- Efficient SQL queries with indexes
- Frontend static generation where possible

### Reliability
- Error handling on all API calls
- Graceful degradation on network failures
- User-friendly error messages
- Retry mechanisms for failed requests

### Accessibility
- WCAG AA compliance
- Keyboard navigation support
- Screen reader compatible
- High contrast mode support

## Development Workflow

Following Spec-Driven Development (SDD):

### 1. Specify (Current Stage)
- ✅ Create specs/overview.md (this file)
- ⏳ Create specs/features/task-crud.md
- ⏳ Create specs/features/authentication.md
- ⏳ Create specs/api/rest-endpoints.md
- ⏳ Create specs/database/schema.md
- ⏳ Create specs/ui/design.md (✅ Done)

### 2. Plan
- Research existing Phase I codebase
- Design backend architecture (models, routes, middleware)
- Design frontend architecture (components, pages, state)
- Define data models and API contracts
- Create plan.md for implementation approach

### 3. Tasks
- Break down plan into atomic, testable tasks
- Organize tasks by feature (CRUD, Auth, UI)
- Mark parallelizable tasks
- Create tasks.md

### 4. Implement
- Set up backend (FastAPI + SQLModel + Neon)
- Set up frontend (Next.js + Better Auth)
- Implement API endpoints with JWT validation
- Implement UI components matching design spec
- Connect frontend to backend
- Test end-to-end workflows

### 5. Deploy
- Deploy backend (Railway/Render/Heroku)
- Deploy frontend (Vercel)
- Configure environment variables
- Test production deployment
- Create demo video

## Success Criteria

Phase II is complete when:
- ✅ All 5 basic features work in web interface
- ✅ All 6 API endpoints functional and secured
- ✅ Users can sign up, sign in, and manage their tasks
- ✅ Each user sees only their own tasks
- ✅ UI matches design spec (glassmorphism, theme toggle, responsive)
- ✅ Performance targets met (load < 1s, ops < 500ms)
- ✅ Deployed and accessible via public URLs
- ✅ Demo video created (max 90 seconds)
- ✅ Code in GitHub with complete documentation

## Out of Scope (Future Phases)

Not included in Phase II:
- ❌ AI Chatbot interface (Phase III)
- ❌ Kubernetes deployment (Phase IV-V)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Recurring tasks (Phase V)
- ❌ Due dates and reminders (Phase V)
- ❌ Priorities, tags, search, filters (Phase V)

Phase II focuses on core full-stack foundation. Advanced features come later.

## Dependencies & Prerequisites

### Backend Setup
- Python 3.13+
- uv package manager
- Neon PostgreSQL account (free tier)
- Environment variables: DATABASE_URL, JWT_SECRET

### Frontend Setup
- Node.js 18+
- npm or yarn
- Better Auth credentials
- Environment variables: NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET

### Development Tools
- Claude Code
- Spec-Kit Plus
- Git
- VS Code (recommended)

## Deployment Targets

### Frontend
- **Platform**: Vercel (recommended for Next.js)
- **URL**: https://evolution-todo-<username>.vercel.app
- **Build**: Automatic on git push
- **Environment**: Production env vars in Vercel dashboard

### Backend
- **Platform**: Railway/Render/Heroku (free tiers available)
- **URL**: https://evolution-todo-api-<username>.railway.app
- **Database**: Neon PostgreSQL (connection string in env)

## Deliverables Checklist

- [ ] Specs folder with all 5 spec files (overview, features, api, database, ui)
- [ ] Backend codebase (FastAPI + SQLModel + Neon)
- [ ] Frontend codebase (Next.js + Better Auth + UI)
- [ ] Root CLAUDE.md with monorepo navigation
- [ ] Updated README.md with setup instructions
- [ ] Deployed frontend URL (Vercel)
- [ ] Deployed backend URL
- [ ] Demo video (90 seconds max)
- [ ] GitHub repo public
- [ ] Submission form filled: https://forms.gle/KMKEKaFUD6ZX4UtY8

## References

- **Hackathon Doc**: /hackathon.md
- **Phase I Constitution**: /.specify/memory/constitution.md
- **Reference UI**: https://evolution-todo.vercel.app/
- **Better Auth Docs**: https://www.better-auth.com/docs
- **Next.js 16 Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Neon Docs**: https://neon.tech/docs

---

**Version**: 1.0.0
**Date**: 2025-12-28
**Status**: Specification Phase
**Next**: Complete feature specs → Create plan → Break into tasks → Implement
