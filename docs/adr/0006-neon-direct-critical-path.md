# ADR 0006: Neon-direct critical path

- **Status:** Proposed
- **Date:** 2026-07-05
- **Deciders:** Architecture Steward + Coordinator (pending Opus acceptance)

## Context

ADR-001 describes Render as the primary API gateway. In production today, the
learner loop (signup → onboarding → diagnostic → plan → chat → progress) runs
on **Vercel Next.js API routes** talking to **Neon Postgres** directly via
`apps/web/src/lib/neon-db.ts`. Render (`apps/api`) is optional and often cold.

Legacy routes (`/api/dashboard`, `/api/memory`) previously proxied Render and
returned empty mocks when unavailable, diverging from server-rendered pages.

## Decision

1. **Neon-direct is the system of record** for all learner-bound state on the
   free-tier critical path.
2. **Render** remains an optional accelerator for Python-only capabilities
   (LangGraph orchestrator, embeddings pipeline, Celery) — not required for
   core UX.
3. All new learner-facing reads/writes on Vercel use `neon-db.ts` (or scoped
   `neon-*.ts` siblings), not `fetch*` helpers to Render.
4. ADR-001 language is **partially superseded** by this ADR for the web tier.

## Consequences

### Positive

- Consistent data between pages and JSON APIs.
- No cold-start dependency for chat and plans.
- Simpler mental model for stream 01-frontend contributors.

### Negative

- Python services stay off the hot path until explicitly wired.
- Business logic duplicated in TypeScript until planners unify or Python moves behind stable APIs.
- `neon-db.ts` concentration risk (see assessment F5).

## Alternatives considered

- **Render-primary (status quo in ADR-001):** Rejected for free-tier reliability.
- **Immediate Render removal:** Rejected — dev sandbox and future agents still need `apps/api`.

## Verification

- `/api/dashboard` and `/api/memory` return Neon snapshots (implemented 2026-07-05).
- Chat route has no Render import.
- `scripts/verify-deploy.ps1` smoke: `/`, `/sign-in`, `/learn` green after deploy.
