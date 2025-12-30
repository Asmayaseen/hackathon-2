# Research - Phase II: Full-Stack Web Application

## Decision: Better Auth + FastAPI JWT Sharing
- **Rationale**: Better Auth handles the frontend authentication UI and session management. By sharing the `JWT_SECRET` (min 32 chars), the FastAPI backend can stateless-ly verify tokens issued by the frontend.
- **Alternatives**: Custom auth on backend (too slow for hackathon), Clerk (external dependency).

## Decision: Neon Serverless PostgreSQL
- **Rationale**: Provides a free tier with connection pooling and SSL support. Perfect for serverless deployments on Vercel.
- **Alternatives**: Supabase (complex auth overlap), Local DB (not cloud-ready).

## Decision: Hugging Face Spaces for Backend
- **Rationale**: Docker SDK allows full control over the FastAPI environment. Port 7860 is required for internal routing.
- **Alternatives**: Railway (paid tier often required for high uptime).
