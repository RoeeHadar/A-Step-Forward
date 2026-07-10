# ADR 0007: Learning planner authority

- **Status:** Accepted (implemented via [ADR-0008](0008-adaptive-wellbeing-planning.md))
- **Date:** 2026-07-05
- **Deciders:** Architecture Steward + Curriculum stream

## Context

Two planners coexist:

| Function | Location | Consumers |
|----------|----------|-----------|
| `buildLearningPlan` | `apps/web/src/lib/learning-plan.ts` | Chat, `/api/learning-plan/next`, agents |
| `generateLearningPlan` | `apps/web/src/lib/neon-db.ts` | Dashboard, plan apply, onboarding |

They use different algorithms (KG mastery walk vs template round-robin). Learners
and agents can see different “next steps” for the same goal (assessment F1).

## Decision

1. **`buildLearningPlan` is authoritative** for concept sequencing and weak-area
   diagnosis (`blocking_atoms`, cross-subject edges).
2. **`generateLearningPlan` becomes a persistence layer** — it calls
   `buildLearningPlan` (or equivalent) to order concepts, then writes
   `learning_plans` / `plan_weeks` for dashboard and quiz week UX.
3. Agent chat context and `/api/learning-plan/next` must never contradict the
   persisted active plan after unification.

## Consequences

### Positive

- Single source of truth for “what to study next”.
- Aligns with `obsidian-vault/_active-context.md` priority #1.

### Negative

- Migration work in stream 07 + 01; integration tests must cover edge cases.
- Week chunking may need to adapt to path output shape.

### Risks

- Breaking existing learners’ stored plans — require regen or one-time migration.

## Alternatives considered

- **Keep dual planners:** Rejected beyond next milestone (F1 P1).
- **Deprecate `plan_weeks` entirely:** Deferred — dashboard/quiz UX depends on it.

## Verification (when implemented)

- `plan-neon.integration.test.ts`: persisted week order matches `/api/learning-plan/next` for fixture learner.
- Manual: Tutor sidebar apply + dashboard week list show same top concepts.

## Implementation status

**Implemented via ADR-0008** (branch `feat/frontend/unify-planners-pr1`, PR1–PR3). `generateLearningPlan()` now delegates concept ordering to `buildUnifiedPlanConceptOrder()` → `buildLearningPlan()` in `plan-worklist.ts`; dashboard weeks and chat snapshot share one engine. See ADR-0008 for wellbeing overlay and rate limits layered on top.
