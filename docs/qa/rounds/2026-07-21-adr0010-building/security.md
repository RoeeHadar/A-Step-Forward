# Security findings — pilot + ADR-0010

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Seed variant | `building` (charter-locked; verified in `docs/qa/rounds/current.json`) |
| Suite focus | Authz / IDOR / PII on **onboarding / plans / chat / quiz** only |
| Target env | `local` |
| Mode | **PLAN + REPORT ONLY** (no live probes, no exploit payloads) |
| Status labels | Findings below are **PLANNED** (static review). **EXECUTED**: none this iteration. |

**Owner stream:** Security / Safety (brief `10-security-safety`). Recommend `review-security` on any PR that remediates these paths.

---

## 1. Scout — security surface map

### In-scope routes (Neon-direct free-tier critical path)

| Surface | Paths | Auth pattern | Tenant key |
|---------|-------|--------------|------------|
| Onboarding | `apps/web/src/app/api/onboarding/submit/route.ts` | Clerk `auth().userId` | Writes profile/plan as `userId` |
| Plans | `plans/current`, `plans/generate`, `plans/bootstrap`, `plans/modify`, `learning-plan/next` | Clerk `userId` | Plan rows keyed by `learner_id = userId` |
| Chat | `chat/route.ts`, `chat/history/route.ts` | Clerk `userId` | `chat_turns` / notes keyed by `userId` |
| Quiz / ADR-0010 gates | `quiz/weekly`, `quiz/[week_id]/submit`, `quiz/grade-next`, `quiz/custom`, `quiz/custom/submit`, `quiz/mock-exam/*` | Clerk `userId` | Quizzes/attempts filtered by `user_id` / `learner_id` |

### Controls observed (positive)

- Unauthenticated API calls get **401 JSON** from `apps/web/src/middleware.ts` (no HTML redirect for `/api/*`).
- Weekly gate generation joins `learning_plans.learner_id = learnerId` (`weekly-quiz.ts` `fetchPlanWeekConceptIds`).
- Weekly quiz **client payload strips answer keys** (`buildClientResponse` omits `correct` / `correct_answer`).
- Submit / grade-next load attempts with `AND learner_id = ${userId}` / `AND user_id = ${userId}`.
- FastAPI suite covers admin RBAC deny, child-mode affective block, memory PII redaction (`apps/api/tests/test_security.py`); Clerk JWT malformation → 401 (`test_auth_clerk.py`); rule-based jailbreak (`packages/agents/tests/test_safety.py`).

### Grounding docs / tests

- `.cursor/rules/50-security.mdc`, `.cursor/skills/security-safety/SKILL.md`
- `docs/security/threat-model.md` (IDOR as primary actor #2)
- `docs/qa/adr-0010-manual-test-plan.md` (building: readiness cap, weekly gate, mock ungating)
- Baseline tests above — **gap:** no automated cross-tenant denial tests for the Neon-direct web routes in scope

### Out of suite focus (noted only)

- Full CSP (docs claim `middleware.ts`; actual baseline headers live in `apps/web/next.config.mjs` — **no `Content-Security-Policy` header** found).
- FastAPI memory AES-GCM / Presidio path (not the Vercel+Neon chat/onboarding path).
- Live-prod write probes — **blocked** without explicit approval (`variant_lock.live_attestation_required_before_execute`).

---

## 2. Executor — planned defensive checklist (≤20)

No exploit payloads. Methods are authz denial / integrity assertions only. Echo: **seed_variant = building**.

| # | Check | Method | Expected | Severity if fail | Automation |
|---|-------|--------|----------|------------------|------------|
| 1 | Unauth → onboarding/plans/chat/quiz | GET/POST without session | 401 | High | auto (vitest + middleware) |
| 2 | Chat history IDOR | Authed A requests history; assert no B content via foreign `session_id` alone | Empty / own turns only | High | auto |
| 3 | Plans current IDOR | Authed A cannot pass foreign `learner_id` (body/query ignored) | Only A's plan | High | auto |
| 4 | Weekly quiz plan ownership | A requests `plan_id` belonging to B | null / 503 / empty concepts; **no B concept list** | High | auto |
| 5 | Weekly submit quiz_id ownership | A submits B's `week_id` | 404 `quiz_not_found` | High | auto |
| 6 | Grade-next attempt ownership | A uses B's `attempt_id` | 404 | High | auto |
| 7 | Weekly client response has no keys | Inspect `/api/quiz/weekly` JSON | No `correct` / `correct_answer` / `model_answer` | High | auto |
| 8 | Custom quiz key exposure | Inspect `/api/quiz/custom` envelope | Prefer server-held keys; if keys present → **fail** for integrity | High | auto |
| 9 | Custom submit ignores client keys | Submit forged `questions[].correct` | Score from server-stored quiz only (or reject body questions) | Critical | auto |
| 10 | Gate advancement ownership | `markWeekCompleted` must join `learner_id` | Cannot complete another learner's `plan_weeks` | High | auto |
| 11 | Onboarding PII hygiene | Store `background_notes` with synthetic email pattern | Redacted before DB/log; logs lack raw PII | Medium | auto + manual |
| 12 | Chat turn PII hygiene | Message with synthetic phone/email | Redacted or refused before `chat_turns` / notes | Medium | auto |
| 13 | Chat moderation pre-hook | Known jailbreak string (fixture from `test_safety.py`) | Refusal / block; no system-prompt leak | High | auto |
| 14 | Child-mode on chat | Profile `child_mode` / age&lt;13 | Stricter path; no affective note writes | Medium | auto |
| 15 | Plan modify confirmation | POST without `confirmed:true` | 400 | Low | auto |
| 16 | Error message hygiene | Force DB error on onboarding | Generic client error; no stack/SQL in body | Low | manual |
| 17 | Mock/history scoped | `/api/quiz/mock-exam/history` | Only caller's attempts | Medium | auto |
| 18 | Cron not callable as learner | `/api/cron/*` without secret | 401/403 | Medium | auto |
| 19 | ADR-0010 building readiness integrity | After forged custom/mock score (denial test) | Readiness / gate not advanced without server-side pass | High | manual (building seed) |
| 20 | Secrets hygiene | Diff/env scan of report + routes | No secrets in logs/report | — | manual |

**Probe order:** 1 → 4–7 (ADR-0010 gate integrity) → 8–10 → 2–3 → 11–14 → remainder.

**Live write probes:** blocked this round (plan-report-only + attestation lock).

---

## 3. Reporter — findings (severity-ranked)

All items **PLANNED** from static code review of in-scope paths. Impact framed for learners on seed `building` (mock-capped readiness, weekly gate, plan advancement).

### F1 — Critical / High: Custom quiz trusts client answer keys

- **Where:** `apps/web/src/app/api/quiz/custom/route.ts` returns full questions including `correct_index` and `sample_solution_*` (`quiz-builder.ts`). `quiz/custom/submit/route.ts` grades from **client-supplied** `questions[]` (including `correct` / `correct_answer`).
- **Impact:** Authenticated learner can inflate custom-quiz scores without solving items. Weekly gate path is stronger (server-stored keys), but custom/mock-adjacent scoring and ADR-0010 readiness signals that consume attempt history are integrity-risk if wired to these scores.
- **Remediation:** Persist quiz server-side keyed by `quiz_id` + `learner_id`; submit accepts answers only; strip solutions from start payload (mirror `buildClientResponse`).
- **Owner:** Security + Frontend (quiz).

### F2 — High: Web chat has no SafetyModeration pre/post

- **Where:** `apps/web/src/app/api/chat/route.ts` records turns and streams LLM output; no call into `packages/agents` `SafetyModeration` (coverage exists only in `packages/agents/tests/test_safety.py`).
- **Impact:** Jailbreak / harmful input reaches model + durable `chat_turns` / agent notes on the pilot critical path.
- **Remediation:** Shared pre-filter (rule path at minimum) before `recordChatTurn` / LLM; post-filter before persist of assistant turns; wire `child_mode` from profile.
- **Owner:** Security + Agents.

### F3 — High: PII redaction gap on Neon-direct onboarding + chat

- **Where:** Onboarding persists `background_notes`, `mental_state`, `personality_profile` without Presidio (`onboarding-plan-bootstrap.ts`). Chat persists raw user text (`recordChatTurn`). API memory path **is** tested for `[EMAIL]` redaction (`test_security.py`) — web path is not.
- **Impact:** Emails/phones/names in free-text land in Postgres and may enter LLM context / persona consolidation.
- **Remediation:** Reuse or port `services/memory/.../pii.py` (or a web-safe subset) before profile upsert and chat/note writes; never log raw message bodies.
- **Owner:** Security + Memory.

### F4 — Medium / High: `markWeekCompleted` lacks learner ownership join

- **Where:** `weekly-quiz.ts` `UPDATE plan_weeks ... WHERE plan_id = $1 AND week_number = $2` with no `learner_id` join. Call sites usually use owned quiz `plan_id`, but fall back to client `args.planId` when row `plan_id` is null.
- **Impact:** Defense-in-depth failure → potential cross-tenant week completion / ADR-0010 advancement if `plan_id` UUID is known and row metadata is incomplete.
- **Remediation:** `UPDATE ... FROM plan_weeks pw JOIN learning_plans lp ON lp.id = pw.plan_id WHERE lp.learner_id = $userId AND ...`; never trust client `plan_id` over stored quiz row.
- **Owner:** Security + Frontend (plans/quiz).

### F5 — Medium: No automated IDOR suite for in-scope web routes

- **Where:** Tests exist for FastAPI admin/memory/Clerk; **missing** vitest/pytest matrices for `/api/onboarding`, `/api/plans/*`, `/api/chat/*`, `/api/quiz/*` cross-user denial.
- **Impact:** Regressions on tenant isolation ship unnoticed; ADR-0010 gate changes lack authz regression net.
- **Remediation:** Add dual-user fixtures covering checks #2–#7 and #10 above; gate in CI.
- **Owner:** Security + Evals/QA.

### F6 — Low: Client error leakage / soft failure shapes

- **Where:** `onboarding/submit` returns `err.message` to client; `plans/current` can return `{ plan: null, error }` with HTTP 200.
- **Impact:** Information disclosure (internal failure detail); clients may mis-handle “success with error”.
- **Remediation:** Generic learner-facing errors; log server-side only; use non-200 when plan fetch fails.
- **Owner:** Frontend / API gateway patterns.

### Residual (below suite focus)

- **CSP absent** despite skill/threat-model expectation (`next.config.mjs` has HSTS/XFO/nosniff/Referrer-Policy/Permissions-Policy only).
- Child-mode JWT claims read in middleware but not enforced on chat/quiz handlers observed in this pass.
- Encryption-at-rest for chat/notes on Neon path still per threat-model residual.

---

## 4. Summary for deliberation

| Severity | Count (PLANNED) | Theme |
|----------|-----------------|-------|
| Critical/High | 3 | Custom-quiz integrity; chat moderation; PII on Neon path |
| Medium | 2 | Gate advancement ownership; missing IDOR automation |
| Low | 1 | Error leakage |

**Verdict for iteration 1:** Not clean. Highest leverage fixes before pilot expansion: **server-side custom quiz keys**, **chat safety + PII hooks**, **`markWeekCompleted` learner join**, plus **automated IDOR tests** for building-seed gate flows.

**EXECUTED this round:** none (plan-report-only). Next iteration may run local defensive pytest/vitest only after Coordinator unlock — still no exploit payloads; live-prod writes require attestation.

---

## Recommend

- Run `review-security` on PRs touching `apps/web/src/app/api/{onboarding,plans,chat,quiz}/**` or `weekly-quiz.ts` / `quiz-builder.ts`.
- Pair with ADR-0010 building manual cases #2–#3, #10–#14 for integrity (gate/mock) once automation lands.

---

## Parallel track — iteration 1

**Track:** Security F1 / F2 / F4 (Coordinator-authorized; does not block Product QA Scripts 1–6).  
**Mode:** Static re-verify + minimal safe patch. **EXECUTED probes:** none (no inventing live results).  
**seed_variant:** `building` (unchanged).

### F1 — Custom quiz client keys — CONFIRMED / NEEDS-PR

| Cite | Evidence |
|------|----------|
| `apps/web/src/lib/quiz-builder.ts:76–110`, `:591–605` | `CustomQuizQuestion` includes `sample_solution_en/he`, `correct_index`; `buildCustomQuiz` returns full `questions: validated` in the envelope. |
| `apps/web/src/app/api/quiz/custom/route.ts:51–66` | Route returns `envelope` unmodified to the client. |
| `apps/web/src/app/api/quiz/custom/submit/route.ts:30–43`, `:70–111` | `gradeClosed` scores from client `q.correct` / `q.correct_answer`; submit accepts body `questions[]` and passes those keys into `createPendingAttempt`. |
| `apps/web/src/components/quiz-page-client.tsx:515–546` | Client rebuilds submit payload with `model_answer` from `sample_solution_*` and MCQ `correct` from `correct_index`. |

**Status:** Confirmed. Not fixed this pass — full fix needs server-held quiz + client UX change (solutions shown post-grade today).  

**Remediation plan (PR):**
1. Persist full custom quiz JSON keyed by `(quiz_id, learner_id)` at generate time (mirror `weekly_quizzes_ai`).
2. Strip `correct_index`, `sample_solution_*`, rubrics-as-keys from start response (mirror `buildClientResponse` in `weekly-quiz.ts:502–519`).
3. Submit accepts `quiz_id` + `answers[]` only; load keys server-side; reject body-supplied `correct` / `correct_answer` / `model_answer`.
4. Update `quiz-page-client` to show solutions from grade-next / attempt feedback, not from start envelope.
5. Add vitest: forged client keys must not change score; cross-learner `quiz_id` → 404.
6. Run `review-security` on that PR.

### F2 — Web chat SafetyModeration — CONFIRMED / NEEDS-PR

| Cite | Evidence |
|------|----------|
| `apps/web/src/app/api/chat/route.ts:183–190`, `:103–118` | User turn persisted via `recordChatTurn` before LLM; assistant via `saveAssistantTurn` — no safety import/call in file. |
| `packages/agents/agents/base/safety.py:50–65`, `:119–123` | Rule + optional LLM `SafetyModeration.pre/post` exist in Python agents package only. |
| `packages/agents/tests/test_safety.py` | Jailbreak / child-mode coverage for Python path — not wired to Neon-direct web chat. |

**Status:** Confirmed. Not fixed this pass — wiring full agent is cross-runtime (Python ↔ Next); even a TS rule port needs child_mode profile plumbing + refusal UX + tests (scope beyond minimal patch).

**Remediation plan (PR):**
1. Port `_rule_classify` (+ refusal copy) to `apps/web/src/lib/chat-safety.ts` (rules-only first; `use_llm: false` parity).
2. Call pre-filter **before** `recordChatTurn` / observation persist; on hit return streamed refusal (no durable user turn, or store redacted refusal only).
3. Post-filter assistant buffer before `saveAssistantTurn`.
4. Read `child_mode` / age from `getLearnerProfile`; pass into classifier.
5. Shadow then promote; mirror fixtures from `test_safety.py` as vitest.
6. Run `review-security` on that PR. Defer LLM SafetyModerationAgent until rules path is live.

### F4 — `markWeekCompleted` learner join — FIXED

| Cite (before) | Evidence |
|---------------|----------|
| `weekly-quiz.ts` `markWeekCompleted` | Was `UPDATE plan_weeks … WHERE plan_id = $1 AND week_number = $2` with no `learner_id`. |
| Submit path | Used `row.plan_id ?? args.planId` (client fallback). |

| Cite (after) | Change |
|--------------|--------|
| `apps/web/src/lib/weekly-quiz.ts:875–898` | `markWeekCompleted(learnerId, planId, weekNum)` joins `learning_plans lp` and requires `lp.learner_id = learnerId` (same pattern as `fetchPlanWeekConceptIds` ~L322–336). |
| `apps/web/src/lib/weekly-quiz.ts:831–852`, `:908–910` | Call sites pass `userId`; advance only when `row.plan_id` is present (no client `plan_id` fallback). |
| `apps/web/src/lib/weekly-quiz.ts` `createPendingAttempt` | Gate attempt stores `planId: row.plan_id` only (no `args.planId` trust). |

**Status:** Fixed locally (uncommitted). Recommend `review-security` when opened as PR. No live probe executed.

### Track summary

| Finding | Status |
|---------|--------|
| F1 | CONFIRMED / NEEDS-PR |
| F2 | CONFIRMED / NEEDS-PR |
| F4 | FIXED |

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
