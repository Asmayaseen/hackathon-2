# Feature: Authentication - Phase II

## Overview
Multi-user authentication system using Better Auth for user management and JWT tokens for API security. Enables user signup, signin, session management, and API authorization.

## Authentication Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Next.js        │       │  Better Auth    │       │  Neon DB        │
│  Frontend       │◀─────▶│  (Auth Server)  │◀─────▶│  (Users table)  │
│                 │  JWT  │                 │ SQL   │                 │
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │                                                   ▲
         │ JWT Token                                         │
         ▼                                                   │
┌─────────────────┐                                         │
│                 │                                          │
│  FastAPI        │──────────────────────────────────────────┘
│  Backend        │  Validates JWT & filters by user_id
│                 │
└─────────────────┘
```

## User Stories

### US-AUTH-1: User Signup (Priority: P1)
```
As a new user
I want to create an account with email and password
So that I can start managing my tasks
```

**Acceptance Criteria:**
- ✅ Signup form with email, name, password fields
- ✅ Email validation (format check)
- ✅ Password requirements (min 8 chars, 1 uppercase, 1 number)
- ✅ Password confirmation field (must match)
- ✅ On success: User created, auto-login, redirect to tasks page
- ✅ On error: Clear error message (email exists, weak password, etc.)
- ✅ Terms of service checkbox (optional but recommended)

**Test Scenarios:**
```
GIVEN I am on signup page
WHEN I enter valid email, name, password
THEN account is created
AND I am automatically logged in
AND redirected to tasks page

GIVEN I enter existing email
WHEN I try to signup
THEN I see error "Email already registered"

GIVEN I enter weak password
WHEN I try to signup
THEN I see error "Password must be at least 8 characters"
```

---

### US-AUTH-2: User Signin (Priority: P1)
```
As an existing user
I want to login with my email and password
So that I can access my tasks
```

**Acceptance Criteria:**
- ✅ Signin form with email and password fields
- ✅ "Remember me" option (extends session)
- ✅ On success: JWT token issued, redirect to tasks page
- ✅ On error: Clear message (invalid credentials, account not found)
- ✅ "Forgot password" link (optional for Phase II)
- ✅ Link to signup page for new users

**Test Scenarios:**
```
GIVEN I have an account
WHEN I enter correct email and password
THEN I am logged in
AND redirected to tasks page
AND JWT token is stored

GIVEN I enter wrong password
WHEN I try to login
THEN I see error "Invalid credentials"

GIVEN I enter non-existent email
WHEN I try to login
THEN I see error "Account not found"
```

---

### US-AUTH-3: Session Persistence (Priority: P1)
```
As a logged-in user
I want my session to persist across page reloads
So that I don't have to login repeatedly
```

**Acceptance Criteria:**
- ✅ JWT token stored securely (httpOnly cookie or localStorage)
- ✅ Token validated on app load
- ✅ If valid: User stays logged in
- ✅ If expired/invalid: Redirect to login
- ✅ Token auto-refreshes before expiry (optional)
- ✅ Logout clears token and redirects to login

**Test Scenarios:**
```
GIVEN I am logged in
WHEN I reload the page
THEN I remain logged in
AND see my tasks

GIVEN my token expires
WHEN I try to access tasks
THEN I am redirected to login

GIVEN I click logout
WHEN logout completes
THEN token is cleared
AND I am redirected to login page
```

---

### US-AUTH-4: Protected Routes (Priority: P1)
```
As the system
I want to protect task pages from unauthenticated access
So that only logged-in users can manage tasks
```

**Acceptance Criteria:**
- ✅ Tasks page requires authentication
- ✅ Unauthenticated users redirected to login
- ✅ After login, redirect to originally requested page
- ✅ Public routes: /, /login, /signup
- ✅ Protected routes: /tasks, /profile (if exists)

**Test Scenarios:**
```
GIVEN I am not logged in
WHEN I try to access /tasks
THEN I am redirected to /login

GIVEN I am not logged in and try /tasks
WHEN I login successfully
THEN I am redirected to /tasks

GIVEN I am logged in
WHEN I access /tasks
THEN I see my tasks page
```

---

### US-AUTH-5: API Authorization (Priority: P1)
```
As the backend API
I want to verify user identity on every request
So that users only access their own data
```

**Acceptance Criteria:**
- ✅ All API endpoints require valid JWT token
- ✅ Token sent in Authorization header: `Bearer <token>`
- ✅ Backend validates token signature and expiry
- ✅ Backend extracts user_id from token payload
- ✅ Backend filters all queries by user_id
- ✅ Unauthorized requests return 401 status
- ✅ Expired tokens return 401 with message "Token expired"

**Test Scenarios:**
```
GIVEN I make API request with valid JWT
WHEN backend validates token
THEN request is authorized
AND user_id is extracted

GIVEN I make request without token
WHEN backend checks authorization
THEN request is rejected with 401

GIVEN I make request with expired token
WHEN backend validates
THEN request is rejected with 401 "Token expired"
```

---

## Functional Requirements

### FR-AUTH-1: User Model
```typescript
interface User {
  id: string;              // Primary key (UUID)
  email: string;           // Unique, required
  name: string;            // Required
  password_hash: string;   // Hashed (bcrypt/argon2)
  created_at: Date;        // Auto-generated
  updated_at: Date;        // Auto-updated
}
```

**Important:** Never store plain-text passwords. Always hash with bcrypt or argon2.

---

### FR-AUTH-2: JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid-string",
    "email": "user@example.com",
    "name": "User Name",
    "iat": 1640000000,       // Issued at (timestamp)
    "exp": 1640604800        // Expiry (7 days default)
  },
  "signature": "..."
}
```

**Token Expiry:** 7 days (configurable via environment variable)

---

### FR-AUTH-3: Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 number (0-9)
- Special characters recommended but not required

**Validation Messages:**
- "Password must be at least 8 characters"
- "Password must contain uppercase letter"
- "Password must contain number"

---

### FR-AUTH-4: Email Validation
- Valid email format (regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$`)
- Case-insensitive (store as lowercase)
- Check uniqueness before signup

**Validation Messages:**
- "Invalid email format"
- "Email already registered"

---

### FR-AUTH-5: Session Management
**Frontend:**
- Store JWT token securely (httpOnly cookie recommended)
- Include token in all API requests: `Authorization: Bearer <token>`
- Clear token on logout

**Backend:**
- Validate token signature using shared secret
- Check token expiry
- Extract user_id from payload
- Return 401 if invalid/expired

---

## Better Auth Configuration

### Better Auth Setup (Next.js)
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL,
  },
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET,
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

### Environment Variables
```env
# Better Auth
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@host/db

# JWT (shared with backend)
JWT_SECRET=same-as-BETTER_AUTH_SECRET
```

**Critical:** BETTER_AUTH_SECRET and JWT_SECRET must be the same so both frontend (Better Auth) and backend (FastAPI) can verify tokens.

---

## FastAPI JWT Middleware

### JWT Validation Middleware
```python
# backend/middleware/auth.py
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

### Protected Route Example
```python
# backend/routes/tasks.py
from fastapi import APIRouter, Depends
from middleware.auth import verify_token

router = APIRouter()

@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, auth_user_id: str = Depends(verify_token)):
    # Verify URL user_id matches authenticated user_id
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Fetch tasks for this user
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks
```

---

## Security Considerations

### SEC-1: Password Hashing
- Use bcrypt or argon2 (NOT md5 or sha1)
- Store only hashed passwords in database
- Never log or expose passwords

### SEC-2: JWT Secret Management
- Use strong secret (min 32 characters, random)
- Never commit secrets to git
- Store in environment variables
- Rotate secrets periodically in production

### SEC-3: HTTPS Required
- All auth endpoints must use HTTPS in production
- Vercel enforces HTTPS automatically
- Development: HTTP okay for localhost only

### SEC-4: Token Storage
**Recommended:** httpOnly cookie (prevents XSS)
**Alternative:** localStorage (vulnerable to XSS, use with caution)

### SEC-5: CORS Configuration
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Production
        "http://localhost:3000",        # Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## UI Components

### Login Page
- Email input (type="email")
- Password input (type="password", show/hide toggle)
- Remember me checkbox
- Submit button (gradient style)
- Link to signup page
- "Forgot password?" link (optional)

### Signup Page
- Email input
- Name input
- Password input (with strength indicator)
- Confirm password input
- Terms checkbox (optional)
- Submit button (gradient style)
- Link to login page

### Protected Layout
- Header with user name and logout button
- Theme toggle
- Navigation sidebar
- Main content area (tasks)

---

## Error Handling

### Common Auth Errors
| Error | Status | Message | User Action |
|-------|--------|---------|-------------|
| Invalid credentials | 401 | "Invalid email or password" | Re-enter credentials |
| Email exists | 400 | "Email already registered" | Use different email or login |
| Weak password | 400 | "Password too weak" | Strengthen password |
| Token expired | 401 | "Session expired. Please login again." | Redirect to login |
| Invalid token | 401 | "Invalid session. Please login again." | Redirect to login |
| No token | 401 | "Authentication required" | Redirect to login |

---

## Testing Checklist

### Unit Tests
- [ ] Password validation logic
- [ ] Email format validation
- [ ] JWT token generation
- [ ] JWT token verification
- [ ] Password hashing

### Integration Tests
- [ ] Signup flow → user created in DB
- [ ] Login flow → JWT token issued
- [ ] Protected route → requires valid token
- [ ] Expired token → 401 error
- [ ] Invalid token → 401 error
- [ ] Logout → token cleared

### E2E Tests
- [ ] Complete signup → login → access tasks → logout flow
- [ ] Signup with existing email → error
- [ ] Login with wrong password → error
- [ ] Access tasks without login → redirect to login
- [ ] Session persists after page reload

---

## Success Metrics

✅ **Authentication complete when:**
- Users can signup with email/password
- Users can login and receive JWT token
- Sessions persist across page reloads
- Protected routes require authentication
- API endpoints validate JWT on every request
- User data isolation works (users see only their tasks)
- Logout clears session and redirects

---

## Out of Scope (Phase II)

❌ **Not included:**
- OAuth (Google, GitHub login) - Future enhancement
- Email verification - Future enhancement
- Password reset via email - Future enhancement
- Two-factor authentication (2FA) - Future enhancement
- Role-based access control (RBAC) - Future enhancement
- Account deletion - Future enhancement
- Profile editing - Future enhancement

**Focus:** Basic email/password auth with JWT. Advanced features later.

---

## Environment Variables Summary

### Frontend (.env.local)
```env
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://...
```

### Backend (.env)
```env
JWT_SECRET=same-as-BETTER_AUTH_SECRET
DATABASE_URL=postgresql://...
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

**Critical:** JWT_SECRET must match BETTER_AUTH_SECRET for token verification to work.

---

**References:**
- Better Auth Docs: https://www.better-auth.com/docs
- JWT Spec: https://jwt.io/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Overview: `/specs/overview.md`
- API Spec: `/specs/api/rest-endpoints.md`
- Database: `/specs/database/schema.md`
