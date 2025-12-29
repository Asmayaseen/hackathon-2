---
id: 002
title: Phase 2 Specifications Complete
stage: spec
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5
feature: phase-2-fullstack
branch: phase-2-fullstack
user: asmayaseen
command: manual
labels: ["phase-2", "spec-driven", "specifications", "completion"]
links:
  spec: specs/overview.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/overview.md
  - specs/ui/design.md
  - specs/features/task-crud.md
  - specs/features/authentication.md
  - specs/api/rest-endpoints.md
  - specs/database/schema.md
  - .spec-kit/config.yaml
  - CLAUDE.md (updated for monorepo)
  - history/prompts/phase-2-fullstack/001-phase-2-initiation.spec.prompt.md
  - history/prompts/phase-2-fullstack/002-specs-completion.spec.prompt.md
tests:
  - null (specs stage, no code yet)
---

## Prompt

**User Request (Urdu):**
```
history/prompt bhi bne
```

**Context:** User requested that PHRs (Prompt History Records) be created to document the specification work for Phase II.

## Response snapshot

**Specifications Created (7 Files):**

### 1. `specs/overview.md`
**Purpose:** Phase II project overview and architecture
**Content:**
- Project objectives and scope
- Technology stack (Next.js 16, FastAPI, SQLModel, Neon DB, Better Auth)
- Monorepo structure
- API architecture diagram
- Data flow
- 6 API endpoints summary
- Database schema overview
- UI design highlights
- Security model
- Development workflow (SDD: Specify → Plan → Tasks → Implement)
- Success criteria
- Deliverables checklist

**Key Sections:**
- Feature Set (5 Basic Level Features)
- Architecture (Frontend ↔ Backend ↔ Database)
- Non-Functional Requirements (Performance, Scalability, Reliability, Accessibility)
- Out of Scope (Phase III+ features)

---

### 2. `specs/ui/design.md`
**Purpose:** Exact UI design specification matching https://evolution-todo.vercel.app/
**Content:**
- Color palette (Purple #8B5CF6, Blue #3B82F6, gradients)
- Dark/Light theme specifications
- Typography (Inter font, 6 font scales)
- Layout structure (Header, Sidebar, Main Content)
- Responsive breakpoints (Mobile, Tablet, Desktop)

**Component Specifications (6 Components):**
1. **Header Component**: Fixed, backdrop-blur, theme toggle
2. **Sidebar Component**: 280px, navigation items, active states
3. **Task Form Component**: Glassmorphism card, floating labels, gradient button
4. **Task Card Component**: Glassmorphism, hover effects, status badge
5. **Status Badge Component**: Color-coded (Pending: Amber, Complete: Green)
6. **Theme Toggle Component**: Circular button, rotation animation

**Visual Effects:**
- Glassmorphism: `backdrop-blur-md`, transparency
- Animations: Hover scale (1.02-1.05), transitions (200ms)
- Shadows: Layered for depth
- Gradient overlays

**Accessibility:**
- WCAG AA compliance
- Keyboard navigation
- Screen reader support
- Focus indicators

**Implementation Notes:**
- Tailwind CSS 4.x
- shadcn/ui components
- Lucide React icons
- Framer Motion animations
- next-themes

---

### 3. `specs/features/task-crud.md`
**Purpose:** Core task CRUD functionality specification
**Content:**
- 5 Basic Level Features (Add, Delete, Update, View, Mark Complete)
- 5 User Stories with acceptance criteria

**User Stories:**
1. **US-1: Create Task** (P1) - Title (required), description (optional), instant feedback
2. **US-2: View Tasks** (P1) - Responsive grid, status badges, empty state, skeleton loaders
3. **US-3: Update Task** (P1) - Inline edit, pre-filled form, Save/Cancel
4. **US-4: Delete Task** (P1) - Confirmation dialog, fade-out animation
5. **US-5: Toggle Completion** (P1) - Checkbox, strikethrough, optimistic UI

**Functional Requirements:**
- Task Data Model (id, user_id, title, description, completed, timestamps)
- Data Isolation (users see only their own tasks)
- Validation Rules (client + server)
- Error Handling (network, validation, server, auth)

**Non-Functional Requirements:**
- Performance: < 1s load, < 500ms CRUD ops
- Usability: Intuitive UI, keyboard accessible, mobile-responsive
- Accessibility: WCAG AA, semantic HTML, ARIA labels
- Security: JWT auth, input sanitization, SQL injection prevention

**Integration Points:**
- 6 API endpoints
- Frontend components (TaskForm, TaskList, TaskCard, StatusBadge, ConfirmDialog)
- State management (React state, optimistic updates)

**Testing Requirements:**
- Unit tests: Validation, rendering, API client
- Integration tests: CRUD workflow
- E2E tests: Full user journey

---

### 4. `specs/features/authentication.md`
**Purpose:** Multi-user authentication with Better Auth + JWT
**Content:**
- Authentication architecture diagram
- 5 User Stories for auth flow

**User Stories:**
1. **US-AUTH-1: Signup** (P1) - Email/name/password, validation, auto-login
2. **US-AUTH-2: Signin** (P1) - Email/password, JWT issued, redirect
3. **US-AUTH-3: Session Persistence** (P1) - JWT stored, auto-refresh, logout
4. **US-AUTH-4: Protected Routes** (P1) - /tasks requires auth, redirect flow
5. **US-AUTH-5: API Authorization** (P1) - JWT validation, user_id extraction

**Functional Requirements:**
- User Model (id, email, name, password_hash, timestamps)
- JWT Token Structure (header, payload with user_id, signature)
- Password Requirements (min 8 chars, uppercase, number)
- Email Validation (format check, uniqueness)
- Session Management (frontend storage, backend validation)

**Better Auth Configuration:**
- JWT secret (shared with backend)
- Database connection (Neon PostgreSQL)
- Token expiry (7 days default)

**FastAPI JWT Middleware:**
- Token verification
- User ID extraction
- 401/403 error handling

**Security Considerations:**
- Password hashing (bcrypt/argon2)
- JWT secret management (env vars)
- HTTPS required (production)
- Token storage (httpOnly cookie recommended)
- CORS configuration

**UI Components:**
- Login page
- Signup page
- Protected layout (header, user menu, logout)

**Error Handling:**
- Invalid credentials → 401
- Email exists → 400
- Weak password → 400
- Token expired → 401 redirect
- Invalid token → 401 redirect

---

### 5. `specs/api/rest-endpoints.md`
**Purpose:** Complete RESTful API specification
**Content:**
- Base URL (dev: localhost:8000, prod: deployed URL)
- Authentication (JWT Bearer token required)
- CORS configuration
- 6 API Endpoints (detailed specs)

**API Endpoints:**
1. **GET /api/{user_id}/tasks** - List all user's tasks
   - Query params: status, sort, order
   - Response: Tasks array + counts
   - Status: 200 (success), 401 (unauthorized), 403 (forbidden)

2. **POST /api/{user_id}/tasks** - Create new task
   - Request body: title (required), description (optional)
   - Validation: 1-200 chars title, max 1000 chars description
   - Response: Created task object
   - Status: 201 (created), 400 (validation error), 401, 403

3. **GET /api/{user_id}/tasks/{id}** - Get task details
   - Response: Single task object
   - Status: 200, 404 (not found), 401, 403

4. **PUT /api/{user_id}/tasks/{id}** - Update task
   - Request body: title and/or description
   - Response: Updated task object
   - Status: 200, 400, 404, 401

5. **DELETE /api/{user_id}/tasks/{id}** - Delete task
   - Response: Confirmation message
   - Status: 200, 404, 401, 403

6. **PATCH /api/{user_id}/tasks/{id}/complete** - Toggle completion
   - Request body: completed (boolean)
   - Response: Updated task object
   - Status: 200, 404, 401

**Security Model:**
- JWT validation on every request
- user_id verification (URL param must match token)
- Data isolation (queries filtered by user_id)

**Error Response Format:**
- Standard: `{"detail": "Error message"}`
- Validation: Array of error objects

**HTTP Status Codes:**
- 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error

**Request/Response Examples:**
- Complete CRUD workflow with cURL commands

**FastAPI Implementation Notes:**
- CORS middleware
- JWT middleware
- Route structure
- Environment variables

---

### 6. `specs/database/schema.md`
**Purpose:** PostgreSQL database schema for Neon Serverless
**Content:**
- Database provider (Neon Serverless)
- 2 Tables with complete schema

**Tables:**
1. **users** (Managed by Better Auth)
   - Columns: id (VARCHAR 36), email (unique), name, password_hash, timestamps
   - Indexes: email (unique), created_at
   - Purpose: User accounts

2. **tasks** (Application data)
   - Columns: id (SERIAL), user_id (FK), title (VARCHAR 200), description (TEXT), completed (BOOLEAN), timestamps
   - Foreign Key: user_id → users.id (ON DELETE CASCADE)
   - Indexes: user_id, completed, created_at, composite (user_id, completed)
   - Purpose: Todo items

**SQL Schema:**
- Complete CREATE TABLE statements
- Indexes for query optimization
- Triggers for auto-updating updated_at
- ON DELETE CASCADE for referential integrity

**SQLModel Models:**
- User model (Python class)
- Task model (Python class)
- Database connection setup
- Session management

**Queries and Patterns:**
- Get all user tasks (with filtering)
- Create task
- Update task
- Delete task
- Toggle completion

**Data Integrity:**
- Foreign key constraints
- NOT NULL constraints
- DEFAULT values
- MVCC for concurrency

**Security Considerations:**
- SQL injection prevention (parameterized queries)
- Password storage (hashed only)
- Connection security (SSL required)

**Neon Setup Instructions:**
- Create account
- Create project
- Get connection string
- Initialize database

---

### 7. `.spec-kit/config.yaml`
**Purpose:** Spec-Kit Plus configuration for the project
**Content:**
- Project metadata (name, version, phase)
- Folder structure definitions
- Phase definitions (5 phases with status)
- Feature tracking
- Technology stack by phase
- Constitution reference
- Development workflow stages
- Hackathon submission details (points, deadlines, bonuses)

**Phases Defined:**
1. phase-1-console: ✅ Completed
2. phase-2-fullstack: ⏳ In Progress (current)
3. phase-3-chatbot: Not started
4. phase-4-k8s-local: Not started
5. phase-5-cloud: Not started

**Features Tracked:**
- Phase I: basic-crud, life-manager, yearly-recurrence (completed)
- Phase II: task-crud, authentication (in-progress)

**Tech Stack Documented:**
- Phase I: Python + uv
- Phase II: Next.js + FastAPI + Neon + Better Auth
- Phase III: ChatKit + Agents SDK + MCP
- Phase IV: Docker + K8s + Helm
- Phase V: Kafka + Dapr + Cloud K8s

---

### 8. `CLAUDE.md` (Updated)
**Purpose:** Root agent instructions for monorepo navigation
**Changes:**
- Added Phase II Monorepo section
- Project structure diagram
- Navigation guidelines (frontend, backend, full-stack)
- Spec-Driven workflow reminder
- Phase II current status

**Navigation Guidelines:**
- Frontend work: Read UI spec → Feature spec → API spec
- Backend work: Read API spec → Auth spec → Database spec
- Full-stack work: Start with overview → Feature spec → Implement backend → Then frontend

---

## Outcome

- ✅ Impact: **Complete Phase II specification set created** - All requirements from hackathon.md documented
- 🧪 Tests: None yet (specification phase, no code)
- 📁 Files:
  - Created: 7 comprehensive specification files
  - Created: .spec-kit/config.yaml
  - Updated: CLAUDE.md (monorepo navigation)
  - Created: 2 PHRs (001-initiation, 002-completion)
- 🔁 Next prompts:
  1. Initialize backend: `cd backend && uv init` + FastAPI + SQLModel + Neon
  2. Initialize frontend: `cd frontend && npx create-next-app@latest`
  3. Implement backend: 6 API endpoints + JWT middleware + Database models
  4. Implement frontend: Next.js app + Better Auth + UI matching specs
  5. Test full-stack integration
  6. Deploy to Vercel (frontend) + Railway/Render (backend)
- 🧠 Reflection: Successfully completed **Specify** stage of Spec-Driven Development. All specifications are comprehensive, detailed, and aligned with hackathon requirements. Ready to move to **Plan** stage (create plan.md) and then **Tasks** stage (create tasks.md) before implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - specs created successfully
- Graders run and results (PASS/FAIL): N/A (spec stage)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Move to Plan stage - create detailed implementation plan (plan.md) that breaks down architecture, components, and technical approach before generating tasks

---

## Spec-Driven Development Progress

### ✅ Specify Stage: COMPLETE
- [x] Overview specification
- [x] UI design specification
- [x] Feature specifications (2: task-crud, authentication)
- [x] API endpoints specification
- [x] Database schema specification
- [x] Configuration files
- [x] Documentation updates

### ⏳ Plan Stage: NEXT
- [ ] Create `specs/phase-2-fullstack/plan.md`
- [ ] Architecture diagrams
- [ ] Component breakdown
- [ ] Implementation approach
- [ ] Technical decisions
- [ ] Risk analysis

### ⏳ Tasks Stage: PENDING
- [ ] Create `specs/phase-2-fullstack/tasks.md`
- [ ] Break plan into atomic tasks
- [ ] Organize by feature
- [ ] Mark dependencies
- [ ] Assign test cases

### ⏳ Implement Stage: PENDING
- [ ] Backend implementation
- [ ] Frontend implementation
- [ ] Integration
- [ ] Testing
- [ ] Deployment

---

## Hackathon Phase II Checklist

### Specifications (✅ Complete)
- [x] All 5 Basic Level features specified
- [x] All 6 API endpoints specified
- [x] Authentication flow specified
- [x] Database schema specified
- [x] UI design specified
- [x] Responsive design patterns defined
- [x] Accessibility requirements documented
- [x] Security model defined

### Implementation (⏳ Next)
- [ ] Backend setup (FastAPI + SQLModel + Neon)
- [ ] Frontend setup (Next.js + Better Auth)
- [ ] 6 API endpoints with JWT
- [ ] 5 CRUD features in UI
- [ ] Authentication flow (signup/signin)
- [ ] EXACT UI match (glassmorphism, theme toggle)

### Testing (⏳ Pending)
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance tests
- [ ] Security audit

### Deployment (⏳ Pending)
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Environment variables configured
- [ ] Demo video (90 seconds)
- [ ] GitHub repository public
- [ ] Submission form filled

---

**Estimated Work Remaining:**
- Plan stage: 2-3 hours (create plan.md with architecture diagrams)
- Tasks stage: 1-2 hours (break down into atomic tasks)
- Implement stage: 10-15 hours (backend + frontend + integration)
- Testing stage: 3-5 hours (unit + integration + E2E)
- Deployment stage: 2-3 hours (Vercel + Railway + demo video)

**Total:** ~18-28 hours of focused implementation work

---

## Summary

**Specification Phase Complete! 🎉**

We have successfully created a **comprehensive, production-ready specification set** for Phase II of the Evolution Todo hackathon project. All specifications follow the Spec-Driven Development workflow and are aligned with hackathon requirements from hackathon.md.

**Key Achievements:**
1. ✅ 7 detailed specification files created
2. ✅ Monorepo structure established
3. ✅ Spec-Kit Plus configured
4. ✅ CLAUDE.md updated for navigation
5. ✅ 2 PHRs documenting the process
6. ✅ Ready to move to Plan → Tasks → Implement stages

**Next Step:** Create `plan.md` to design the technical implementation approach, then break it into tasks in `tasks.md`.
