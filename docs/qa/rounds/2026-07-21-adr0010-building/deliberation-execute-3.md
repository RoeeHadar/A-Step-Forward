# Deliberation Brief (Post-Execute) — iteration 3

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (locked — matches `docs\qa\rounds\current.json`) |
| Iteration | **3 of max 4** |
| Mode | Post-execute deliberation (after deploy `0b61077b` + prod QA-B03/B11 PASS) |
| Crew | DeliberationCrew (5 advocates + facilitator) |
| Prior briefs | `deliberation.md` (plan-only); `deliberation-execute-1.md`; `deliberation-execute-2.md` — **not overwritten** |
| Binding decision | **None** — Coordinator owns sign-off |

This brief is **non-binding**. Suggestions below are for Coordinator deliberation only.

---

## Advocate briefs (sequential) — given EXECUTED evidence

### Integration Advocate

**Agreements:** Iter-2 Neon boundary **#8–11/#16 PASS** still stands (fail-no-advance, gate pass→advance, lesson≠week complete, `building` fingerprint). Iter-3 product retest on prod does **not** contradict those DB results — B11 live now shows the same advance shape QA could not isolate in iter 2 (week1 completed → week2 active → week4 appended). Variant lock intact. Deploy `0b61077b` (advance on gate pass + `/app`|`/app/plan`) aligns Stream A helpers with UI observation.

**Challenges:**
- **Clerk-authenticated HTTP** for checklist wording on #10/#11/#13/#16 remains open — DB-boundary ≠ route-auth green. Do not inflate iter-3 B11 UI PASS into “Integration HTTP closed.”
- Shared-pilot process risk is **mitigated this pass** (isolated B11 succeeded) but not eliminated as a standing hygiene rule.
- Residual Integration gaps (onboarding/bootstrap HTTP #14/#15, chat #17) are out of ADR-0010 iter-3 scope — do not reopen as blockers for B03/B11 closeout.

**≤3 recommendations:**
1. Accept #8–11/#16 DB PASSes + prod B11 UI as **convergent evidence** Stream A gate/advance works end-to-end for `building`.
2. Keep Clerk HTTP as optional follow-on — not required to call ADR gate math green after live B11.
3. Preserve serialize-before-reseed rule for any future mutating Integration pass on shared pilot Neon.

**seed_variant:** `building`

---

### UI / E2E Advocate

**Agreements:** Production mock-exam RSC crash from iter 2 is **cleared** — QA-B03 catalog + exam detail render (sections + התחל מבחן). B11 advance UI now **proven** in isolation: `/app/plan` shows שבוע 2 · פעיל, week1 הושלם, banner "התוכנית עודכנה לפי ההתקדמות שלך"; fail@66% correctly did not advance. Deploy + verify-deploy SUCCESS for `0b61077b` is credible ship evidence for those UI paths.

**Challenges:**
- **UI suite Playwright ADR twins remain not fully green** — plan-only / coverage gaps (weekly gate, readiness banner, mock ungate) are still open as **automation debt**, even though Product QA browser + Neon covered the live journeys this round.
- Product QA browser PASS ≠ UI crew checklist closeout. Do not claim “UI suite green.”
- Taste / remediation-chip still out of clean criteria (unchanged).

**≤3 recommendations:**
1. Do **not** block ADR product closeout on Playwright twins — live HE journeys for B03/B11 passed.
2. If Coordinator opens iter 4, prefer a **scoped** Playwright twin for gate pass→advance and/or mock catalog smoke — not a full e2e rewrite.
3. Keep HE/RTL visual banner attestation as nice-to-have; B11 plan UI + cue already observed live.

**seed_variant:** `building`

---

### Product QA Advocate

**Agreements:** Iteration 3 delivered the scoped outcomes from iter-2 deliberation: **QA-B03 PASS** (mock catalog + detail) and **QA-B11 PASS** (fail@66% no advance; pass@93% → week1 completed, week2 active, week4 appended; `plan_adapted` cue). Attestation + prior unit/Neon scripts (B02/B09/B10/B12) remain supportive. ADR-0010 building P0 matrix rows that drove this round’s product FAIL/PARTIAL are now green on prod. Deploy `0b61077b` + verify-deploy SUCCESS.

**Challenges:**
- **PASS on B03/B11 ≠ unanimous-clean.** Scripts 7–8 (P1) still unauthorized; full matrix P1–P2 rows not claimed.
- `qa.md` ledger may still show iter-2 FAIL/PARTIAL labels until Coordinator/QA steward updates — treat **iterations/3.md** + this brief as authoritative for iter-3 outcomes.
- Mock **ungate readiness >70%** after scored mock sit was the original B03 full journey; this pass confirmed catalog/detail render (RSC fix). If full ungate+My Tests reload was not re-run beyond render, note as residual matrix depth — do not silently downgrade severity if Coordinator still requires scored-mock ungate for §F #16.

**≤3 recommendations:**
1. Record B03/B11 as **PASS** for this round’s binding ledger; keep `building` lock.
2. Prefer **close round with explicit deferrals** *or* a tightly scoped **iter 4** — do not reopen B03/B11 without regression signal.
3. Optionally authorize Scripts 7–8 only if iter 4 has spare capacity after Security/UI priorities.

**seed_variant:** `building`

---

### Security Advocate

**Agreements:** Live gate submit + plan advance on production again exercised scored paths (`test_attempts`, week status mutation). Mock-exam fix shipped without reported client `learner_id` / forgeable ownership regressions in this deliberation’s evidence set. Variant lock OK. No new exploit work claimed this pass.

**Challenges:**
- **F1 (custom-quiz client keys) / F2 (chat SafetyModeration pre/post)** remain **CONFIRMED / NEEDS-PR** — parallel debt **not cleared** by ADR frontend fixes. These are real authz/integrity findings, not speculative.
- Unanimous-clean across *all* suite P0s cannot be claimed while F1/F2 stay NEEDS-PR.
- Shared-pilot account hygiene remains a process note, not a product FAIL.

**≤3 recommendations:**
1. Do **not** treat B03/B11 PASS as Security suite closeout.
2. If Coordinator continues to iter 4: prioritize F1/F2 PRs (+ `review-security`) over new ADR matrix rows.
3. If Coordinator closes the round: **explicitly defer** F1/F2 with owners — not silent waive.

**seed_variant:** `building`

---

### Evals Advocate

**Agreements:** Binding bar remains web Vitest + manual/`building` evidence. Prod B03/B11 PASS strengthens ADR confidence without promoting LLM baselines. No fabricated eval runs. Stale `evals/report.md` still not an attestation.

**Challenges:**
- Prefer a focused regression (route/component/unit smoke) for mock-exam `examsById` and gate-advance-on-submit so RSC/advance do not regress silently — may already be partial in deploy; do not invent LLM suites.
- Mentor/Reviewer LLM harness gaps remain secondary.
- **No baseline promote** this round.

**≤3 recommendations:**
1. Still **no baseline promote**.
2. Confirm CI Vitest / lint gates stayed green with `0b61077b` (verify-deploy already SUCCESS).
3. Optional: add/extend a small unit or route assertion for mock catalog map + advance trigger — only if iter 4 or a follow-on chore, not a blocker for product PASS ledger.

**seed_variant:** `building`

---

## Facilitator synthesis

### Agreements

1. **Variant lock intact:** `current.json`, iter-3 checklist, prior suite footers — all **`building`**. **No CRITICAL mismatch.**
2. **Iter-3 product scope achieved:** Deploy `0b61077b` (mock-exam RSC + `advanceRollingPlanWindow` after gate pass + on `/app`|`/app/plan`); verify-deploy **SUCCESS**; **QA-B03 PASS**; **QA-B11 PASS** (fail no-advance + pass advance + UI cue).
3. **Stream A corroborated end-to-end:** Integration iter-2 Neon #8–11/#16 + isolated prod B11 UI now agree on gate fail/pass and week roll.
4. **Stream B mock path unblocked for catalog/detail** after prior production RSC FAIL.
5. **Unanimous-clean cannot be claimed** — Security F1/F2 NEEDS-PR; UI Playwright ADR twins not fully green; Integration Clerk HTTP still open; P1 Scripts 7–8 unauthorized.
6. **No baseline promote** — unchallenged.
7. **Circuit breaker: 3 / 4** — one iteration remaining if Coordinator continues.

### Conflicts

| Topic | Positions | Facilitator note (non-binding) |
|-------|-----------|--------------------------------|
| **Close round vs iter 4** | Product QA/UI: ADR B03/B11 blockers cleared — close-or-defer OK. Security: F1/F2 still NEEDS-PR. UI: Playwright debt remains. | Facilitator **leans close with explicit deferrals** *or* **one scoped iter 4** (F1/F2 and/or tiny Playwright twin) — not reopen B03/B11. Escalate-to-stop only if Manager demands full-suite unanimous-clean inside the last slot. |
| **Is B03 “full” §F ungate?** | Product QA notes catalog/detail PASS clearly; scored-mock→readiness>70%+My Tests depth may be thinner than original script. | Coordinator should confirm whether render-level PASS meets this round’s acceptance; if full ungate required and not executed, optionally authorize a **narrow** retest in iter 4 — not a FAIL claim without evidence of regression. |
| **Does live B11 close Integration HTTP?** | Integration: no. Product QA: UI journey green. | **Compatible:** label split — UI/ADR journey PASS; Clerk HTTP gap remains deferred. |
| **Unanimous-clean?** | No advocate claims all open P0s clean. | **no** — see below. |

### Variant lock

| Check | Result |
|-------|--------|
| `current.json` `seed_variant` | `building` |
| Iter 3 deploy / retest notes | `building` re-seed for B11 |
| Integration prior fingerprint | phase `building` |
| Mismatch / wrong-variant evidence | **None** |
| **CRITICAL seed_variant mismatch?** | **No** |

### What PASSED (EXECUTED iter 3 + carried)

| Suite | Passed |
|-------|--------|
| Product QA (iter 3) | **QA-B03 PASS**; **QA-B11 PASS** (prod, isolated); prior attestation / B02/B09/B10/B12 supportive |
| Integration (iter 2 carry) | #8, #9, #10*, #11*, #16* Neon DB/API-boundary |
| Deploy | `0b61077b` verify-deploy **SUCCESS** |
| UI / Security / Evals | — (not primary executors this pass; UI journeys observed via Product QA) |

\*DB-boundary PASS; Clerk HTTP still open.

### What FAILED / PARTIAL / still open

| Suite | Status |
|-------|--------|
| Security | **F1 / F2 CONFIRMED / NEEDS-PR** |
| UI / E2E | Playwright ADR twins **not fully green** (automation debt) |
| Integration | Clerk-authenticated HTTP for #10/#11/#13/#16 still open |
| Product QA | Scripts 7–8 (P1) unauthorized; residual matrix depth optional |
| Evals | No baseline promote; LLM harness gaps secondary |

### Suggestions for Coordinator (non-binding)

1. **Do not declare unanimous-clean** (`unanimous_clean` stays `false`).
2. **Primary lean — close round with explicit deferrals** of: Security F1/F2 (NEEDS-PR), UI Playwright ADR twins, Integration Clerk HTTP, Scripts 7–8. Record ADR building P0 product blockers (B03/B11) as **PASS** on prod after `0b61077b`.
3. **Alternate — continue iteration 4** (last slot) only if scoped to: (a) Security F1/F2 PRs + review-security, and/or (b) one Playwright twin / optional full mock-ungate depth check. Do **not** re-litigate B03/B11 without regression.
4. **Escalate-to-stop / manager** only if leadership requires unanimous-clean including F1/F2 + full Playwright inside one remaining iteration — that bar is unlikely to clear honestly in iter 4 alone.
5. **Keep `building` lock.** Do not flip variant.
6. Update suite ledgers (`qa.md` status rows) to reflect iter-3 PASS so FAIL/PARTIAL from iter 2 are not left as the headline.
7. **Circuit breaker:** **3 / 4**. Product FAIL/PARTIAL that drove iter 3 are resolved; remaining opens are parallel debt / automation — iterate only with tight scope, else close+defer.

### Unanimous-clean?

**no**

Rationale: Advocates do **not** unanimously agree all open P0s are clean. Security F1/F2 remain NEEDS-PR; UI Playwright ADR coverage is not fully green; Integration Clerk HTTP gaps remain. ADR product cases B03/B11 are PASS on prod, but that is insufficient for `unanimous_clean=true`.

---

## Facilitator closing

Binding decision: **reserved for Coordinator**.

**Non-binding summary for Coordinator:** Iteration 3 shipped `0b61077b`, verified deploy, and turned prior **B03 FAIL** / **B11 PARTIAL** into **PASS** on production (mock catalog/detail; fail@66% no advance; pass@93% week roll + UI cue). Integration Neon #8–11/#16 remain supportive. Variant lock OK (`building`). **Unanimous-clean: no** (Security F1/F2, UI Playwright, Clerk HTTP). Suggest **close round with explicit deferrals**, or **one scoped iter 4** for Security F1/F2 (± thin Playwright) — not escalate-to-stop by default. Iteration **3 of 4**.

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
