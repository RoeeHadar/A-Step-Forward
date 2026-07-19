# ADR 0010: Assessment-driven progression & gating

- **Status:** Accepted — Streams A, B, E shipped; C/D/F cores shipped (2026-07-19)
- **Date:** 2026-07-19
- **Deciders:** Product owner + Opus (planning)
- **Extends:** [ADR-0009](0009-goal-paced-adaptive-planning.md) (living goal-paced planner). Constrained by [ADR-0006](0006-neon-direct-critical-path.md) (Vercel + Neon hot path), [ADR-0007](0007-learning-planner-authority.md) (planner authority), [ADR-0008](0008-adaptive-wellbeing-planning.md) (wellbeing overlay).
- **Source:** Grilling session 2026-07-19 (onboarding → final exam). 16 confirmed decisions.

## Context

ADR-0009 shipped the living, goal-paced planner: an anchored frontier walk, weekly re-pace from mastery + trailing velocity, a goal-reached wind-down, a Tests archive, and a **soft** week gate (pass advances; time also advances; a fail only records a remediation signal).

The grilling session surfaced two problems and a stronger product stance:

1. **Advancement is not actually earned.** `lesson-complete.ts` bumps `concept_mastery` to `LESSON_READ_BASELINE = 0.7` on "mark complete," and `maybeCompleteActiveWeek()` completes the week — and thus advances the plan — once every concept is ≥ 0.7. **A learner can breeze through the entire plan by clicking "complete," never taking a quiz.** This directly contradicts the product intent that *assessments*, not lesson views, judge mastery.
2. **The soft gate does not gate.** Time-based advance moves learners past material they never demonstrated. The intended behavior is "progression only upon passing."
3. **Product stance (owner):** the site is a *tool*, not a predictor of success; students may breeze without attention; **quizzes and tests are the way to judge**; readiness must never imply guaranteed success and must stay humble to the last day.

**Pilot context (unchanged):** no active learners yet; tens of Bagrut (372/471/572) learners; free-tier infra; bilingual HE-default; no external links in learner content; Clerk auth; learner-side plan mutations are template-only (`ASF_PLAN_UPDATE`); a separate agent is rewriting lessons, so lesson bodies / `agent_hints` / `lesson_skill_atoms` remain a moving target.

## Decision

Progression is **earned through assessment**, not lesson completion. The plan advances only on demonstrated competence, corrects wrong assumptions through cumulative probing, retains through spaced decay, and drives a humble path to a coverage-plus-mock definition of readiness.

### A. Gating & advancement

1. **Hard gate + soft override.** A fail or no-attempt blocks new material. Time no longer auto-advances the rolling window. The soft override unlocks only after the learner is stuck too long (~2 consecutive remediation weeks on the same material) **or** they explicitly choose "skip ahead anyway" — so nobody is permanently stranded, but nobody is silently skipped forward.
2. **Failure loop.** Up to **2 same-week retakes** (freshly generated items on the same concepts). Still failing → the next week becomes a **remediation week** on the weakest concepts, then re-gate.
3. **Pass criteria.** Aggregate score ≥ `GATE_PASS_THRESHOLD` (0.75) **AND** every frontier-**critical** concept in the week ≥ a floor (~0.6). A strong average cannot mask a zero on a hard prerequisite; non-critical weak spots fold into spaced review instead of blocking.
4. **Lessons decoupled from advancement.** Marking a lesson read records only a light **exposure** signal (below the critical floor and below "mastered") and **never** completes a week or grants advancement-mastery. Gates/tests are the sole driver of week completion and of the mastery that feeds `advanceRollingPlanWindow`. This retires `maybeCompleteActiveWeek()` as an advancement path.

### B. Assessment hierarchy (all archived)

5. **Three tiers.**
   - **Weekly gate** — short; advances the week; mostly MCQ + some numeric/short-answer (auto-graded) to cut guessing.
   - **Milestone/unit test** — at frontier checkpoints; longer, cumulative/mixed, exam-style; can trigger a re-plan; includes some **below-anchor prerequisite probes** and open-response graded by Grader/Reviewer.
   - **Final mock exam(s)** — near the deadline; full-length, timed, exam conditions; produces a readiness score.
6. **Anti-gaming.** Rotate/randomize items to block memorization; milestone/final tiers add Reviewer-graded open-response (rubric + feedback stored in the archive); mastery weighting discounts lucky-guess patterns.
7. **Difficulty adaptation.** Calibrated per assessment to current per-concept mastery; adaptive **between** assessments (results feed forward). Items stay **fixed within** a given test — fair, reviewable, cleanly archivable — rather than live-branching CAT.

### C. Evaluation integrity (fit-to-purpose & correction)

8. **Wrong-anchor self-correction.** The onboarding **diagnostic** (not just self-ratings) seeds the anchor. Milestone tests and periodic gates include a few below-anchor prerequisite probes; a failed probe pulls that foundation into remediation and **lowers the anchor**, so a mis-stated level self-corrects within a milestone — not at the final exam.
9. **Decay + resurfacing.** Mastery decays over time (FSRS-style). The due-review queue resurfaces it, and milestone/final tests deliberately sample older concepts. A failed re-check lowers mastery and injects a targeted refresh into the plan (same engine as the post-completion refresh loop).

### D. Elevation & completion

10. **Finished early → advance and scale.** Passing the gate early advances immediately (already shipped); sustained high trailing velocity grows `weekly_load` and, once comfortably ahead, weaves in **within-goal stretch** (elevation).
11. **Plan completion → maintenance loop.** Clearing the frontier is not terminal: the system keeps issuing quizzes/tests, re-surfaces the weakest subjects, and refreshes basics — because completion ≠ retained mastery.
12. **Goal-track / deadline changes are suggested, never automatic.** Sustained over-performance surfaces a learner/mentor-confirmed prompt (aim higher / sit earlier). Any goal/deadline change re-derives the frontier but **preserves** mastery + the Tests archive.

### E. Re-planning & wellbeing

13. **At-risk triage.** When `required_velocity > capacity`, prioritize frontier-critical / high-downstream / exam-weighted concepts, defer or compress low-value stretch, and offer learner-confirmed levers (add hours / extend deadline / narrow goal). Proactively **route to the Mentor** for the motivational + plan-update conversation.
14. **Returning learner (gap > ~14 days).** Apply decay → short "welcome back" warm-up to recalibrate → rebuild the rolling window from current (decayed) mastery → re-check the deadline (may flip to at-risk → triage + Mentor).
15. **Wellbeing modulates HOW, not WHETHER.** High anxiety / mastery-shock → lighter weeks (lower `weekly_load`), softer tone, relaxed pace, heavier review near the exam — but the pass bar and gates never soften. Extreme distress routes to Mentor + safety.

### F. Readiness (humble by design)

16. **Readiness = coverage + proven performance.** Exam-ready = (1) high frontier mastery (~90% of critical concepts, decay-applied) **AND** (2) passing ≥ 1 full-length timed mock at target under exam conditions. Constraints:
    - **Never signal guaranteed success.** The site is a tool and cannot predict the outcome; always encourage continued practice until test day.
    - **Concave readiness curve.** Gains near the top are deliberately harder to earn (50→55% easier than 80→85%) so the number never breeds false confidence.
    - **Final phase** shifts from new material to mocks + targeted review of mock-revealed gaps.
    - **Day before the exam:** theory go-over + a Mentor anxiety-clearing talk only — no new material, no hard testing.

## Consequences

**Positive**
- Advancement reflects demonstrated competence; the breeze-through loophole is closed.
- Hidden foundation gaps self-correct mid-journey instead of at the exam.
- Retention is measured and defended (decay + resurfacing).
- Readiness is honest and motivating rather than falsely reassuring.

**Costs / risks**
- More assessment surface (three tiers, open-response grading) → Grader/Reviewer latency + cost on Vercel; needs budgeting and caching.
- Hard gating risks frustration/stranding → mitigated by retakes, remediation weeks, soft override, and Mentor routing.
- Decoupling lessons from advancement changes existing UX expectations (must be communicated in-product).
- Several numeric parameters need calibration and eval before trusting the gate.

## Open questions (calibration / eval — defer to streams)

- Exact params: pass threshold, critical floor, FSRS decay constants, "stuck" counts, gap-day cutoff, readiness bar (~90% critical), final-phase length.
- Milestone placement on the frontier (per unit? every K critical concepts?).
- Prerequisite-probe selection (how many below-anchor, which).
- Reviewer/open-response grading budget + item-bank size + rotation strategy on free tier.
- Whether the concave readiness curve is a display transform or part of the mastery math.

## Phased implementation streams

Ordered by leverage/risk. Each ships behind graceful degradation and is verified (tsc + lint + unit + CI Deploy Web) per the deploy rule.

- **Stream A — Earned advancement (integrity fix, highest priority).** ✅ **Shipped 2026-07-19.**
  Decouple lessons from advancement (#4): lesson-read → exposure signal only; retire `maybeCompleteActiveWeek()` as an advancement path. Enforce the hard gate + per-critical-concept pass criteria (#1–#3) in `advanceRollingPlanWindow` (remove time-based auto-advance to new material; keep it only as the soft-override backstop). Failure loop scaffolding (retake counter, remediation-week flag).

  **What shipped:**
  - `lesson-complete.ts`: `LESSON_READ_BASELINE = 0.7` → `LESSON_EXPOSURE_LEVEL = 0.35` (below the 0.6 critical floor and 0.8 mastered line), applied via `GREATEST` so it can never lower an assessed score. `maybeCompleteActiveWeek()` removed entirely — **lessons never complete a week or advance the plan.** `markLessonCompleteThin` keeps its `{ new_mastery, week_completed }` shape (`week_completed` always `false`) for API stability; no frontend consumes it.
  - `plan-pacing.ts`: pure, tested gate decision `evaluateGatePass({ aggregateScore, perTopic, goalKey })` → `{ passed, failed_critical, aggregate_ok }`. Pass = aggregate ≥ `GATE_AGGREGATE_THRESHOLD` (0.75) **AND** every frontier-CRITICAL concept *assessed in the gate* ≥ `GATE_CRITICAL_FLOOR` (0.6). A strong average can't mask a zero on a hard prerequisite; a critical concept never assessed can't fail the gate. `criticalConceptsForGoal(goalKey)` reads the frontier manifest. `selectNextConcepts` now lets **weak concepts bypass the exclusion set** so a failed week's concepts are re-teachable (remediation carry-forward).
  - `weekly-quiz.ts`: `passed` now comes from `evaluateGatePass` (goal resolved from `personality_profile.goal_key` → `profile.goal`, guarded by `hasFrontier`), not a bare aggregate. `failed_critical` concepts are unioned into `weak_concepts` for remediation and returned to the client + recorded in the attempt.
  - `neon-db.ts` `advanceRollingPlanWindow`: **hard gate** — only a gate-`completed` week advances to new material; time alone no longer advances. **Soft-override backstops** prevent stranding: long overdue (> 14-day grace past the gate due date) OR gate retakes exhausted (≥ 3 `weekly_gate` attempts, via `countGateAttempts`). On a soft-override advance, the failed week's `weak_concepts` (via `getLatestGateWeakConcepts`) carry forward as remediation. The active week is now always closed out when advancing (never two active weeks).
  - `test-attempts.ts`: added `countGateAttempts()` and `getLatestGateWeakConcepts()` (both graceful — return 0/[] on a missing table).
  - Tests: 7 new pacing tests (gate decision + critical set + remediation bypass); full web suite green except a pre-existing local `schemas.test.ts` module-resolution failure (unrelated; fails with Stream A changes stashed too).

  **Deferred within Stream A (follow-ups):** an explicit `remediation_week` flag + retake counter surfaced in UI, and a learner-facing "you must pass the gate to continue" affordance. Current behavior relies on `plan_weeks.status` + attempt counts; the soft override guarantees no learner is ever hard-stranded.
- **Stream B — Assessment tiers & anti-gaming.** ✅ **Core shipped 2026-07-19.**
  Add milestone/unit tests + final mock generation (#5), mixed question formats with Reviewer-graded open-response for milestone/final (#6), item rotation, and between-assessment difficulty calibration (#7). Extend the Tests archive to the new kinds.

  **Shipped:** gate **retake item rotation** (anti-gaming #6/#7 within-fixed): `weekly_quizzes_ai` gains a `rotation` dimension = prior gate-attempt count, so retakes regenerate fresh LLM items (varied numbers/scenarios/correct-option, higher temperature) while reloads within a rotation stay cached. Full **mock exams are now archived** into `test_attempts` (`kind='mock_exam'`, `MOCK_PASS_THRESHOLD=0.6` on auto-graded MCQ) — unifying "all assessments archived" and feeding the readiness mock-gate. Tests archive UI is now **kind-aware** (weekly gate / mock / milestone labels) and renders open (non-MCQ) items gracefully.
  **Deferred:** a dedicated milestone/unit-test generator + placement, Reviewer-graded open-response scoring pipeline (needs Grader budget), and between-assessment difficulty auto-calibration beyond the existing per-concept mastery steer.
- **Stream C — Evaluation integrity.** ⚙️ **Decay shipped 2026-07-19; probes deferred.**
  Diagnostic-seeded anchor + below-anchor prerequisite probes with anchor-lowering (#8); FSRS-style decay + due-queue resurfacing + failed-recheck refresh injection (#9).

  **Shipped:** FSRS-style **mastery decay** (`decayMastery`, 45-day half-life) applied in the readiness computation so stale mastery counts for less (Stream E). The existing `skill_practice` due-review scheduler already resurfaces low-score atoms.
  **Deferred:** below-anchor **prerequisite probes** inside milestone tests + automatic **anchor-lowering** on a failed probe (depends on the deferred milestone generator); failed-recheck refresh injection into the plan.
- **Stream D — Re-planning, wellbeing, returning learner.** ⚙️ **Wellbeing load-ease shipped 2026-07-19.**
  At-risk criticality triage + Mentor routing (#13); returning-learner recalibration (#14); wellbeing load/tone/pace modulation wired to the gate/pacing without touching the pass bar (#15); suggested (learner-confirmed) goal/deadline elevation (#10–#12).

  **Shipped (#15):** an active wellbeing bias now **lightens `weekly_load`** via a pure `loadMultiplier` (`WELLBEING_LOAD_EASE=0.6`, floored at 1 concept) in `computePacing`/`computeFullPacing` — modulating HOW MUCH new material, **never** the gate/pass bar. (Tone/ordering modulation already existed from ADR-0008.)
  **Deferred:** at-risk criticality triage with proactive Mentor routing (#13); explicit returning-learner warm-up recalibration flow (#14) — note decay already discounts stale mastery on return; learner-confirmed goal/deadline elevation prompts (#10–#12).
- **Stream E — Readiness & final phase.** ✅ **Core shipped 2026-07-19.**
  Coverage + mock readiness definition, concave readiness transform, final-phase mode (mocks + gap review), day-before theory + Mentor mode, and the "never guaranteed" framing across the UI (#16).

  **Shipped:** `readiness.ts` — readiness = decay-applied **critical-concept coverage** mapped through a **concave** transform (`ceiling*(1-(1-c)^2)`, gains near the top cost more coverage: 80→85 harder than 50→55), **mock-gated** (≤0.70 without a passed mock), hard-capped below 1.0 (`READINESS_CEILING=0.95` — never "guaranteed"). `exam_ready` needs ≥90% critical coverage AND a passed mock. Phase derivation: `day_before` (≤1d: theory + Mentor only), `final_phase` (≤14d: mocks + gap review), `building` otherwise. Surfaced on the plan dashboard banner (honest number + humble/phase note, bilingual) via optional `planPacingSchema` fields.
  **Deferred:** a dedicated final-phase plan MODE that mechanically swaps new-material weeks for mock+gap-review weeks (currently guidance + readiness signal); day-before UI lockout of new lessons.
- **Stream F — Evals & calibration (cross-cutting).** ⚙️ **Unit calibration shipped 2026-07-19.**
  Pair with `.cursor/skills/run-evals`: calibrate thresholds/params, add gate/remediation/trajectory/readiness eval suites, and validate that gating decisions match graded ground truth before trusting them in production.

  **Shipped:** `assessment-calibration.test.ts` pins the gate ground-truth matrix, decay half-life, and readiness monotonicity/concavity/mock-gate/exam-ready invariants so parameter tweaks can't silently change semantics. Plus 20 new unit tests across readiness + pacing.
  **Deferred:** the full promptfoo/DeepEval online harness and threshold sweep against graded learner data (no live learners yet).
