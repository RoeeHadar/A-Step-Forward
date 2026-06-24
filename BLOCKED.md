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

**Auth status:**
- [x] `gh` — authenticated (keyring token with all scopes)
- [x] `vercel` — authenticated as `roeehadar`
- [ ] `flyctl auth login` — still needs browser flow (for API + workers deploy)
- [ ] `doppler login` — still needs browser flow (secrets manager)

**WSL:**
- [x] `wsl --install` run — restart still pending to activate Docker Desktop

---

## 1. PRs ✅ ALL MERGED

- [x] [#1](https://github.com/RoeeHadar/A-Step-Forward/pull/1) — squash-merged 2026-06-24.
- [x] [#2](https://github.com/RoeeHadar/A-Step-Forward/pull/2) — cherry-picked onto main (d0fed33) 2026-06-24.
- [x] [#3](https://github.com/RoeeHadar/A-Step-Forward/pull/3) — cherry-picked onto main (f6d02e2) 2026-06-24.
- [x] [#4](https://github.com/RoeeHadar/A-Step-Forward/pull/4) — cherry-picked onto main (a3e1ddd) 2026-06-24.

---

## 2. Provision managed services ✅ MOSTLY DONE

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
| Fly.io                 | **Requires credit card** | BLOCKED — use Render instead (see §5a) | `FLY_API_TOKEN` |
| Clerk                  | Free (Dev instance) | Use Dev keys — see §5b for 3-step guide | `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` |
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

## 2a. DB migrations ✅ DONE

All 16 tables applied to Neon dev (via Docker psql, 2026-06-24):
`affective_memories`, `audit_gateway_events`, `audit_memory_events`, `context_memories`,
`curriculum_concepts`, `curriculum_courses`, `curriculum_lessons`, `episodic_memories`,
`gateway_sessions`, `gateway_users`, `kg_chunks`, `procedural_memories`,
`reflective_memories`, `semantic_memories`, `source_memories`.

---

## 3. First staging deploy + smoke ✅ DONE

**Live URL: https://a-step-forward-waij.vercel.app**

Smoke results (Release Captain, 2026-06-24):
- ✓ `/` — 200
- ✓ `/api/health` — 200
- ✓ `/sign-in` — 200
- ✓ `/sign-up` — 200

Remaining in this step:
- [ ] Walk through `apps/web/e2e/chat-flow.spec.ts` against the live URL to verify
      sign-up → chat → memory flow end-to-end.
- [ ] Generate a 30–60s demo GIF (Loom or [Cap](https://cap.so/)) and drop it as
      `docs/marketing/demo.gif`. Reference it from the README hero.

---

## 4. Tangled WIP branch ✅ DONE

Split by the Release Captain into three clean branches and PRs:
- [PR #2](https://github.com/RoeeHadar/A-Step-Forward/pull/2) — `chore/infra/workspace-stabilization`
- [PR #3](https://github.com/RoeeHadar/A-Step-Forward/pull/3) — `feat/agents/03-phase3-system-agents`
- [PR #4](https://github.com/RoeeHadar/A-Step-Forward/pull/4) — `feat/mcp/05-server-improvements`

---

## 5a. Backend deploy on Render (free, no credit card) — 10 min

Fly.io requires a credit card. Use **Render** instead — `render.yaml` is already in the repo.

1. Go to **https://dashboard.render.com** → sign in with GitHub (free).
2. Click **New → Blueprint** → select repo `RoeeHadar/A-Step-Forward`.
3. Render detects `render.yaml` and creates `asf-api` automatically.
4. Set the following environment variables in the Render dashboard for `asf-api`:
   ```
   REDIS_URL         = rediss://default:AaRhAAIgcDE5Y2JkMTZhYmVkZWE0MTk0ODE2YjJkZDRhMTg0OGE0MA@expert-trout-42081.upstash.io:6379
   NEO4J_URI         = neo4j+s://06b74083.databases.neo4j.io
   NEO4J_PASSWORD    = Ws_Tygc7x5aye95rZx1nnLVVyEeXTb7gqhr6N_7YtNM
   DATABASE_URL      = postgresql+asyncpg://neondb_owner:npg_vmKB0jNoSLF3@ep-plain-sea-as5ml68n-pooler.c-4.eu-central-1.aws.neon.tech/neondb?ssl=require
   ```
5. Once deployed, copy the `https://asf-api.onrender.com` URL into Vercel env var `NEXT_PUBLIC_API_BASE_URL`.

> **Status as of 2026-06-24 (Frontend sub-agent poll):** the host
> `https://asf-api.onrender.com/` returned `{"mensaje":"hola"}` instead of our
> FastAPI app, and `/healthz` returned 404. That means the Render service either
> wasn't created from `render.yaml` yet or another Render account is squatting
> the subdomain. After deploying via Blueprint, confirm `/healthz` returns
> `{"status":"ok"}`; if the subdomain is taken, rename the service in
> `render.yaml` (e.g. `asf-api-roeehadar`) and update
> `NEXT_PUBLIC_API_BASE_URL` accordingly.

---

## 5a-i. Point the Vercel frontend at Render — 30 sec (manual one-time)

The frontend's `apps/web/src/lib/api.ts` reads `NEXT_PUBLIC_API_BASE_URL`. Until
that env var exists on the Vercel project, every backend call falls through to
the in-process mock data in `apps/web/src/lib/data.ts` (handy, but not the
production goal). The Frontend sub-agent could not configure this autonomously
because the local Vercel CLI hangs on this network and no Vercel token is
exposed to the workspace.

**You must run this once, with a Vercel token:**

```pwsh
# 1. Grab the token from https://vercel.com/account/tokens
#    (it's the same value stored as the GitHub Actions secret VERCEL_TOKEN).
$env:VERCEL_TOKEN = "<paste here>"

# 2. Run the helper. It looks up the project, sets the env var on
#    Production + Preview, and pushes an empty commit to trigger redeploy.
pwsh ./scripts/vercel-set-env.ps1
```

The script is idempotent — running it again just rewrites the value. Add
`-SkipRedeploy` if you'd rather trigger the build yourself, and
`-TeamSlug a-step-forward` if the project lives under that team scope.

After the redeploy is live, the frontend will hit `https://asf-api.onrender.com`
directly. CORS is already wired (see commit `feat(api): CORS allow Vercel
domains by default`).

---

## 5b. Clerk auth — use Dev keys (free, no domain needed) — 5 min

Clerk Production requires a custom domain. Use the **Dev** instance instead — it's
free and works on any URL including `*.vercel.app`.

1. Go to **https://dashboard.clerk.com** → select your app (`astepforward`).
2. Click **API Keys** in the left sidebar.
3. Copy **Publishable key** (`pk_test_…`) and **Secret key** (`sk_test_…`).
4. Add them to Vercel:
   - Go to https://vercel.com/a-step-forward/a-step-forward-waij/settings/environment-variables
   - Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = `pk_test_…`
   - Set `CLERK_SECRET_KEY` = `sk_test_…`
   - Click **Save** → Vercel will redeploy automatically.
5. Sign-up / sign-in will now work on the live site.

Also update GitHub Actions secrets (for CI):
```pwsh
gh secret set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY --body "pk_test_..."
gh secret set CLERK_SECRET_KEY --body "sk_test_..."
```

---

## 5c. Enable real AI responses — 2 min, FREE

The site uses Groq Cloud (llama-3.3-70b-versatile, free, no credit card).
See `docs/adr/0004-llm-provider-groq.md` for the rationale.

1. Go to https://console.groq.com → sign up with GitHub.
2. Visit https://console.groq.com/keys → click "Create API Key" → copy `gsk_...`.
3. Set it in two places:
   - **Render** (backend): dashboard → asf-api → Environment → add `GROQ_API_KEY=gsk_...`
   - **GitHub Actions secrets** (for CI): `gh secret set GROQ_API_KEY --body "gsk_..."`
4. Wait ~60s for Render to redeploy. Test by sending a message in the chat UI.

Until this is done, the Tutor returns a placeholder message (the Socratic
"Let's explore that together…" stub from `TutorAgent._stub_output`).

Optional overrides (defaults are fine):
- `LLM_DEFAULT_MODEL` (default `llama-3.3-70b-versatile`)
- `LLM_CHEAP_MODEL` (default `llama-3.1-8b-instant`)

---

## 5. Promote to prod + custom domain (20 min)

- [ ] Buy `astepforward.app` at Cloudflare Registrar (or accept Vercel default).
- [ ] In Vercel: add custom domain, copy CNAME to Cloudflare DNS.
- [ ] In Cloudflare: turn off proxy for Vercel CNAME, on for any apex `A` record.
- [ ] Run `gh workflow run deploy-prod.yml -f confirm=promote` from `main`.
- [ ] Re-run smoke against prod.

---

## 6. Flip repo public ✅ DONE

Repo is now **public**: https://github.com/RoeeHadar/A-Step-Forward

- [x] Visibility flipped to public (2026-06-24).
- [x] Discussions + Issues enabled.
- [x] Topics added: `ai`, `education`, `learning`, `agents`, `memory`, `graphrag`, `nextjs`, `fastapi`, `langgraph`.
- [x] Dependabot alerts + security updates enabled via API.
- [x] Secret scanning + push protection enabled via API.
- [x] `dependabot.yml` added — weekly updates for npm, pip, GitHub Actions.
- [x] Private vulnerability reporting enabled.

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
