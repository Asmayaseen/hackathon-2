# Quickstart: Dashboard - Task Management Interface

**Feature**: 1-dashboard
**Date**: 2025-12-29

## Prerequisites

- Node.js 18+ installed
- Python 3.13+ installed
- Neon PostgreSQL database configured
- `.env` files set up in both frontend/ and backend/

## Start Backend

```bash
cd backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Run FastAPI server
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Start Frontend

```bash
cd frontend

# Install dependencies (if needed)
npm install

# Run Next.js dev server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Test Flow

1. Open http://localhost:3000
2. Click "Get Started" or "Sign Up"
3. Create an account with name, email, password
4. You'll be redirected to /tasks (dashboard)
5. Add tasks using the form
6. Toggle completion with checkboxes
7. Use filter buttons (All/Pending/Completed)
8. Edit or delete tasks as needed

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
JWT_SECRET=your-secret-key
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Testing (curl)

### Signup

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"password123"}'
```

### Signin

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'
```

### Get Tasks

```bash
curl http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}"
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Task","description":"Optional desc"}'
```

## Troubleshooting

### Database Connection Issues

- Verify DATABASE_URL in .env
- Check Neon dashboard for connection status
- Run `python migrate.py` to reset tables if schema mismatch

### Authentication Errors

- Clear localStorage and try signin again
- Check JWT_SECRET matches between backend runs
- Verify token is being sent in Authorization header

### CORS Issues

- Ensure frontend is calling correct API URL
- Backend CORS is configured for localhost:3000
