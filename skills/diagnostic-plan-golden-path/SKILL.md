---
name: diagnostic-plan-golden-path
description: >
  Golden path for Vercel onboarding diagnostic (6 MCQs) and first learning-plan
  persist. Read before changing diagnostic session logic, plan generation on
  complete, or the "Creating plan…" client UX.
---

# Diagnostic → plan golden path (Vercel / Neon)

## End-to-end contract

```
/onboarding → POST /api/onboarding/submit → /diagnostic
/diagnostic → POST /api/diagnostic/start (fresh or pending-only resume)
            → POST /api/diagnostic/[id]/answer × 6
                 └─ on last answer: kickoffOnboardingPlan() server-side
            → generatePlanWithRetry() (client)
                 ├─ poll GET /api/plans/current?exists=1 every 1.5s
                 └─ POST /api/plans/generate (backup; server auto fast when no plan)
            → redirect /app when has_plan=true
```

**Target SLO:** `hasActiveLearningPlan()` true within **~10–15s** after the last diagnostic answer.

## Diagnostic — what works

| Practice | Why |
|----------|-----|
| **6 questions** (`DIAGNOSTIC_QUESTIONS_PER_SESSION` in `diagnostic-start.ts`) | Enough signal; avoids bank exhaustion and duplicate stems. |
| **Fresh session on start** unless one **pending unanswered** question exists | Prevents stale "complete" sessions skipping to plan. |
| **Mark stems asked only on answer**, not on serve | Was root cause of "zero questions" — queue drained before learner answered. |
| **Validation queue from concepts with available MCQs** (`buildAvailableValidationQueue`) | Never enqueue concepts with no renderable item. |
| **Client step counter from `responses.length`** | Legacy `question_idx` + partial resume caused "question 5 of 6" on Q1. |
| **`diagnosticAnsweredCount(state)`** server-side | Single source of truth for progress/completion. |

## Diagnostic — what failed (do not reintroduce)

| Anti-pattern | Symptom |
|--------------|---------|
| Resume partial sessions as complete | Skip straight to plan with wrong counts |
| Pre-serve stem reservation | Empty question list |
| Trust `question_idx` for UI progress | Counter starts at 5, completion says 7 |
| 12-question session on thin bank | Duplicates, timeouts, exhausted pool |
| Retry storm on plan lock | "Plan update already in progress" loop |

## Plan generation — what works

| Practice | File / API |
|----------|------------|
| **Server kickoff on last diagnostic answer** | `kickoffOnboardingPlan()` in answer route — plan starts before client POST |
| **Auto fast path when learner has no plan** | Works even if client bundle omits `?fast=1` |
| **`loadActivePlanStub` in ensure/wait** | No textbook hydration blocking exists poll |
| **Block adaptive full regen for 15 min** | `isFreshOnboardingPlan()` prevents mastery_shock clobber |

## Plan generation — what failed

| Anti-pattern | Symptom |
|--------------|---------|
| `buildUnifiedPlanConceptOrder` → `buildLearningPlan` on first plan | 60–120s+ Vercel; client timer climbs forever |
| Full content hydration before INSERT | Plan row never visible to poll |
| Client waits on POST only (55s abort) then gives up | Timer keeps going but no redirect |
| Retry POST on lock error | Amplifies contention |
| Return full hydrated plan from generate route | Large payload; unnecessary for redirect |

## Key files

| Area | Path |
|------|------|
| Session state | `apps/web/src/lib/diagnostic-plan.ts` |
| Start / answer routes | `apps/web/src/app/api/diagnostic/` |
| Diagnostic UI | `apps/web/src/app/diagnostic/page.tsx` |
| Client plan poll | `apps/web/src/lib/diagnostic-plan-client.ts` |
| Fast concept order | `apps/web/src/lib/plan-worklist.ts` → `buildFastPlanConceptOrder` |
| Plan persist | `apps/web/src/lib/neon-db.ts` → `generateLearningPlan({ fastPath })` |
| Generate API | `apps/web/src/app/api/plans/generate/route.ts` |
| Exists poll | `apps/web/src/app/api/plans/current/route.ts?exists=1` |

## When to use full path (not fast)

Use default `buildUnifiedPlanConceptOrder` (BFS + atoms) when:

- Tutor / Curriculum Designer regenerates plan mid-journey
- `plan-apply.ts` learner template modifications
- Adaptive refresh after substantial mastery change

Onboarding + post-diagnostic **always** use `?fast=1`.

## Verification checklist

1. Reset learner or use fresh Clerk user.
2. Complete onboarding + 6 diagnostic questions.
3. "Creating plan…" timer should stop and redirect within ~15s.
4. `GET /api/plans/current?exists=1` → `{ has_plan: true }`.
5. Dashboard shows week 1 concepts (titles may hydrate lazily on full fetch).

## Related skills

- `skills/onboarding-flow/SKILL.md` — questionnaire → profile fields
- `skills/use-learning-plan/SKILL.md` — planner contract for agents
- `skills/neon-direct-route/SKILL.md` — Vercel + Neon route patterns
