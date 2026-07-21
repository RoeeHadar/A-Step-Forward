# UI / E2E Report — ADR-0010 + Pilot (`building`)

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (locked — cite only; do not switch) |
| Suite focus | Pilot + ADR-0010 |
| Target env | `local` (`PLAYWRIGHT_BASE_URL` → `http://localhost:3000`) |
| Mode | **PLAN + REPORT ONLY** |
| Runtime | Cursor Auto / UI Tester Crew (scout → executor → reporter) |
| Execution | **None this iteration** — no Playwright run, no browser smoke, no fabricated passes |
| Label legend | **PLANNED** = specified for later execute; **EXECUTED** = not applicable this round |

Charter check: `docs/qa/rounds/current.json` → `seed_variant: building` ✓.

---

## 1. Scout — Flow map

### Grounding (read)

| Source | Role |
|--------|------|
| `docs/qa/rounds/current.json` | Variant lock |
| `PLAN.md` Testing row | Vitest + Playwright |
| `.cursor/skills/add-a-frontend-page/SKILL.md` | App Router / a11y / E2E expectation |
| `.cursor/skills/taste/SKILL.md` | Taste ≠ functional blocker |
| `.cursor/skills/diagnostic-plan-golden-path/SKILL.md` | Onboarding → plan UX contract |
| `.cursor/skills/math-notation-integrity/SKILL.md` | KaTeX / HE-out-of-math |
| `docs/qa/adr-0010-manual-test-plan.md` | Decisions #2, #3, #9–14, #16 for `building` |
| `apps/web/tests/e2e/`, `apps/web/e2e/`, `apps/web/playwright.config.ts` | Actual coverage |
| `docs/qa/cohort-pilot/` | Multi-student pilot (manual) |

### Learner-facing surfaces (product)

| Flow | Primary routes / components | ADR-0010 / pilot relevance (`building`) |
|------|------------------------------|----------------------------------------|
| Sign-in | `/sign-in` (Clerk) | Gate for all authenticated flows |
| Onboarding → plan | `/onboarding` → submit → `/app` or `/plan-setup`; thin bootstrap | Golden path SLO; not ADR-0010 gate but pilot entry |
| Dashboard / plan | `/app`, `/app/plan`, `/dashboard`; `learning-plan-dashboard.tsx` | Readiness ~70% mock-capped; weekly quiz CTA; lesson complete ≠ week advance |
| Weekly gate | `/quiz/[week_id]?plan_id=&week_num=`; `week-quiz-client.tsx` | Decisions #10–14 (kinds, pass, retake, soft override) |
| Mock exam | `/app/quiz/mock-exam`; `mock-exam-client.tsx` | Decisions #2–3 (needs-mock note → pass ungates) |
| My Tests | `/app/tests`, `/app/tests/[id]`; `tests-archive.tsx` | Decision #15 (archive; mock after pass) |
| Custom quiz | `/app/quiz` | Exam-prep adjacent; not weekly gate |
| Learn / lessons | `/learn/**`, `/app/lessons/**`, `/lessons/**` | Math LTR; exposure only (#9) |
| Chat agents | `/app/chat/[agent]` | Pilot coaching; Mentor on final-phase variants (not primary `building`) |
| Settings / persona | `/settings/persona` | Wellbeing bias (#16) — load change, bar unchanged |
| Educator | `/educator/**` | Cohort pilot teacher path |

### Covered by Playwright

| Spec | Path | What it covers | Notes |
|------|------|----------------|-------|
| Tutor chat smoke | `apps/web/tests/e2e/chat.spec.ts` | Sign-in → `/app/chat/tutor` → send → non-empty assistant | Only file under `playwright.config.ts` `testDir` (`./tests/e2e`). Skips unless `CLERK_TEST_USER_EMAIL` / `CLERK_TEST_USER_PASSWORD` |
| Public pages (orphan) | `apps/web/e2e/chat-flow.spec.ts` | Landing, `/api/health`, `/sign-in`; optional chat with `E2E_CLERK_*` | **Not in `testDir`** — will not run via `pnpm e2e` as configured. Env var names disagree with `chat.spec.ts` |

**No Playwright** for: onboarding/plan-setup, pacing/readiness banner, weekly gate, mock exam, tests archive, `/learn` math, persona/settings, educator, mobile viewports, HE locale matrix.

### Manual-only (today)

- Full ADR-0010 matrix for `building` (`docs/qa/adr-0010-manual-test-plan.md` rows 2–3, 9–14, 16) via `node scripts/seed-pilot-demo.mjs --variant building`
- Cohort pilot walkthrough (`docs/qa/cohort-pilot/`)
- Math integrity at lesson authoring time (CI: `scripts/audit-lesson-math.mjs`) — **not** browser E2E
- Soft-override / remediation carry-forward UX (backend in `neon-db.ts` / `test-attempts.ts`; **no** explicit remediation chip in UI — ADR notes deferred)

### Gaps (severity-ranked, coverage)

| Sev | Gap | Why it matters |
|-----|-----|----------------|
| **P0** | Zero E2E for weekly gate (`/quiz/...`) | Core ADR-0010 progression; HE open/numeric/short_answer majority (#10b) |
| **P0** | Zero E2E for readiness / mock-cap banner on `/app` | Decision #2 fingerprint for `building` (~70% + needs-mock copy) |
| **P0** | Zero E2E for mock exam pass → readiness ungate + My Tests | Decision #3 |
| **P1** | Orphan + dual Clerk env vars | `e2e/` vs `tests/e2e/`; `E2E_CLERK_*` vs `CLERK_TEST_USER_*` — CI/local confusion |
| **P1** | No `data-testid` in `apps/web/src` | Durable selectors missing; HE/EN label churn will break role-only specs |
| **P1** | Soft override / retake rotation untested in UI | Decisions #12–14; fail/retake UX only manual |
| **P2** | Onboarding golden path untested in Playwright | Timeout / plan-setup recovery historically fragile |
| **P2** | No locale×viewport matrix (HE@375, HE@1280, EN@1280) | RTL on plan/quiz/mock |
| **P2** | No KaTeX render smoke in browser | CI lint ≠ broken-red-box in quiz/lesson UI |
| **P3** | Deferred UX: remediation chip + “pass to continue” on plan card | Documented non-blocking ADR follow-up — **taste/product polish**, not execute blocker |

### Suggested new specs (file paths)

| File | Focus |
|------|--------|
| `apps/web/tests/e2e/public-smoke.spec.ts` | Move/adopt landing + health + sign-in from orphan `e2e/` |
| `apps/web/tests/e2e/auth.setup.ts` | Shared Clerk storageState (unify env: prefer `E2E_CLERK_*`) |
| `apps/web/tests/e2e/plan-readiness.building.spec.ts` | Seed `building` → `/app` readiness ≤~70% + needs-mock note (HE) |
| `apps/web/tests/e2e/weekly-gate.building.spec.ts` | Week-1 quiz kinds mix, fail critical floor, pass advance, retake rotation |
| `apps/web/tests/e2e/mock-exam.building.spec.ts` | Mock CTA → pass ≥60% → readiness >70% → `/app/tests` |
| `apps/web/tests/e2e/lesson-exposure.spec.ts` | Mark lessons complete → week does **not** advance (#9) |
| `apps/web/tests/e2e/learn-math-smoke.spec.ts` | One math-heavy lesson: no KaTeX error box; formula `dir=ltr` |
| `apps/web/tests/e2e/onboarding-plan.spec.ts` | Gated: submit → `has_plan` / plan-setup fallback &lt;25s abort path |
| `apps/web/tests/e2e/persona-wellbeing.spec.ts` | Gated: anxiety bias → fewer concepts, same gate bar (#16) |

---

## 2. Executor — Executable UI plan (≤20 checks)

**Local:** `pnpm --filter @asf/web dev` + `pnpm --filter @asf/web e2e`.  
**Seed (gated):** `node scripts/seed-pilot-demo.mjs --variant building` against local/Neon URL — never commit secrets.  
**Locale matrix:** HE primary (default cookie/`LOCALE_COOKIE`), EN secondary.  
**Viewports:** mobile `375`, desktop `1280`.  
**Selectors:** prefer `getByRole` / `getByLabel`; add `data-testid` on pacing %, quiz start, mock start, tests list before hardening specs.  
**Auth:** all checks below except #1–2 are **Clerk-gated**.

| # | Check (suggested Playwright title) | Steps (high level) | Expected UI | Sev | Suggested path | Gate |
|---|--------------------------------------|--------------------|-------------|-----|----------------|------|
| 1 | `public: landing loads` | `goto /` @1280 | 2xx; H1 brand/learn | P2 | `public-smoke.spec.ts` | none |
| 2 | `public: sign-in renders` | `goto /sign-in` | Clerk form visible | P2 | `public-smoke.spec.ts` | none |
| 3 | `auth: storageState` | Clerk email/password → `/app` | Session cookie | P0 | `auth.setup.ts` | Clerk |
| 4 | `building: readiness mock-capped` | Seed building → hard-refresh `/app` HE@1280+375 | Readiness ~70% (not 100%); HE needs-mock copy (`readiness_needs_mock`) | P0 | `plan-readiness.building.spec.ts` | Clerk + seed |
| 5 | `building: weekly quiz CTA` | From `/app` click `התחל מבחן שבועי` | Navigates `/quiz/{weekId}?plan_id=&week_num=` | P0 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 6 | `building: gate item kinds hard` | Open week-1 quiz **before** study | Majority open / numeric / short_answer (not trivial all-MCQ) | P0 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 7 | `building: critical floor fail` | Submit high average but miss critical topic | Gate **fails**; week stays active | P0 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 8 | `building: gate pass advances` | Pass aggregate ≥0.75 + critical ≥0.6 → reload `/app` | Week 1 completed; week 2 active | P0 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 9 | `building: retake rotates bank` | Fail → immediate retake | Fresh item set (≠ identical stems) | P1 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 10 | `building: soft override after 3 fails` | Fail gate 3× → reload plan | Advances anyway; weak topics carried (concept list) | P1 | `weekly-gate.building.spec.ts` | Clerk + seed |
| 11 | `building: lessons ≠ advance` | Complete all week-1 lesson UIs → reload | Still week 1 | P1 | `lesson-exposure.spec.ts` | Clerk + seed |
| 12 | `building: mock ungates readiness` | `/app/quiz/mock-exam` → pass ≥60% → `/app` | Readiness &gt;70%; note changes | P0 | `mock-exam.building.spec.ts` | Clerk + seed |
| 13 | `building: mock in My Tests` | After #12 open `/app/tests` | Kind-aware label + pass/fail + date | P1 | `mock-exam.building.spec.ts` | Clerk + seed |
| 14 | `math: lesson KaTeX smoke` | Open one authored math lesson HE@1280 | No red KaTeX error; math LTR | P1 | `learn-math-smoke.spec.ts` | Clerk (or public learn if allowed) |
| 15 | `chat: tutor reply` | Existing smoke | Non-empty assistant ≥20 chars | P2 | `chat.spec.ts` (unify env) | Clerk |
| 16 | `rtl: plan banner 375` | `/app` HE@375 | Banner + CTA usable; no clipped % / overflow | P2 | `plan-readiness.building.spec.ts` | Clerk + seed |
| 17 | `en: readiness copy` | Locale EN → `/app` | EN needs-mock string | P2 | `plan-readiness.building.spec.ts` | Clerk + seed |
| 18 | `onboarding: plan &lt;10s or plan-setup` | Fresh user onboarding submit | `has_plan` or `/plan-setup` recovery; no infinite Creating… | P1 | `onboarding-plan.spec.ts` | Clerk + disposable user |
| 19 | `wellbeing: load not bar` | High-anxiety profile vs baseline | Fewer concepts/week; pass threshold text/behavior unchanged | P2 | `persona-wellbeing.spec.ts` | Clerk + seed |
| 20 | `infra: fix orphan e2e` | Point `testDir` or move specs; one Clerk env | `pnpm e2e` runs public + gated suites | P1 | `playwright.config.ts` | none |

**seed_variant:** `building`

---

## 3. Reporter — Findings

### Status honesty

| Category | Result |
|----------|--------|
| Specs executed this round | **0** |
| Passes claimed | **0** (none fabricated) |
| Failures observed in browser | **N/A** — not run |
| Coverage / process findings | Below — from repo + ADR map only |

### Functional / coverage blockers (not taste)

| ID | Sev | Finding | Locale / viewport | Repro (when execute) | Evidence |
|----|-----|---------|-------------------|----------------------|----------|
| UI-01 | **P0** | ADR-0010 weekly gate has no Playwright coverage | HE@1280 | Seed building → `/app` → start week quiz → assert kinds / pass-fail | Only `tests/e2e/chat.spec.ts` exists |
| UI-02 | **P0** | Mock-capped readiness + needs-mock banner untested | HE/EN @375+1280 | Seed building → `/app` → assert ~70% + copy | `PacingBanner` in `learning-plan-dashboard.tsx`; manual plan row #2 |
| UI-03 | **P0** | Mock exam → readiness ungate → My Tests untested | HE@1280 | Pass mock → reload `/app` + `/app/tests` | Routes exist; no e2e |
| UI-04 | **P1** | Playwright config ignores `apps/web/e2e/`; Clerk env split | n/a | Run `pnpm e2e` — orphan specs never load | `playwright.config.ts` `testDir: './tests/e2e'` |
| UI-05 | **P1** | No `data-testid` hooks on critical ADR controls | HE/EN | Grep `data-testid` in `apps/web/src` → empty | Selector fragility for #4–13 |
| UI-06 | **P1** | Soft-override / remediation carry-forward has no learner-visible chip | HE | Fail 3× → week advances but no “remediation” affordance | ADR-0010 “Notes / known gaps”; backend-only |
| UI-07 | **P1** | Onboarding golden-path timeouts historically UI-blocking; still no E2E | HE | New user submit; watch Creating… / plan-setup | `diagnostic-plan-golden-path` skill |
| UI-08 | **P2** | Browser KaTeX smoke missing (CI lint ≠ UI) | HE lesson | Open math lesson; look for red error box | `math-notation-integrity` |

### Taste notes (non-blocking)

| ID | Note |
|----|------|
| T-01 | Deferred “pass to continue” on plan card — product clarity, not a functional gate bug |
| T-02 | Pacing banner density on 375 may feel cramped — verify in execute #16; polish only unless CTA unusable |
| T-03 | Dual quiz entry points (`/app/quiz` custom vs week gate) — IA clarity for pilot; document in walkthrough |

### Screenshot placeholders (for execute iteration)

```
docs/qa/rounds/2026-07-21-adr0010-building/artifacts/
  01-app-readiness-building-he-1280.png
  02-app-readiness-building-he-375.png
  03-week-quiz-kinds-he.png
  04-gate-fail-critical-floor.png
  05-gate-pass-week2.png
  06-mock-pass-readiness.png
  07-my-tests-mock.png
  08-lesson-math-katex.png
```

_(Directory not created — plan-only.)_

### Recommendations (next execute iteration)

1. Unify Playwright layout + Clerk env; promote public smoke into `tests/e2e/`.
2. Add `data-testid`s: `pacing-readiness`, `pacing-note`, `start-week-quiz`, `mock-exam-start`, `tests-archive-row`.
3. Automate checks #4–13 against seed `building` before claiming ADR-0010 UI green.
4. Keep taste / deferred chips out of unblock criteria.

---

## Footer

seed_variant: building  
round_id: 2026-07-21-adr0010-building
