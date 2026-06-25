# Coordinator Directive — Round 7 (2026-06-26)

Read `14-adaptive-learning-architecture.md` first for the architectural vision.
This directive is the concrete task list for right now.

---

## State of the world

### Live
- Frontend: https://a-step-forward-waij.vercel.app ✅ (Vercel)
- Backend: https://asf-api-q566.onrender.com ⚠️ (Render — **now optional**, free-tier path no longer depends on it)
- DB: Neon Postgres (12 tables incl. new `chat_turns`, `external_resources` + extended `learner_profiles`).
- KG: Neo4j Aura (PREREQUISITE_OF edges seeded). Now duplicated as static JSON in `apps/web/src/lib/kg-data.json` for fast Vercel access.

### main (clean, CI passing)
- **11 migrations** (0001 → 0011_onboarding_extras).
- Migration 0011 just ran successfully via `Migrate Neon` workflow.
- PR #27 just merged: **full Vercel-direct flow for onboarding, diagnostic, plans, chat memory + curated external resources on /learn**.
- All 3 user-visible goals delivered:
  1. ✅ Learning center functional with our data + curated external resources.
  2. ✅ AI chat works end-to-end with per-agent memory + KG/profile context.
  3. ✅ 4-step onboarding (technical + mental) → next-test-aware weekly plan.

### Manager-level changes this round
- New skill `skills/neon-direct-route/SKILL.md` — pattern for Render-optional Vercel routes.
- New skill `skills/chat-memory-context/SKILL.md` — how chat persistence + context injection works.
- New skill `skills/onboarding-flow/SKILL.md` — end-to-end onboarding → diagnostic → plan.
- `apps/web/src/lib/neon-db.ts` is now the **single Vercel access layer** for free-tier features.
- `scripts/build-kg-json.mjs` regenerates the KG snapshot when YAMLs change.

### Pending manual / infra follow-up

| Item | Action | Owner |
|------|--------|-------|
| Seed `external_resources` table | Run `Seed DB (one-shot)` workflow with `external-resources` (or `all`) | Coordinator (one click) |
| Verify Vercel envs: `DATABASE_URL`, `GROQ_API_KEY`, `NEXT_PUBLIC_API_BASE_URL` | One-time check in Vercel Settings → Environment Variables | User |
| Render env vars (`GROQ_API_KEY`, `CLERK_SECRET_KEY`, …) | Now **optional** — only needed if we ever route through Render again | User (defer) |
| 58 Dependabot vulnerabilities (3 critical) | Batch-bump + open PR | Infra agent |
| Branch cleanup (`feat/frontend/learn-content-browser`, `feat/security/10-safety-hardening`, `fix/infra/prod-e2e-verify`) | Delete after final sweep | Coordinator |

---

## Priorities — execute in order

### P0 — Verify live site (no code change)

1. Hit https://a-step-forward-waij.vercel.app/learn — confirm subject cards appear (math, physics, calculus, linear_algebra), each with a "Curated resources" badge or section count.
2. Click into one subject (e.g. `/learn/math`) — confirm:
   - Sections list (if any).
   - **"More free resources"** panel with Khan Academy, OpenStax, etc.
3. Sign up a fresh user — confirm redirect to `/onboarding`.
4. Walk all 4 onboarding steps — confirm redirect to `/diagnostic`, then `/dashboard` with a weekly plan.
5. Open `/app/chat/tutor` — send a message. Confirm a real response (not the mock). Switch to `/app/chat/mentor` — confirm fresh persona but profile context still present.

If any step fails, escalate to manager with screenshots + browser console logs.

---

### P1 — Seed `external_resources` table [Infra]

Trigger `Seed DB (one-shot)` workflow with input `external-resources`.

```
gh workflow run "Seed DB (one-shot)" -f target=external-resources
```

Confirms the 18 curated entries from `content/external-resources.yaml` land in the table. After this the static fallback in `lib/external-resources.ts` is the secondary source.

**Acceptance:** Seed workflow goes green; `gh api ...` query returns ≥18 rows; the resources still render on `/learn/[subject]` (no regression).

---

### P2 — Phase F: Error diagnosis [Agents]

**Goal:** When a learner submits a wrong quiz answer, classify *why* (concept gap vs. computational error vs. misread) and feed remediation into the next session.

**Branch:** `feat/agents/phase-f-error-diagnosis`

**Steps:**
1. Add `error_diagnosis` JSONB column to `quiz_responses` via migration 0012.
2. In `services/learning_path/learning_path_service/quiz_repository.py` (`submit_quiz`):
   - For each wrong answer, call new `diagnose_error(item, chosen, learner_profile)` helper that uses Groq to classify into `{conceptual, procedural, careless, misread}`.
   - Persist classification + remediation hint per response.
3. In the chat tutor system prompt, surface recent diagnoses (top 3) so the AI can address them proactively.
4. In `/dashboard`, surface a "What to revisit" card if any `conceptual` diagnoses exist in the last 7 days.

**Acceptance:** Submitting a quiz with mixed answers writes `error_diagnosis` JSON; tutor chat references the diagnosis when learner asks about a recent quiz mistake; eval for `assessment_generator` updated.

---

### P3 — Phase G: Dynamic exercise generation [Agents]

**Goal:** Generate concept-specific practice problems on demand, scaled to learner difficulty.

**Branch:** `feat/agents/phase-g-exercise-gen`

**Steps:**
1. New endpoint `POST /api/exercises/generate` with body `{concept_id, difficulty?, count?}`.
2. Pull recent mastery + profile to pick difficulty if not specified.
3. Use Groq to generate 3–10 exercises with worked solutions per concept.
4. Cache by `(concept_id, difficulty)` in a new `generated_exercises` table.
5. Surface from concept cards in `/dashboard` as "Practice this".

**Acceptance:** Generates valid LaTeX-rendered exercises; cache hit ≥ 70% within first week; eval for exercise quality scores ≥ 0.75.

---

### P4 — Infra housekeeping [Infra]

1. **Dependabot batch:** Open PR titled `chore(deps): batch security updates` resolving the 58 vulnerabilities. Group by ecosystem; smoke test the build.
2. **Branch cleanup:** Delete the 3 stale branches listed above.
3. **Render env hygiene:** Document in `docs/infra/render-optional.md` that Render is now optional and which envs would be needed to bring it back in the critical path.

---

### P5 — OCR scanned physics PDFs [Infra]

The ~20 scanned physics PDFs in `Learning Database/Physics/Bagrut/...` still have no extracted text. Add an OCR pass:

1. Install `pytesseract` + Hebrew language pack in a one-shot script `scripts/ocr_pdfs.py`.
2. Resume-friendly: skip files already in `content_sections`.
3. Run via a new `OCR PDFs` workflow with manual dispatch.

**Acceptance:** All Physics Bagrut PDFs have extractable text in `content_sections`; `/learn/physics/bagrut` shows them with previews.

---

## Rules for all agents (unchanged)

- Conventional commits: `<type>(<scope>): <subject>`.
- Branches: `feat/<stream>/<short-name>`, `fix/<stream>/<short-name>`, `eval/<stream>/<short-name>`.
- One task = one branch = one PR. No mega-PRs.
- Must pass: lint, typecheck, unit tests, touched-prompt evals.
- Run `review-bugbot` skill on every PR.
- Run `review-security` on PRs touching auth, memory, graphrag, mcp, RBAC, encryption, payments.
- No secrets in code. `.env*` is gitignored.
- Coverage ≥ 80% for new services; ≥ 70% for frontend components.
- **NEW:** Free-tier critical-path routes must follow `skills/neon-direct-route/SKILL.md` — no hard Render dependency.
- **NEW:** Anything touching chat persistence must follow `skills/chat-memory-context/SKILL.md`.
- **NEW:** Anything touching the onboarding fields must follow `skills/onboarding-flow/SKILL.md`.

## Coordinator responsibilities

- **P0 first** (smoke test live site) before assigning any agent work.
- **P1 second** (seed external_resources) — single workflow run, no agent needed.
- Then dispatch P2–P5 in parallel to Agents and Infra streams.
- Escalate to manager if:
  - Migration 0011 verification fails on Neon.
  - Vercel preview for any new PR shows the `/learn` or `/onboarding` flow broken.
  - More than 2 P2 tasks block on shared state.

---

## Quick reference — what just changed

| File | Purpose |
|------|---------|
| `apps/web/src/lib/neon-db.ts` | Unified Neon access layer for Vercel |
| `apps/web/src/lib/kg-data.json` | Pre-built KG snapshot (92 concepts) |
| `apps/web/src/lib/external-resources.ts` | Static fallback + DB read for /learn |
| `apps/web/src/lib/onboarding-gate.ts` | Redirect logged-in users without a profile |
| `apps/web/src/app/onboarding/page.tsx` | 4-step questionnaire (was 3) |
| `apps/web/src/app/api/{onboarding,diagnostic,plans,chat}/...` | All Neon-direct now |
| `infra/alembic/versions/0011_onboarding_extras.py` | New columns + 2 new tables |
| `content/external-resources.yaml` | Curated 3rd-party resource registry |
| `scripts/build-kg-json.mjs` | Rebuild KG JSON from YAML |
| `scripts/seed-external-resources.mjs` | Seed external_resources table |
| `skills/{neon-direct-route,chat-memory-context,onboarding-flow}/SKILL.md` | New patterns |
