# Wave 2 retest report — post Wave A fixes

Date: 2026-07-21  
Mode: **roleplay: agent** (browser walkthrough on localhost)  
Site: `http://localhost:3000` (UI fixes not yet on production)  
Roster: `docs/qa/cohort-pilot/roster-w2.json`  
Accounts: **T2**, **R1**, **R2**, **R3** (`asf.w2.*+clerk_test@example.com`) — different from Wave 1

## Fixes under test

| ID | Fix | Expected |
|----|-----|----------|
| A1 | Plan-fit for mid-mastery 5pt (`building` + `bagrut_math_5`) | Week cards at 5pt depth (derivatives / hypothesis), not 3pt foundations |
| A2 | Chat empty-state while content/loading | No «אין הודעות עדיין» once messages exist or chat is loading |
| A3 | Onboarding disabled «הבא» hint | Status text lists missing fields |

## Setup notes

- W2 users provisioned + seeded via `scripts/setup-cohort-w2.mjs` (Neon + Clerk).
- Local `.env.local` had `NEXT_PUBLIC_SITE_URL=[SENSITIVE]` from a bad Vercel pull → `Invalid URL` in `layout.tsx`. Set to `http://localhost:3000` for this retest.
- LLM base URL in local env appears similarly broken (`Failed to parse URL from …/chat/completions`) — Tutor returned the soft fallback message. **Does not block A2** (empty-state check).

## Results

| Check | Persona | Result | Evidence |
|-------|---------|--------|----------|
| A1 plan_fit_5pt | R1 | **PASS** | `/app` week: בדיקת השערות, כללי גזירה, יישומי נגזרות — שליטה 5 יח׳; goal chip `bagrut_math_5`. No מרובעים יסודות. |
| A2 chat_empty_state | R1 | **PASS** | Idle showed empty copy; after send (loading + reply/fallback) empty copy **absent**; user question + assistant text visible. |
| teacher_chip | R1 | **PASS** | «מורה: Wave2 Teacher» on `/app`. |
| A3 onboarding_cta_hint | R2 | **PASS** | `/onboarding`: «הבא» disabled; `status`: «כדי להמשיך: כיתה / שכבה · מטרת למידה». |
| teacher_link / roster | T2 | **PASS** | `/educator`: «מחוברים (3)» — Wave2 R1, R2, R3. |

### Outcome: **Wave A fixes verified** (3/3 primary checks PASS)

Secondary smoke (teacher + social wiring) also green on new accounts.

## Regression / follow-ups (not A1–A3 blockers)

1. **Ship Wave A to production** before human Wave 2 — UI fixes (A2/A3) are local-only until commit/push/deploy; A1 seed logic already affected W2 Neon seed.
2. **Repair local secrets hygiene** — `vercel env pull` left `[SENSITIVE]` placeholders for SITE_URL (and likely LLM URL). Prefer known-good values from Vercel dashboard / `.database-url.local` pattern.
3. **Tutor live answers on localhost** need a valid OpenAI-compatible base URL + key; soft fallback still exercises transcript UI.
4. Next.js 15 `headers()` / `cookies()` sync warnings spam the dev log (pre-existing).

## Verdict

Wave A addressed the three high-confidence Wave 1 themes. Re-test with **new** teacher + students confirms plan-fit, chat empty-state, and onboarding hint. Ready to iterate toward a human pilot once fixes are on production.
