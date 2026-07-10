# ADR 0008: Adaptive wellbeing planning and unified learning path

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Product owner + Architecture Steward
- **Supersedes / extends:** [ADR-0007](0007-learning-planner-authority.md) (implementation); aligns with [ADR-0006](0006-neon-direct-critical-path.md) (Vercel + Neon hot path)

## Context

A Step Forward differentiates from generic adaptive tutors through **dependency-aware planning** (static KG + backward BFS + mastery-weighted skill atoms) and **wellbeing-aware pacing** (morale-boost topic selection without clinical framing). An internal audit (2026-07-10) found:

| Intended behavior | Shipped behavior (pre-ADR) |
| --- | --- |
| Single authoritative “what to study next” | Two planners: `buildLearningPlan()` (chat/API) vs `generateLearningPlan()` (dashboard weeks) with different algorithms |
| Anxiety-aware curated topics | `exam_anxiety` intent with **`injectLearningPlanSnapshot: false`** and LLM-improvised gap naming |
| Proactive plan adaptation to learner signals | Plan changes mostly **template-only** via Tutor sidebar; profile anxiety only affects prompt tone |
| Cross-subject root cause | `buildLearningPlan()` uses cross-edges; weekly planner does not |

**Pilot context (2026-07-11):** No active learners yet; target ~tens of students within months, predominantly **Bagrut (new curriculum: 372/471/572)**, some makhina and university tracks. Per-learner logic must not depend on cohort composition. All infra on **free tiers** (Vercel, Neon, Render, Neo4j Aura, Groq) with **no near-term paid-tier plan** — cost-sensitive throttling (dreaming/consolidation frequency) is not required for launch.

**Product decisions confirmed:**

1. Morale/anxiety adaptation affects **both** chat guidance **and** persisted `plan_weeks`.
2. **Soft framing** in learner-facing copy; full rationale only if explicitly asked.
3. **Proactive** replan from profile and measured signals, not only explicit chat intent.
4. Internal agent memory must record wellbeing bias state; learners see neutral change notices, not mechanism.
5. Plan migration on schema bump is acceptable **with caution** (version gate + pilot-first regen).

**Known accepted tradeoff:** Generic dashboard copy (“התוכנית עודכנה לפי ההתקדמות שלך”) may allow perceptive teens to pattern-match plan changes after stress mentions. Disclosure policy covers honest answers when asked; no additional concealment layer in v1.

---

## Decision

### 1. Single learning-path engine (implements ADR-0007)

1. **`buildLearningPlan()`** (`apps/web/src/lib/learning-plan.ts`) is the **only** authority for concept sequencing, urgency, `blocking_atoms`, and cross-subject backward BFS.
2. **`generateLearningPlan()`** (`apps/web/src/lib/neon-db.ts`) becomes a **persistence and calendar layer**: calls the unified engine (plus wellbeing overlay), then writes `learning_plans` / `plan_weeks`.
3. Chat snapshot, `GET /api/learning-plan/next`, and dashboard active week **must not contradict** after unification.

### 2. Wellbeing module (new, server-side)

Introduce a dedicated module (proposed path: `apps/web/src/lib/wellbeing-plan-bias.ts`) responsible for:

| Responsibility | Owner |
| --- | --- |
| Signal ingestion | Profile `mental_state.anxiety`, exam dates, mastery deltas, chat intent |
| Internal state | `wellbeing_plan_bias` (JSON on learner profile or dedicated column) |
| Morale concept selection | `selectMoraleConcepts()` — strength-anchored 1-hop neighbors on combined graph |
| Persisted plan overlay | Blend into active week (~60% goal-critical / ~40% morale-adjacent when bias active) |
| Cooldown / rate limits | See §3 |
| Audit metadata | `plan_adjustment_kind`, `plan_last_adjusted_at` |

**Morale selection algorithm (v1):**

1. Identify strength concepts: `concept_mastery ≥ 0.7` (or top-N by atom success in learner’s subjects).
2. Expand 1-hop via within-subject prereqs + cross-edges (`prereq`, `applies_to`, `generalizes`; cap depth 1).
3. Filter: on-track for learner `goal_key` / `points_group`; exclude concepts with urgency above goal-critical threshold unless mastery-shock override.
4. Score: prior success, lower blocking weight, still exam-relevant.
5. Merge with `buildLearningPlan()` output using configured ratio when bias active.

### 3. Two-layer replanning with asymmetric rate limits

**Layer A — internal state (immediate, no cooldown):**

- Update `wellbeing_plan_bias` on any qualifying signal change.
- Refresh chat injection snapshot for current session.
- Write/update Mentor private note (internal rationale).

**Layer B — persisted `plan_weeks` rewrite (gated):**

Rewrite active/upcoming week only when a **threshold** is crossed **and** cooldown allows (unless exempt).

| Trigger | Threshold | Cooldown / cap |
| --- | --- | --- |
| Anxiety band | Profile or updated `mental_state.anxiety` crosses **into ≥ 7** | Subject to shared wellbeing rewrite budget (below) |
| Exam window | First entry into **≤ 14 days** before `next_test_date` | One rewrite per exam window; may bypass 72h cooldown **once** when entering **≤ 7 days** |
| Chat wellbeing | `exam_anxiety` intent | Same budget as anxiety band |
| **Mastery shock** | Concept mastery drops **≥ 0.25** in one update, or crosses **from ≥ 0.6 to < 0.4** | **Exempt from weekly rewrite cap** (still respects minimum **24h** spacing between any two persisted rewrites to prevent same-day thrash) |

**Shared wellbeing rewrite budget (anxiety + exam-window + chat triggers only):**

- Minimum **72 hours** between wellbeing-class rewrites.
- Maximum **2 wellbeing-class rewrites per calendar week**.
- **Mastery-shock rewrites do not consume** the weekly cap of 2.

Rationale: self-reported anxiety is the signal most worth rate-limiting; measured skill drop is objective and must not be blocked because anxiety already consumed the cap.

### 4. Plan change authority exceptions

| Change type | Authority | Learner initiation |
| --- | --- | --- |
| Goal, hours, exam scope, cram priorities | Tutor sidebar **template only** (`ASF_PLAN_UPDATE`) | Required |
| Wellbeing / morale / mastery-shock adaptation | **Server** (`wellbeing-plan-bias` + unified planner) | Not required |
| Learner-initiated casual chat request | Redirect to template (unchanged) | — |

### 5. Agent ownership and chat behavior

| Agent | Role |
| --- | --- |
| **Mentor** | Owns wellbeing bias policy, internal notes, proactive replan triggers |
| **Tutor** | Executes sessions; receives injected snapshot; soft-framed copy |
| **Coach** | Drills from unified path + `weak_atoms` (unchanged contract) |

**Anxiety turn fix (v1):** For `exam_anxiety` intent:

- Set **`injectLearningPlanSnapshot: true`** (structured list from server, not improvised gaps).
- Replace “name 2–3 improvised gaps” with soft-framed guidance using server-selected concepts.
- Keep direct, reassuring interaction mode.

Profile `mental_state.anxiety ≥ 7` continues to inject tone guidance on every turn.

### 6. Disclosure and dashboard UX

| Surface | Policy |
| --- | --- |
| Chat | Soft, rational framing (“נחזק את הבסיס השבוע…”). No algorithm or strength-based reveal. |
| Learner asks directly | Honest explanation permitted per disclosure policy. |
| Dashboard | **Neutral notice** on any server-driven plan change: e.g. “התוכנית עודכנה לפי ההתקדמות שלך” / “Your plan was updated based on your progress.” |
| `/settings/persona` | No concealed rationale; optional high-level preference only (“responds well to gradual wins”). |

Store `plan_adjustment_kind`: `wellbeing` | `learner_template` | `mastery` | `exam_window` for internal audit.

### 7. Memory and context (free-tier appropriate)

- **No embedding clustering** on Vercel hot path (unchanged).
- **Dreaming / consolidation** frequency unchanged; no paid-tier hedge required.
- Durable wellbeing context lives in **`wellbeing_plan_bias` + Mentor notes + persona** (trimmed), not long `chat_turns` replay.
- Chat budgets remain per `chat-context-policy.ts` unless integration tests show overflow.

### 8. Retrieval architecture (unchanged hot path; GraphRAG frozen)

| Concern | v1 production path |
| --- | --- |
| Dependency / next topic | Static `kg-data.json` + `kg-cross-edges.json` + `buildLearningPlan()` |
| Message-relevant concepts | Keyword match (max 3) in chat route |
| GraphRAG (Neo4j + pgvector) | **Phase 2** — optional Render; not required for Bagrut pilot |

**Phase 2 freeze:** Do not expand Neo4j CI seeding or chunk corpus until a single integration point is chosen (e.g. Q&A Explainer long-tail fallback). Document in vault; do not delete existing stack.

### 9. Track and curriculum defaults (pilot)

- Onboarding and plan defaults target **new Bagrut curriculum** (372/471/572).
- Legacy 382 calculus references remain in catalogue for documentation only, not default enrollment.
- Per-learner filtering via `quiz-concept-filter.ts` / `points_group` (unchanged).

### 10. Plan migration

- Add `plan_schema_version` (integer) on `learning_plans`.
- On version bump: regenerate plan on next login for affected learners.
- Pilot rollout first; avoid blind mass regen without version gate and integration test coverage.

### 11. Pilot compliance (ages 16–18)

Bagrut pilot cohort is typically **16–18**. Compliance focus:

- **Informed consent** (one line at onboarding): self-reported stress/anxiety is used to adjust study pacing and topic order; not diagnosis; not shared with third parties.
- **Data minimization:** store only necessary fields; internal bias JSON not learner-editable as raw mechanism dump.
- Do **not** treat COPPA as the primary compliance frame for this pilot; age-appropriate transparency and consent norms apply instead.

---

## Consequences

### Positive

- Dashboard and chat share one golden path — trust preserved.
- Flagship wellbeing differentiation becomes **server-enforced**, not LLM-improvised.
- Cooldown asymmetry prevents jitter while preserving response to objective mastery drops.
- Module boundary (`wellbeing-plan-bias.ts`) allows Phase 2 signals without replanning architecture.

### Negative

- `neon-db.ts` + new module coupling until further extraction.
- Server-driven plan changes require new integration tests and migration discipline.
- Generic dashboard notice may leak weak pattern to attentive users (accepted).

### Risks

- Over-active internal bias updates without persisted rewrite could confuse agents if snapshot and dashboard diverge — mitigate by always deriving chat snapshot from same engine output as would be persisted when gate opens.
- Template-only product docs must be updated to document wellbeing exception — doc drift if skipped.

---

## Alternatives considered

| Alternative | Why rejected |
| --- | --- |
| Keep dual planners | Contradictory next steps (F1); undermines trust |
| Chat-only morale (no `plan_weeks`) | Violates product “both surfaces” requirement |
| Full concealment (silent plan changes) | Erodes trust when learner notices drift |
| Single shared rewrite counter for all triggers | Blocks mastery-shock after anxiety/exam rewrites |
| Improvise gaps on anxiety turns | Bypasses structured KG; current anti-pattern |
| GraphRAG on Vercel hot path for v1 | Cost/complexity; dependency reasoning is graph-native |
| Populate unused `level_focus` schema in v1 | Separate-file-per-track is de facto standard; defer or deprecate fields |

---

## Implementation status

**Shipped on branch `feat/frontend/unify-planners-pr1` (PR1–PR3, 2026-07-11):**

- **PR1** — Unified planner: `plan-worklist.ts` + `buildUnifiedPlanConceptOrder()`; `generateLearningPlan()` calls `buildLearningPlan()` for concept sequencing.
- **PR2** — Wellbeing module: `wellbeing-plan-bias.ts` (signal ingestion, morale selection, cooldown gates, `wellbeing_plan_bias` persistence).
- **PR3** — Chat + UX: compact baseline, 4-turn session-gated memory, anxiety intent snapshot injection, `plan-adjustment-notice` on dashboard.

PR4 (this doc reconciliation) updates ADRs, skills, and vault notes. Remaining checklist items: integration tests, pilot rollout, content gaps.

## Verification (when implemented)

- `plan-neon.integration.test.ts`: persisted week order matches `/api/learning-plan/next` for fixture learners.
- Wellbeing cooldown tests: anxiety rewrite capped; mastery-shock exempt from weekly cap; 24h minimum spacing.
- Anxiety intent: snapshot injected; no “improvise gaps” primary instruction.
- Dashboard: neutral notice on `plan_adjustment_kind !== learner_template`.
- Manual pilot script: learner with anxiety ≥ 7 sees blended week without mechanism in copy.

---

## Related

- [ADR-0007](0007-learning-planner-authority.md) — planner authority (this ADR implements)
- [ADR-0006](0006-neon-direct-critical-path.md) — Neon-direct SSOT
- [ADR-0005](0005-embeddings-sentence-transformers.md) — GraphRAG embeddings (Phase 2)
- `obsidian-vault/curriculum/learning-path-architecture.md`
- Execution checklist: [../plans/adaptive-wellbeing-integration-checklist.md](../plans/adaptive-wellbeing-integration-checklist.md)
