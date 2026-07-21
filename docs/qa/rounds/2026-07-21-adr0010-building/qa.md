# Product QA Report — ADR-0010 / Pilot

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Suite | Product QA (scenario designer → executor → reporter) |
| Focus | pilot + ADR-0010 |
| Target env | local |
| Mode | **EXECUTE authorized** (Scripts 1–6; iteration 1 Coordinator decision) |
| Charter lock | `docs/qa/rounds/current.json` → `seed_variant: building` ✓ |
| Iteration | 1 / 4 |

## Charter attestation

- Read `current.json`: `seed_variant` = **building** (matches charter; proceeded).
- Grounded in: `docs/qa/adr-0010-manual-test-plan.md`, ADR-0010, `use-learning-plan`, `diagnostic-plan-golden-path`, `onboarding-flow`, `scripts/seed-pilot-demo.mjs`, vault `_active-context` (pilot seeded building).
- **Live seed + Neon fingerprint (iteration 1 execute):** `node scripts/seed-pilot-demo.mjs --variant building` → PASS. DB attest: goal `bagrut_math_5`, critical ≈81.8%, readiness displayed **70%**, `passedMocks=0`, phase `building`, multi-week plan (week 1 active + upcoming). Pilot `user_3Fakzy…`. Browser MCP unavailable (no signed-in `/app` session) — UI banner not visually confirmed.

---

## Setup (mandatory before any execute pass)

```powershell
# Local / corp-proxy TLS only — never commit DATABASE_URL
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
$env:DATABASE_URL='<Neon URL from local secrets>'
node scripts/seed-pilot-demo.mjs --variant building
# Optional wellbeing case:
# node scripts/seed-pilot-demo.mjs --variant building --anxiety 8
$env:DATABASE_URL=$null; $env:NODE_TLS_REJECT_UNAUTHORIZED=$null
```

**Fingerprint after seed (`building`):**

- Goal: `bagrut_math_5`; ~82% critical mastered; ~8wk deadline; **no** passed mock.
- Display readiness **capped ~70%** + “sit a mock exam” note; phase = `building`.
- Active multi-week plan (week 1 active, upcoming weeks) — richest interactive start for gates/retakes.
- Pilot account: `roeehadar@gmail.com` (or `--user-id` / `--email` override).
- Hard-refresh `/app` after every seed. One account = one state; re-seed to reset.

**Prod-destructive flag:** seeding writes mastery + plan + clears passed mocks for the target learner. Safe for the designated pilot account; **do not** point at unrelated production users.

**Unit sanity (optional pre-flight, not a substitute for UI):**  
`pnpm --filter @asf/web test` — especially `assessment-calibration.test.ts` / gate invariants.

---

## Scenario matrix (≤16, prioritized)

Prioritize ADR-0010 rows whose **Variant** column is `building`. Other-variant cases are deferred (Coordinator unlock required).

| ID | P | ADR link | Variant | Steps (summary) | Expected outcome | Status |
|----|---|----------|---------|-----------------|------------------|--------|
| QA-B02 | P0 | ADR-0010 §F #16 / matrix #2 | building | Open `/app`, read pacing/readiness banner | Readiness capped ~70%; mock-gate note (“sit a mock”); never 100% | EXECUTED — PASS (Neon+unit; UI visual blocked) |
| QA-B03 | P0 | ADR-0010 §F #16 / matrix #3 | building | Sit mock from `/app`, score ≥ 60%; reload | Readiness rises above 70%; note changes; mock in **My Tests** | EXECUTED — BLOCKED (no signed-in mock UI) |
| QA-B09 | P0 | ADR-0010 §A #4 / matrix #9 | building | Mark all week-1 lessons complete; reload `/app` | Week does **not** advance; still week 1 (exposure only) | EXECUTED — PASS (DB exposure sim) |
| QA-B10 | P0 | ADR-0010 §A #3 / matrix #10 | building | Week-1 quiz: high aggregate, miss ≥1 critical topic | Gate **fails** (critical floor 0.6) despite good average | EXECUTED — PASS (unit) |
| QA-B11 | P0 | ADR-0010 §A #1–3 / matrix #11 | building | Pass week-1 quiz (agg ≥ 0.75, all critical ≥ 0.6); reload | Week 1 completed; advances to week 2; concepts re-paced | EXECUTED — BLOCKED (no live gate submit) |
| QA-B12 | P0 | ADR-0010 §B #6 / matrix #12 | building | Fail week-1 quiz; immediate retake | Retake shows **fresh** bank items (anti-gaming), not identical set | EXECUTED — PASS (unit+wiring) |
| QA-B10b | P1 | ADR-0010 §B #5 / matrix #10b | building | Open week-1 quiz **before** studying | Majority open/numeric/short_answer from lesson bank; not trivial MCQ breeze | PLANNED |
| QA-B13 | P1 | ADR-0010 §A #2 / matrix #13 | building | Fail with weak critical; advance via soft override | Weak concept(s) carried into next week | PLANNED |
| QA-B14 | P1 | ADR-0010 §A #1 / matrix #14 | building | Fail weekly gate 3× without passing | Soft override advances; weak topics carried forward | PLANNED |
| QA-B16 | P1 | ADR-0010 §E #15 / matrix #16 | building + `--anxiety 8` | Compare weekly concept load vs baseline building | Fewer new concepts when wellbeing bias on; **pass thresholds unchanged** | PLANNED |
| QA-ONB | P2 | Golden path / onboarding-flow | fresh* | 4-step onboarding → plan on `/app` | `has_plan` <10s; rolling 2 weeks × ≤4 concepts; no diagnostic gate | PLANNED (needs `fresh` or new user — **variant unlock**) |
| QA-CHAT | P2 | Pilot continuity | building | Tutor/Mentor chat turn → reload → same agent | Memory/persona continuity; no cross-agent private-note leak | PLANNED |
| QA-X04 | P2 | Matrix #4 concave | fresh/building/near-exam | Compare readiness across three seeds | ~0% → ~70% → ~95%; top gains smaller | DEFERRED (multi-variant) |
| QA-X01 | P2 | Matrix #1 humble 100% | near-exam | Banner | ~95%, not 100% | DEFERRED |
| QA-X07 | P2 | Matrix #7 behind pace | at-risk | Badge | Amber “Behind pace” | DEFERRED |
| QA-X15 | P2 | Matrix #15 Tests archive | near-exam | My Tests → mock detail | Kind label, pass/fail, per-topic bars | DEFERRED |

\*Onboarding path intentionally conflicts with locked `building` seed; Coordinator must authorize a temporary `fresh` flip or a separate Clerk test user.

---

## Executable scripts (top ≤8 P0/P1)

All scripts assume prior setup: `node scripts/seed-pilot-demo.mjs --variant building` and hard-refresh `/app` while signed in as the pilot learner. Echo: **seed_variant = building**.

### Script 1 — QA-B02: Mock-gated readiness (P0)

1. Seed `building`; open `/app`.
2. Locate readiness / pacing banner.
3. **Pass:** displayed readiness ≈ 70% (trend OK if ± small drift); copy references sitting a mock; value ≠ 100%.
4. **Fail signals:** readiness > ~75% without a mock; “exam ready / guaranteed”; missing mock cue.

### Script 2 — QA-B03: Mock ungates readiness (P0)

1. From seeded `building`, start a mock exam from `/app` (or product mock entry point).
2. Complete with score ≥ 60% (pass mock).
3. Reload `/app`; open **My Tests**.
4. **Pass:** readiness > 70%; mock-gate note gone or replaced; mock listed in archive with pass.
5. **Fail signals:** still capped at 70%; mock missing from archive; readiness 100%.
6. **Reset:** re-seed `--variant building` (clears passed mocks).

### Script 3 — QA-B09: Lessons ≠ advancement (P0)

1. Seed `building`; note active week number and concept list (week 1).
2. Open each week-1 lesson; mark complete / “done reading” for all.
3. Reload `/app` (and/or fetch current plan).
4. **Pass:** still on week 1; week status not `completed` via lesson path; mastery may show exposure (~0.35) but plan did not advance.
5. **Fail signals:** week auto-completed; week 2 becomes active solely from lesson completes (`maybeCompleteActiveWeek` regression).

### Script 4 — QA-B10: Critical-floor gate fail (P0)

1. Seed `building`; open week-1 weekly gate/quiz.
2. Answer so overall score looks strong but **at least one frontier-critical concept** in the gate scores &lt; 0.6.
3. Submit.
4. **Pass:** `passed = false`; UI/API surfaces failed critical; week does not advance.
5. **Fail signals:** gate passes on aggregate alone; week advances despite failed critical.

### Script 5 — QA-B11: Gate pass → advance + re-pace (P0)

1. Re-seed `building` (clean week-1).
2. Take week-1 gate; achieve aggregate ≥ 0.75 **and** every assessed critical ≥ 0.6.
3. Reload `/app`.
4. **Pass:** week 1 marked completed; week 2 active; upcoming concepts reflect re-pace / mastery.
5. **Fail signals:** stuck on week 1 after true pass; two active weeks; no re-pace.

### Script 6 — QA-B12: Retake rotation / anti-gaming (P0)

1. Seed `building`; start week-1 gate; **fail** (or abandon mid-way if product counts attempt — prefer full fail submit).
2. Record item stems/ids (screenshot or copy).
3. Immediately retake the same week gate.
4. **Pass:** item set differs (rotated/fresh bank); not byte-identical question list.
5. **Fail signals:** identical stems/order on retake (gaming path).

### Script 7 — QA-B10b: Hard authored-bank mix (P1)

1. Seed `building`; open week-1 quiz **before** studying lessons.
2. Classify item kinds (MCQ vs open/numeric/short_answer).
3. **Pass:** majority non-trivial constructed-response from lesson bank; beginners cannot breeze on guessable MCQ-only.
4. **Fail signals:** near-100% trivial MCQ; items unrelated to week concepts / empty bank fallback spam.

### Script 8 — QA-B14 (+ B13 carry-forward): Soft override after 3 fails (P1)

1. Seed `building`.
2. Fail the week-1 gate **three** times (retakes exhausted), preferably with a stable weak critical topic.
3. Trigger plan fetch / reload that runs `advanceRollingPlanWindow` (or wait for overdue path if UI requires — prefer attempt-count override).
4. **Pass:** plan advances despite fails; weak concepts appear in the next week (remediation carry-forward); learner not stranded.
5. **Fail signals:** permanent block with no override; advance with **empty** weak carry-forward; silent time-only advance without attempt exhaustion.
6. **Note:** QA-B13 can be observed as the carry-forward half of this script; QA-B16 is a separate seed with `--anxiety 8` (compare `weekly_load` / concept counts; thresholds 0.75 / 0.6 unchanged).

---

## Results table (iteration 1)

| ID | Priority | Result | Label | ADR / notes |
|----|----------|--------|-------|-------------|
| QA-B02 | P0 | PASS | EXECUTED | Neon fingerprint 70% + mock-gate unit + `readiness_needs_mock` copy wired; **UI banner not visually confirmed** (browser MCP / Clerk session unavailable) |
| QA-B03 | P0 | BLOCKED | EXECUTED | Needs signed-in mock sit + reload; math-only check shows ungate ~92% but **not** live-executed |
| QA-B09 | P0 | PASS | EXECUTED | DB exposure sim on week-1 concepts: week 1 stayed `active`, week 2 not advanced; `markLessonCompleteThin` returns `week_completed: false` |
| QA-B10 | P0 | PASS | EXECUTED | Unit: critical-below-floor fails despite strong aggregate (`assessment-calibration` + `plan-pacing`); live quiz UI not run |
| QA-B11 | P0 | BLOCKED | EXECUTED | Pass criteria unit-covered; live gate submit → `markWeekCompleted` + re-pace **not** exercised without auth/UI |
| QA-B12 | P0 | PASS | EXECUTED | Unit: `pickGateQuestionsFromBank` rotation≠identical; wired via `weekly-quiz` `rotation=countGateAttempts`; live retake UI not run |
| QA-B10b | P1 | — | PLANNED | Hard bank mix (not in Scripts 1–6 authorize) |
| QA-B13 | P1 | — | PLANNED | Remediation carry-forward |
| QA-B14 | P1 | — | PLANNED | Soft override @ 3 attempts |
| QA-B16 | P1 | — | PLANNED | Wellbeing load bias |
| QA-ONB | P2 | — | PLANNED / blocked on variant | Needs fresh or alt user |
| QA-CHAT | P2 | — | PLANNED | Chat memory continuity |
| QA-X* | P2 | — | DEFERRED | Other seed variants |

**EXECUTED count:** 6 (Scripts 1–6). Results: **4 PASS / 0 FAIL / 2 BLOCKED**.  
**Known product gaps (from ADR-0010 notes, not retested):** deferred UI chips (“remediation”, “pass to continue”); numeric drift on readiness display is acceptable if gating decisions hold.

---

## Execute log — iteration 1

**When:** 2026-07-21 (Cursor Auto Product QA Executor)  
**Authority:** Coordinator binding decision in `iterations/1.md` — Scripts 1–6 only; `seed_variant` remains `building`.

### Seed / attestation

1. `DATABASE_URL` present in `apps/web/.env.local` (not in shell env); seed loads via `loadEnvLocal()`.
2. Ran `node scripts/seed-pilot-demo.mjs --variant building` (twice: pre-execute + post–B09 restore).
3. Neon fingerprint after seed:
   - goal `bagrut_math_5`, hours 10, ~55d to deadline, phase `building`
   - critical coverage ≈ **81.8%** (18/22), mastery rows 26
   - readiness displayed ≈ **70%**, `passedMocks = 0`
   - plan weeks: **1 active** (4 concepts) + **2 upcoming** (4 each)
4. **Attestation: PASS** (not BLOCKED-PENDING-SEED).
5. Browser MCP: tab create/navigate failed repeatedly (`No browser tab available` / view not found) → no signed-in `/app` UI pass.

### Unit tests

```text
pnpm --filter @asf/web test -- assessment-calibration plan-pacing gate-question-bank readiness
→ 4 files, 61 tests, all PASS (exit 0)
```

### Script outcomes (detail)

| Script | ID | Result | Evidence |
|--------|-----|--------|----------|
| 1 | QA-B02 | PASS | Live Neon 70% + no passed mock; `MOCK_GATED_CEILING=0.7`; UI copy `readiness_needs_mock` (“sit a full mock…”); readiness unit mock-gate |
| 2 | QA-B03 | BLOCKED | Cannot complete mock exam without Clerk UI; concave+ungate math only (would rise above 70%) |
| 3 | QA-B09 | PASS | Applied exposure 0.35 to week-1 concepts in Neon; week statuses unchanged; code path never completes week |
| 4 | QA-B10 | PASS | Calibration matrix: critical just below 0.6 → `passed=false` despite agg 0.95 |
| 5 | QA-B11 | BLOCKED | Gate pass→`markWeekCompleted` exists in `weekly-quiz.ts`; no live submit/reload to confirm week 2 + re-pace |
| 6 | QA-B12 | PASS | `gate-question-bank` rotation test + production `rotation` keyed by attempt count |

### Environment limits (honesty)

- No Clerk-authenticated browser session → Scripts needing `/app` interaction (esp. 2, 5) stay BLOCKED.
- Scripts 1/3/4/6 accepted on Neon + unit/code confirmation per Coordinator “as far as environment allows”.
- Re-seeded `building` after B09 exposure sim so parallel suites see a clean fingerprint.
- Scripts 7–8 (P1) **not** authorized this pass.

---

## Coordinator next actions

1. Unblock QA-B03 / QA-B11 with a signed-in local or pilot browser session (hard-refresh `/app` after seed); re-run only those IDs.
2. Keep variant lock: do **not** flip to `near-exam` / `at-risk` mid-round without updating `current.json` + all suite reports.
3. Schedule QA-ONB on a secondary Clerk user or a dedicated Coordinator-approved `fresh` window so onboarding golden path is covered without clobbering building gate tests.
4. Pair execute results with UI/Integration crews (banner copy visual, `/api` gate payloads) and Security (quiz attempt IDOR) before declaring unanimous clean.
5. If any P0 fails on live UI retest: file against Stream A (advancement/gate) or Stream B (retake/mock archive); re-seed and re-run only failed IDs within iteration budget (max 4).
6. Optionally authorize Scripts 7–8 (QA-B10b / QA-B14) after B03/B11 unblocked.

---

## Not tested (honesty)

- Live signed-in browser walkthrough of `/app` readiness banner, mock exam, or weekly gate submit/retake.
- Production Vercel smoke as a substitute for local UI (out of scope for this execute without auth).
- Cohort multi-student roster (`seed-cohort-pilot.mjs`) — separate from single-pilot ADR matrix.
- Milestone/unit-test tier and Reviewer-graded open-response budget (ADR-0010 §B deeper than weekly gate).
- Cross-variant concave curve and day-before / goal-complete pacing badges.
- Scripts 7–8 / remaining P1–P2 matrix rows.

---

## Execute log — iteration 2 (production + Clerk)

| Script | ID | Result | Evidence |
|--------|-----|--------|----------|
| — | Attestation | PASS | `/app/plan` ~70% readiness + mock cue; week 1 active after seed |
| 2 | QA-B03 | **FAIL** | `/app/quiz/mock-exam` (+ `?id=math_5pt_mock_1`) → production RSC “Something went wrong” |
| 5 | QA-B11 | **PARTIAL** | Live weekly quiz submit **92%** / `passed=true`; week advance **inconclusive** (Integration iter2 reseed raced). Isolated retest pending in same iteration. |

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
