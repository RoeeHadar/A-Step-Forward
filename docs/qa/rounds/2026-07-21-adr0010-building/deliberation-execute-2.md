# Deliberation Brief (Post-Execute) — iteration 2

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (locked — matches `docs/qa/rounds/current.json`) |
| Iteration | **2 of max 4** |
| Mode | Post-execute deliberation (after QA-B03/B11 live + Integration #8–11/#16 Neon boundary) |
| Crew | DeliberationCrew (5 advocates + facilitator) |
| Prior briefs | `deliberation.md` (plan-only); `deliberation-execute-1.md` — **not overwritten** |
| Binding decision | **None** — Coordinator owns sign-off |

This brief is **non-binding**. Suggestions below are for Coordinator deliberation only.

---

## Advocate briefs (sequential) — given EXECUTED evidence

### Integration Advocate

**Agreements:** Neon connectivity unblocked vs iter-1 (`SELECT 1` OK). Checks **#8–11/#16 PASS** at DB/API-boundary SQL: `building` fingerprint, readiness ≤70% without mock, fail-gate no advance, **gate pass → week 1 completed + week 2 active**, lesson exposure ≠ week complete. Aligns with Product QA’s live gate **submit** half of B11 (`passed=true`, 92%). Variant lock intact; post-mutation re-seed was intentional hygiene.

**Challenges:**
- **DB-boundary ≠ live UI journey:** #11 PASSed `markWeekCompleted` + advance SQL, but QA-B11 week-advance observation was **contaminated** by Integration’s post-#11/#16 `building` re-seed (week_id / plan state raced). Do not merge “SQL advance green” into “pilot UI advance confirmed.”
- **Clerk HTTP still open:** Checklist wording for #10/#11/#16 still lacks authenticated route round-trips — remaining coverage gap, not a FAIL this pass.
- **Cross-suite race is process P0:** Shared pilot Neon + parallel mutators without serialize/hand-off → false PARTIAL/inconclusive on B11. Escalate coordination, not product logic, for that half.

**≤3 recommendations:**
1. Treat #8–11/#16 DB PASSes as **strong evidence** Stream A gate math works at Neon; still require **isolated** QA-B11 UI reload (no concurrent reseed) before calling advance green.
2. Serialize iter-3: Integration mutators **after** QA finishes B11 observe, or use a freeze / “do not reseed until QA ack” window.
3. Optional follow-on: Clerk HTTP for #13/#16 — parallel, not blocking mock-exam fix.

**seed_variant:** `building`

---

### UI / E2E Advocate

**Agreements:** Clerk signed-in production `/app` unblocked vs iter-1 — attestation and weekly-quiz UI path ran. QA-B03 is a **real product FAIL** (RSC crash on `/app/quiz/mock-exam`), not an env BLOCKED. B11 submit UI worked (92% pass surface).

**Challenges:**
- **Mock exam page is broken in production** — learner cannot sit mock → readiness ungate journey dead regardless of Neon readiness math.
- **B11 advance UI still unproven** — plan still showed week 1 after submit, but Integration reseed raced; withhold FAIL on advance until isolated re-run.
- UI suite itself still largely plan-only for Playwright twins; this execute was Product QA browser, not UI crew checklist closeout.

**≤3 recommendations:**
1. Iteration 3 **must** fix `/app/quiz/mock-exam` RSC (Stream B / frontend) before claiming mock-ungate or readiness >70% live.
2. Isolated B11: re-seed `building` once → pass gate → **hard-refresh `/app/plan` with no Integration reseed** → confirm week 2 + re-pace.
3. Keep taste / remediation-chip out of clean criteria.

**seed_variant:** `building`

---

### Product QA Advocate

**Agreements:** Iteration 2 moved B03/B11 off BLOCKED into honest labels: **B03 FAIL**, **B11 PARTIAL**. Attestation PASS (~70% + mock cue, week 1). Live weekly gate submit is real progress vs iter-1. Integration DB #11 supports that advance *can* work when `markWeekCompleted` runs — consistent with partial B11 (submit half green).

**Challenges:**
- **FAIL is new this round:** mock-exam RSC is a ship-blocking P0 for ADR-0010 §F mock ungate — not a flaky BLOCKED.
- **PARTIAL ≠ PASS:** Do not rebrand B11 as green from Integration SQL alone; UI advance inconclusive by process race.
- P1 Scripts 7–8 still unauthorized — correct until B03 fixed and B11 isolated pass.

**≤3 recommendations:**
1. Open **iteration 3** scoped to: (a) fix + retest QA-B03 mock ungate; (b) isolated QA-B11 advance observe; keep `building`.
2. Do **not** escalate-to-stop yet — 2/4 iterations used; one clear product FAIL + one process-contaminated PARTIAL is actionable, not stuck-env.
3. After B03 green + B11 isolated PASS, optionally authorize Scripts 7–8; still no unanimous-clean until those land or are explicitly deferred.

**seed_variant:** `building`

---

### Security Advocate

**Agreements:** Live gate submit exercised production path touching `test_attempts` / weekly submit — good for integrity story. Integration #11 used `markWeekCompleted` with learner join (F4 shape). Variant lock OK. No new exploit work this pass.

**Challenges:**
- F1 (custom-quiz client keys) / F2 (chat pre-filter) remain open from prior brief — parallel debt, not cleared by iter-2 execute.
- Mock-exam RSC crash is availability/integrity UX failure on a scored path; fix PR should get normal review; if mock route auth/body changes, pair light defensive IDOR glance.
- Shared-account reseed races can confuse audit trails of attempts — process hygiene for pilot Neon.

**≤3 recommendations:**
1. Do not block iter-3 ADR fix on F1/F2 — keep Security parallel track.
2. On mock-exam fix PR: confirm no client `learner_id` / forgeable attempt ownership regressions.
3. After isolated B11: optional defensive IDOR matrix still queued, not required for mock-exam triage.

**seed_variant:** `building`

---

### Evals Advocate

**Agreements:** Binding bar remains web Vitest + manual/`building` evidence. Integration DB PASSes + QA live submit strengthen Stream A confidence without promoting LLM baselines. No fabricated evals.

**Challenges:**
- Mock-exam RSC will not show in calibration Vitest — need regression coverage once root cause known (route/component test or smoke).
- Do not cite soft `evals.yml` / stale reports as green.
- Mentor/Reviewer LLM gaps still secondary while B03 FAIL open.

**≤3 recommendations:**
1. Still **no baseline promote**.
2. After mock-exam fix: add/extend a focused unit or route smoke so RSC regresses in CI.
3. Prefer existing ADR Vitest green as gate; no new LLM eval invention this round.

**seed_variant:** `building`

---

## Facilitator synthesis

### Agreements

1. **Variant lock intact:** `current.json`, QA/Integration footers, live attestation — all **`building`**. **No CRITICAL mismatch.**
2. **Honest ledger:** B03 upgraded BLOCKED → **FAIL** (production RSC). B11 upgraded BLOCKED → **PARTIAL** (submit PASS; advance inconclusive). Integration #8–11/#16 **PASS** at Neon boundary. Zero fabricated passes.
3. **Stream A gate math largely corroborated:** fail-no-advance + pass-advance work at DB; live UI achieved `passed=true` / 92%.
4. **Stream B / mock path is broken in production:** `/app/quiz/mock-exam` RSC crash blocks readiness ungate journey.
5. **Process conflict explained:** Integration reseed after mutating checks raced QA-B11 plan observe — advance UI not confirmed, not necessarily product FAIL.
6. **Unanimous-clean cannot be claimed** — B03 FAIL; B11 incomplete; Clerk HTTP / UI Playwright still open; Security F1/F2 prior debt.
7. **No baseline promote** — unchallenged.

### Conflicts

| Topic | Positions | Facilitator note (non-binding) |
|-------|-----------|--------------------------------|
| **Does Integration #11 close QA-B11?** | Integration: advance SQL PASS. Product QA: UI advance PARTIAL / inconclusive. | **Compatible if labeled split:** DB path green; **UI journey still open**. Prefer isolated B11 retest over declaring FAIL or PASS on advance. |
| **Iteration 3 fix vs escalate-to-stop** | QA/UI: fix mock-exam + isolated B11. Env escalate less urgent (Clerk+Neon worked). | Facilitator **leans open iteration 3** for product fix + isolated observe — not escalate-to-stop. Escalate only if mock fix stalls or races persist without serialize. |
| **Is B03 a frontend-only bug?** | UI/QA: RSC on mock-exam page. Integration: mock archive routes exist; not retested this scope. | Triage in apps/web mock-exam route/page; Integration can smoke post-fix if needed. |
| **Burn iteration on process race?** | Integration: reseed was correct hygiene. QA: contaminated advance. | Both right — **serialize** next execute; do not spend a full iteration only on blame. |

### Variant lock

| Check | Result |
|-------|--------|
| `current.json` `seed_variant` | `building` |
| QA / Integration execute footers | `building` |
| Live attestation (iter 2) | `/app/plan` ~70% + mock cue; Integration seed fingerprint phase `building` |
| Mismatch / wrong-variant evidence | **None** |
| **CRITICAL seed_variant mismatch?** | **No** |

### What PASSED

| Suite | Passed (EXECUTED iter 2) |
|-------|--------------------------|
| Product QA | Attestation; B11 **submit half** (92%, `passed=true`) |
| Integration | #8, #9, #10, #11, #16 (Neon DB/API-boundary) |
| UI / Security / Evals | — (not primary executors this pass; prior iter-1 unit/security track unchanged) |

### What FAILED / PARTIAL / still open

| Suite | Status |
|-------|--------|
| Product QA | **QA-B03 FAIL** — `/app/quiz/mock-exam` RSC “Something went wrong” |
| Product QA | **QA-B11 PARTIAL** — advance / re-pace UI inconclusive (Integration reseed race) |
| Integration | Clerk-authenticated HTTP for #10/#11/#13/#16 still open |
| Prior carry | Security F1/F2; UI Playwright ADR twins; Evals LLM harness; P1 Scripts 7–8 |

### Suggestions for Coordinator (non-binding)

1. **Do not declare unanimous-clean.**
2. **Prefer open iteration 3** (not escalate-to-stop): scope =
   - **Fix** production `/app/quiz/mock-exam` RSC → re-run **QA-B03** (mock ≥60% → readiness ungate + My Tests).
   - **Isolated QA-B11:** single `building` seed → gate pass → observe `/app/plan` week advance **with Integration freeze / no reseed until QA ack**.
3. **Escalate** (hold / manager) only if: mock-exam root cause unclear after one fix attempt, or shared-Neon races cannot be serialized — not as default given 2/4 and clear FAIL target.
4. **Keep `building` lock.** Do not flip variant to work around mock crash.
5. Treat Integration #11 as **supporting evidence**, not a substitute for B11 UI PASS.
6. Security F1/F2 remain parallel — do not block mock-exam fix.
7. **Circuit breaker:** **2 / 4**. Actionable product FAIL + process-fixable PARTIAL → iterate; avoid plan-only churn.

### Unanimous-clean?

**no**

Rationale: QA-B03 **FAIL**; QA-B11 not fully green; Integration HTTP auth gaps remain; prior Security/UI/Evals open items; process race prevented clean advance confirm.

---

## Facilitator closing

Binding decision: **reserved for Coordinator**.

**Non-binding summary for Coordinator:** Iteration 2 delivered first **product FAIL** (production mock-exam RSC) and a **PARTIAL** B11 (live 92% gate pass; week advance inconclusive due to Integration reseed race). Integration #8–11/#16 **PASS** at Neon DB boundary — including gate pass→advance SQL — so Stream A logic looks sound; do **not** equate that with UI journey clean. Variant lock OK (`building`). **Unanimous-clean: no.** Suggest **iteration 3** = fix mock-exam + isolated B11 UI advance (serialize suites); escalate-to-stop only if fix/race control fails. Iteration **2 of 4**.

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
