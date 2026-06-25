# Coordinator Directive — Round 4 (2026-06-25, post build-fix)

> Read this after `12-coordinator-directive.md`. This round's tasks assume the
> `fix/coordinator-round3` branch is now green on Vercel and ready to merge.

---

## Context

Branch `fix/coordinator-round3` is 6 commits ahead of `main`. ESLint + TypeScript
are clean. Vercel preview is rebuilding from `ac8e60d`. Assume it passes.

Commits on the branch (newest first):
- `ac8e60d` docs: ESLint-fails-build warning in frontend skill
- `5cb87dc` fix: remove unused `stop` from `useChat` (was the real build error)
- `fe5b02e` docs: ESM transpile post-mortem logged in skill
- `531a227` fix: ESM-only remark/rehype packages added to `transpilePackages`
- `987cbcb` fix: Bugbot findings on Round 3
- `6216a8e` feat: Round 3 — chat cold-start, /learn pipeline, /book booking

---

## P0 — Merge `fix/coordinator-round3` into `main`

Once the Vercel preview is green (check the deployment at
`a-step-forward-waij-git-fix-coordinator-round3-a-step-forward.vercel.app`):

1. Open a PR: `fix/coordinator-round3` → `main`. Title: `fix(frontend): Round 3 — chat cold-start, learn pipeline, booking page`.
2. Run the `review-bugbot` skill.
3. Address any findings, then squash-merge.
4. Confirm Render auto-deploys the new API routes (`/v1/content/*`, `/v1/bookings`).
5. Run the Alembic migration on Neon to create `content_sections`, `bagrut_exams`,
   and `bookings` tables:
   ```
   alembic upgrade head
   ```
   (This can be done by running the migration script against the Neon DATABASE_URL
   via the CI workflow or a one-shot Render job.)

---

## P1 — In-flight branch triage (do this in parallel with P0)

Three branches are 21 commits ahead AND 21 commits behind main — they diverged
before the recent merge train. Assess each:

### `chore/infra/workspace-stabilization`
```
git log main..chore/infra/workspace-stabilization --oneline
```
Cherry-pick only the commits that are not already on `main`. Likely candidates:
- `uv` workspace / `pyproject.toml` cleanups
- ruff scope adjustments
- Makefile improvements
- `scripts/fix-workspace-sources.ps1`

Do NOT bring the `0002_core_tables.py` deletion if `main` already has the
per-service migrations superseding it. Validate with `alembic upgrade head`
on a fresh DB before merging.

Open as: `chore(infra): workspace stabilization` PR → `main`.

### `feat/agents/03-phase3-system-agents`
```
git log main..feat/agents/03-phase3-system-agents --oneline
```
Check whether the Research, KG Builder, and Content Curator agent implementations
are materially better than what's on `main` (look at
`packages/agents/agents/system/{research,kg_builder,content_curator}/`).
If yes: rebase onto main, PR as `feat(agents): phase-3 system agents`.
If the same code is already on main via `wip/agents-phase3-snapshot`: archive the branch.

### `feat/mcp/05-server-improvements`
```
git log main..feat/mcp/05-server-improvements --oneline
```
Cherry-pick any improvements to the FastMCP servers (auth context, schema
validation, telemetry) that are not yet on `main`. PR as `feat(mcp): server improvements`.

### Branches to delete (already identical or superseded):
- `feat/curriculum/openstax-ingest` — 0 ahead of main, safe to delete.
- `feat/frontend/chat-cold-start-fix` — superseded by the Round 3 fix. Delete.
- Old stacked frontend branches (`feat/frontend/01-foundation` through
  `feat/frontend/09-educator-admin`) — all merged into main already. Delete.
- Old graphrag branches (`feat/graphrag/01-ontology-migration` through
  `feat/graphrag/04-mcp-evals`) — if merged, delete.
- Old MCP branches (`feat/mcp/01-memory` through `feat/mcp/04-progress`) — same.

Clean up with:
```
git push origin --delete <branch-name>
```
Log deletions in `docs/sprint.md`.

---

## P2 — Content database seeding (needs human for first run, then automated)

The ingest script `scripts/ingest_learning_db.py` is ready. The human will run it
locally (they have the `Learning Database/` PDFs). Your job is to make sure the
infrastructure is ready when they do:

1. Verify `0008_content_sections` migration landed on Neon (check via
   `GET https://asf-api-q566.onrender.com/v1/subjects` — should return `[]`
   rather than a 404 or 500).
2. Add `GET /v1/admin/content/status` to the Render deployment. This should return:
   ```json
   { "total_sections": 0, "last_ingest": null, "failed_files": [] }
   ```
   before any seeding, and real counts after.
3. Document the ingest command in `docs/infra/local-dev.md` under a
   "Seeding content" section.

---

## P3 — Chat verification after deploy

After `fix/coordinator-round3` merges and Render redeploys:

1. Hit `https://asf-api-q566.onrender.com/healthz` and confirm 200.
2. Hit `https://asf-api-q566.onrender.com/readyz` and confirm 200.
3. Hit `https://asf-api-q566.onrender.com/v1/warmup` and confirm warm.
4. From the live frontend: sign in → open `/app/chat/tutor` → send "Hello" →
   confirm a real streaming response (not the mock fallback
   `"That's a great question…"`).
   
If chat still returns the mock fallback after the timeout fix:
- Check Render logs for `GROQ_API_KEY` errors (look for `401` or `invalid_api_key`).
- If confirmed key issue: add `ANTHROPIC_API_KEY` to Render env (sync: false,
  set manually) and enable the Anthropic fallback path in
  `packages/agents/agents/base/llm.py`. Document the switch in `docs/adr/0006-llm-fallback.md`.
- The user explicitly said not to rotate keys yet, so only switch to the fallback
  if Groq is confirmed broken.

---

## P4 — Dependabot triage (low priority, do after P0-P3)

GitHub reports 58 vulnerabilities on the default branch (3 critical, 18 high).
There are also 8 Dependabot PRs open for GitHub Actions and npm deps:
- `actions/checkout-7`, `actions/setup-python-6`, `dopplerhq/cli-action-4`,
  `orhun/git-cliff-action-4`, `pnpm/action-setup-6` (GH Actions)
- `apps/web/ai-sdk`, `apps/web/clerk`, `apps/web/nextjs`, `apps/web/react`,
  `apps/web/typescript-6.0.3` (npm)

Merge the safe ones (GH Actions bumps and patch-level npm bumps) in a batch PR.
Hold back major version bumps (e.g., `nextjs` major, `react` major) until the
site is stable.

---

## P5 — `/book` booking page: wire Resend

The `/book` page is live but needs `RESEND_API_KEY` to send the tutor email.
Add to `BLOCKED.md` (under "Remaining human tasks"):

```
3. **Resend API key** — sign up at resend.com (free tier), create an API key,
   set RESEND_API_KEY in Render environment variables. Also set:
   - TUTOR_EMAIL=<your email>
   - RESEND_FROM=A Step Forward <noreply@yourdomain.com>  (or onboarding@resend.dev for free tier)
   Without this, bookings are saved to Postgres only (no email notification).
```

Do not block the merge on this — it degrades gracefully (DB-only).

---

## P6 — Continue ongoing missions from Round 2/3

Coordinate with stream agents to keep making progress on:

- **Memory (04)**: real Postgres + pgvector embeddings. Is it live on Neon or still the in-memory stub?
  Check `services/memory/memory_service/stores/repository.py` — if still in-memory, this is the
  biggest remaining backend gap.
- **GraphRAG (05)**: the hybrid endpoint is live (`/v1/graphrag/hybrid` with graceful fallback).
  Wire the `/learn` lesson reader so that clicking "Chat with Tutor about this" passes the
  `context=<section_id>` to the orchestrator, which then seeds the KG query with the section.
- **Security (10)**: RBAC cross-learner isolation tests are still pending. Schedule these
  before any marketing push.
- **Evals (08)**: Tutor eval gates are mocked (promptfoo CI job runs but uses mock responses).
  Move to real Groq/Anthropic calls in the eval harness so the gates are meaningful.

---

## Post-merge checklist (Release Captain)

After P0 merges:

- [ ] `/learn` page is live and returns either content or the "run make ingest" placeholder
- [ ] `/book` page is live with working form (DB-only if no Resend key)
- [ ] Chat timeout is 55s with warm-up banner
- [ ] `GET /v1/subjects` returns 200 (empty array is fine, 404/500 is not)
- [ ] `GET /v1/admin/content/status` returns 200
- [ ] CI green on `main`
- [ ] `BLOCKED.md` updated with Resend instructions

---

## Build error post-mortem (for future sub-agents)

Two build failures on `fix/coordinator-round3` were diagnosed and fixed:

**Error 1** (red herring, local only): `UNABLE_TO_VERIFY_LEAF_SIGNATURE` — TLS-inspecting
proxy on the developer's machine blocks Google Fonts during local `next build`.
This does NOT occur on Vercel. Do not chase this locally; use `npx next lint` and
`npx tsc --noEmit` for local validation instead.

**Error 2** (real Vercel failure): `@typescript-eslint/no-unused-vars` on `stop`
destructured from `useChat` in `agent-chat.tsx`. Next.js runs ESLint during build;
any error exits with code 1.

**Rules now in `skills/add-a-frontend-page/SKILL.md`**:
1. Always run `npx next lint --dir src` before pushing.
2. Always add ESM-only packages (remark-*, rehype-*, unified, micromark) to
   `transpilePackages` in `next.config.mjs`.
