# BLOCKED — human-only actions

Everything below requires a human with dashboard access. Core infrastructure is
**LIVE**; remaining items are browser validation, key rotation, and optional polish.

**Live URLs**

| Surface | URL | Status |
| --- | --- | --- |
| Frontend | https://a-step-forward-waij.vercel.app | ✅ 200 |
| Backend | https://asf-api-q566.onrender.com | ✅ `/healthz` + `/readyz` green |

---

## 1. Already done ✅

- Phase-1 merged to `main`; repo **public**
- Neon: 16 tables, curriculum seed (1 course / 8 concepts / 9 lessons)
- Vercel frontend deployed; Render backend live (`asf-api-q566.onrender.com`)
- Memory episodic writes wired (`cef3a43`); Groq LLM + Tutor streaming (ADR-0004)
- GraphRAG: 31 Neon chunks + Neo4j graph (ADR-0005)
- Cron dreaming + decay on GitHub Actions (`9f57509`)
- CI green; Tutor eval gates (mocked promptfoo + regression)
- Vercel env wired via `wire-vercel-env.yml` (session 4 run **success**):
  `NEXT_PUBLIC_API_BASE_URL`, Clerk publishable + secret keys
- Render env: `GROQ_API_KEY`, `CLERK_JWKS_URL`, `CLERK_ISSUER` (manager, session 5)
- Governance: LICENSE, SECURITY.md, ADRs, Dependabot, secret scanning

---

## 2. Remaining human tasks

Complete in a browser (~10 min). No dashboard wiring left for launch.

1. **Sign-up / auth** — open https://a-step-forward-waij.vercel.app/sign-up → create
   account → confirm redirect into the app (Clerk dev keys on Vercel).

2. **Chat with Tutor** — open a lesson → send a message → confirm a real Groq
   (Llama-3.3-70B) response streams back (not the Socratic stub).

3. **Rotate keys after launch** — Groq + Clerk test keys were shared in chat during
   setup. Re-issue in Groq console, Clerk dashboard, Render env, Vercel env, and
   GitHub Actions secrets. See §4.

4. **Optional:** register `astepforward.app` and wire DNS → Vercel.

5. **Optional:** post launch using copy in `docs/marketing/` (HN, Product Hunt, LinkedIn).

6. **Resend API key (booking emails)** — sign up at [resend.com](https://resend.com) (free tier),
   create an API key, and set in **Render** and **Vercel** environment variables:
   - `RESEND_API_KEY=<key>`
   - `TUTOR_EMAIL=<your email>`
   - `RESEND_FROM=A Step Forward <onboarding@resend.dev>` (free tier) or your verified domain

   Without this, `/book` submissions are saved to Postgres only (no email notification).
   Also set `BOOKING_API_SECRET` (same random string on Render + Vercel) so the API
   rejects direct unauthenticated booking spam.

---

## 3. Post-launch polish (defer)

- [ ] E2E: `apps/web/e2e/chat-flow.spec.ts` against live URL
- [ ] Demo GIF → `docs/marketing/demo.gif`, link from README
- [ ] Hero / OG assets in `docs/assets/`
- [ ] Dependabot triage (58 open advisories on default branch as of 2026-06-24)
- [ ] Neo4j local testing — blocked by TLS-inspecting proxy; verified on Render/CI

---

## 4. Post-launch security hygiene

- [ ] Rotate Groq `GROQ_API_KEY` (Render + GitHub Actions)
- [ ] Rotate Clerk `pk_test_` / `sk_test_` (Vercel + GitHub Actions)
- [ ] Revoke one-shot Vercel tokens if any were created ad hoc
- [ ] Enable Clerk production instance + custom domain before public marketing push

---

## 5. Reference — re-wire env if needed

```pwsh
# Vercel (uses GitHub secrets — no local token)
gh workflow run wire-vercel-env.yml

# Local fallback
$env:VERCEL_TOKEN = "<from https://vercel.com/account/tokens>"
pwsh ./scripts/wire-env-vars.ps1 -ClerkPublishableKey "<pk_test_…>" -ClerkSecretKey "<sk_test_…>"
```

Render dashboard → **asf-api** → Environment: `GROQ_API_KEY`, `CLERK_JWKS_URL`,
`CLERK_ISSUER` (never commit values to git — push protection is enabled).

---

## Custom domain + Clerk production

### 7. Custom domain: astepforward.app
Manual steps required:
a. Purchase/configure domain DNS to point to Vercel (add CNAME record in registrar)
b. In Vercel dashboard: add custom domain under project settings
c. Wait for SSL provisioning (~5 min)
d. In Clerk dashboard: create a Production instance (separate from Dev)
e. Set the Production instance's allowed origins to https://astepforward.app
f. Copy the Production CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY
g. Update Vercel env vars: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY to production values
h. Update NEXT_PUBLIC_SITE_URL in Vercel to https://astepforward.app
i. Redeploy

### 8. Key rotation
After step 7 above:
a. Rotate GROQ_API_KEY — generate a new one at console.groq.com, update in Render + GitHub Secrets + Vercel
b. Delete old Clerk dev keys from all env stores

Before cutover, run `python scripts/verify_prod_env.py` with production env vars set locally
(or in CI) to confirm `DATABASE_URL`, `GROQ_API_KEY`, and `CLERK_SECRET_KEY` are reachable.

---

## Memory persistence (stream I)

- **DATABASE_URL** must be set (Neon Postgres connection string) for memory events to persist.
  Set it in Render env vars and GitHub Actions secrets.
- Episodic memory writes via `MemoryService` are **already wired** in the orchestrator
  (`services/orchestrator/orchestrator/episodic.py`); each chat turn also writes a lightweight
  row to `memory_events` after the SSE stream completes (`apps/api/app/routers/chat.py`).
- Dreamer cron (`.github/workflows/cron-dreaming.yml`) runs nightly via GitHub Actions
  (`workers.jobs.dreaming`). Wire to a Render cron endpoint when the Dreamer worker is
  deployed there.

---

When browser validation and key rotation are done, delete this file in a commit titled
`chore: launched 🚀`.

---

## GraphRAG seeding (stream J)

- **DATABASE_URL** must point to Neon Postgres for kg_chunks vector search to work.
- **NEO4J_URI** must point to AuraDB Free for KG walk enrichment; without it, hybrid search
  falls back to vector-only (graceful degradation is implemented).
- Authenticated hybrid search is already wired at `POST /v1/graphrag/hybrid` (via
  `GraphRAGService`). Public graceful GET search: `GET /v1/search?q=…&top_k=5`.
- To seed foundations-of-math content: run `python scripts/ingest_graphrag.py` with
  `DATABASE_URL` and `NEO4J_URI` set. For OpenStax STEM bulk ingest:
  `python scripts/ingest_content.py` with `DATABASE_URL` set (upserts kg_chunks with
  384-dim embeddings; apply Alembic migration `0006_kg_chunks_384` first).
- sentence-transformers must be installed: `pip install sentence-transformers asyncpg` in
  the services/graphrag environment.
