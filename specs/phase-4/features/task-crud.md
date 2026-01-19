# Feature: Task CRUD Operations - Phase II

## Overview
Core task management functionality for Evolution Todo web application. Users can create, read, update, and delete tasks through a modern web interface with multi-user support and persistent storage.

## Basic Level Features (5 Required)

### 1. Add Task ✅
**User can create new todo items**

**Requirements:**
- Title field (required, 1-200 characters)
- Description field (optional, max 1000 characters)
- Form validation (client + server)
- Instant feedback on success/error
- Task associated with authenticated user

**UI Elements:**
- Glassmorphism card with task form
- Floating label inputs
- Gradient submit button
- Success/error toast notifications

---

### 2. Delete Task ✅
**User can remove tasks permanently**

**Requirements:**
- Delete button on each task card
- Confirmation dialog before deletion
- Immediate removal from UI
- Success/error feedback
- Permanent deletion (no undo in Phase II)

**UI Elements:**
- Trash icon button
- Confirmation modal with task title
- Fade-out animation on deletion
- Error toast if deletion fails

---

### 3. Update Task ✅
**User can modify task details**

**Requirements:**
- Edit button on each task card
- Inline edit or modal form
- Pre-filled with current data
- Save/Cancel actions
- Validation same as create
- Immediate UI update

**UI Elements:**
- Pencil icon button
- Edit form (inline or modal)
- Save/Cancel buttons
- Success/error toast

---

### 4. View Task List ✅
**User can see all their tasks**

**Requirements:**
- Display only user's own tasks
- Responsive grid layout (1-3 columns)
- Each task shows: title, description, status, date, actions
- Completed tasks have visual distinction
- Empty state when no tasks
- Loading state while fetching

**UI Elements:**
- Task cards in responsive grid
- Status badges (Pending/Complete)
- Hover effects and animations
- Skeleton loaders
- Empty state message

---

### 5. Mark as Complete ✅
**User can toggle task completion status**

**Requirements:**
- Completion toggle on each task card
- Immediate visual feedback
- Status badge updates
- Optimistic UI update
- Revert on API error

**UI Elements:**
- Checkbox or toggle button
- Checkmark animation
- Strikethrough title when complete
- Lower opacity for completed tasks
- Status badge color change

---

## User Stories

### US-1: Create Task (Priority: P1)
```
As a logged-in user
I want to create a new task with title and description
So that I can track things I need to do
```

**Acceptance Criteria:**
- ✅ Task form is prominently displayed
- ✅ Title is required (1-200 chars)
- ✅ Description is optional (max 1000 chars)
- ✅ Submit button disabled until title entered
- ✅ On success: task appears in list, form clears, toast shown
- ✅ On error: error message shown, form data preserved

**Test Scenarios:**
```
GIVEN I am logged in
WHEN I enter title "Buy groceries" and click Submit
THEN a new task is created
AND task appears in my task list
AND form clears for next entry

GIVEN I try to submit without title
WHEN I click Submit
THEN button remains disabled
AND I see validation message

GIVEN API fails during creation
WHEN I retry submission
THEN error toast is shown
AND form data is preserved
```

---

### US-2: View Tasks (Priority: P1)
```
As a logged-in user
I want to see all my tasks in a clean layout
So that I know what I need to do
```

**Acceptance Criteria:**
- ✅ Only my tasks are shown (filtered by user_id)
- ✅ Tasks in responsive grid (1-3 columns)
- ✅ Each card shows: title, description, status, date, actions
- ✅ Completed tasks have lower opacity + strikethrough
- ✅ Empty state when no tasks
- ✅ Skeleton loaders while fetching

**Test Scenarios:**
```
GIVEN I have 5 tasks (3 pending, 2 complete)
WHEN I view my task list
THEN I see all 5 tasks in grid
AND completed tasks have strikethrough
AND newest tasks appear first

GIVEN I have no tasks
WHEN I view task list
THEN I see empty state message
AND task form is visible

GIVEN tasks are loading
WHEN data is being fetched
THEN I see skeleton placeholders
```

---

### US-3: Update Task (Priority: P1)
```
As a logged-in user
I want to edit my task's title and description
So that I can keep tasks accurate
```

**Acceptance Criteria:**
- ✅ Edit button on each task card
- ✅ Edit form pre-filled with current data
- ✅ Can modify title and/or description
- ✅ Save updates task, Cancel discards changes
- ✅ Immediate UI update on success
- ✅ Error message if update fails

**Test Scenarios:**
```
GIVEN I have task "Buy milk"
WHEN I click Edit, change to "Buy milk and eggs", Save
THEN task updates immediately
AND success toast is shown

GIVEN I am editing a task
WHEN I click Cancel
THEN changes are discarded
AND original content is restored

GIVEN API fails during update
WHEN I click Save
THEN error toast is shown
AND edit mode stays open
```

---

### US-4: Delete Task (Priority: P1)
```
As a logged-in user
I want to permanently remove tasks
So that my list stays clean
```

**Acceptance Criteria:**
- ✅ Delete button on each task card
- ✅ Confirmation dialog before deletion
- ✅ Task removed immediately after confirm
- ✅ Fade-out animation
- ✅ Success toast shown
- ✅ Cancel keeps task

**Test Scenarios:**
```
GIVEN I have task "Old task"
WHEN I click Delete and confirm
THEN task is removed from list
AND success toast is shown

GIVEN I click Delete
WHEN I click Cancel in dialog
THEN task remains in list
AND dialog closes

GIVEN API fails during delete
WHEN I confirm deletion
THEN task remains in list
AND error toast is shown
```

---

### US-5: Toggle Completion (Priority: P1)
```
As a logged-in user
I want to mark tasks complete/incomplete
So that I can track progress
```

**Acceptance Criteria:**
- ✅ Completion toggle on each card
- ✅ Immediate visual feedback (strikethrough, checkmark)
- ✅ Status badge updates
- ✅ Optimistic UI update
- ✅ Revert if API fails

**Test Scenarios:**
```
GIVEN I have pending task "Write report"
WHEN I click completion toggle
THEN task shows as complete (strikethrough)
AND status badge updates

GIVEN I have completed task
WHEN I click toggle
THEN task shows as pending
AND strikethrough is removed

GIVEN API fails during toggle
WHEN request errors
THEN task reverts to previous state
AND error toast is shown
```

---

## Functional Requirements

### FR-1: Task Data Model
```typescript
interface Task {
  id: number;              // Auto-generated
  user_id: string;         // From JWT auth
  title: string;           // Required, 1-200 chars
  description?: string;    // Optional, max 1000 chars
  completed: boolean;      // Default: false
  created_at: Date;        // Auto-generated
  updated_at: Date;        // Auto-updated
}
```

### FR-2: Data Isolation
- Users see only their own tasks
- API filters all queries by authenticated user_id
- Frontend never receives other users' tasks

### FR-3: Validation Rules
**Client-side:**
- Title: required, 1-200 characters
- Description: optional, max 1000 characters
- Real-time validation feedback

**Server-side:**
- Same rules enforced
- 400 Bad Request on validation error
- User-friendly error messages

### FR-4: Error Handling
- Network errors: "Network connection lost"
- Validation errors: Specific field messages
- Server errors: "Something went wrong"
- Unauthorized: Redirect to login
- Not found: "Task not found"

---

## Non-Functional Requirements

### NFR-1: Performance
- Task list loads in < 1 second
- CRUD operations complete in < 500ms
- Optimistic UI updates instant (<50ms)

### NFR-2: Usability
- Intuitive UI, self-explanatory
- Clear feedback for all actions
- Keyboard accessible (Tab, Enter)
- Mobile-responsive

### NFR-3: Accessibility
- WCAG AA compliance
- Semantic HTML
- ARIA labels on icons
- Focus indicators
- Screen reader friendly

### NFR-4: Security
- JWT authentication required
- Input sanitization (XSS prevention)
- SQL injection prevention (parameterized queries)
- User isolation enforced

---

## Integration Points

### API Endpoints Used
- `POST /api/{user_id}/tasks` - Create
- `GET /api/{user_id}/tasks` - Read list
- `GET /api/{user_id}/tasks/{id}` - Read single
- `PUT /api/{user_id}/tasks/{id}` - Update
- `DELETE /api/{user_id}/tasks/{id}` - Delete
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle

### Frontend Components
- `TaskForm` - Create tasks
- `TaskList` - Display grid
- `TaskCard` - Individual task
- `StatusBadge` - Visual indicator
- `ConfirmDialog` - Delete confirmation

### State Management
- React state (useState/useContext)
- Optimistic updates
- API sync on mutations

---

## Out of Scope (Phase II)

❌ **Not included:**
- Recurring tasks (Phase V)
- Due dates (Phase V)
- Priorities (Phase V)
- Tags/categories (Phase V)
- Search/filter (Phase V)
- Undo delete
- Task history
- Collaboration

**Focus:** Basic CRUD with authentication. Advanced features in Phase V.

---

## Testing Checklist

- [ ] Create task with valid data → succeeds
- [ ] Create task without title → validation error
- [ ] Create task with >200 char title → validation error
- [ ] View task list → only my tasks shown
- [ ] Update task title → changes persist
- [ ] Delete task with confirmation → task removed
- [ ] Toggle completion → status updates
- [ ] API error during create → error toast + retry
- [ ] API error during update → error toast + retry
- [ ] API error during delete → task stays + error toast
- [ ] Optimistic toggle → reverts on API error
- [ ] Mobile responsive → works on small screens
- [ ] Keyboard navigation → all actions accessible
- [ ] Screen reader → announces changes

---

## Success Metrics

✅ **Phase II Complete when:**
- All 5 basic features functional
- CRUD operations work reliably
- UI matches design spec
- Performance targets met
- Accessibility audit passes
- Multi-user isolation works
- Deployed and accessible

---

**References:**
- Overview: `/specs/overview.md`
- API Spec: `/specs/api/rest-endpoints.md`
- Database: `/specs/database/schema.md`
- UI Design: `/specs/ui/design.md`
