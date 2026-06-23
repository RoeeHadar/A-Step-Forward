# BLOCKED — items the Release Captain cannot complete autonomously

The Release Captain (this chat) executed everything that can be done from
inside the workspace: merge train, governance files, marketing copy, diagrams,
smoke scripts, CI hardening. Below is the **closed list of human-only actions**
required to get from the current state (`release/phase-1-integration` ready for
review) to a launched, public site.

Each item is independently actionable. You can knock them out in any order
within a phase. Estimated total wall-clock if you have an evening: **2.5–4 h**.

---

## 0. One-time prereqs

These tools are needed to drive the rest.

**Installed by Release Captain:**
- [x] GitHub CLI (`gh`) — v2.95
- [x] Node 20+ — v24.17
- [x] pnpm 9.12 — via npm, global bin at `%APPDATA%\Local\pnpm`
- [x] uv — v0.11.23
- [x] flyctl — v0.4.60 (at `%USERPROFILE%\.fly\bin`)
- [x] Vercel CLI — v54.15.1 (via pnpm global)
- [x] Doppler CLI — v3.76.0 (binary at `%USERPROFILE%\.doppler`)

**Still needed from you (interactive auth, 10 min):**
- [ ] `gh auth login` — the stored git OAuth token lacks `read:org`; the
      Release Captain used `GH_TOKEN` env var for PR creation but you need a
      full login for branch protection, reviews, etc.
- [ ] `flyctl auth login` — browser flow.
- [ ] `vercel login` — browser/device flow.
- [ ] `doppler login` — browser flow.

**WSL (required for Docker Desktop on Windows):**
- [ ] WSL is not installed. Docker Desktop needs it. Run in **admin PowerShell**:
      ```powershell
      wsl --install
      ```
      Then restart the computer. After restart, Docker Desktop will work and
      `make up` will boot the local stack (Postgres+pgvector, Redis, Neo4j, etc.).
      Until then, Alembic migration validation runs against Neon cloud Postgres
      (step 2 → provision Neon first, then run migrations).

---

## 1. Open PRs (DONE by Release Captain)

Four PRs are open and waiting for review + merge:

| PR | Branch | Base | Size |
| -- | ------ | ---- | ---- |
| [#1](https://github.com/RoeeHadar/A-Step-Forward/pull/1) | `release/phase-1-integration` | `main` | 135 files, +7k lines — frontend + GraphRAG + launch polish |
| [#2](https://github.com/RoeeHadar/A-Step-Forward/pull/2) | `chore/infra/workspace-stabilization` | `release/phase-1-integration` | workspace pyproject cleanup, uv.lock, alembic fixes |
| [#3](https://github.com/RoeeHadar/A-Step-Forward/pull/3) | `feat/agents/03-phase3-system-agents` | `release/phase-1-integration` | Research, KG Builder, Content Curator agents |
| [#4](https://github.com/RoeeHadar/A-Step-Forward/pull/4) | `feat/mcp/05-server-improvements` | `release/phase-1-integration` | MCP server typed errors + expanded tests |

- [ ] Run `review-bugbot` skill on PR #1 (the main integration PR).
- [ ] Run `review-security` skill on PR #1 (touches auth middleware and safety evals).
- [ ] Squash-merge #1 to main when CI is green.
- [ ] Merge #2, #3, #4 after #1 (or open new PRs re-based on main).

---

## 2. Provision managed services (45–60 min)

All hosting decisions are locked in `RESUME-README.md` and `09-infra-resume.md`.
Each provider has a free tier sufficient for launch traffic.

| Service                | Tier        | What to create                                           | Output → Doppler key             |
| ---------------------- | ----------- | -------------------------------------------------------- | -------------------------------- |
| Neon Postgres          | Free        | Project `a-step-forward`, branches `dev`/`stg`/`prd`     | `DATABASE_URL`                   |
| Upstash Redis          | Free        | DB `asf-stg`, `asf-prd`                                  | `REDIS_URL`                      |
| Neo4j AuraDB           | Free        | Instance `asf-stg`                                       | `NEO4J_URI`, `NEO4J_PASSWORD`    |
| Cloudflare R2          | Free (10GB) | Bucket `asf-uploads`                                     | `R2_ACCESS_KEY_ID`, `R2_SECRET`, `R2_BUCKET`, `R2_ENDPOINT` |
| Doppler                | Free        | Project `a-step-forward`, configs `dev`, `stg`, `prd`    | `DOPPLER_TOKEN` (per env)         |
| Vercel                 | Hobby       | Project linked to `apps/web`; root dir = `apps/web`      | `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` |
| Fly.io                 | Hobby       | Apps `asf-api`, `asf-workers` (start here; MCP apps later) | `FLY_API_TOKEN`                  |
| Clerk                  | Free        | App `astepforward`, instances `dev`, `prod`              | `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET` |
| Anthropic              | Paid        | API key                                                  | `ANTHROPIC_API_KEY`              |
| OpenAI                 | Paid        | API key                                                  | `OPENAI_API_KEY`                 |
| Voyage AI              | Free start  | API key                                                  | `VOYAGE_API_KEY`                 |
| Cohere                 | Free start  | API key                                                  | `COHERE_API_KEY`                 |
| Sentry                 | Free        | Project `a-step-forward`                                 | `SENTRY_DSN`, `SENTRY_AUTH_TOKEN` |
| Langfuse (self-host)   | n/a         | Fly app `asf-langfuse` (or use cloud free tier)          | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` |
| Cloudflare Registrar   | Paid (~$10) | Register `astepforward.app` (or fallback `learn.astepforward.app`) | n/a (DNS only) |

Push everything into Doppler:

```pwsh
doppler login
doppler projects create a-step-forward
doppler configs create dev --project a-step-forward
doppler configs create stg --project a-step-forward
doppler configs create prd --project a-step-forward
# then doppler secrets set KEY=VAL --project a-step-forward --config <env>
```

Generate service tokens for CI and store them as GitHub Actions secrets at
`https://github.com/RoeeHadar/A-Step-Forward/settings/secrets/actions`:

- `DOPPLER_TOKEN_STG`, `DOPPLER_TOKEN_PRD` (service tokens per env).
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
- `FLY_API_TOKEN`.
- `STAGING_DATABASE_URL`, `PRODUCTION_DATABASE_URL` (for migration jobs).

> The existing `.github/workflows/deploy-*.yml` already reference these names.

---

## 3. First staging deploy + smoke (15 min)

Once secrets are in place, push to `main` (after the PR from step 1 lands):

- [ ] Watch `deploy-web.yml`, `deploy-api.yml`, `deploy-workers.yml` succeed in
      Actions.
- [ ] Run smoke:

      ```pwsh
      $env:WEB_BASE_URL = '<your-vercel-staging-url>'
      $env:API_BASE_URL = '<your-fly-api-url>'
      .\scripts\smoke\e2e.ps1
      ```

- [ ] Walk through `apps/web/e2e/chat-flow.spec.ts` against the deployed URL
      (`pnpm --filter @asf/web exec playwright test --reporter=line --base-url=<staging>`).
- [ ] Generate a 30–60s demo GIF (Loom or
      [Cap](https://cap.so/)) and drop it as
      `docs/marketing/demo.gif`. Reference it from the README hero.

---

## 4. Tangled WIP branch — surgery before merging (30–60 min)

`wip/agents-phase3-snapshot` mixes Phase-3 agents (research, kg_builder,
content_curator, …) with workspace-stabilization (pyproject + uv.lock + ruff +
alembic 0002_core_tables deletion + scripts/fix-workspace-sources.ps1). Per
`09-infra-resume.md` it must be split. Recommended approach:

1. `git checkout -b chore/infra/workspace-stabilization main` and cherry-pick
   only the infra files listed in `09-infra-resume.md`. Validate
   `alembic upgrade head` + `downgrade base` on a fresh Postgres docker.
2. `git checkout -b feat/agents/phase3 main` and cherry-pick only the agent
   code (`packages/agents/agents/system/research/`, `.../kg_builder/`,
   `.../content_curator/`, and prompts under `prompts/`).
3. Open them as two PRs in that order. Run `review-bugbot` on both.

The Release Captain did **not** touch this branch — surgery here without the
ability to run `uv sync` and `alembic` was unsafe.

---

## 5. Promote to prod + custom domain (20 min)

- [ ] Buy `astepforward.app` at Cloudflare Registrar (or accept Vercel default).
- [ ] In Vercel: add custom domain, copy CNAME to Cloudflare DNS.
- [ ] In Cloudflare: turn off proxy for Vercel CNAME, on for any apex `A` record.
- [ ] Run `gh workflow run deploy-prod.yml -f confirm=promote` from `main`.
- [ ] Re-run smoke against prod.

---

## 6. Flip repo public + enable community surfaces (10 min)

After Phase-C bars are met (smoke green, Sentry < 0.5%, p95 < 2.5s, evals
green for ≥ 24h):

- [ ] `gh repo edit RoeeHadar/A-Step-Forward --visibility public --accept-visibility-change-consequences`
- [ ] `gh repo edit --enable-discussions --enable-issues`
- [ ] Enable Dependabot:
      `https://github.com/RoeeHadar/A-Step-Forward/settings/security_analysis`
      → turn on Dependabot alerts, security updates, version updates, secret
      scanning.
- [ ] Enable private vulnerability reporting on the same page.
- [ ] Add the topics: `ai`, `education`, `learning`, `agents`, `memory`,
      `graphrag`, `nextjs`, `fastapi`, `langgraph`.

---

## 7. Marketing (15 min)

Copy is already drafted under `docs/marketing/`:

- [ ] Generate hero illustration (`docs/assets/hero.png`) — the Release Captain
      attempted via `GenerateImage` but you may want to regenerate / replace.
- [ ] Generate OG card (`docs/assets/og-card.png`) — wired into `apps/web` via
      `apps/web/src/app/layout.tsx` metadata. Confirm both Twitter card and OG
      tags resolve to the right asset on Vercel.
- [ ] Post `docs/marketing/launch-hn.md` to https://news.ycombinator.com/submit
      between 8–11am ET Tue/Wed/Thu (best traffic).
- [ ] Post `docs/marketing/launch-ph.md` to https://www.producthunt.com — set
      "launching tomorrow" 24h before 00:01 PT.
- [ ] Post the LinkedIn + Twitter thread from `docs/marketing/social-copy.md`.

---

## 8. Nice-to-have, post-launch (defer if tight on time)

- [ ] MCP server Fly apps (`asf-mcp-memory`, `asf-mcp-graphrag`,
      `asf-mcp-curriculum`, `asf-mcp-progress`) — add `infra/fly/asf-mcp-*.toml`
      and matching deploy job. Currently MCP servers run in-process / locally.
- [ ] Memory Phase-2 (real Postgres + pgvector backed memory_service) — stream
      04 owner.
- [ ] Backend Phase-2 (Clerk JWT verification, rate limits, schema codegen
      from Python → TS) — stream 02 owner.
- [ ] Curriculum seed expansion beyond the math fractions example.
- [ ] Evals expansion (per-agent thresholds, retrieval evals coverage).

---

## What the Release Captain shipped (so you don't redo it)

**Branches pushed to origin:**
- `release/phase-1-integration` — frontend + graphrag + safety merged + launch polish + pyproject fixes + ruff format + mypy fix.
- `chore/infra/workspace-stabilization` — pyproject workspace sources, uv.lock, alembic migration cleanup, Makefile, ruff scoping.
- `feat/agents/03-phase3-system-agents` — Research, KG Builder, Content Curator agents + eval matrices.
- `feat/mcp/05-server-improvements` — typed MCP errors, tool expansions, full test suites.

**PRs open:**
- [#1](https://github.com/RoeeHadar/A-Step-Forward/pull/1), [#2](https://github.com/RoeeHadar/A-Step-Forward/pull/2), [#3](https://github.com/RoeeHadar/A-Step-Forward/pull/3), [#4](https://github.com/RoeeHadar/A-Step-Forward/pull/4)

**Governance + docs:**
- `LICENSE` (MIT), `SECURITY.md`, `CHANGELOG.md`, `cliff.toml`.
- `.github/workflows/changelog.yml`, `.github/workflows/repo-health.yml`.
- `docs/adr/README.md` (ADR index).
- `docs/marketing/copy.md`, `launch-hn.md`, `launch-ph.md`, `social-copy.md`.
- `docs/diagrams/architecture.md`, `docs/diagrams/graphrag.md`.
- `scripts/smoke/e2e.sh`, `scripts/smoke/e2e.ps1`.
- README polished with hero image, badges, agent matrix.

**CLIs installed:**
- pnpm 9.12 · flyctl 0.4.60 · Vercel CLI 54.15.1 · Doppler CLI 3.76.0

**Code validated locally:**
- `ruff check .` — all checks passed.
- `ruff format .` — 9 scripts files reformatted.
- `mypy` — no issues (fixed `DeclarativeBase` type annotation in `infra/alembic/env.py`)
- `pnpm install` — succeeded (peer warnings for react 19 in Clerk/shadcn are pre-existing, not blocking).
- Alembic migration validation skipped — Docker Desktop requires WSL (see §0).

When every box above is checked, delete this file in the commit titled
`chore: launched 🚀`.
