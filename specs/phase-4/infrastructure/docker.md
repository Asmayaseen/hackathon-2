# Infrastructure Specification: Docker Containerization

**Phase**: 4 - Local Kubernetes Deployment
**Created**: 2026-01-18
**Status**: Complete

## Overview

Docker containerization specifications for frontend and backend services.

## Backend Dockerfile

### Requirements

| Requirement | Specification |
|-------------|---------------|
| Base Image | Python 3.12 slim |
| Package Manager | UV (fast Python package installer) |
| Exposed Port | 8000 |
| Entry Point | Uvicorn ASGI server |

### Build Stages

1. **Single Stage Build** (development/local):
   - Install system dependencies (gcc, curl)
   - Install UV package manager
   - Copy dependency files (pyproject.toml, requirements.txt)
   - Install Python dependencies
   - Copy application code
   - Run uvicorn

### Environment Variables

| Variable | Purpose |
|----------|---------|
| HOST | Bind address (0.0.0.0) |
| PORT | Server port (8000) |
| DATABASE_URL | Neon PostgreSQL connection |
| OPENAI_API_KEY | OpenAI API access |
| BETTER_AUTH_SECRET | JWT signing secret |

### Build Command

```bash
docker build -t todo-backend:latest ./backend
```

---

## Frontend Dockerfile

### Requirements

| Requirement | Specification |
|-------------|---------------|
| Base Image | Node 20 slim |
| Build Tool | npm |
| Exposed Port | 3000 |
| Entry Point | Node standalone server |

### Build Stages

1. **Builder Stage**:
   - Install build dependencies (python3, make, g++)
   - Install npm dependencies
   - Build Next.js application

2. **Runner Stage**:
   - Copy built artifacts
   - Run as non-root user (nextjs:nodejs)
   - Execute standalone server

### Environment Variables

| Variable | Purpose |
|----------|---------|
| NODE_ENV | Environment (production) |
| PORT | Server port (3000) |
| NEXT_PUBLIC_API_URL | Backend API URL |

### Build Command

```bash
docker build -t todo-frontend:latest ./frontend
```

---

## Docker Compose (Local Development)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

## Acceptance Criteria

- [ ] Backend image builds successfully under 5 minutes
- [ ] Frontend image builds successfully under 5 minutes
- [ ] Backend container starts and responds on /health
- [ ] Frontend container starts and serves UI
- [ ] Images are under 500MB each (optimized)
- [ ] Containers run as non-root users
