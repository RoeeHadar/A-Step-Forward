# ADR 0009: Goal-paced adaptive planning (living plans)

- **Status:** Proposed
- **Date:** 2026-07-19
- **Deciders:** Product owner + Opus (planning)
- **Extends:** [ADR-0007](0007-learning-planner-authority.md) (planner authority), [ADR-0008](0008-adaptive-wellbeing-planning.md) (unified path + wellbeing overlay); constrained by [ADR-0006](0006-neon-direct-critical-path.md) (Vercel + Neon hot path)

## Context

The current plan-creation path does not do what the product promises. Concretely, from the code as shipped:

| Intended behavior | Shipped behavior (pre-ADR) |
| --- | --- |
| First plan correlated to the end goal, paced against the deadline | `onboarding-plan-bootstrap.ts` → static goal→concept-list lookup (`onboarding-self-score.ts`), first 8 concepts, 2 fixed weeks. No KG traversal, no mastery weighting, **no pacing to `next_test_date` / `final_goal_date`**. |
| Personalized to attributes + how the student learns | Attributes (`attention_span`, `preferred_style`, `mental_state`, `personality_profile`) captured but **do not shape the plan** — only chat tone. |
| Aimed at weaknesses and strengths | Mid-journey `buildLearningPlan()` mastery-weights the KG walk (good), but the **first** plan ignores mastery beyond seeded self-scores; strengths are never leveraged. |
| Adaptive to trajectory + time-to-goal + continuous learning | `advanceRollingPlanWindow()` only promotes the next concepts when a week is **past due** (time-based). No velocity, no trend, no on-track/at-risk signal, no finished-early handling. |
| Optimize the student's potential | Undefined; no stretch behavior. |

The onboarding-plan first-create path is also **latency-fragile**: the golden-path skill (`.cursor/skills/diagnostic-plan-golden-path/SKILL.md`) documents repeated `FUNCTION_INVOCATION_TIMEOUT` failures whenever `neon-db.ts` / `kg-data.json` / BFS / LLM work touched the onboarding critical path. Any redesign must respect those scars.

**Concurrency constraint:** a separate agent is actively rewriting lessons. Lesson bodies, `lesson_skill_atoms` (the `teaches` mapping), and `agent_hints` are therefore a moving target during this work.

**Pilot context (unchanged from ADR-0008):** no active learners yet; target tens of Bagrut (372/471/572) learners; all infra free-tier; bilingual HE-default; no external links in learner content; Clerk auth; plan mutations are template-only from the learner side (`ASF_PLAN_UPDATE`) except server-driven adaptation.

## Decision

Rebuild plan creation as a **living, goal-paced planner** with a hybrid engine. The plan optimizes **probability of reaching the goal by the deadline**, re-adapts continuously to the learner's trajectory, and executes targeting through **dynamically generated practice** (because lessons are static content).

### 1. Objective function

The planner's single primary objective is **maximize P(goal attained by deadline)**, expressed as pacing mastery of the goal frontier against time remaining. It is explicitly **not deterministic** — it is recomputed as the learner acts. All other inputs (attributes, wellbeing, personality) are constraints or modifiers, never the primary objective.

### 2. Hybrid engine (fast skeleton + async enrichment)

| Layer | Owner | Runs where | Budget |
| --- | --- | --- | --- |
| **Deterministic skeleton** | new `plan-pacing.ts` engine | Vercel hot path (onboarding + rolling advance) | fast, no LLM, no `neon-db` monolith |
| **LLM enrichment** | Curriculum Designer agent | async `POST /api/plans/enrich` (client-triggered post-redirect) + cron backstop | slow OK, off critical path |

The deterministic engine is authoritative for sequencing and pacing (extends ADR-0007). The LLM only enriches: rationale copy, learning-style tuning within guardrails, and practice-prescription shaping. Enrichment **never** blocks the learner from seeing a plan.

### 3. Goal-frontier manifest + velocity pacing

**Manifest is derived from the KG, not hand-authored (resolved 2026-07-19).** The KG already encodes `points_levels[]` and `subject` per concept, and `plan-worklist.ts:DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY` maps each goal key to a terminal concept. A build script (`scripts/build-goal-frontiers.mjs`) generates a **pre-ordered goal-frontier manifest** (`apps/web/src/lib/goal-frontiers.generated.json`, keyed on `concept_id`):

```
frontier(goal_key, points_group) =
  { c in KG : c.points_levels ∩ allowedLevelsForProfile(points_group, subjects) ≠ ∅
              AND c.subject ∈ subjects }
  topologically ordered by prereq depth toward the goal terminal concept.
```

A thin hand-authored override file (`apps/web/src/lib/goal-frontiers.overrides.json`) may only: reorder within the derived set, define the **stretch frontier**, and flag **criticality exceptions**. This keeps the manifest in sync with KG + lesson changes automatically and insulated from lesson-body churn (it keys on `concept_id`).

**Criticality is derived (resolved):** a concept is `goal_critical` when it is a transitive prerequisite of the goal terminal concept(s) within the frontier, OR its downstream degree within the frontier is high (≥ a configured fan-out). Override file can flip specific concepts. **Conservative default: treat as critical when ambiguous** (protects the soft-override gate).

**Stretch frontier is derived (resolved):** concepts in the learner's subject(s) tagged one `points_level` above the goal (e.g. `5pt` concepts for a `4pt` goal), plus cross-subject `applies_to` enrichment neighbors. Overridable.

Pacing math (deterministic, cheap):

- `mastered_concepts = { c : concept_mastery.score ≥ 0.8 }` — reuses the existing `MASTERY_THRESHOLD` (`learning-plan.ts`) so "mastered" is consistent everywhere.
- `remaining_scope = |frontier − mastered_concepts|`
- `weeks_left = weeks between now and next_test_date` (fallback `final_goal_date`, fallback 12-week default horizon; floor at 1)
- `required_velocity = remaining_scope ÷ weeks_left` (concepts/week)
- `capacity` (resolved): `base = clamp(round(hours_per_week ÷ 2.5), 1, 6)` concepts/week; then scaled by attention span — `× 0.75` when `attention_span` is short, `× 1.0` medium, `× 1.15` long — and floored at 1. Session length = `attention_span` bucket (short ≈ 15 min, medium ≈ 30, long ≈ 45).
- `weekly_load = clamp(min(capacity, required_velocity), 1, CONCEPTS_PER_ROLLING_WEEK)`
- `status = at_risk` when `required_velocity > capacity`; `ahead` when trailing velocity > `required_velocity`; else `on_track`.
- **Velocity window (resolved):** trailing 21 days (≈3 weeks) of mastered concepts/atoms, falling back to "since plan start" when the plan is younger than that.

The manifest being pre-ordered means the **onboarding skeleton is a cheap slice** — no BFS on the critical path. Mid-journey re-sequencing still uses `buildLearningPlan()` mastery-weighted BFS (off critical path).

### 4. Personalization: attributes control HOW, not WHAT

Concept **selection** stays mastery + goal-frontier driven in every case (this is the differentiator and the testable part). Learner attributes tune execution:

| Attribute | Lever |
| --- | --- |
| `attention_span` | session length + concepts/week granularity |
| `hours_per_week` | weekly load / capacity |
| `preferred_style` | question-kind mix + practice modality |
| `mental_state` (anxiety/motivation/confidence) | wellbeing overlay (ADR-0008) + pacing aggressiveness |
| `personality_profile` | tone/framing (LLM enrichment layer) |

Strengths are leveraged by **skipping already-mastered material** (existing `MASTERY_THRESHOLD` behavior) rather than reordering toward favored subjects.

### 5. Potential = adaptive ambition

- Each goal has a **core frontier** and a **stretch frontier** in the manifest.
- When trajectory shows the learner is **ahead of required velocity with strong mastery**, the planner raises ambition: deeper concepts, harder question kinds, cross-subject enrichment edges, or a goal upgrade (e.g. 4→5 units) surfaced as a suggestion.
- When **behind**, protect the core frontier and defer all stretch/enrichment.
- Because **lessons are static**, ambition is executed by **dynamically generating** exercises/quizzes/tests calibrated to the learner's current level, building on `POST /api/quiz/custom` + `build-custom-quiz` + `author-question-bank`. A plan item is therefore a **practice prescription**, not just a concept id: `{ concept_id, target_atoms[], kind_mix, difficulty, gate?: quiz_spec }`.
- **Difficulty calibration (resolved 2026-07-19):** difficulty is chosen per prescription from the learner's **concept-mastery band** — `easy` when `concept_mastery.score < 0.4`, `medium` for `0.4–0.75`, `hard` for `> 0.75` — then modulated one step easier when the **mastery trend is regressing**, and targeted at the concept's weakest `skill_practice` atoms. The existing `validateQuestion` difficulty-spread rule (≥1 easy + ≥1 medium at count ≥3; ≥1 hard at count ≥6) still applies, so a prescription band sets the *center of gravity*, not a single fixed difficulty.

### 6. Trajectory model + re-plan triggers

Trajectory signals (persisted as learner planning state):

- **Velocity** — atoms/concepts mastered per week vs `required_velocity`.
- **Mastery trend** — improving / plateau / regressing.
- **Consistency** — sessions attended vs planned.

Re-plan / re-pace triggers:

| Trigger | Action |
| --- | --- |
| Week advance (gate passed) | promote next week, recompute pace |
| Finished early | **overflow (resolved 2026-07-19):** if `status = at_risk` or `on_track` → pull the next week's concepts forward (bank progress against the deadline); if `status = ahead` → offer stretch/deepen the current frontier (adaptive ambition, §5). Learner can always decline and stop. |
| Behind at week end | carry over unfinished + reduce load + flag `at_risk` |
| Quiz/gate failure | insert targeted remediation on weak atoms, re-test |
| Deadline change | recompute `required_velocity`, re-slice |
| Wellbeing/anxiety spike | ADR-0008 wellbeing overlay (unchanged) |

### 7. Onboarding critical-path strategy (two-phase)

1. **Phase 1 — submit stays thin** (`onboarding-plan-bootstrap.ts` extended, still no `neon-db`/`kg-data` monolith): build the 2-week skeleton from the **pre-ordered manifest** sliced by capacity/pace + seeded self-scores. Returns `has_plan: true` in < 5–10s. All golden-path hard rules preserved.
2. **Phase 2 — async enrich** via new `POST /api/plans/enrich` (client fires after redirect; Vercel cron backstop, mirroring `POST /api/cron/consolidate-memory`): LLM enrichment, full-horizon pacing preview, and practice prescriptions written back to Neon. A `plan_enrichment_status` flag drives graceful UI (`skeleton` → `enriched`).

### 8. Competency gate between weeks

- Each rolling week ends with a **mastery-check quiz/test** (generated, level-calibrated). Passing is required to advance; on pass the plan updates.
- **Fail → remediation loop → soft override:** planner injects targeted generated exercises on the weak atoms and re-tests. After a remediation round, the learner may advance but the concept is marked **`shaky`**, scheduled for spaced re-review, and kept **blocking only if it is a goal-critical prerequisite**.
- Pass threshold **relaxes slightly for non-critical concepts under deadline pressure** (never for goal-critical prerequisites). This reconciles the mastery gate with the deadline objective without dead-ends.
- **Gate spec (resolved 2026-07-19):** generated via `buildCustomQuiz` with `kind_mix: 'closed'` (fast, objectively gradable), **8–12 items** covering the week's concepts/atoms. **Pass = overall ≥ 75% AND no goal-critical atom below 50%.** Non-critical relaxation lowers the overall bar to **65%** when `status = at_risk` inside the exam window. Open/short-answer items are excluded from the gate (their grading is self-reported per `build-custom-quiz`) but may appear in non-gating practice.
- **Persistence (resolved):** gate attempts, the learner's answers, per-item correctness, and any Reviewer feedback persist to a new `test_attempts` table (feeds §9 archive); the gate outcome sets `plan_adjustment_kind = 'gate'` and updates planning state (`shaky` flags, velocity).

### 9. Tests archive

New learner-facing surface: past tests/quizzes with the **student's own answers** and the **Reviewer's feedback**, so learners can study from mistakes. Requires persisting attempts + Reviewer feedback and a new page under `apps/web/src/app/`.

### 10. Spaced review budget

Reserve **~20–30% of weekly capacity** (rising as the deadline nears) for **FSRS-due + `shaky` atoms**, reusing the existing Coach FSRS due queue rather than a new scheduler. Interleave review with new concepts each week.

### 11. Lesson-rewrite coordination (contract boundary)

The planner depends **only on stable identifiers**: `concept_id` (KG, stable) and the canonical skill-atom universe (`.cursor/skills/cross-subject-kg/SKILL.md`, stable). Lesson content, `lesson_skill_atoms`, and `agent_hints` are **best-effort enrichment that degrades gracefully** (`hasLesson: false` → generate practice live). The goal-frontier manifest keys on `concept_id`, so the two work-streams do not collide.

### 12. Resolved parameters (2026-07-19)

Consolidated defaults so nothing is left hand-wavy. All are reversible engineering choices, tunable after pilot data.

| Parameter | Resolved value | Source |
| --- | --- | --- |
| Frontier source | Derived from KG `points_levels` + `subject` + goal terminal; thin override file | §3 |
| "Mastered" threshold | `concept_mastery.score ≥ 0.8` | reuse `MASTERY_THRESHOLD` |
| Capacity | `clamp(round(hours_per_week ÷ 2.5),1,6)` × attention-span factor (0.75/1.0/1.15) | §3 |
| Weekly load cap | `CONCEPTS_PER_ROLLING_WEEK` (4) | `plan-worklist.ts` |
| Deadline source | `next_test_date` → `final_goal_date` → 12-week default | §3 |
| Velocity window | Trailing 21 days; else since plan start | §3 |
| `goal_critical` | Transitive prereq of goal terminal OR high downstream degree; override; default critical | §3 |
| Stretch frontier | One points-level above goal + `applies_to` neighbors | §3 |
| Difficulty band | `<0.4` easy / `0.4–0.75` medium / `>0.75` hard; −1 step if regressing | §5 |
| Gate quiz | `closed`, 8–12 items; pass ≥ 75% AND no goal-critical atom < 50% | §8 |
| Gate relaxation | Overall bar → 65% for non-critical when `at_risk` inside exam window | §8 |
| Review budget | ~20–30% weekly capacity, rising near deadline; FSRS queue | §10 |
| Enrichment cadence | Client-fired post-redirect + cron backstop (hourly sweep) | §7 |
| `plan_schema_version` | Bump to 3; gated regen on next login | ADR-0008 §10 |
| `plan_adjustment_kind` | Add `pacing`, `gate`, `overflow`, `remediation` to existing set | §8 / ADR-0008 |

## Consequences

### Positive

- Plans become genuinely goal-correlated, deadline-paced, weakness-aimed, attribute-personalized, and continuously adaptive — the product's core promise.
- Onboarding stays within the Vercel budget (thin skeleton) while depth arrives async.
- Competency gates + generated practice make targeting real despite static lessons.
- Stable-ID contract lets the lesson-rewrite agent proceed in parallel safely.
- Extends (does not replace) the ADR-0007/0008 unified planner + wellbeing overlay.

### Negative / costs

- New build step + thin override file for goal frontiers (derived from KG, so low authoring cost, but the override file needs curation and a coverage eval).
- New persistence: planning state (velocity/trend/shaky), practice prescriptions, `test_attempts` + feedback, enrichment status, gate results.
- More moving parts to test; adaptivity increases integration-test surface.

### Risks

- Manifest quality gates everything — a wrong frontier mis-paces every learner. **Mitigated** by deriving from the KG (which lessons already track) + a coverage eval that fails CI when a goal's frontier is empty or excludes its terminal concept.
- Derived criticality could mis-tag a concept; **mitigated** by the conservative "critical when ambiguous" default + override file.
- Soft-override could let a shaky goal-critical concept slip if criticality is mis-tagged — mitigate by making goal-critical the conservative default.
- Generated-practice difficulty calibration is hard; poor calibration undermines gates. Start conservative, add eval harness.

## Alternatives considered

| Alternative | Why rejected |
| --- | --- |
| Pure LLM-authored plan every time | Latency/cost/variance; breaks onboarding budget; not testable |
| Keep single-goal-concept BFS + even spread | No frontier/scope notion; can't measure "% to goal" or pace |
| Attributes reorder concepts (WHAT) | Risks learning-styles pseudoscience; weakens the mastery-driven differentiator |
| Hard mastery gate (time always slips) | Dead-ends learners against a real deadline |
| Time-only advance (gate advisory) | Reintroduces today's non-adaptive, mastery-blind behavior |
| Wait for lesson rewrite to finish | Serializes two independent efforts unnecessarily |
| New spaced-repetition scheduler | Duplicates Coach FSRS queue |

## Phased implementation plan (streams)

**v1 (deterministic core):**

1. **Curriculum stream** — `scripts/build-goal-frontiers.mjs` derives `goal-frontiers.generated.json` from KG (`points_levels` + subject + goal terminal, topo-ordered); thin `goal-frontiers.overrides.json` for ordering/stretch/criticality exceptions; coverage eval (fails CI when a goal frontier is empty or omits its terminal concept).
2. **Frontend/planner stream** — `plan-pacing.ts` deterministic engine (velocity pacing, capacity, at-risk/ahead); extend `onboarding-plan-bootstrap.ts` to slice the manifest; extend `advanceRollingPlanWindow` → competency-gated advance + overflow/behind handling.
3. **Backend/practice stream** — practice-prescription shape on plan items; week-gate quiz generation via `POST /api/quiz/custom`; remediation loop + soft-override + `shaky` marking.
4. **Frontend stream** — Tests archive page (attempts + student answers + Reviewer feedback); skeleton→enriched plan UI states.
5. **Schema/migrations stream** — planning state (velocity/trend/shaky), practice prescriptions, `test_attempts` (+ student answers, per-item correctness, Reviewer feedback), `plan_enrichment_status`, gate results (JSONB where soft, columns where queried); `plan_schema_version` → 3 + gated regen (per ADR-0008 §10); extend `plan_adjustment_kind` enum with `pacing`/`gate`/`overflow`/`remediation`.
6. **Evals/QA stream** — pacing correctness, gate/remediation behavior, manifest coverage, trajectory triggers; spaced-review budget.

**v1.1 (depth):**

7. **Agents stream** — `POST /api/plans/enrich` + Curriculum Designer LLM enrichment (rationale, learning-style tuning, prescription shaping).
8. **Adaptive-ambition stretch** — ahead-of-pace detection → stretch frontier + goal-upgrade suggestions.

## Verification (when implemented)

- `build-goal-frontiers` produces a non-empty frontier for every goal key that includes its terminal concept (coverage eval, CI gate).
- Onboarding submit returns `has_plan: true` < 10s with a manifest-sliced 2-week skeleton (no `neon-db`/BFS/LLM on the path).
- Pacing: fixture learner with a near deadline is flagged `at_risk`; with a far deadline, load matches capacity not required_velocity.
- Gate: failing the week quiz triggers remediation; after a round, advance with `shaky` + scheduled review; goal-critical concept stays blocking.
- Overflow: finishing a week early surfaces stretch/next material.
- Tests archive: past attempt shows student answers + Reviewer feedback.
- Lesson-rewrite independence: planner produces a valid plan when `hasLesson: false` for frontier concepts.

## Implementation status

- **Stream 1 (goal-frontier manifest + coverage gate) — done (2026-07-19):**
  - `scripts/build-goal-frontiers.mjs` derives the manifest from the KG (`points_levels` + subject + terminal spine, topo-ordered, criticality + downstream degree). University tracks scoped tighter than the quiz allowlist (calc1 ≠ la).
  - `apps/web/src/lib/goal-frontiers.generated.json` (committed) — 8 goals, all with terminal present in core.
  - `apps/web/src/lib/goal-frontiers.overrides.json` — thin optional override layer (empty by default).
  - `apps/web/src/lib/goal-frontiers.test.ts` — 58-assertion CI coverage gate (non-empty core, terminal present + critical, real KG ids, disjoint stretch, foundations-first order). Passes typecheck + lint.
- **Stream 2 (deterministic pacing engine) — done (2026-07-19):**
  - `apps/web/src/lib/plan-pacing.ts` — pure, dependency-light engine (imports only the manifest, safe for the onboarding critical path). Computes remaining scope, `required_velocity`, `capacity` (hours + attention span), `weekly_load`, pace `status` (ahead/on_track/at_risk), `goal_readiness`, session minutes, and foundations-first `next_concepts`.
  - `apps/web/src/lib/plan-pacing.test.ts` — 17 unit tests (capacity, session, weeksUntil, status transitions, edge cases). Green (test + typecheck + lint).
  - Not yet wired into any route — pure library, no behavior change in production.
- **Stream 3a (read-only pacing overlay) — done (2026-07-19):**
  - `computePlanPacing()` in `neon-db.ts` attaches a `PlanPacing` overlay to
    `getCurrentPlan()` (goal readiness, weeks-left, remaining scope, required
    velocity vs capacity, pace status). Computed from profile `goal_key` +
    concept mastery + deadline. Null when the goal has no frontier.
  - `planPacingSchema` + optional `pacing` on `learningPlanSchema` (`@asf/schemas`).
  - Bilingual `PacingBanner` on the plan dashboard (readiness bar + pace chip +
    weeks-to-goal). **Read-only trajectory overlay — does NOT change concept
    selection**, so it cannot contradict the persisted plan (avoids the
    ADR-0008 dashboard-vs-engine hazard).
  - Verified: typecheck + lint + `pnpm --filter @asf/web build` all green.
  - Deferred (needs a decision): frontier-driven concept SELECTION for the
    FIRST plan. At onboarding there's no mastery yet, so a foundations-first
    frontier slice would start advanced-goal learners at `arithmetic`. Requires
    goal-level baseline mastery seeding (curriculum decision) before wiring —
    tracked for a later stream.
- **Stream 3c (agent trajectory-awareness) — done (2026-07-19):**
  - Chat route injects a "Goal pacing" block into the internal context for
    tutor / coach / curriculum_designer / progress_analyzer: goal readiness %,
    time-to-goal, pace status, and a status-specific framing hint (behind →
    protect core + morale; ahead → offer stretch). Reuses the mastery already
    loaded on the chat path (no extra DB call). Read-only framing.
  - Verified: typecheck + lint + production build green.
- Deferred / owner-gated (asked, user delegated to judgment):
  - **First-plan SELECTION** left on current goal-keyed entry points (no
    onboarding regression); frontier drives the agent + overlay layers instead.
  - **Week-gates + Tests archive + planning-state persistence** need a
    production Neon migration — not run autonomously. Migration scripts + code
    to be authored for owner execution when prioritized.
- Streams 3b (gates), 4 (tests archive), 5 (schema), 6 (evals): pending.

## Related

- [ADR-0006](0006-neon-direct-critical-path.md), [ADR-0007](0007-learning-planner-authority.md), [ADR-0008](0008-adaptive-wellbeing-planning.md)
- `.cursor/skills/diagnostic-plan-golden-path/SKILL.md`, `.cursor/skills/use-learning-plan/SKILL.md`, `.cursor/skills/onboarding-flow/SKILL.md`, `.cursor/skills/build-custom-quiz/SKILL.md`, `.cursor/skills/cross-subject-kg/SKILL.md`
- `obsidian-vault/curriculum/learning-path-architecture.md`
