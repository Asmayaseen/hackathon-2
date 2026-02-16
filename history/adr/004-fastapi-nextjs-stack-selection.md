# ADR-004: FastAPI + Next.js as Core Application Stack

**Status**: Accepted
**Date**: 2026-02-11
**Decision Makers**: asmayaseen (compliance with hackathon mandate)
**Context**: Phase II full-stack technology selection

## Context

The Evolution Todo project required a full-stack web application in Phase II, replacing the Phase I Python console app. The hackathon (Panaversity PIAIC/GIAIC "Evolution of Todo") mandated specific technologies to ensure consistent evaluation across participants and hands-on experience with a modern AI-native, cloud-native stack.

The core question: which frontend framework, backend framework, ORM, and database should power the multi-phase application across Phases II-V (web app, AI chatbot, Kubernetes deployment, cloud-native event-driven architecture)?

### Constraints

- Hackathon constitution (Principle III: Technology Stack Adherence) declares the stack **mandatory and MUST NOT be substituted**.
- The stack must support progressive enhancement: basic CRUD (Phase II) through event-driven microservices (Phase V).
- Frontend and backend must communicate via REST with JWT authentication.
- The database must be serverless-compatible for zero-ops deployment.

## Decision

Use the mandated stack:

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) | 16+ |
| Backend | Python FastAPI | 0.115+ |
| ORM | SQLModel | 0.0.31+ |
| Database | Neon Serverless PostgreSQL | - |
| Auth | JWT (PyJWT, HS256) | - |
| Styling | Tailwind CSS + shadcn/ui | 4.x |
| Animations | Framer Motion | - |

## Alternatives Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **FastAPI + Next.js (chosen)** | Async Python, auto-docs (OpenAPI), App Router SSR/RSC, SQLModel = Pydantic + SQLAlchemy, Neon = zero-ops PG | Two languages (Python + TypeScript), SQLModel less mature than Django ORM | Mandated; also the strongest fit for AI workloads |
| Django + React (CRA/Vite) | Mature ORM, admin panel, large ecosystem | Synchronous by default, no built-in OpenAPI, React CRA deprecated | Not mandated; Django's sync model is a poor fit for AI streaming |
| Express.js + Next.js (full JS) | Single language, shared types, tRPC possible | No built-in validation, weaker AI/ML ecosystem, no SQLModel equivalent | Not mandated; Python required for MCP SDK and Agents SDK |
| Flask + Next.js | Lightweight, familiar | No async, no auto-validation, no OpenAPI, manual everything | Flask lacks the structure needed for 10+ route files |

### Why This Stack Fits the Project

1. **FastAPI + Pydantic**: automatic request/response validation, OpenAPI docs, async support for AI streaming (Phase III chat), and native compatibility with OpenAI/MCP Python SDKs.
2. **SQLModel**: combines Pydantic validation with SQLAlchemy ORM in a single model definition, eliminating schema duplication between API and DB layers.
3. **Next.js App Router**: server-side rendering, file-based routing, React Server Components, and first-class Vercel deployment for the frontend.
4. **Neon PostgreSQL**: serverless auto-scaling, connection pooling, branching for dev/staging, and zero-ops in production. `pool_pre_ping=True` handles idle disconnections.
5. **Progressive enhancement**: FastAPI's `APIRouter` pattern scales from 2 routes (Phase II) to 14 routers (Phase V) without structural changes. Next.js App Router scales similarly.

## Consequences

### Positive

- **Single model definition**: SQLModel classes serve as both Pydantic schemas and ORM models, reducing boilerplate.
- **Auto-generated API docs**: FastAPI produces OpenAPI 3.1 documentation without manual effort.
- **AI-native**: Python backend runs MCP server, OpenAI Agents SDK, and Whisper transcription in-process.
- **K8s-ready**: Stateless FastAPI + Neon (external DB) = horizontally scalable pods with no session affinity.
- **Deployment simplicity**: Frontend deploys to Vercel (zero-config), backend to any container runtime.

### Negative

- **Two-language codebase**: Python backend and TypeScript frontend require context-switching and separate CI pipelines.
- **SQLModel maturity**: fewer resources and community patterns compared to Django ORM or raw SQLAlchemy.
- **Neon cold starts**: serverless database has occasional latency spikes on first connection after idle period (mitigated by `pool_pre_ping`).

### Risks

- SQLModel does not support Alembic autogenerate perfectly for all column types (JSON, Enum). Manual migration review is required.
- Next.js 16 introduced breaking changes (async params, Turbopack default) that affect upgrade paths.

## Related

- Constitution: `.specify/memory/constitution.md` (Principle III)
- Hackathon requirements: `hackathon.md` (Phase II stack table)
- Specs overview: `specs/overview.md`
- Backend structure: `phase-2/backend/main.py`, `phase-2/backend/models.py`
- Frontend structure: `phase-2/frontend/src/app/layout.tsx`
