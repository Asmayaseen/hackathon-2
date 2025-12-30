# Tasks: Phase II Full-Stack Web Application

## Phase 1: Setup (Shared Infrastructure)
- [x] T001 [P] Configure root package.json for monorepo workspace support
- [x] T002 [P] Configure root vercel.json for Next.js + FastAPI routing
- [x] T003 [P] Setup .env.example templates in phase-2/frontend and phase-2/backend

## Phase 2: Foundational (Blocking Prerequisites)
- [x] T004 Setup database schema and trigger for updated_at in phase-2/backend/db.py
- [x] T005 [P] Implement User and Task SQLModel entities in phase-2/backend/models.py
- [x] T006 [P] Implement JWT Authentication middleware in phase-2/backend/middleware/auth.py
- [x] T007 Initialize CORS middleware with allowed origins in phase-2/backend/main.py

## Phase 3: User Story: Authentication (Priority: P1) 🎯 MVP
- [x] T008 [US-AUTH] Configure API Client with JWT in phase-2/frontend/lib/api.ts
- [x] T009 [US-AUTH] Create Signin page with form validation in phase-2/frontend/app/auth/signin/page.tsx
- [x] T010 [US-AUTH] Create Signup page with password requirements in phase-2/frontend/app/auth/signup/page.tsx
- [x] T011 [US-AUTH] Implement Protected Route middleware for /tasks in phase-2/frontend/middleware.ts

## Phase 4: User Story: Create & View Tasks (Priority: P1)
- [x] T012 [US1] Implement POST /api/{user_id}/tasks endpoint in phase-2/backend/routes/tasks.py
- [x] T013 [US1] Create TaskForm component with glassmorphism in phase-2/frontend/components/TaskForm.tsx
- [x] T014 [US2] Implement GET /api/{user_id}/tasks endpoint in phase-2/backend/routes/tasks.py
- [x] T015 [US2] Create TaskList and TaskCard components in phase-2/frontend/components/TaskList.tsx

## Phase 5: User Story: Update, Delete & Complete (Priority: P1)
- [x] T016 [US3] Implement PUT /api/{user_id}/tasks/{id} endpoint in phase-2/backend/routes/tasks.py
- [x] T017 [US4] Implement DELETE /api/{user_id}/tasks/{id} with confirmation in phase-2/backend/routes/tasks.py
- [x] T018 [US5] Implement PATCH /api/{user_id}/tasks/{id}/complete in phase-2/backend/routes/tasks.py
- [x] T019 [US5] Implement Optimistic UI toggle for Completion in phase-2/frontend/components/TaskItem.tsx

## Phase N: Polish & Cross-Cutting Concerns
- [x] T020 [P] Implement Theme Toggle (Sun/Moon) in phase-2/frontend/components/ThemeToggle.tsx
- [x] T021 [P] Setup loading skeletons for TaskList in phase-2/frontend/components/TaskList.tsx
- [x] T022 Documentation updates in README.md and quickstart.md
