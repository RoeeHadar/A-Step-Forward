# apps/web — A Step Forward frontend

Next.js 15 (App Router, RSC) + TypeScript + Tailwind v4 + shadcn/ui + Vercel AI SDK.

## Quick start

```bash
# From repo root
pnpm install
cp apps/web/.env.example apps/web/.env.local
# Add Clerk keys to .env.local
pnpm dev
```

Open http://localhost:3000.

## Phase 1 routes

| Route | Purpose |
|-------|---------|
| `/` | Marketing landing |
| `/sign-in`, `/sign-up` | Clerk auth |
| `/app` | Learner dashboard |
| `/app/chat/[agent]` | Streaming agent chat |
| `/app/lessons/[lessonId]` | Lesson view |
| `/app/memory` | Memory Inspector |
| `/app/progress` | Progress charts |
| `/educator` | Educator dashboard (RBAC) |
| `/admin` | Admin dashboard (RBAC) |

## Scripts

```bash
pnpm lint        # ESLint
pnpm typecheck   # tsc --noEmit
pnpm test        # Vitest
pnpm e2e         # Playwright (set E2E_CLERK_* for full chat flow)
pnpm build       # Production build
```

## Architecture notes

- **RSC by default** — client islands marked with `"use client"`.
- **Zod** at every API boundary via `@asf/schemas`.
- **TanStack Query** hooks in `src/hooks/use-learner-data.ts` for client refetches.
- **Zustand** UI state in `src/stores/ui-store.ts`.
- **Mock data** in `src/lib/data.ts` when the FastAPI gateway is offline.
- **CSP** enforced in `middleware.ts` (no `unsafe-inline` for scripts).

## Required env

See `apps/web/.env.example`. Clerk keys are required for protected routes.

## Rules

- `.cursor/rules/10-typescript-style.mdc`
- `skills/add-a-frontend-page/SKILL.md`
- `.cursor/subagent-briefs/01-frontend.md`
