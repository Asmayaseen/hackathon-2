# Frontend Guidelines (Phase II)

## Stack
- Next.js 16 (App Router)
- TypeScript
- Tailwind CSS 4.x
- next-themes (dark/light mode)
- axios (API client)
- Framer Motion (animations)

## Project Structure
- `/src/app/` — Pages and layouts (App Router)
- `/src/app/auth/` — Signin and Signup pages
- `/src/app/tasks/` — Task management page
- `/src/app/dashboard/` — Dashboard with stats
- `/src/app/settings/` — User preferences
- `/src/components/` — Reusable UI components
- `/src/lib/api.ts` — Backend API client (axios)
- `/src/hooks/` — Custom React hooks
- `/middleware.ts` — Next.js edge middleware

## Patterns
- Use client components (`'use client'`) for all interactive pages
- All backend calls go through `/src/lib/api.ts`
- JWT token stored in `localStorage.auth_token`
- Token attached to every request via axios interceptor
- 401 responses trigger auto-redirect to `/auth/signin`

## Styling
- Tailwind CSS classes only — no inline styles
- Dark theme: glassmorphism cards, cyan/fuchsia neon accents
- Light theme: clean white cards with subtle shadows
- Responsive: mobile-first, breakpoints at `sm:` (640px)
- See `specs/ui/design.md` for full design system

## API Client Usage
```typescript
import { api } from '@/lib/api';

// Auth
const response = await api.signin(email, password);
const response = await api.signup(name, email, password);

// Tasks
const tasks = await api.getTasks(userId, { status: 'pending' });
await api.createTask(userId, { title: 'Buy milk' });
await api.updateTask(userId, taskId, { completed: true });
await api.deleteTask(userId, taskId);
```

## Environment Variables
- `NEXT_PUBLIC_API_URL` — Backend URL (default: `http://localhost:8000`)

## Commands
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
```

## Spec References
- UI Design: `specs/ui/design.md`
- Features: `specs/features/task-crud.md`
- Auth: `specs/features/authentication.md`
- API: `specs/api/rest-endpoints.md`
