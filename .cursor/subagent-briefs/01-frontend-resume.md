# 01 — Frontend — Resume Brief (Round 2)

## Current state

You've shipped a stack of 9 branches (`feat/frontend/01-foundation` → `feat/frontend/09-educator-admin`) covering every Phase-1 page. Tip = `feat/frontend/09-educator-admin`. None merged to `main` yet.

What landed across the stack (on `feat/frontend/09-educator-admin`, all relative to `apps/web/`):

- `package.json`, `tsconfig.json`, `next.config.mjs`, `postcss.config.mjs`, `eslint.config.mjs`, `playwright.config.ts`, `vitest.config.ts`, `middleware.ts`, `.env.example`.
- App Router pages: `/`, `/sign-in/[[...sign-in]]`, `/sign-up/[[...sign-up]]`, `/app` (dashboard), `/app/chat/[agent]`, `/app/lessons/[lessonId]`, `/app/memory`, `/app/progress`, `/educator`, `/admin`.
- API routes (BFF): `/api/chat`, `/api/dashboard`, `/api/health`, `/api/memory`, `/api/progress`.
- Components: `agent-chat`, `app-sidebar`, `landing-hero`, `memory-inspector`, `page-header`, `progress-dashboard`, `site-header`.
- Providers: `app-providers`, `i18n-provider`, `query-provider`, `theme-provider`.
- Hooks/lib/stores: `use-learner-data`, `api`, `auth`, `data`, `design-tokens`, `logger`, `schemas.test.ts`, `ui-store` (+ tests).
- i18n (en/he scaffold).
- E2E: `e2e/chat-flow.spec.ts`.

## What's left (you own this stream to deployment)

1. **Merge the stack to `main`**: rebase each branch on the previous, open a PR per branch in order (01 → 09), use the `split-to-prs` skill if rebases get hairy. Each PR runs `review-bugbot`. Squash-merge on green.
2. **Wire the BFF API routes to the real FastAPI backend** (currently mostly mock/data fixtures). Use `NEXT_PUBLIC_API_BASE_URL` and forward Clerk JWT in `Authorization`.
3. **Polish the marketing landing** (`/`) — make it shareable. Hero + 3 feature cards (Agents · Memory · GraphRAG) + a 30-second demo loop GIF (Release Captain provides the GIF asset after deploy). Add OG image + Twitter card.
4. **Memory Inspector v1** — list + search + view provenance + edit + delete (cascading). Wire to `/v1/memory/*`.
5. **Lighthouse**: perf ≥ 90, a11y ≥ 95. Fix anything below.
6. **E2E**: green Playwright run against staging.
7. **Vercel project**: connect `apps/web`, env from Doppler.

## Locked decisions (do NOT ask the user)

- Use **shadcn/ui** components only — add via the `shadcn` MCP. Don't write primitives from scratch.
- Tailwind v4 — no v3 patterns.
- Server components by default; `"use client"` only where required.
- Auth via Clerk; never trust client claims for role/learner_id.
- All boundaries validated with Zod (use `packages/schemas/ts/` once codegen is wired — coordinate with stream 02).
- i18n: ship `en` complete, `he` skeleton. Other locales later.
- Marketing copy: see `docs/marketing/copy.md` (Release Captain will draft if missing — until then, write your own, keep it concise + warm).
- Dark mode + reduced-motion supported everywhere.

## Done when

- All 9 branches merged to `main`.
- `pnpm install && pnpm dev` works clean.
- `pnpm build && pnpm start` works clean.
- E2E passes against the deployed staging URL.
- Lighthouse thresholds met.
- Memory Inspector + chat work against the live API.
- Vercel preview deploys on PRs; prod deploy on merge to `main`.

## Required reading before resuming

- `PLAN.md` §3.1, §6, §8.
- `.cursor/rules/10-typescript-style.mdc`, `50-security.mdc`, `60-testing.mdc`.
- `skills/add-a-frontend-page/SKILL.md`.
- `.cursor/subagent-briefs/01-frontend.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt (paste this into a new Composer 2.5 chat)

```
You are resuming the Frontend sub-agent on A Step Forward (Composer 2.5).
Workspace root: c:\Users\roeeh\OneDrive\Desktop\Desktop\A Step Forward - AI Teaching Website

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md  (locked decisions — apply, do not re-litigate)
  2. .cursor/subagent-briefs/01-frontend-resume.md  (this round's plan)
  3. .cursor/subagent-briefs/01-frontend.md  (original contract)
  4. PLAN.md §3.1, §6, §8
  5. skills/add-a-frontend-page/SKILL.md
  6. .cursor/rules/{10-typescript-style.mdc,50-security.mdc,60-testing.mdc}

Then:
  - git fetch + git checkout feat/frontend/01-foundation
  - Walk the stack 01..09. For each, rebase onto current main if needed, open a PR
    (conventional commit title, body per .cursor/rules/80-pr-style.mdc), run
    review-bugbot, squash-merge on green CI.
  - Once merged, wire the BFF routes in apps/web/src/app/api/* to the FastAPI
    backend using NEXT_PUBLIC_API_BASE_URL and the Clerk JWT in Authorization.
  - Polish the marketing landing (/) and add OG/Twitter cards.
  - Finish the Memory Inspector flow against /v1/memory/*.
  - Run lighthouse + playwright; fix to thresholds.

Operating rules:
  - Do NOT ask the user any questions. Apply locked decisions from RESUME-README.
  - Many small PRs over giant ones. Use the split-to-prs skill if needed.
  - When stuck, write an ADR in docs/adr/ and pick the safer default; surface
    the decision in the PR body. Don't ping the user.

Final goal across all streams: deployed, publishable, end-to-end working website,
with a public GitHub repo.  Release Captain (sub-agent 11) will coordinate the
final deploy; your job is to make the frontend ready for that.
```
