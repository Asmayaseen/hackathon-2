# Evolution Todo Monorepo

Welcome to the Evolution Todo project. This repository is organized as a production-ready monorepo containing multiple implementation phases.

## 📁 Repository Structure

- **[phase-1/](./phase-1)**: Advanced Python CLI Application (In-memory).
- **[phase-2/](./phase-2)**: Full-Stack Web Application (FastAPI + Next.js).
  - **[frontend/](./phase-2/frontend)**: Next.js 16 Web UI.
  - **[backend/](./phase-2/backend)**: FastAPI REST API.
- **[specs/](./specs)**: Shared architectural and feature specifications.

## 🚀 Quick Start (Phase 2)

### Prerequisites
- Node.js 18+ & npm
- Python 3.12+ & [uv](https://docs.astral.sh/uv/)
- Vercel CLI (`npm install -g vercel`)

### Local Development
```bash
# Install dependencies
npm install

# Run Frontend
npm run dev:frontend

# Run Backend
npm run dev:backend
```

## ☁️ Deployment (Vercel)

This monorepo is optimized for seamless deployment on Vercel.

### 1. Configure Environment
Copy the example environment files and fill in your credentials (including your Neon PostgreSQL `DATABASE_URL`):
- `phase-2/frontend/.env.example` -> `.env.local`
- `phase-2/backend/.env.example` -> `.env`

### 2. Deploy via CLI
```bash
# Standard deployment
vercel

# Production deployment
vercel --prod
```

### 3. Vercel Dashboard Settings
Ensure you add the following Environment Variables in the Vercel Dashboard:
- `DATABASE_URL`: Your Neon PostgreSQL connection string.
- `BETTER_AUTH_SECRET`: Secret for authentication.
- `JWT_SECRET`: Secret for token signing.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
