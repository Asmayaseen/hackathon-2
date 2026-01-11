---
title: Evolution Todo API
emoji: ✅
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# Evolution Todo API

FastAPI backend for Evolution Todo application - A cyberpunk-themed task management system.

## Features

- 🔐 JWT Authentication (signup/signin)
- ✅ Full CRUD operations for tasks
- 🗄️ PostgreSQL database with SQLModel
- 🔒 Secure password hashing with bcrypt
- 🌐 CORS-enabled for frontend integration
- 🤖 AI Chatbot with OpenAI Agents SDK
- 🎤 Voice transcription (English + Pakistani Urdu)
- 🛠️ MCP Tools for task management (12 tools)
- 🗣️ Multi-language support (English + Urdu, Hindi rejected)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user

### Tasks
- `GET /api/{user_id}/tasks` - Get all tasks (with status filter)
- `GET /api/{user_id}/tasks/{task_id}` - Get single task
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

## Environment Variables

Required in Hugging Face Space Secrets:

```
DATABASE_URL=postgresql://user:password@host:port/dbname?sslmode=require
JWT_SECRET=your_secure_random_secret_key
CORS_ORIGINS=https://frontend-zto4odyj8-asma-yaseens-projects.vercel.app,http://localhost:3000
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

## Tech Stack

- **Framework:** FastAPI 0.115+
- **Database:** PostgreSQL with SQLModel
- **Auth:** JWT + bcrypt
- **Server:** Uvicorn
- **Container:** Docker

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run server
uvicorn main:app --reload --port 7860
```

## Deployment

This Space automatically deploys from the Dockerfile. Make sure to set the required secrets in Space settings.

---

Built with ❤️ for Hugging Face Spaces

<!-- Rebuild triggered: 2026-01-11 - Phase 3 Complete: Voice + AI Chat + Language Support (English + Urdu) -->
