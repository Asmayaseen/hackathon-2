---
title: Evolution Todo API
emoji: ✅
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Evolution Todo API

RESTful API backend for the Evolution Todo application.

## Features

- User Authentication (JWT)
- Task CRUD Operations
- PostgreSQL Database (Neon)
- FastAPI Framework

## API Endpoints

- `GET /` - Health check
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `GET /users/{user_id}/tasks` - Get user tasks
- `POST /users/{user_id}/tasks` - Create task
- `PUT /users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /users/{user_id}/tasks/{task_id}` - Delete task

## Environment Variables

Set these in Hugging Face Space secrets:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `CORS_ORIGINS` - Allowed origins (comma-separated)
