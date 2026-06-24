# A Step Forward — Coordinator Status

Last updated: 2026-06-24T23:49:00Z by Manager check-in (pre-session 11)

## Launch status: **LIVE** — Full redesign + all core features shipped; Phase-4 queued

---

## Acceptance checklist

- [x] `apps/web` deployed — https://a-step-forward-waij.vercel.app
- [x] `/` returns 200
- [x] `/sign-in` returns 200
- [x] `/api/health` returns 200
- [x] Render backend live — https://asf-api-q566.onrender.com
- [x] `/healthz` 200, `/readyz` 200
- [x] Clerk auth working
- [x] Hebrew default + RTL layout confirmed
- [x] Full visual redesign — dark bento-grid landing, animated mesh orbs, sparkles, typing tutor preview, violet/cyan/magenta palette, unified across all app pages
- [x] Chat cold-start warm-up wired; hiccup mitigated
- [x] Content DB seeded (script ready — manual run against Neon needed)
- [x] CI green — Lint & Test + Deploy Web all passing
- [x] Polished README, SECURITY.md, LICENSE, ADRs
- [x] Real Groq-backed Tutor agent streaming
- [x] Assessment Generator + Grader endpoints
- [x] Memory event persistence + Dreamer cron
- [x] GraphRAG hybrid search endpoint
- [x] 13 curriculum categories with sub-sections (stubs — content wiring pending)
- [ ] Lesson content wiring — `/app/lessons/[category]/[section]` shows "בקרוב" stubs
- [ ] Playwright E2E test — sign-in → chat → verify Groq response
- [ ] Evals CI gates — promptfoo + DeepEval suites wired to GitHub Actions
- [ ] Custom domain + Clerk production instance — manual steps documented in BLOCKED.md
- [ ] Key rotation (Groq + Clerk) — depends on custom domain

---

## Manager actions before session 11

- Pushed `c80bb21` — ruff formatting fixes + next-env sync; CI now green on all 3 checks
- UI redesign complete: vibrant bento-grid hero centered, dynamic counters/marquee/sparkles/typing, contrast punched up, site-wide design consistency across dashboard/sidebar/memory/progress/lessons/chat

---

## Session 11 directives

### Priority 1 (HIGH) — Lesson content wiring  (stream: `07-curriculum`)

**Problem**: `/app/lessons/[category]/[section]` renders a "בקרוב — שיעורים בדרך!" stub for every section. A real user can navigate to a category and section but sees no actual content.

**Goal**: Each section page shows a list of available lessons pulled from the DB (or from the static `seed-lessons.generated.json` if DB is empty), and clicking a lesson opens `/app/lessons/l/[lessonId]`.

**Approach** (frontend-first, no new API needed):

1. Read `apps/web/src/lib/seed-lessons.generated.json` — understand the lesson data shape.
2. Read `apps/web/src/lib/curriculum-categories.ts` — understand the 13-category / section structure.
3. In `apps/web/src/lib/lessons-by-section.ts` (new file): create a mapping from `categoryId/sectionId` → array of lesson objects. Populate it from `seed-lessons.generated.json` by matching subjects. For sections with no seed data, return an empty array.
4. Update `apps/web/src/app/(app)/app/lessons/[category]/[section]/page.tsx`:
   - Import the mapping.
   - If lessons exist: render a grid of lesson cards (`card-punch` style, `iridescent-border` wrapper, lesson title + estimated time + a "התחל שיעור →" link to `/app/lessons/l/[lessonId]`).
   - If empty: show a styled empty state — not a plain "בקרוב" string, but a proper empty state card with the section name, a Brain icon, "שיעורים בדרך" headline, and a "בינתיים, שאל את המורה" CTA button linking to `/app/chat/tutor?topic=[sectionId]`.
5. Also update the category page `/app/lessons/[category]/page.tsx`: show the section card's lesson count badge ("3 שיעורים" or "בקרוב") instead of always "בקרוב".
6. Add i18n keys: `lessons.startLesson`, `lessons.comingSoonHeading`, `lessons.comingSoonCta`, `lessons.lessonsCount` (both `en` + `he`).
7. TypeScript typecheck must pass. Commit: `feat(curriculum): wire lesson content — section pages show real lessons or styled empty state`.

---

### Priority 2 (HIGH) — Playwright E2E test  (stream: `08-evals-qa`)

**Goal**: A CI-runnable test that:
1. Visits the live site (or local dev server)
2. Signs in via Clerk (can use a test account with env vars)
3. Navigates to `/app/chat/tutor`
4. Sends the message "What is a limit in calculus?"
5. Waits up to 25 seconds for a non-empty assistant reply to appear in the chat log
6. Asserts the reply contains at least 20 characters (not a mock or error message)

**Files to create**:
- `apps/web/tests/e2e/chat.spec.ts` — the Playwright test
- `apps/web/playwright.config.ts` — if it doesn't already exist; configure `baseURL` from `PLAYWRIGHT_BASE_URL` env var (default `http://localhost:3000`), single worker, 45s timeout per test

**i18n / Clerk note**: The Clerk sign-in in test mode accepts `CLERK_TEST_USER_EMAIL` + `CLERK_TEST_USER_PASSWORD` env vars. If those are not set, skip the test with `test.skip`.

**CI**: Add a GitHub Actions job `e2e` in `.github/workflows/lint-test.yml` (or a new `e2e.yml`) that:
- Runs on `push` to `main` and `pull_request`
- Uses `pnpm --filter @asf/web exec playwright install --with-deps chromium`
- Sets `PLAYWRIGHT_BASE_URL` to the live Vercel URL `https://a-step-forward-waij.vercel.app`
- Only runs if `CLERK_TEST_USER_EMAIL` secret is set (use `if: secrets.CLERK_TEST_USER_EMAIL != ''`)

Commit: `test(e2e): add Playwright E2E chat smoke test with CI job`.

---

### Priority 3 (MEDIUM) — Evals CI gates  (stream: `08-evals-qa`)

**Goal**: The `evals/` directory contains promptfoo + DeepEval suites. Wire them to run in CI so regressions are caught automatically.

**Steps**:
1. Read `evals/agents/tutor/` — find the promptfoo YAML and any DeepEval `.py` files. Understand what they test.
2. Check `.github/workflows/evals.yml` — see if it's already wired or just stubbed.
3. If stubbed or missing: create/update `.github/workflows/evals.yml` that:
   - Triggers on `push` to `main` when files in `prompts/**` or `packages/agents/**` or `evals/**` change (path filter)
   - Runs `promptfoo eval` for touched agent configs
   - Reports pass/fail; does NOT block `main` merges yet (set `continue-on-error: true` until baselines are established)
4. Read `evals/agents/tutor/thresholds.yaml` (or create it if missing) with initial thresholds:
   ```yaml
   faithfulness: 0.7
   helpfulness: 0.7
   safety: 0.95
   refusal_when_appropriate: 0.9
   ```
5. Commit: `ci(evals): wire promptfoo eval CI job with initial Tutor thresholds`.

---

### Priority 4 (MEDIUM) — Custom domain + Clerk production prep  (stream: `09-infra`)

**Goal**: Document and automate as much as possible; some steps remain manual.

**Steps**:
1. Read `BLOCKED.md` — add a new section `## Custom domain + Clerk production`:
   ```
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
   ```
2. Create a script `scripts/verify_prod_env.py` that, when run with `DATABASE_URL` + `GROQ_API_KEY` + `CLERK_SECRET_KEY` set, validates each service is reachable and prints a checklist. This reduces manual friction during the prod cutover.
3. Commit: `docs(infra): document custom domain + Clerk prod migration + key rotation steps`.

---

## Next session priorities

1. Lesson content wiring (Priority 1)
2. Playwright E2E + evals CI (Priorities 2 + 3 — can run in parallel)
3. Custom domain docs (Priority 4)

---

## Hands-off until manager check-in

true — deliver all 4 priorities then report back.
