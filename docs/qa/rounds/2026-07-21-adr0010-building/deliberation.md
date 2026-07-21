# Deliberation Brief — 2026-07-21-adr0010-building

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (locked — matches `docs/qa/rounds/current.json`) |
| Iteration | **1 of max 4** |
| Mode | Plan + report only (all five suites: **0 EXECUTED**) |
| Crew | DeliberationCrew (5 advocates + facilitator) |
| Binding decision | **None** — Coordinator owns sign-off |

This brief is **non-binding**. Suggestions below are for Coordinator deliberation only.

---

## Advocate briefs (sequential)

### Integration Advocate

**Agreements with peers:** Shares Product QA / UI priority on hard gate, lesson≠advance, and `building` readiness fingerprint. Accepts Evals’ claim that Vitest calibration is the current automated ground truth — but insists that **unit green ≠ pilot green** without Neon/HTTP contracts. Aligns with Security that weekly gate ownership must be exercised under auth.

**Challenges:**
- **Security F1 (custom-quiz client keys):** Integrity issue is real, but for *this* round’s ADR-0010 `building` focus the weekly gate / mock-exam paths are the progression spine. Do not let custom-quiz remediation crowd out Neon gate-advance harness unless Coordinator expands suite focus.
- **UI elevating remediation-chip absence to P1 (UI-06):** Backend soft-override is an Integration/QA contract; missing chip is polish (ADR notes deferred). Severity inflation risks blocking on taste.
- **FastAPI `test_integration.py` green:** Must not be read as ADR-0010 coverage (I-P1-3). Security’s positive FastAPI RBAC notes are orthogonal to Vercel+Neon.

**≤3 recommendations:**
1. Authorize local execute of Integration checks **1–5, 19** (no secrets), then **8–16** on approved dev Neon — prioritize gate fail/pass → `advanceRollingPlanWindow` + lesson non-advance.
2. Add `seed-pilot-demo.mjs --assert` (or equivalent) for `building` fingerprint (phase, mock-cap readiness).
3. Label CI so Phase-1 FastAPI integration is not mistaken for pilot gate.

**seed_variant:** `building`

---

### UI / E2E Advocate

**Agreements:** Zero Playwright for weekly gate / readiness banner / mock ungate is a true functional coverage hole (UI-01–03), not taste. Aligns with Product QA Scripts 1–6 as the manual twin of proposed specs. Supports Integration’s lesson≠advance E2E.

**Challenges:**
- **Product QA / ADR “deferred chips” vs UI-06 P1:** Soft-override *behavior* (advance + weak carry) is P0/P1 product; absence of a remediation chip is **non-blocking** (T-01). Downgrade chip gap for unblock criteria.
- **Integration P0 Neon harness vs UI P0 Playwright:** Both needed; prefer shared seed + `data-testid`s so one building seed serves API and browser execute. Do not serialize forever on “API first” if Coordinator wants pilot walkthrough confidence.
- **Taste notes (T-02/T-03):** Explicitly out of unanimous-clean criteria.

**≤3 recommendations:**
1. Unify Playwright `testDir` + Clerk env; add `data-testid`s on pacing/quiz/mock/tests before hardening specs.
2. Execute plan checks **#4–13** against seed `building` (HE@1280 primary) in a later iteration after attestation.
3. Keep taste / deferred chips out of unblock; pair banner copy asserts with QA-B02/B03.

**seed_variant:** `building`

---

### Product QA Advocate

**Agreements:** ADR-0010 `building` matrix rows #2–3, #9–14, #16 are correctly prioritized across Integration/UI. Lesson-complete ≠ week advance (QA-B09) must not be forgotten. Variant lock respected; multi-variant cases deferred.

**Challenges:**
- **Security Critical custom-quiz / chat moderation:** Valid safety findings, but Product QA’s P0 scripts are gate/mock/readiness. Coordinator should track Security remediations on a parallel track without delaying Scripts 1–6 execute authorization.
- **QA-ONB needs `fresh` or alt Clerk user:** Conflicts with locked `building` seed — not a suite error; needs Coordinator unlock or secondary account (do not flip `current.json` mid-round casually).
- **Evals “Vitest + manual = binding bar”:** Agree for *this* iteration’s honesty, but Product QA still requires **executed** Scripts 1–6 before any “ADR-0010 pilot clean” narrative.

**≤3 recommendations:**
1. Authorize execute pass: Scripts **1–6 (P0)** first on attested local `building` seed; then 7–8 (P1).
2. Keep variant lock; schedule QA-ONB on secondary user or approved `fresh` window.
3. Pair execute results with UI (banner/CTA) + Integration (API payloads) + Security (quiz IDOR) before claiming clean.

**seed_variant:** `building`

---

### Security Advocate

**Agreements:** Cross-suite need for automated ownership/IDOR on quiz/plans/chat. `markWeekCompleted` missing learner join (F4) is a real defense-in-depth risk for ADR advancement — Integration’s gate HTTP checks should assert tenant isolation, not only pass/fail math. PII + moderation gaps on Neon-direct path are in-scope for pilot chat/onboarding.

**Challenges:**
- **Other suites under-weight F1:** Custom quiz trusting client keys is **Critical/High** integrity — if any pilot or readiness path consumes custom/mock-adjacent scores, ADR signals are forgeable. Weekly-gate-only focus is incomplete for integrity.
- **UI/Product treating chat as P2:** Web chat has **no** SafetyModeration pre/post (F2) while agents package tests exist — escalate relative to “continuity only” framing (QA-CHAT / I-P1-2).
- **Speculative exploit framing:** Reject; findings are static review only. No live probes this iteration — do not invent EXECUTION results.

**≤3 recommendations:**
1. Remediate server-side custom quiz storage + answer-only submit; strip keys from start payload (mirror weekly `buildClientResponse`).
2. Add learner_id join on `markWeekCompleted`; never prefer client `plan_id` over owned quiz row.
3. Queue automated IDOR matrix (checks #2–7, #10) + chat rule-based pre-filter + PII hygiene on onboarding/chat writes; run `review-security` on those PRs.

**seed_variant:** `building`

---

### Evals Advocate

**Agreements:** ADR-0010 truth today is web Vitest + manual `building` plan — not promptfoo/DeepEval. Oppose any baseline promote this round. Aligns with Integration: calibration units are necessary but insufficient for journey coverage. Mentor/Reviewer suite absence matters if those paths are exercised in pilot.

**Challenges:**
- **“CI soft evals = coverage”:** `evals.yml` `continue-on-error` can false-green; do not cite tutor promptfoo as ADR attestation.
- **Security/Product severity on agent gaps:** For locked `building` focus, Mentor day-before / at-risk evals are secondary to gate/readiness units + manual Scripts 1–6 — escalate only if Coordinator enables those streams mid-round.
- **Expanding LLM harness this iteration:** Wrong leverage; prefer TOUCH_MAP for ADR web libs + execute existing units.

**≤3 recommendations:**
1. Treat web ADR calibration tests + `adr-0010-manual-test-plan.md` (`building`) as the binding QA bar until LLM evals catch up — **no baseline promote**.
2. Expand `TOUCH_MAP` / CI path filters to `plan-pacing`, `readiness`, `weekly-quiz`, `gate-question-bank`, `lesson-complete`.
3. Later (not binding this iter): gate/readiness eval packages; Mentor/Reviewer templates; mock providers for grader/assessment_generator.

**seed_variant:** `building`

---

## Facilitator synthesis

### Agreements

1. **Variant lock intact:** All five reports attest `seed_variant: building` matching `current.json`. **No CRITICAL variant mismatch.**
2. **Honesty ledger:** Every suite is plan-report-only; **EXECUTED = 0**; no fabricated passes. Unanimous-clean cannot be claimed from planning alone.
3. **Shared P0 product spine for `building`:** Mock-capped readiness (~70% + needs-mock), mock ungate, weekly gate critical-floor fail, gate pass → advance, lesson complete ≠ advance, retake rotation — covered consistently by Integration / UI / Product QA matrices.
4. **Automated gap shape:** Strong pure-logic Vitest; weak Neon-direct HTTP, Playwright ADR flows, and `evals/` LLM harness for progression. FastAPI Phase-1 integration is orthogonal.
5. **Security integrity themes accepted in principle:** Tenant ownership on gate advancement, missing web IDOR automation, Neon-path PII/moderation weaker than FastAPI memory path.
6. **No baseline promote** (Evals) — unchallenged.
7. **Deferred multi-variant / taste / remediation-chip UX** should not block iteration-1 execute of the `building` P0 scripts.

### Conflicts

| Topic | Positions | Facilitator note (non-binding) |
|-------|-----------|--------------------------------|
| **Custom-quiz client keys (Sec F1) vs weekly-gate-first focus** | Security: Critical/High, fix before pilot expansion. Integration/QA: primary spine is weekly gate/mock. | Track as parallel High integrity debt; do not drop — but Coordinator may sequence after or beside Scripts 1–6. |
| **Chat: moderation (Sec F2 High) vs continuity P1/P2** | Security escalates missing SafetyModeration on web chat. Integration/QA treat chat as secondary to gates. | Real conflict on priority, not on facts. Suggest Security+Agents track without claiming ADR gate blocked solely by chat. |
| **Remediation chip (UI-06 P1) vs deferred polish** | UI listed P1; QA/ADR notes + UI taste section say non-blocking. | Treat **behavior** (soft override + weak carry) as P1; **chip** as non-blocking. |
| **What is “binding bar” this round?** | Evals: Vitest + manual plan. Integration/QA/UI: also need executed Neon/HTTP/E2E before “clean.” | Compatible if phrased: units bind *math*; executed Scripts 1–6 + key Integration/UI checks bind *pilot journey*. |
| **Onboarding golden path** | QA-ONB / UI P2 need `fresh` or alt user; lock is `building`. | Process conflict only — needs Coordinator unlock, not a report error. |

### Variant lock check

| Check | Result |
|-------|--------|
| `current.json` `seed_variant` | `building` |
| integration.md / ui.md / qa.md / security.md / evals.md | All echo `building` |
| Mismatch / wrong-variant evidence cited | **None** |
| Live attestation before execute | Still required (`variant_lock.live_attestation_required_before_execute`) |
| **CRITICAL seed_variant mismatch?** | **No** |

### Suggestions for Coordinator (non-binding)

1. **Do not declare unanimous-clean** after iteration 1 — zero suites executed; Security static findings remain open.
2. **Authorize a local execute slice** after live seed attestation (`--variant building` on disposable/dev Neon): Product QA Scripts 1–6 + Integration checks 1–5/8–11/16 + optional UI readiness/gate smoke once Clerk secrets available.
3. **Keep `current.json` on `building`**; use a second Clerk user or a dedicated window for onboarding (`fresh`) rather than flipping the round mid-flight.
4. **Queue Security remediations** (custom quiz server keys, `markWeekCompleted` learner join, chat pre-filter + PII) with `review-security` on those PRs — parallel to ADR execute, not silently deferred forever.
5. **CI hygiene:** TOUCH_MAP for ADR web libs; avoid treating FastAPI integration or soft `evals.yml` as pilot attestation; no eval baseline promote.
6. **Circuit breaker:** This is iteration **1 / 4**. Prefer execute + targeted fixes over another pure planning loop unless Coordinator needs scope clarification on Security vs gate sequencing.

### Unanimous-clean?

**no**

Rationale: Plan-only pass across all suites; open P0 coverage gaps (Neon/HTTP/E2E); open Security Critical/High static findings; no executed green attestation for ADR-0010 `building` journey.

---

## Facilitator closing

Binding decision: **reserved for Coordinator**. This document records agreements, conflicts, and suggestions only. Iteration 1 of 4 complete for Deliberation; Tester execute and Coordinator sign-off remain pending.

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
