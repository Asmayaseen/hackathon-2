# REST API Endpoints Specification - Phase II

## Overview
RESTful API for Evolution Todo application. All endpoints require JWT authentication and enforce user data isolation. Built with FastAPI and secured with JWT middleware.

## Base Configuration

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-app.railway.app` (or your deployed backend URL)

### Authentication
All endpoints require JWT token in Authorization header:
```http
Authorization: Bearer <jwt-token>
```

### Content Type
```http
Content-Type: application/json
```

### CORS
Backend configured to accept requests from:
- `http://localhost:3000` (development)
- `https://your-app.vercel.app` (production)

---

## API Endpoints (6 Total)

### 1. List All Tasks
Get all tasks for the authenticated user.

**Endpoint:** `GET /api/{user_id}/tasks`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |
| status | string | query | No | Filter: "all", "pending", "completed" (default: "all") |
| sort | string | query | No | Sort by: "created", "updated", "title" (default: "created") |
| order | string | query | No | Order: "asc", "desc" (default: "desc") |

**Request Example:**
```http
GET /api/user-123/tasks?status=pending&sort=created&order=desc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 (Success):**
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user-123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-28T10:30:00Z",
      "updated_at": "2025-12-28T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": "user-123",
      "title": "Write report",
      "description": null,
      "completed": false,
      "created_at": "2025-12-27T15:20:00Z",
      "updated_at": "2025-12-27T15:20:00Z"
    }
  ],
  "total": 2,
  "pending": 2,
  "completed": 0
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response 403 (Forbidden):**
```json
{
  "detail": "Forbidden - user_id mismatch"
}
```

---

### 2. Create New Task
Create a new task for the authenticated user.

**Endpoint:** `POST /api/{user_id}/tasks`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // Optional
}
```

**Validation Rules:**
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters

**Request Example:**
```http
POST /api/user-123/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response 201 (Created):**
```json
{
  "id": 3,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-28T11:00:00Z",
  "updated_at": "2025-12-28T11:00:00Z"
}
```

**Response 400 (Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response 403 (Forbidden):**
```json
{
  "detail": "Forbidden - user_id mismatch"
}
```

---

### 3. Get Task Details
Retrieve a single task by ID.

**Endpoint:** `GET /api/{user_id}/tasks/{id}`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |
| id | integer | path | Yes | Task ID |

**Request Example:**
```http
GET /api/user-123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 (Success):**
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-28T10:30:00Z",
  "updated_at": "2025-12-28T10:30:00Z"
}
```

**Response 404 (Not Found):**
```json
{
  "detail": "Task not found or you don't have access"
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response 403 (Forbidden):**
```json
{
  "detail": "Forbidden - user_id mismatch"
}
```

---

### 4. Update Task
Update an existing task's title and/or description.

**Endpoint:** `PUT /api/{user_id}/tasks/{id}`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |
| id | integer | path | Yes | Task ID |

**Request Body:**
```json
{
  "title": "Buy groceries and fruits",  // Optional
  "description": "Milk, eggs, bread, apples, bananas"  // Optional
}
```

**Validation Rules:**
- At least one field (title or description) must be provided
- `title`: If provided, 1-200 characters
- `description`: If provided, max 1000 characters

**Request Example:**
```http
PUT /api/user-123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas"
}
```

**Response 200 (Success):**
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": false,
  "created_at": "2025-12-28T10:30:00Z",
  "updated_at": "2025-12-28T11:15:00Z"  // Updated timestamp
}
```

**Response 400 (Validation Error):**
```json
{
  "detail": "Title exceeds maximum length of 200 characters"
}
```

**Response 404 (Not Found):**
```json
{
  "detail": "Task not found or you don't have access"
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

---

### 5. Delete Task
Permanently delete a task.

**Endpoint:** `DELETE /api/{user_id}/tasks/{id}`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |
| id | integer | path | Yes | Task ID |

**Request Example:**
```http
DELETE /api/user-123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 (Success):**
```json
{
  "message": "Task deleted successfully",
  "id": 1
}
```

**Response 404 (Not Found):**
```json
{
  "detail": "Task not found or you don't have access"
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response 403 (Forbidden):**
```json
{
  "detail": "Forbidden - user_id mismatch"
}
```

---

### 6. Toggle Task Completion
Mark a task as complete or incomplete.

**Endpoint:** `PATCH /api/{user_id}/tasks/{id}/complete`

**Parameters:**
| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | string | path | Yes | User's unique ID (must match JWT) |
| id | integer | path | Yes | Task ID |

**Request Body:**
```json
{
  "completed": true  // true = mark complete, false = mark incomplete
}
```

**Request Example:**
```http
PATCH /api/user-123/tasks/1/complete
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "completed": true
}
```

**Response 200 (Success):**
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,  // Status updated
  "created_at": "2025-12-28T10:30:00Z",
  "updated_at": "2025-12-28T11:20:00Z"  // Updated timestamp
}
```

**Response 404 (Not Found):**
```json
{
  "detail": "Task not found or you don't have access"
}
```

**Response 401 (Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

---

## Security Model

### JWT Validation
Every request must include a valid JWT token:
```python
# Backend middleware
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### User ID Verification
Every endpoint verifies that the `user_id` in the URL matches the authenticated user:
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, auth_user_id: str = Depends(verify_token)):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # Proceed with query...
```

### Data Isolation
All database queries are filtered by `user_id`:
```python
# Only return tasks belonging to authenticated user
tasks = db.query(Task).filter(Task.user_id == auth_user_id).all()
```

---

## Error Response Format

### Standard Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error Response
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

---

## HTTP Status Codes

| Status | Meaning | When Used |
|--------|---------|-----------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing/invalid/expired token |
| 403 | Forbidden | Valid token but user_id mismatch |
| 404 | Not Found | Task doesn't exist or user doesn't own it |
| 500 | Internal Server Error | Unexpected server error |

---

## Request/Response Examples

### Complete CRUD Workflow

#### 1. Create Task
```bash
curl -X POST http://localhost:8000/api/user-123/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete tutorial"}'
```

#### 2. List All Tasks
```bash
curl -X GET http://localhost:8000/api/user-123/tasks \
  -H "Authorization: Bearer <token>"
```

#### 3. Get Task Details
```bash
curl -X GET http://localhost:8000/api/user-123/tasks/1 \
  -H "Authorization: Bearer <token>"
```

#### 4. Update Task
```bash
curl -X PUT http://localhost:8000/api/user-123/tasks/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI & SQLModel"}'
```

#### 5. Toggle Completion
```bash
curl -X PATCH http://localhost:8000/api/user-123/tasks/1/complete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

#### 6. Delete Task
```bash
curl -X DELETE http://localhost:8000/api/user-123/tasks/1 \
  -H "Authorization: Bearer <token>"
```

---

## Rate Limiting (Future Enhancement)

**Out of Scope for Phase II**, but recommended for production:
- 100 requests per minute per user
- 429 Too Many Requests response when exceeded

---

## API Versioning (Future Enhancement)

**Out of Scope for Phase II**, but for future scalability:
- Version in URL: `/api/v1/{user_id}/tasks`
- Allows breaking changes without affecting existing clients

---

## Testing Checklist

### Manual Testing (Postman/cURL)
- [ ] Create task with valid data → 201
- [ ] Create task without auth → 401
- [ ] Create task with wrong user_id → 403
- [ ] Create task without title → 400
- [ ] List tasks → 200 with array
- [ ] List tasks with status filter → filtered results
- [ ] Get task by ID → 200 with task object
- [ ] Get non-existent task → 404
- [ ] Update task → 200 with updated data
- [ ] Update with invalid data → 400
- [ ] Toggle completion → 200 with updated status
- [ ] Delete task → 200 with confirmation
- [ ] Delete non-existent task → 404

### Integration Tests (Pytest)
- [ ] All endpoints with valid JWT → success
- [ ] All endpoints without JWT → 401
- [ ] All endpoints with expired JWT → 401
- [ ] Cross-user access attempts → 403
- [ ] CORS headers present on all responses

---

## Success Metrics

✅ **API complete when:**
- All 6 endpoints functional
- JWT authentication enforced
- User data isolation working
- Validation errors clear and helpful
- CORS configured correctly
- Error handling comprehensive
- Performance: responses < 500ms

---

## FastAPI Implementation Notes

### Main App Structure
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks

app = FastAPI(title="Evolution Todo API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(tasks.router)
```

### Environment Variables
```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

---

**References:**
- FastAPI Docs: https://fastapi.tiangolo.com/
- JWT Spec: https://jwt.io/
- Overview: `/specs/overview.md`
- Task CRUD: `/specs/features/task-crud.md`
- Authentication: `/specs/features/authentication.md`
- Database: `/specs/database/schema.md`
