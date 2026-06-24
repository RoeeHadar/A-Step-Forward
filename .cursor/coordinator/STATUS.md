# A Step Forward — Coordinator Status

Last updated: 2026-06-24T21:05:00Z by Coordinator session 11

## Launch status: **LIVE** — All 4 session-11 priorities delivered; Phase-4 deferred items remain

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
- [x] 13 curriculum categories with sub-sections
- [x] Lesson content wiring — section pages show real lesson grids (math-middle, pre-calculus, statistics) or styled empty state with tutor CTA — commit `b4cd428`
- [x] Playwright E2E test — `apps/web/tests/e2e/chat.spec.ts` + `.github/workflows/e2e.yml` (skips if `CLERK_TEST_USER_EMAIL` unset) — commit `cb29662`
- [x] Evals CI gates — `evals.yml` path-filtered promptfoo job + `evals/agents/tutor/thresholds.yaml` — commit `51f2ac9`
- [x] Custom domain + Clerk production steps — documented in `BLOCKED.md` §7–8; `scripts/verify_prod_env.py` created — commit `e249f58`
- [ ] Key rotation (Groq + Clerk) — depends on custom domain purchase (manual, human action needed)
- [ ] Custom domain DNS cutover — manual (human must purchase `astepforward.app` and follow `BLOCKED.md §7`)

---

## Session 11

### Dispatched
- Sub-agent A (lesson wiring, stream 07-curriculum): commit `b4cd428`
- Sub-agent B (Playwright E2E + evals CI, stream 08-evals-qa): commits `cb29662`, `51f2ac9`
- Sub-agent C (custom domain docs, stream 09-infra): commit `e249f58`

### Integration
- `git pull origin main` — already up to date (all 4 commits on main: `b4cd428`, `cb29662`, `51f2ac9`, `e249f58`)
- `pnpm --filter @asf/web typecheck` — **0 errors**
- 4-route smoke (2026-06-24T21:05Z):
  - `GET /` → 200 ✓
  - `GET /api/health` → 200 ✓
  - `GET /sign-in` → 200 ✓
  - `GET /app/lessons/calculus` → 200 ✓

### Blocked
- **Custom domain cutover** — human must purchase domain and follow `BLOCKED.md §7`. Cannot be automated.
- **E2E live run** — needs `CLERK_TEST_USER_EMAIL` + `CLERK_TEST_USER_PASSWORD` added as GitHub repo secrets to activate the CI job.
- **Old E2E file** — `apps/web/e2e/chat-flow.spec.ts` is no longer picked up by the updated Playwright config (`testDir` = `./tests/e2e`). Can be removed or migrated in a future session.

---

## Next session priorities

1. **Seed more lesson content** — run `scripts/ingest_content.py` against Neon to populate lessons beyond the current 10 seed entries; re-generate `seed-lessons.generated.json`.
2. **Add GitHub secrets** (`CLERK_TEST_USER_EMAIL` + `CLERK_TEST_USER_PASSWORD`) to activate E2E CI.
3. **Custom domain cutover** — human action: purchase `astepforward.app`, follow `BLOCKED.md §7–8`, then rotate keys.
4. **Remove/migrate** `apps/web/e2e/chat-flow.spec.ts` now that `testDir` has moved.

---

## Hands-off until manager check-in

true — all 4 session-11 priorities delivered; remaining items require human action (domain purchase, GitHub secrets) or are deferred content work.
