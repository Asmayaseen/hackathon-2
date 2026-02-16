# Backend AI Guardian Rules

These rules govern all AI-assisted backend development across phases 2-5. Every code change, review, and generation must comply.

## Stack

- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy core underneath)
- **Database**: Neon Serverless PostgreSQL
- **Auth**: PyJWT (HS256), password hashing
- **Validation**: Pydantic v2
- **Migrations**: Alembic (phase-4+), manual scripts (phase-2/3)
- **Events**: Dapr Pub/Sub over Kafka (phase-5)
- **Logging**: `python-json-logger` structured JSON (phase-4+)
- **Package manager**: UV preferred, pip fallback

## Folder Structure Rules

```
backend/
├── main.py                 # App factory, CORS, lifespan, router registration
├── db.py                   # Engine + get_session dependency (single source)
├── models.py               # ALL SQLModel table models (single file)
├── routes/                 # One file per domain, each exports `router`
│   ├── auth.py
│   ├── tasks.py
│   ├── stats.py
│   ├── search.py
│   ├── history.py
│   ├── notifications.py
│   ├── preferences.py
│   ├── bulk.py
│   ├── recurrence.py
│   ├── export_import.py
│   ├── chat.py             # Phase 3+
│   ├── voice.py            # Phase 3+
│   ├── events.py           # Phase 5 (Dapr subscriptions)
│   └── cron_handlers.py    # Phase 5 (Dapr cron bindings)
├── middleware/
│   └── auth.py             # verify_token dependency
├── schemas/                # Phase 4+: separate request/response models
│   ├── task.py
│   ├── user.py
│   └── common.py
├── services/               # Phase 4+: external service clients (Dapr, etc.)
├── events/                 # Phase 5: publisher + event schemas
│   ├── publisher.py
│   └── schemas.py
├── monitoring/             # Phase 4+: logging config + middleware
│   ├── logging_config.py
│   └── middleware.py
├── migrations/             # Hand-written migration scripts
├── alembic/                # Phase 4+: Alembic migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py         # Fixtures: test client, DB setup, auth helpers
│   ├── api/                # Endpoint tests
│   ├── unit/               # Pure function tests
│   └── integration/        # Cross-service tests
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Structure Constraints

- **One router per domain file** in `routes/`. Never put unrelated endpoints in the same file.
- **All SQLModel table classes** live in `models.py`. No model definitions in route files.
- **Request/response Pydantic models** may be co-located in the route file for phase-2/3 but MUST move to `schemas/` in phase-4+.
- **Database engine and `get_session`** live only in `db.py`. Never create engines elsewhere.
- **No circular imports.** Routes import from `models`, `db`, `middleware` -- never the reverse.

## API Design Rules

### Routing

- All routes MUST be under the `/api/` prefix.
- Auth routes: `/api/auth/signup`, `/api/auth/signin`.
- Resource routes: `/api/{user_id}/tasks`, `/api/{user_id}/tasks/{task_id}`.
- Use `APIRouter(prefix="/api", tags=["domain"])` or `APIRouter(prefix="/api/auth", tags=["auth"])`.

### HTTP Methods

| Operation | Method | Path | Success Code |
|-----------|--------|------|--------------|
| List | GET | `/api/{user_id}/tasks` | 200 |
| Create | POST | `/api/{user_id}/tasks` | 201 |
| Read | GET | `/api/{user_id}/tasks/{id}` | 200 |
| Update | PUT | `/api/{user_id}/tasks/{id}` | 200 |
| Delete | DELETE | `/api/{user_id}/tasks/{id}` | 204 |
| Bulk ops | POST | `/api/{user_id}/tasks/bulk/*` | 200 |
| Search | GET | `/api/{user_id}/tasks/search` | 200 |

### Response Envelope

- Success: return Pydantic model directly (FastAPI serializes).
- List endpoints: return `{ "tasks": [...], "total": N, "page": N, "page_size": N, "has_next": bool }`.
- Errors: raise `HTTPException` with `status_code` and `detail` string.
- NEVER return raw dicts from endpoints; always use a Pydantic `BaseModel` or `response_model`.

### Status Codes

- Use `from fastapi import status` constants (`status.HTTP_201_CREATED`, etc.).
- 400: bad request / validation (Pydantic handles 422 automatically).
- 401: missing or invalid JWT.
- 403: user_id mismatch (attempting to access another user's data).
- 404: resource not found.
- 409: conflict (duplicate email on signup).
- 500: unhandled errors (caught by global exception handler).

### Query Parameters

- Filtering: `?completed=true`, `?priority=high`, `?tags=work,urgent`.
- Sorting: `?sort_by=created_at&sort_order=desc`.
- Pagination: `?page=1&page_size=20` (max page_size=100).
- Date range: `?due_before=2026-02-01&due_after=2026-01-01`.
- Use `Query()` with validation: `page: int = Query(1, ge=1)`.

### Versioning

- Current: no URL-based version prefix (v1 is implicit).
- When a breaking change is needed, add `/api/v2/` routes in new files under `routes/v2/`.
- NEVER modify existing response shapes for shipped endpoints. Add new fields, don't remove or rename.

## Auth Enforcement Rules

### JWT Middleware

- `middleware/auth.py` exports `verify_token` as a FastAPI dependency.
- Every protected route MUST include `user_id: str = Depends(verify_token)`.
- `verify_token` decodes the Bearer token and returns `user_id` from the payload.
- Token payload: `{ "user_id": str, "email": str, "exp": datetime, "iat": datetime }`.

### User Isolation (Critical)

- Every data-access route MUST verify that the URL `{user_id}` matches the JWT `user_id`.
- Pattern:
  ```python
  @router.get("/api/{user_id}/tasks")
  async def get_tasks(
      user_id: str,
      authenticated_user_id: str = Depends(verify_token),
      session: Session = Depends(get_session)
  ):
      if user_id != authenticated_user_id:
          raise HTTPException(status_code=403, detail="Access denied")
  ```
- NEVER skip this check. Cross-user data access is a critical security violation.

### Auth Endpoint Security

- Password hashing: use `passlib[bcrypt]` or `hashlib.sha256` (current). Bcrypt preferred for new code.
- JWT secret: read from `JWT_SECRET` env var. Minimum 32 characters.
- Token expiry: 7 days (`JWT_EXPIRATION_HOURS = 168`).
- NEVER log tokens, passwords, or password hashes.
- NEVER include the JWT secret as a default value in production code.

## Database & ORM Rules

### SQLModel Conventions

- All table models inherit `SQLModel` with `table=True`.
- Explicit `__tablename__` on every model.
- Use `Field()` for all columns: `Field(primary_key=True)`, `Field(foreign_key="users.id")`, `Field(index=True)`.
- JSON columns: `sa_column=Column(JSON)` (e.g., tags).
- Enums: define as `str, Enum` classes, store as string in DB.
- `Optional[int] = Field(default=None, primary_key=True)` for auto-increment PKs.
- `datetime = Field(default_factory=datetime.utcnow)` for timestamps.

### Session Management

- Use `get_session` dependency from `db.py` (context manager yields `Session`).
- NEVER create sessions manually in route handlers.
- Use `session.add()` + `session.commit()` + `session.refresh()` for writes.
- Use `select(Model).where(...)` for reads. Never raw SQL unless unavoidable.
- Keep session scope tight: fetch, transform, commit, return. No open sessions across await boundaries.

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    echo=False,            # True only in dev
    pool_pre_ping=True,    # Reconnect stale connections
    pool_size=10,
    max_overflow=20
)
```

- `echo=True` is acceptable in development. MUST be `False` in production/container builds.
- `pool_pre_ping=True` is required for Neon (serverless connections may idle-disconnect).

### Query Patterns

- Always scope queries by `user_id`: `select(Task).where(Task.user_id == user_id)`.
- Use `.offset()` and `.limit()` for pagination. Never fetch unbounded result sets.
- For count queries: `select(func.count()).select_from(Task).where(...)`.
- Add `index=True` to any column used in WHERE or ORDER BY clauses.

## Migration Discipline

### Phase 2-3: Manual Migrations

- `migrate.py`: destructive reset (DROP + CREATE). Development only.
- `migrations/*.py`: incremental schema changes with raw SQL.
- Always include a rollback section (commented or in separate function).

### Phase 4+: Alembic

- Config in `alembic.ini`, env in `alembic/env.py`.
- `target_metadata = SQLModel.metadata` (auto-imports all models).
- Version files in `alembic/versions/` with descriptive names: `YYYY_MM_DD_HHMM-NNN_description.py`.
- Commands:
  ```bash
  alembic revision --autogenerate -m "add_field_x_to_tasks"
  alembic upgrade head
  alembic downgrade -1
  ```
- NEVER use `--autogenerate` blindly. Always review the generated migration.
- Every migration MUST have both `upgrade()` and `downgrade()` functions.
- NEVER use `DROP TABLE` in production migrations. Use `ALTER TABLE` or create new tables.
- Test migrations against a staging database before production.

### Migration Safety Checklist

- [ ] `downgrade()` reverses the `upgrade()` exactly.
- [ ] No data loss (columns dropped only after data is migrated).
- [ ] Indexes added for new query patterns.
- [ ] Nullable columns or defaults for new required fields.
- [ ] Migration tested locally with `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`.

## Error Handling Standards

### Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

- NEVER expose internal error messages, stack traces, or database errors to clients in production.
- The global handler MUST include CORS headers if the frontend relies on them for error responses.
- Log the full traceback server-side at ERROR level.

### Route-Level Error Handling

- Use specific `HTTPException` with meaningful `detail` strings.
- Catch database errors (`IntegrityError`, `OperationalError`) and convert to 400/409/500.
- Pattern:
  ```python
  task = session.get(Task, task_id)
  if not task:
      raise HTTPException(status_code=404, detail="Task not found")
  if task.user_id != user_id:
      raise HTTPException(status_code=403, detail="Access denied")
  ```

### Error Response Format

All errors MUST return JSON:
```json
{ "detail": "Human-readable error message" }
```

For validation errors (automatic from Pydantic):
```json
{ "detail": [{ "loc": ["body", "title"], "msg": "field required", "type": "value_error.missing" }] }
```

## Logging & Observability

### Structured Logging (Phase 4+)

- Use `monitoring/logging_config.py` for setup: JSON format in containers, plain text in dev.
- Get loggers via `logging.getLogger(__name__)` -- never `print()` in production code.
- Log levels:
  - `DEBUG`: SQL queries, request payloads (dev only).
  - `INFO`: request started/completed, business events, startup.
  - `WARNING`: non-critical failures (Dapr unavailable, deprecated usage).
  - `ERROR`: unhandled exceptions, database failures, auth failures.
  - `CRITICAL`: startup failures, missing required config.

### Request Logging Middleware

- `monitoring/middleware.py` adds `X-Request-ID` correlation header.
- Skip logging for health check paths: `/health`, `/ready`, `/metrics`.
- Log: method, path, status code, duration_ms, request_id.
- Use `extra={}` dict for structured fields, not string interpolation.

### What to Log

- Auth failures (invalid token, user mismatch) at WARNING.
- CRUD operations at INFO (event type + resource ID, not full payload).
- External service calls (Dapr, AI APIs) at INFO with duration.
- Database errors at ERROR with sanitized query context.

### What NEVER to Log

- Passwords, password hashes, JWT tokens, API keys.
- Full request/response bodies in production (use DEBUG only).
- PII beyond user_id (no emails, names in structured logs).

## Performance Constraints

### Response Time Targets

- CRUD endpoints: < 200ms p95.
- Search endpoints: < 500ms p95.
- AI/chat endpoints: < 5s p95 (LLM latency).
- Health checks: < 50ms.

### Database

- Connection pool: 10 base + 20 overflow.
- Use `pool_pre_ping=True` for serverless DB.
- Index all foreign keys and frequently filtered columns.
- Paginate all list endpoints (max 100 items per page).
- NEVER use `SELECT *` equivalent without pagination.

### Background Tasks

- Event publishing (Dapr/Kafka) MUST be fire-and-forget: never block the request.
- Use `asyncio.create_task()` or FastAPI `BackgroundTasks` for async side effects.
- Set timeouts on all external HTTP calls: `timeout=5.0` for Dapr, `timeout=30.0` for AI APIs.

### Startup

- `create_db_and_tables()` runs on startup via lifespan/`on_event("startup")`.
- Health check (`/health`) returns immediately without DB call.
- Readiness check (`/ready`) verifies DB connectivity with `SELECT 1`.

## Security Constraints

### CORS

- Allowed origins from `CORS_ORIGINS` env var (comma-separated).
- Default to `http://localhost:3000` for local dev.
- NEVER use `allow_origins=["*"]` in production.
- `allow_credentials=True` is required for JWT cookie flows.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes | JWT signing key (min 32 chars) |
| `CORS_ORIGINS` | Yes | Allowed frontend origins |
| `GROQ_API_KEY` | Phase 3+ | AI chat API key |
| `DAPR_HTTP_PORT` | Phase 5 | Dapr sidecar port (default 3500) |
| `DAPR_PUBSUB_NAME` | Phase 5 | Pub/Sub component name |
| `LOG_LEVEL` | No | Logging level (default INFO) |
| `SERVICE_NAME` | No | Service identifier for logs |

- NEVER commit `.env` files. Only `.env.example` with placeholder values.
- Fail fast on startup if required env vars are missing (`raise ValueError`).

### Input Validation

- All request bodies MUST use Pydantic `BaseModel` with field constraints.
- String fields: `min_length`, `max_length`.
- Enum fields: `pattern` regex or Pydantic `Literal`/`Enum`.
- Numeric fields: `ge`, `le`, `gt`, `lt` where applicable.
- NEVER trust client-provided `user_id` -- always verify against JWT.
- NEVER use f-strings to build SQL. Always use parameterized queries via SQLModel/SQLAlchemy.

### Dependency Security

- Pin all dependencies in `requirements.txt` with minimum versions.
- Use `--no-cache-dir` in Dockerfile pip install.
- Prefer slim base images: `python:3.12-slim`.

## Testing Requirements

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── api/                 # Endpoint integration tests
│   ├── test_auth.py
│   ├── test_tasks.py
│   ├── test_health.py
│   └── test_chat.py
├── unit/                # Pure function tests
│   └── test_agent.py
└── integration/         # Cross-service tests
    └── test_mcp_server.py
```

### Fixtures

- `conftest.py` sets `ENVIRONMENT=test` and `LOG_LEVEL=WARNING` BEFORE imports.
- `setup_database` fixture: `scope="session"`, creates tables, cleans up after.
- `test_client` fixture: `scope="session"`, returns `TestClient(app)`.
- `auth_headers` fixture: registers a test user, logs in, returns `{"Authorization": "Bearer <token>"}`.

### What to Test

- Every endpoint: auth required (401 without token).
- CRUD: create, read, update, delete with valid data.
- Validation: missing required fields (422), invalid values.
- Authorization: user isolation (403 when accessing another user's data).
- Edge cases: empty lists, not found (404), duplicate entries (409).
- Pagination: page boundaries, sort order.

### Test Commands

```bash
pytest tests/ -v                    # Run all tests
pytest tests/api/ -v                # API tests only
pytest tests/unit/ -v               # Unit tests only
pytest tests/ -v --tb=short -q      # Concise output
```

### Test Naming

- Files: `test_<domain>.py`.
- Classes: `TestTaskEndpoints`, `TestTaskEndpointsWithAuth`.
- Methods: `test_<action>_<condition>` (e.g., `test_get_tasks_requires_auth`).

## Event-Driven Patterns (Phase 5)

### Event Publishing

- Events are published via Dapr Pub/Sub HTTP API (not direct Kafka client).
- Publisher in `events/publisher.py`, schemas in `events/schemas.py`.
- Topics: `task-events`, `reminders`, `task-updates`.
- Publishing MUST be fire-and-forget: wrap in `asyncio.create_task()`.
- If Dapr sidecar is unavailable, log a warning and continue (graceful degradation).

### Event Schemas

- All events use Pydantic `BaseModel`.
- Include: `event_type`, `task_id`, `user_id`, `timestamp`.
- Datetime fields serialized as ISO 8601 strings.

### Subscription Endpoints

- Dapr subscription discovery: `GET /dapr/subscribe` returns topic-to-route mapping.
- Event handler routes: `POST /api/events/{topic}` parse CloudEvents format.

## Commands

```bash
# Development
uvicorn main:app --reload --port 8000

# Production (container)
uvicorn main:app --host 0.0.0.0 --port 7860

# Tests
pytest tests/ -v

# Migrations (phase 4+)
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Linting
ruff check .
ruff format .
```

## Spec References

- API Endpoints: `specs/api/rest-endpoints.md`
- Database Schema: `specs/database/schema.md`
- Authentication: `specs/features/authentication.md`
- Task CRUD: `specs/features/task-crud.md`
- Phase 5 Events: `specs/phase-5/spec.md`
