# Phase 2 Quickstart

## Local Setup
1. **Root**: `npm install`
2. **Backend**: 
   - `cd phase-2/backend`
   - `uv sync`
   - Create `.env` from `.env.example`
   - `uvicorn main:app --reload`
3. **Frontend**:
   - `cd phase-2/frontend`
   - Create `.env.local` from `.env.example`
   - `npm run dev`

## Deployment
- **Frontend**: `vercel` from root.
- **Backend**: Update Docker secrets in Hugging Face with `DATABASE_URL` and `JWT_SECRET`.
