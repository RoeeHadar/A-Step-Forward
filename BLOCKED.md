# BLOCKED — items the Release Captain cannot complete autonomously

The Release Captain (this chat) executed everything that can be done from
inside the workspace: merge train, governance files, marketing copy, diagrams,
smoke scripts, CI hardening. Below is the **closed list of human-only actions**
required to get from the current state (`release/phase-1-integration` ready for
review) to a launched, public site.

Each item is independently actionable. You can knock them out in any order
within a phase. Estimated total wall-clock if you have an evening: **2.5–4 h**.

---

## 0. One-time prereqs (10 min)

These tools are needed by anyone (human or sub-agent) to drive the rest. The
Release Captain's sandbox doesn't have them.

- [ ] Install **GitHub CLI** — https://cli.github.com/ — then `gh auth login`.
- [ ] Install **Node 20+** and **pnpm 9.12+** — `winget install OpenJS.NodeJS.LTS`
      then `corepack enable && corepack prepare pnpm@9.12.0 --activate`.
- [ ] Install **uv** (Python package manager) — `pipx install uv` or
      `winget install --id astral-sh.uv`.
- [ ] Install **Docker Desktop** (for local Postgres / migrate-check).
- [ ] Install **flyctl** — `iwr https://fly.io/install.ps1 -useb | iex`.
- [ ] Install **Vercel CLI** — `pnpm i -g vercel`.
- [ ] Install **Doppler CLI** — `winget install Doppler.doppler`.

---

## 1. Land the integration branch (5 min, GH UI or `gh`)

The Release Captain pushed `release/phase-1-integration` — six new commits on
top of `main` integrating the frontend, GraphRAG, and security stacks (3
merge commits + 3 polish commits).

- [ ] Open the PR:
      ```pwsh
      gh pr create --base main --head release/phase-1-integration `
        --title "feat: integrate phase-1 stacks (frontend, graphrag, safety) + launch polish" `
        --body-file .cursor/subagent-briefs/RELEASE-CAPTAIN-PR-BODY.md
      ```
- [ ] Run `review-bugbot` skill on the PR.
- [ ] Run `review-security` skill (touches auth/safety evals).
- [ ] Squash-merge when green.

> If `gh` was used, the body should be auto-derived from the file mentioned
> below; otherwise, copy the body from
> [`.cursor/subagent-briefs/RELEASE-CAPTAIN-PR-BODY.md`](.cursor/subagent-briefs/RELEASE-CAPTAIN-PR-BODY.md)
> when opening in the GitHub UI.

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

- `release/phase-1-integration` branch with three clean stack merges.
- `LICENSE` (MIT), `SECURITY.md`, `CHANGELOG.md`, `cliff.toml`.
- `.github/workflows/changelog.yml`, `.github/workflows/repo-health.yml`.
- `docs/adr/README.md` (ADR index).
- `docs/marketing/copy.md`, `launch-hn.md`, `launch-ph.md`, `social-copy.md`.
- `docs/diagrams/architecture.md`, `docs/diagrams/graphrag.md`.
- `scripts/smoke/e2e.sh`, `scripts/smoke/e2e.ps1`.
- README polish with hero block, badges, agent matrix.
- `BLOCKED.md` (this file).

When every box above is checked, delete this file in the commit titled
`chore: launched 🚀`.
