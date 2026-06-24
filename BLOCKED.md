# BLOCKED — human-only actions

Everything below requires a human with dashboard access. The Coordinator and
sub-agents do **not** stop for these — they are tracked here for the product
owner to knock out independently.

**Live frontend:** https://a-step-forward-waij.vercel.app (Vercel smoke green on
`/`, `/api/health`, `/sign-in`, `/lessons/lesson-whole-numbers`)

---

## 0. Prerequisites

| Tool | Status |
| --- | --- |
| GitHub CLI (`gh`) | ✅ authenticated |
| Node 20+ / pnpm 9 | ✅ installed |
| Vercel CLI | ✅ authenticated as `roeehadar` |
| Docker Desktop + WSL2 | ✅ installed (use for `psql` against Neon) |
| Doppler / Fly.io | ⏭ skipped — secrets via GitHub Actions + Render/Vercel env vars |

---

## 1. Already done ✅

- All Phase-1 PRs merged to `main`; repo is **public**
- Neon dev: 16 tables migrated (including `kg_chunks`, `episodic_memories`)
- Curriculum seed in Neon: 1 course / 8 concepts / 9 lessons
- Vercel deploy live; marketing landing + learner UI shipped
- Memory episodic writes wired in orchestrator (`cef3a43`)
- Groq LLM provider + ADR-0004 committed; Tutor uses `LLM.astream`
- GraphRAG: 31 Neon chunks + Neo4j graph ingested (`743b9e5`, `39432b0`); ADR-0005
- GitHub Actions cron-dreaming + cron-decay (`9f57509`); `DATABASE_URL` secret set
- Governance: LICENSE (MIT), SECURITY.md, ADRs, Dependabot, secret scanning

---

## 2. Managed services ✅ provisioned

Neon, Upstash Redis, and Neo4j AuraDB (asf-stg) are created. AuraDB auth:
`NEO4J_URI=neo4j+s://06b74083.databases.neo4j.io`, **`NEO4J_USER=neo4j`**,
**`NEO4J_DATABASE=neo4j`** (not the instance id). GitHub Actions secrets
updated; `.env.local` mirrors these for local dev.

> **Local Neo4j note:** the developer machine uses a TLS-inspecting proxy, so
> `neo4j+s://` handshakes fail locally. Do not burn cycles debugging this —
> Neo4j connectivity is verified on GitHub Actions runners and in AuraDB
> console. Re-run `scripts/ingest_graphrag.py` from CI or a clean network if
> graph re-ingest is needed.

Optional / deferred: Cloudflare R2 uploads, Sentry, Langfuse, custom domain,
Doppler (not required for launch).

---

## 3. Remaining launch checklist

**Backend URL:** `https://asf-api-q566.onrender.com` (Render service `asf-api`, Blueprint applied).

Complete **§5d** below (~3 min) to go live. Everything else in this section is reference.

### 5a. Backend on Render ✅ (deployed — env vars pending)

Render service exists at `https://asf-api-q566.onrender.com`. `/healthz` will not respond until
`CLERK_JWKS_URL` + `GROQ_API_KEY` are set (see §5d). `APP_ENV=staging` triggers
`validate_auth_config()` at startup — missing Clerk JWKS prevents the process from booting.

Database / Redis / Neo4j connection strings should already be on the service from Blueprint setup.

### 5a-i. Point Vercel at Render

Until `NEXT_PUBLIC_API_BASE_URL` is set, the frontend falls back to mock data.

**Option A — GitHub Actions (no local token):**

```pwsh
gh workflow run wire-vercel-env.yml
```

Uses `VERCEL_TOKEN`, `RENDER_API_BASE_URL`, and Clerk secrets from GitHub Actions.

**Option B — local script:**

```pwsh
$env:VERCEL_TOKEN = "<from https://vercel.com/account/tokens>"
pwsh ./scripts/wire-env-vars.ps1 `
  -ClerkPublishableKey "<pk_test_…>" `
  -ClerkSecretKey "<sk_test_…>"
```

Legacy one-var helper: `pwsh ./scripts/vercel-set-env.ps1 -ApiBaseUrl "https://asf-api-q566.onrender.com"`

### 5b. Clerk Dev keys ✅ (values provided — wire via §5d)

Production Clerk needs a custom domain. **Dev keys** work on `*.vercel.app`. Keys are set on
Vercel via §5d and mirrored in GitHub Actions secrets.

### 5c. Groq API key ✅ (value provided — paste on Render via §5d)

See `docs/adr/0004-llm-provider-groq.md`. Key goes on **Render** (`asf-api` env), not Vercel.

### 5d — Final wire-up (3 min)

> 🔑 **ROTATE THESE KEYS AFTER LAUNCH** — see §13.

**One step:** open https://dashboard.render.com → **asf-api** → **Environment** → paste all
three lines below → **Save Changes** (Render redeploys ~60s). Then run
`gh workflow run wire-vercel-env.yml` (or `scripts/wire-env-vars.ps1`) and push the empty
redeploy commit if not already on `main`.

```
GROQ_API_KEY=<gsk_… from manager secure note / Groq dashboard>
CLERK_JWKS_URL=https://joint-python-37.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://joint-python-37.clerk.accounts.dev
```

(Vercel vars `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`
are set via `wire-vercel-env.yml` / `wire-env-vars.ps1` — not on Render.)

After Render redeploy: `GET https://asf-api-q566.onrender.com/healthz` → `{"status":"ok"}`.

### 5. Custom domain (optional, post-launch)

- Register `astepforward.app` (or keep Vercel default)
- Wire DNS → Vercel; run `deploy-prod.yml` when ready

---

## 4. Post-launch polish (defer if tight)

- [ ] E2E: `apps/web/e2e/chat-flow.spec.ts` against live URL (sign-up → chat → memory)
- [ ] Demo GIF → `docs/marketing/demo.gif`, link from README
- [ ] Marketing posts in `docs/marketing/` (HN, Product Hunt, social)
- [ ] Hero / OG assets in `docs/assets/`

---

## 5. GitHub Actions secrets (for CI + cron)

Set at https://github.com/RoeeHadar/A-Step-Forward/settings/secrets/actions:

| Secret | Used by | Status |
| --- | --- | --- |
| `DATABASE_URL` | CI migrations, cron-dreaming, cron-decay | ✅ set (alias of STAGING_DATABASE_URL) |
| `REDIS_URL` | cron jobs | verify in dashboard |
| `NEO4J_URI`, `NEO4J_PASSWORD`, `NEO4J_USER` | cron jobs, GraphRAG CI | ✅ set |
| `GROQ_API_KEY` | cron-dreaming, evals | ✅ set |
| `RENDER_API_BASE_URL` | wire-vercel-env, frontend | ✅ set (`https://asf-api-q566.onrender.com`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` | wire-vercel-env | ✅ set |
| `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | deploy-web, wire-vercel-env | ✅ set |

Cron workflows run on schedule or via **Actions → Run workflow**. They execute
real jobs when `DATABASE_URL` is set (no longer dry-run-only in CI).

---

## 13. Post-launch security hygiene

- [ ] **Rotate all keys shared during launch** — Groq (`GROQ_API_KEY`), Clerk (`pk_test_` / `sk_test_`), and re-issue GitHub Actions secrets
- [ ] Revoke any Vercel tokens created for one-shot wiring
- [ ] Confirm Render env vars are not logged in deploy output
- [ ] Enable Clerk production instance + custom domain before public marketing push
- [ ] Run Dependabot security PR triage (58 open advisories on default branch as of 2026-06-24)

---

When every launch item above is done, delete this file in a commit titled
`chore: launched 🚀`.
