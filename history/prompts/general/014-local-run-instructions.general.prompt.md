---
ID: 014
TITLE: Local run instructions for monorepo
STAGE: general
DATE_ISO: 2026-01-04
SURFACE: agent
MODEL: claude-sonnet-4.5-20250929
FEATURE: none
BRANCH: 1-phase2-advanced-features
USER: default
COMMAND: localhost run karo
LABELS: ["devops", "local-development", "monorepo"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
  - none
TESTS_YAML:
  - none
---

## Prompt
localhost run karo

## Response
I've explored the codebase and identified the commands to run both the FastAPI backend and Next.js frontend.

### 1. Backend (FastAPI)
- Directory: `phase-2/backend`
- Port: 8000
- Command: `uvicorn main:app --reload --port 8000`

### 2. Frontend (Next.js)
- Directory: `phase-2/frontend`
- Port: 3000
- Command: `npm run dev`

I provided the user with step-by-step instructions to start both services in separate terminals.

## Outcome
The user was informed how to run the application locally in the monorepo structure.
