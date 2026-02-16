# Feature Specification: User Authentication

**Feature ID**: FEAT-AUTH-001
**Created**: 2025-12-29
**Updated**: 2026-02-10
**Status**: Implemented (Phase II - V)
**Phases**: II (JWT Auth), III (Chat Auth), IV (Containerized), V (K8s Secrets)
**Source Files**: `routes/auth.py`, `middleware/auth.py`, `frontend/src/app/auth/`, `frontend/src/lib/api.ts`, `frontend/middleware.ts`

---

## 1. Auth Overview

Evolution Todo uses a **stateless JWT-based authentication system** spanning two services:

- **FastAPI Backend** — issues and verifies JWTs, stores users in Neon PostgreSQL
- **Next.js Frontend** — collects credentials, stores tokens, attaches them to every request

There is **no session table**. Authentication state lives entirely within the JWT. The backend never calls the frontend to verify a user; the token is self-contained.

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Token format | JWT (HS256) | Stateless, no session store needed |
| Hashing | SHA256 (`hashlib`) | Simple, sufficient for hackathon scope |
| Token storage (client) | `localStorage` + cookie | localStorage for API calls, cookie for SSR middleware |
| Token lifetime | 7 days | Balance between UX and security |
| Refresh tokens | **Not implemented** | Out of scope for hackathon; re-login on expiry |
| User ID format | UUID v4 | Globally unique, no sequential enumeration |
| Shared secret | `JWT_SECRET` env var | Same value in frontend and backend |

---

## 2. Authentication Flow Diagram

```
                         ┌──────────────────────────────────┐
                         │        SIGNUP / SIGNIN           │
                         └──────────────────────────────────┘

 ┌─────────────┐  POST /api/auth/signup   ┌─────────────┐  INSERT/SELECT  ┌──────────┐
 │  Next.js    │ ───────────────────────> │  FastAPI     │ ──────────────> │ Neon DB  │
 │  Frontend   │  POST /api/auth/signin   │  Backend     │ <───────────── │ (users)  │
 │             │ <─── { token, user }     │              │                 │          │
 └──────┬──────┘                          └──────────────┘                 └──────────┘
        │
        │ Store in:
        │  1. localStorage.auth_token
        │  2. localStorage.user_id / user_email / user_name
        │  3. document.cookie (auth_token, max-age=604800)
        │
        ▼
                         ┌──────────────────────────────────┐
                         │     AUTHENTICATED REQUESTS        │
                         └──────────────────────────────────┘

 ┌─────────────┐  Authorization: Bearer <JWT>  ┌─────────────┐
 │  Next.js    │ ────────────────────────────> │  FastAPI     │
 │  (axios     │                               │  verify_token│
 │  intercept) │ <──── 200 / 401 / 403         │  middleware  │
 └─────────────┘                               └──────┬──────┘
                                                       │
        On 401:                                        │  jwt.decode(token, JWT_SECRET)
        - Clear localStorage                           │  → extract user_id
        - Clear cookie                                 │  → compare with URL {user_id}
        - Redirect → /auth/signin                      │  → 403 if mismatch
                                                       ▼
                                               ┌──────────────┐
                                               │ Route Handler │
                                               │ (tasks, chat, │
                                               │  stats, etc.) │
                                               └──────────────┘
```

---

## 3. Signup Process

**Endpoint**: `POST /api/auth/signup`
**Source**: `routes/auth.py:62`

### Step-by-Step Flow

1. Frontend collects: `name`, `email`, `password`, `confirmPassword`
2. **Client-side validation**:
   - Password length >= 8 characters
   - Password === confirmPassword
   - All fields non-empty (HTML `required`)
3. Frontend calls `api.signup(name, email, password)` via axios
4. Backend validates via Pydantic:
   - `name`: 1-255 chars
   - `email`: valid EmailStr format
   - `password`: 8-255 chars
5. Backend checks `SELECT * FROM users WHERE email = ?`
   - If exists → 400 `"Email already registered"`
6. Backend creates user:
   - `id` = `uuid.uuid4()`
   - `password_hash` = `sha256(password)`
   - `created_at` = `utcnow()`
7. Backend generates JWT:
   - Payload: `{ user_id, email, exp: now+7d, iat: now }`
   - Signed with `JWT_SECRET` using HS256
8. Backend returns `{ token, user: { id, email, name } }`
9. Frontend stores:
   - `localStorage.auth_token = token`
   - `localStorage.user_id = user.id`
   - `localStorage.user_email = user.email`
   - `localStorage.user_name = user.name`
   - `document.cookie = "auth_token=<token>; path=/; SameSite=Lax; max-age=604800"`
10. Frontend redirects to `/tasks` via `window.location.href` (hard redirect)

---

## 4. Login Process

**Endpoint**: `POST /api/auth/signin`
**Source**: `routes/auth.py:119`

### Step-by-Step Flow

1. Frontend collects: `email`, `password`
2. Frontend calls `api.signin(email, password)` via axios
3. Backend queries `SELECT * FROM users WHERE email = ?`
   - Not found → 401 `"Invalid email or password"`
4. Backend compares `sha256(password)` with `user.password_hash`
   - Mismatch → 401 `"Invalid email or password"` (same message — no email enumeration)
5. Backend generates JWT (same as signup)
6. Backend returns `{ token, user: { id, email, name } }`
7. Frontend stores token + user info (same as signup)
8. Frontend redirects to `/tasks`

### Security Note: Credential Enumeration Prevention

Both "user not found" and "wrong password" return the **identical** error message `"Invalid email or password"`. An attacker cannot determine whether an email is registered.

---

## 5. JWT Lifecycle

### Token Structure

```
Header:  { "alg": "HS256", "typ": "JWT" }
Payload: { "user_id": "uuid", "email": "john@example.com", "exp": 1735689600, "iat": 1735084800 }
Signature: HMAC-SHA256(header.payload, JWT_SECRET)
```

### Timeline

```
  Login                                  Expiry (7 days later)
    │                                         │
    ├─── Token valid ────────────────────────►│
    │    (all API calls succeed)              │
    │                                         │
    │                                         ├──► 401 "Token expired"
    │                                         │    Frontend clears storage
    │                                         │    Redirect → /auth/signin
    │                                         │    User must re-login
```

### Configuration

| Parameter | Value | Source |
|---|---|---|
| `JWT_SECRET` | env var (min 32 chars) | `os.getenv("JWT_SECRET", "your-secret-key-min-32-chars")` |
| `JWT_ALGORITHM` | `HS256` | Hardcoded |
| `JWT_EXPIRATION_HOURS` | `168` (7 days) | Hardcoded `24 * 7` |

### Token Issuance Points

| Action | Issues Token |
|---|---|
| Signup | Yes — immediate login after registration |
| Signin | Yes |
| Page refresh | No — reuses stored token |
| Token expiry | No — user must re-login |

---

## 6. Token Refresh Strategy

**Current implementation: NO refresh tokens.**

When the JWT expires (after 7 days):

1. Backend returns 401 with `"Token expired. Please login again."`
2. Frontend axios interceptor catches the 401
3. Frontend clears all localStorage keys (`auth_token`, `user_id`, `user_email`, `user_name`)
4. Frontend redirects to `/auth/signin`
5. User re-authenticates manually

### Why No Refresh Token

- Hackathon scope: simplicity over production-grade token rotation
- 7-day expiry provides reasonable UX without refresh complexity
- Single-token model avoids refresh-token storage, rotation, and revocation logic

### Production Upgrade Path

If upgrading, implement:
- Short-lived access token (15 min)
- Long-lived refresh token (30 days) stored in HttpOnly cookie
- `POST /api/auth/refresh` endpoint
- Token rotation on each refresh

---

## 7. Protected Routes Behavior

### Backend Protection (`middleware/auth.py`)

**Source**: `middleware/auth.py:18` — `verify_token()` function

Every protected route declares `authenticated_user_id: str = Depends(verify_token)`:

1. Extract Bearer token from `Authorization` header
2. `jwt.decode(token, JWT_SECRET, algorithms=["HS256"])`
3. Extract `user_id` from decoded payload
4. Return `user_id` to route handler
5. Route handler compares `user_id` with URL `{user_id}` parameter

### Frontend Protection (`middleware.ts`)

**Source**: `frontend/middleware.ts`

**Current state**: Middleware is **temporarily unlocked** (returns `NextResponse.next()` unconditionally). Route matcher is configured for `/tasks/:path*` and `/auth/:path*` but no token check is enforced at the Next.js layer.

**Actual protection** relies on the backend: if no token is present, axios requests fail with 401, and the response interceptor redirects to `/auth/signin`.

### Client-Side Token Attachment (`api.ts`)

**Source**: `frontend/src/lib/api.ts:18`

Axios request interceptor reads `localStorage.auth_token` and sets `Authorization: Bearer <token>` on every outgoing request. If the token is missing, the request goes without auth and the backend returns 401.

### Route-Level User Isolation

Every task-related route enforces:

```python
if user_id != authenticated_user_id:
    raise HTTPException(status_code=403, detail="Cannot access other users' tasks")
```

This prevents User A from accessing User B's data even with a valid JWT.

---

## 8. Error States

### Backend Error Taxonomy

| Error | HTTP Status | Detail Message | Trigger |
|---|---|---|---|
| Missing token | 401 | `"Not authenticated"` | No `Authorization` header (FastAPI HTTPBearer) |
| Expired token | 401 | `"Token expired. Please login again."` | `jwt.ExpiredSignatureError` |
| Invalid token | 401 | `"Invalid token. Please login again."` | `jwt.InvalidTokenError` (bad signature, malformed) |
| Missing user_id in payload | 401 | `"Invalid token: user_id not found"` | Corrupted/manually crafted token |
| Cross-user access | 403 | `"Cannot access other users' tasks"` | URL user_id != JWT user_id |
| Duplicate email | 400 | `"Email already registered"` | Signup with existing email |
| Wrong credentials | 401 | `"Invalid email or password"` | Signin with bad email or password |
| Validation error | 422 | Pydantic detail | Short password, invalid email format |

### Frontend Error Handling

| Scenario | Behavior |
|---|---|
| 401 from any endpoint | Clear localStorage + cookie → redirect `/auth/signin` |
| 400 on signup | Display error message below form |
| 401 on signin | Display `"Invalid credentials"` below form |
| Network error | Display `"Registration failed"` or `"Invalid credentials"` |
| Form loading | Disable all inputs + show spinner in submit button |

---

## 9. Security Considerations

### Current Strengths

| Control | Implementation |
|---|---|
| Password hashing | SHA256 before storage — never stored in plaintext |
| No credential enumeration | Identical error for wrong email and wrong password |
| Token expiry | 7-day automatic expiration enforced by backend |
| User isolation | Every endpoint verifies JWT user_id matches URL user_id |
| CORS | Backend restricts to frontend origin |
| Shared secret | Loaded from `JWT_SECRET` environment variable |

### Known Limitations

| Risk | Severity | Detail | Mitigation Path |
|---|---|---|---|
| SHA256 is fast (brute-forceable) | Medium | Not a memory-hard hash like bcrypt/argon2 | Upgrade to bcrypt with cost factor 12 |
| Token in localStorage | Medium | Vulnerable to XSS — JS can read it | Move to HttpOnly cookie |
| No rate limiting | Medium | Login endpoint can be brute-forced | Add rate limiter middleware |
| No refresh tokens | Low | User must re-login every 7 days | Implement refresh token rotation |
| No CSRF protection | Low | Cookie-based token without CSRF | Add CSRF token or use SameSite=Strict |
| JWT_SECRET default fallback | High | Code has a hardcoded fallback `"your-secret-key-min-32-chars"` | Remove fallback; fail on missing env var |
| No password complexity rules | Low | Only minimum 8 chars enforced | Add uppercase/number/special char requirement |
| No account lockout | Low | Unlimited login attempts | Lock after 5 failed attempts |
| Frontend middleware bypassed | Medium | Middleware returns `next()` unconditionally | Re-enable token check in middleware.ts |

### Secrets Management Across Phases

| Phase | Secret Storage |
|---|---|
| II (Local dev) | `.env` file |
| III (HuggingFace) | HF Secrets |
| IV (Minikube) | Helm `values-local.yaml` + K8s Secrets |
| V (Cloud K8s) | K8s Secrets / Dapr Secrets Store |

---

## 10. Acceptance Criteria

```gherkin
Feature: User Authentication

  # --- SIGNUP ---
  Scenario: Successful signup
    When I POST /api/auth/signup with name="Test" email="test@example.com" password="password123"
    Then status is 200
    And response contains non-empty "token" string
    And response.user contains "id" (UUID), "email", "name"
    And a user record exists in database with sha256-hashed password
    And the token decodes to { user_id: <uuid>, email: "test@example.com" }

  Scenario: Duplicate email
    Given "test@example.com" exists in database
    When I POST /api/auth/signup with email="test@example.com"
    Then status is 400
    And detail is "Email already registered"

  Scenario: Short password
    When I POST /api/auth/signup with password="short"
    Then status is 422 (Pydantic validation)

  # --- SIGNIN ---
  Scenario: Successful signin
    Given user exists with email="test@example.com" password_hash=sha256("password123")
    When I POST /api/auth/signin with email="test@example.com" password="password123"
    Then status is 200
    And response contains valid JWT

  Scenario: Wrong password
    When I POST /api/auth/signin with correct email but wrong password
    Then status is 401
    And detail is "Invalid email or password"

  Scenario: Non-existent email
    When I POST /api/auth/signin with email="ghost@example.com"
    Then status is 401
    And detail is "Invalid email or password" (same message — no enumeration)

  # --- TOKEN VERIFICATION ---
  Scenario: Valid token accepted
    Given valid JWT for user_id "abc-123"
    When I GET /api/abc-123/tasks with Authorization: Bearer <token>
    Then request proceeds normally (200)

  Scenario: Expired token
    Given JWT with exp in the past
    When I call any protected endpoint
    Then status is 401 and detail is "Token expired. Please login again."

  Scenario: Missing token
    When I GET /api/{user_id}/tasks without Authorization header
    Then status is 401

  # --- USER ISOLATION ---
  Scenario: Cross-user blocked
    Given JWT for user_id "user-A"
    When I GET /api/user-B/tasks
    Then status is 403 and detail is "Cannot access other users' tasks"

  # --- FRONTEND ---
  Scenario: Token stored on login
    When I successfully sign in
    Then localStorage contains auth_token, user_id, user_email, user_name
    And document.cookie contains auth_token with max-age=604800

  Scenario: Auto-redirect on 401
    Given my token has expired
    When any API call returns 401
    Then localStorage is cleared
    And I am redirected to /auth/signin

  Scenario: Client-side password validation (signup)
    When password.length < 8 on signup form
    Then error "Password must be at least 8 characters" shown
    And form is NOT submitted to backend

  Scenario: Client-side password match validation
    When password !== confirmPassword on signup form
    Then error "Passwords do not match" shown
    And form is NOT submitted to backend
```

---

## Related Specs

- `specs/database/schema.md` — Users table definition (id, email, name, password_hash)
- `specs/features/task-crud.md` — Protected endpoints that depend on auth
- `specs/api/rest-endpoints.md` — Full endpoint documentation including auth routes
- `specs/ui/design.md` — Signin/Signup page visual design

---

## Revision History

| Date | Change | Author |
|---|---|---|
| 2025-12-29 | Initial draft | spec-kit |
| 2026-02-10 | Complete rewrite: aligned to Phase 2 source code; added flow diagrams, step-by-step processes, JWT lifecycle, token refresh strategy, frontend middleware analysis, security threat table with severity, production upgrade paths | claude-code |
