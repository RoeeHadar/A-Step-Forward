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

Complete in any order. Estimated wall-clock: **~30–60 min**.

### 5a. Backend on Render (~10 min)

Fly.io requires a credit card — **use Render** (`render.yaml` is in the repo).

1. https://dashboard.render.com → sign in with GitHub
2. **New → Blueprint** → repo `RoeeHadar/A-Step-Forward`
3. Render creates `asf-api` from `render.yaml`
4. Set env vars on the service:

   ```
   DATABASE_URL   = postgresql+asyncpg://neondb_owner:npg_vmKB0jNoSLF3@ep-plain-sea-as5ml68n-pooler.c-4.eu-central-1.aws.neon.tech/neondb?ssl=require
   REDIS_URL      = rediss://default:AaRhAAIgcDE5Y2JkMTZhYmVkZWE0MTk0ODE2YjJkZDRhMTg0OGE0MA@expert-trout-42081.upstash.io:6379
   NEO4J_URI      = neo4j+s://06b74083.databases.neo4j.io
   NEO4J_USER     = neo4j
   NEO4J_DATABASE = neo4j
   NEO4J_PASSWORD = <from AuraDB dashboard>
   GROQ_API_KEY   = <see §5c>
   ```

5. Confirm deploy: `GET /healthz` → `{"status":"ok"}`

> **Render URL note (2026-06-24):** `https://asf-api.onrender.com/` currently
> serves an unrelated app (`{"mensaje":"hola"}`) and `/healthz` returns 404.
> The Blueprint either was not applied yet or the subdomain is taken. After
> deploy, verify `/healthz`. If the name is squatted, rename the service in
> `render.yaml` (e.g. `asf-api-roeehadar`) and use that URL everywhere below.

### 5a-i. Point Vercel at Render (~30 sec)

Until `NEXT_PUBLIC_API_BASE_URL` is set, the frontend falls back to mock data.

```pwsh
$env:VERCEL_TOKEN = "<from https://vercel.com/account/tokens>"
pwsh ./scripts/vercel-set-env.ps1 -ApiBaseUrl "https://<your-actual-render-url>"
```

Script sets Production + Preview env vars and triggers redeploy. Use
`-SkipRedeploy` to set vars only; `-TeamSlug a-step-forward` if needed.

### 5b. Clerk Dev keys (~5 min)

Production Clerk needs a custom domain. **Dev keys** work on `*.vercel.app`.

1. https://dashboard.clerk.com → app `astepforward` → **API Keys**
2. Copy `pk_test_…` and `sk_test_…`
3. Vercel → project env vars:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - `CLERK_SECRET_KEY`
4. Save → redeploy. Optionally mirror to GitHub Actions secrets for CI.

### 5c. Groq API key (~2 min, free)

See `docs/adr/0004-llm-provider-groq.md`.

1. https://console.groq.com/keys → create key (`gsk_…`)
2. Set on **Render** (`asf-api` env) and **GitHub Actions** secret `GROQ_API_KEY`
3. Wait ~60s for Render redeploy; chat should return real Llama-3.3-70B tokens

Until set, Tutor returns the Socratic stub from `TutorAgent._stub_output`.

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
| `GROQ_API_KEY` | cron-dreaming, evals | verify in dashboard |
| `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | deploy-web | verify in dashboard |
| `CLERK_*` | CI auth tests | optional |

Cron workflows run on schedule or via **Actions → Run workflow**. They execute
real jobs when `DATABASE_URL` is set (no longer dry-run-only in CI).

---

When every launch item above is done, delete this file in a commit titled
`chore: launched 🚀`.
