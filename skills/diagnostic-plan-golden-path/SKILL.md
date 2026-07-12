---
name: diagnostic-plan-golden-path
description: >
  Golden path for onboarding → first learning plan (rolling 2-week window) and
  plan-setup fallback. Read before changing onboarding submit, plan generation,
  or the "Creating plan…" UX.
---

# Onboarding → rolling plan golden path (Vercel / Neon)

## End-to-end contract

```
/onboarding (4 steps: goals → background → motivation → tutor style)
  └─ POST /api/onboarding/submit
       └─ bootstrapOnboardingPlan()  ← thin module, NOT neon-db
            ├─ profile upsert
            ├─ ≤8 mastery seeds
            ├─ DELETE old plans (no advisory lock)
            └─ INSERT plan + 2 weeks (≤4 concepts each)
  └─ client → /app if has_plan; on abort → /plan-setup

/plan-setup → POST /api/plans/bootstrap (same thin path)
GET /api/plans/current → advanceRollingPlanWindow when week past due

**Never import `neon-db.ts` from onboarding/submit or plans/bootstrap** — it pulls
`kg-data.json` (~325KB) and caused `FUNCTION_INVOCATION_TIMEOUT`.

**Never use advisory-lock + `1/0` transactions on the onboarding path** — Neon HTTP
driver hung on contention.
```

**Target SLO:** onboarding submit completes with plan in **< 10s** (avoid Vercel `FUNCTION_INVOCATION_TIMEOUT`).

## Rolling window (critical)

| Rule | Why |
|------|-----|
| **Materialize only 2 weeks** | Full 12–24 week calendars timed out serverless (`FUNCTION_INVOCATION_TIMEOUT`) |
| **≤ 4 concepts per week** | Tiny DB transaction; enough for dashboard |
| **Sequential chunks** (`chunkConceptsIntoWeeks`) | Week 1 = first concepts; not round-robin |
| **`advanceRollingPlanWindow`** | When active week past due → complete it, promote upcoming, append next week from current mastery |
| **Horizon `end_date`** | Still reflects exam/goal timeline for UX; content weeks are rolling |

Do **not** regenerate the entire multi-week plan on onboarding. Mid-journey full regen only via explicit `?full=1` or agent template apply.

## What failed (do not reintroduce)

| Anti-pattern | Symptom |
|--------------|---------|
| Plan entire exam horizon (up to 24 weeks) on submit | `FUNCTION_INVOCATION_TIMEOUT` |
| Round-robin dozens of concepts across many weeks | Slow + pedagogically wrong |
| Client-only POST after diagnostic with 55–90s poll | Timer climbs forever |
| Long retry sleeps inside createOnboardingPlan | Extends past Vercel limit |
| Full `buildLearningPlan` BFS before first INSERT | 60s+ hang |

## Key files

| Area | Path |
|------|------|
| Onboarding submit | `apps/web/src/app/api/onboarding/submit/route.ts` |
| Create + advance | `neon-db.ts` → `createOnboardingPlan`, `advanceRollingPlanWindow` |
| Chunking | `plan-worklist.ts` → `chunkConceptsIntoWeeks`, `ROLLING_VISIBLE_WEEKS` |
| Plan setup UI | `apps/web/src/app/plan-setup/page.tsx` |
| Exists poll | `GET /api/plans/current?exists=1` |

## Related skills

- `skills/onboarding-flow/SKILL.md`
- `skills/use-learning-plan/SKILL.md`
