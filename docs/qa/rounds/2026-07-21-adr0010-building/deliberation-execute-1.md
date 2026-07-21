# Deliberation Brief (Post-Execute) — iteration 1

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (locked — matches `docs/qa/rounds/current.json`) |
| Iteration | **1 of max 4** |
| Mode | Post-execute deliberation (after Scripts 1–6 + Integration local + Security F1/F2/F4 track) |
| Crew | DeliberationCrew (5 advocates + facilitator) |
| Prior brief | `deliberation.md` (plan-only) — **not overwritten** |
| Binding decision | **None** — Coordinator owns sign-off |

This brief is **non-binding**. Suggestions below are for Coordinator deliberation only.

---

## Advocate briefs (sequential) — given EXECUTED evidence

### Integration Advocate

**Agreements:** Product QA’s unit/calibration PASSes align with Integration checks #1/#3–5/#19. Security F4 (`markWeekCompleted` learner join) closes a real defense-in-depth hole Integration flagged for gate advancement. Evals’ “Vitest ≠ journey” stance is confirmed: Neon/HTTP #8–16 still **BLOCKED-PENDING-NEON**.

**Challenges:**
- **QA Neon seed PASS vs Integration `SELECT 1` fetch failed:** Same charter env, divergent connectivity outcomes. Do not treat QA’s seed fingerprint as Integration HTTP contract green — Integration’s gate fail/pass → advance and lesson HTTP (#10–11, #16) remain unproven on this host.
- **Check #2 “FAIL” labeling:** Weekly-quiz suite load fails under real `.env.local` `channel_binding=require`; logic PASSes with dummy URL. Process/env hygiene issue, not ADR math FAIL — avoid false-red narratives.
- **UI still plan-only:** Without Clerk browser, UI cannot corroborate Integration’s remaining P0s even if Neon recovers.

**≤3 recommendations:**
1. Escalate **Neon connectivity** (reachable dev URL / network) before another pure planning loop; re-run Integration #8–11 + #16 only when `SELECT 1` works.
2. Fix Vitest eager-`neon()` / `channel_binding` collect breakage so ADR unit suites stay green without dummy-URL workarounds.
3. Land F4 PR + `review-security`; keep FastAPI Phase-1 (#7) labeled orthogonal.

**seed_variant:** `building`

---

### UI / E2E Advocate

**Agreements:** QA-B03 / QA-B11 BLOCKED for lack of signed-in `/app` session validates UI-01–03 as still open. Taste / remediation-chip remain non-blocking (Coordinator downgrade stands). Browser MCP failure is an environment blocker, not a product FAIL.

**Challenges:**
- **QA-B02 PASS without visual banner:** Neon+unit evidence is real; UI advocate still withholds “banner green” until HE@1280 screenshot / Playwright check #4.
- **Do not open iteration 2 as Playwright-first** while Clerk session + Neon are both flaky — auth.setup is the unblock, not more planned specs.
- **Evals still plan-only:** Fine; UI does not need LLM evals to smoke readiness/gate once Clerk works.

**≤3 recommendations:**
1. Coordinator: provide Clerk-authenticated local (or storageState) session → re-run UI checks #4–8 + #12 twin to QA-B02/B03/B11.
2. Add `data-testid`s before hardening Playwright; unify `testDir` / Clerk env (UI-04/05) as infra PR, not blocker for unanimous-clean yet.
3. Keep taste / UI-06 chip out of clean criteria.

**seed_variant:** `building`

---

### Product QA Advocate

**Agreements:** Scripts 1–6 executed honestly: **4 PASS / 0 FAIL / 2 BLOCKED**. Live `building` seed attestation succeeded (goal, ~81.8% critical, readiness ~70%, phase `building`, multi-week plan). Spine math holds (B02/B09/B10/B12). Security parallel track did not block Scripts 1–6 as intended.

**Challenges:**
- **BLOCKED ≠ FAIL, but also ≠ clean:** B03 (mock ungate) and B11 (gate pass → advance) are the live journey heart of ADR-0010 — unit coverage alone must not rebrand as pilot clean.
- **Integration Neon BLOCKED** while QA seeded successfully: escalate env intervention; do not flip variant or invent UI results.
- **P1 Scripts 7–8** still unauthorized — correct until B03/B11 unblocked.

**≤3 recommendations:**
1. Open **iteration 2** only after Clerk session + reachable Neon intervention; re-run **only** QA-B03 + QA-B11 (and optional UI visual for B02).
2. Keep `seed_variant: building`; schedule QA-ONB on secondary user / approved `fresh` window separately.
3. Pair next execute with Integration #10–11/#16 and Security IDOR matrix — still no unanimous-clean claim.

**seed_variant:** `building`

---

### Security Advocate

**Agreements:** Parallel track delivered: **F4 FIXED** locally (learner join + no client `plan_id` fallback). F1/F2 **CONFIRMED / NEEDS-PR**. Product QA / Integration correctly did not wait on F1 for Scripts 1–6. Variant lock intact.

**Challenges:**
- **Report header drift:** Top of `security.md` still says “EXECUTED: none” / plan-only while parallel track documents F4 fix — process honesty OK if readers use the Parallel track section; Coordinator should treat F4 as executed remediation, not “none.”
- **F1 still Critical/High:** Custom-quiz client keys remain forgeable; weekly path is stronger, but integrity debt is not closed by F4 alone.
- **QA-B11 live path** will exercise `markWeekCompleted` — F4 fix should ship (PR + `review-security`) before claiming advancement ownership green in production.

**≤3 recommendations:**
1. Open PR for F4 immediately; run `review-security`; do not leave fix uncommitted across iterations.
2. Queue F1 (server-held custom quiz keys) and F2 (TS chat pre-filter) as next Security PRs — parallel to iter-2 gate UI, not dropped.
3. After Neon+Clerk: defensive IDOR checks #4–7/#10 (no exploit payloads).

**seed_variant:** `building`

---

### Evals Advocate

**Agreements:** Execute confirmed binding bar = web Vitest + manual/scripted `building` evidence. No baseline promote. Product QA’s 61 ADR-related unit PASSes match planned checklist #1. UI/Evals remain plan-only — expected.

**Challenges:**
- **Do not cite soft `evals.yml` or stale `evals/report.md` as post-execute green.**
- **Integration env FAIL on weekly-quiz collect** is infra, not a reason to weaken calibration pins.
- Mentor/Reviewer suite gaps stay secondary while B03/B11 blocked.

**≤3 recommendations:**
1. Still **no baseline promote**.
2. Expand `TOUCH_MAP` / CI filters to ADR web libs when convenient (non-blocking for iter-2 unblock).
3. Prefer re-running existing Vitest after F4 PR over inventing LLM gate evals this round.

**seed_variant:** `building`

---

## Facilitator synthesis

### Agreements

1. **Variant lock intact:** All five suite reports + `current.json` echo `seed_variant: building`. **No CRITICAL variant mismatch / drift.**
2. **Honesty ledger improved:** Product QA Scripts 1–6 and Integration local checks were actually run; UI + Evals remain plan-only (no fabricated browser/LLM passes). Security parallel track: F4 fixed, F1/F2 still open.
3. **Partial P0 spine green (math/DB where possible):** QA-B02 (Neon fingerprint + units), B09 (exposure ≠ advance), B10 (critical floor), B12 (retake rotation) **PASS**; Integration calibration/lint/tsc/bootstrap anti-pattern **PASS**.
4. **Shared remaining blockers are environmental:** Clerk-authenticated browser session (QA-B03/B11, UI P0s) and Integration host Neon HTTP `fetch failed` (checks #8–16) — not product FAILs observed this pass.
5. **Security progress real but incomplete:** F4 FIXED (local); F1/F2 NEEDS-PR; no live IDOR probes.
6. **No baseline promote** — unchallenged.
7. **Unanimous-clean cannot be claimed** — P0 live journey paths still BLOCKED; F1/F2 open; UI/Evals not executed.

### Conflicts

| Topic | Positions | Facilitator note (non-binding) |
|-------|-----------|--------------------------------|
| **Neon reachable?** | Product QA: seed + fingerprint PASS. Integration: `SELECT 1` → `fetch failed`, #8–16 BLOCKED. | Real env conflict. Prefer escalate connectivity / shared probe recipe over blaming either suite. Do not merge “QA seeded” into “Integration Neon contracts green.” |
| **Is B02 “PASS” enough without UI?** | QA: PASS on Neon+unit+copy wiring. UI: visual/Playwright still open. | Compatible if labeled **partial** — journey clean needs banner smoke later. |
| **Iteration 2 vs escalate first** | QA/UI lean: need Clerk+Neon before more scripts. Integration: Neon net + Vitest URL hygiene. Security: ship F4 PR now. | Facilitator recommends **escalate env intervention first**, then open iteration 2 for B03/B11 + Integration #8–11/#16 — not another plan-only loop. |
| **F1 priority vs gate UI** | Security: still Critical/High. Others: parallel OK. | Unchanged from plan-only brief — parallel track continues; F4 landed, F1/F2 next. |
| **security.md mode header** | Header says EXECUTED none; body has F4 FIXED. | Not variant drift — documentation inconsistency. Treat Parallel track as authoritative for F1/F2/F4 status. |

### Variant lock

| Check | Result |
|-------|--------|
| `current.json` `seed_variant` | `building` |
| integration / ui / qa / security / evals footers | All `building` |
| Live seed attestation (QA execute) | `--variant building` → PASS fingerprint |
| Mismatch / wrong-variant evidence | **None** |
| **CRITICAL seed_variant mismatch?** | **No** |

### What PASSED

| Suite | Passed (EXECUTED) |
|-------|-------------------|
| Product QA | QA-B02, B09, B10, B12 (Scripts 1,3,4,6) — Neon fingerprint + units / DB sim / rotation |
| Integration | Checks #1, #3, #4, #5 (source), #6 (w/ dummy URL workaround), #19; #2 logic PASS under dummy URL |
| Security | F4 remediation applied locally (`markWeekCompleted` + learner join; no client plan_id fallback) |
| UI | — (still plan-only) |
| Evals | — (still plan-only; Vitest ADR bar exercised via QA/Integration) |

### What BLOCKED

| Suite | Blocked |
|-------|---------|
| Product QA | QA-B03 (mock ungate), QA-B11 (gate pass → advance + re-pace) — no Clerk `/app` session / browser MCP |
| Integration | #8–16, #18 BLOCKED-PENDING-NEON (`fetch failed`); #17 secrets; #7 FastAPI orthogonal FAIL (no fastapi) |
| Security | F1 / F2 still NEEDS-PR; no live defensive probes |
| UI | All ADR Playwright / browser checks still PLANNED |
| Evals | Planned LLM/harness checks still not run (by design this iter) |

### Suggestions for Coordinator (non-binding)

1. **Do not declare unanimous-clean.** Iteration 1 execute was partial; 2 P0 scripts BLOCKED; F1/F2 open; UI zero browser execute.
2. **Escalate environment intervention before / as gate to iteration 2:** (a) Clerk signed-in local or Playwright `storageState` for pilot user; (b) confirm shared Neon reachability (`SELECT 1` + seed) on the Integration executor host — reconcile QA vs Integration connectivity split.
3. **Recommend open iteration 2** after that intervention, scoped to: re-run QA-B03 + QA-B11; Integration #8–11 + #16; optional UI readiness/mock/gate smoke (#4–8, #12). Do **not** spend iteration 2 on another plan-only pass.
4. **Ship F4 as PR** + `review-security` now (parallel). Queue F1 then F2 PRs; keep parallel to ADR UI execute.
5. **Keep `building` lock.** Onboarding/`fresh` stays secondary account / dedicated window.
6. **Fix Vitest + `.env.local` `channel_binding` collect breakage** so unit green is trustworthy without dummy URL.
7. **Circuit breaker:** still **1 / 4**. Prefer escalate → targeted re-execute over planning churn. If Clerk+Neon cannot be unblocked within the round, escalate to stop/hold rather than burning iterations on BLOCKED repeats.

### Unanimous-clean?

**no**

Rationale: Not all P0s executed clean — QA-B03/B11 BLOCKED; Integration Neon/HTTP P0s BLOCKED; UI ADR E2E not run; Security F1/F2 still open. F4 fixed is progress, not clean. Zero product FAILs this pass does not equal unanimous-clean.

---

## Facilitator closing

Binding decision: **reserved for Coordinator**.

**Non-binding summary for Coordinator:** Iteration 1 execute delivered honest partial green on ADR math/DB (4/6 QA scripts PASS; Integration units/lint green) with **0 FAIL**, but **live mock ungate + gate-advance and Neon HTTP contracts remain BLOCKED** on Clerk session / Neon connectivity. Security F4 fixed locally; F1/F2 still need PRs. Variant lock OK (`building`). **Unanimous-clean: no.** Prefer **escalate Clerk + Neon**, then **open iteration 2** for B03/B11 + Integration #8–11/#16 — not another plan-only loop. Iteration **1 of 4**.

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
