# ADR-001: JWT Tokens Over Session-Based Authentication

**Status**: Accepted
**Date**: 2025-12-29
**Decision Makers**: asmayaseen
**Context**: Phase II authentication architecture

## Context

The Evolution Todo application requires multi-user authentication across a Next.js frontend and FastAPI backend. The hackathon specifies Better Auth for the frontend, but the backend is a separate Python service that needs to verify user identity.

## Decision

Use **stateless JWT (HS256)** tokens with a shared secret between frontend and backend, instead of session-based authentication with a shared session store.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **JWT (chosen)** | Stateless, no session DB, scales horizontally, self-contained | Token can't be revoked, larger payload, no refresh flow |
| Session + Redis | Revocable, smaller cookies | Requires shared Redis, adds infra complexity, statefulness |
| OAuth2 + OIDC | Industry standard, token refresh | Over-engineered for hackathon, complex setup |

## Rationale

- Hackathon scope favors simplicity over production-grade session management
- Stateless tokens align with Phase IV/V Kubernetes deployment (any pod can verify)
- 7-day expiry provides reasonable UX without refresh token complexity
- SHA256 hashing is acceptable for hackathon (would use bcrypt in production)

## Consequences

- **Positive**: No session store needed, backend verifies independently, K8s-ready
- **Negative**: No token revocation, user must wait 7 days or clear localStorage to "logout" from other devices
- **Mitigated by**: Short-enough expiry (7 days) and frontend clears tokens on logout

## Related

- `specs/features/authentication.md`
- `phase-2/backend/routes/auth.py`
- `phase-2/backend/middleware/auth.py`
