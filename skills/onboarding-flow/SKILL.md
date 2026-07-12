---
name: onboarding-flow
description: >
  How the 4-step learner questionnaire feeds into the diagnostic and weekly
  plan generation. Read before adding a new onboarding question, changing
  what plan generation considers, or adjusting the diagnostic length.
---

# Onboarding → diagnostic → plan flow

## End-to-end path

```
Sign-up (Clerk)            apps/web/src/app/sign-up/.../page.tsx
  └─ forceRedirectUrl='/onboarding'

/onboarding                apps/web/src/app/onboarding/page.tsx
  ├─ Steps 0–3: goals, background, motivation, tutor mode
  └─ POST /api/onboarding/submit
       bootstrapOnboardingPlan() — thin module (NOT neon-db)
       router.push('/app') when has_plan; abort → /plan-setup

/plan-setup                POST /api/plans/bootstrap fallback

/diagnostic                redirects to /plan-setup (legacy)

/dashboard                 apps/web/src/app/dashboard/page.tsx
  └─ getCurrentPlan(userId) → renders LearningPlanDashboard
```

## What learner_profiles captures

| Column | Source |
|--------|--------|
| `goal` | Step 0 dropdown (or free text if "other") |
| `grade_level`, `points_group` | Step 0 dropdowns |
| `subjects` | Step 0 toggles (math, physics) |
| `hours_per_week`, `preferred_style`, `attention_span` | Step 1 |
| `self_scores` | Step 3 sliders, mapped to 0.1–0.9 mastery on submit |
| `next_test_name`, `next_test_date` | Step 0 — drives plan length |
| `final_goal_date` | Step 0 — fallback plan length |
| `mental_state` (JSONB) | Step 2 — motivation, anxiety, confidence, preferred_study_time, has_quiet_space, support_system, why_this_goal |
| `personality_profile` (JSONB) | Step 2 — Netflix-style preference vector |

## How plan generation uses the profile

**First plan (onboarding):** `bootstrapOnboardingPlan()` in
`apps/web/src/lib/onboarding-plan-bootstrap.ts` — do **not** call neon-db here
(see `skills/diagnostic-plan-golden-path/SKILL.md` trial-and-error log).

**Mid-journey:** `generateLearningPlan()` in `neon-db.ts` may use the full planner;
rolling window still prefers 2 visible weeks unless explicitly expanded.

## Diagnostic behavior

`/api/diagnostic/start` builds a **6-question** validation queue from concepts that
have renderable MCQs in `diagnostic_items` (see `skills/diagnostic-plan-golden-path/SKILL.md`).
Fresh sessions start on each visit unless one pending unanswered question exists
(page refresh mid-question). **Not** an adaptive CAT — that lives on Render.

`/api/diagnostic/[id]/answer` looks up the chosen letter's correctness via
`options.correct` on the item row, updates `concept_mastery` for the topic, and
returns either the next question or the completion payload.

## Adding a new question to onboarding

1. Add UI to `apps/web/src/app/onboarding/page.tsx` in the relevant step.
2. Include the value in the body of the `POST /api/onboarding/submit` call.
3. Either:
   - Add the field to `OnboardingPayload` + a new column in a fresh migration
     (extend `learner_profiles`), **or**
   - Nest it under `mental_state` / `personality_profile` JSONB (no migration needed).
4. Reference it from `buildContextPrompt` if it should affect chat tone.

Always prefer JSONB columns for soft/qualitative attributes; reserve real
columns for values plan generation needs to query on (dates, numerics).

## Plan length tuning
The 4-week default and 12-week cap live in `generateLearningPlan()`. First plan
after diagnostic uses `fastPath: true` (`buildFastPlanConceptOrder`) — see
`skills/diagnostic-plan-golden-path/SKILL.md`. If you need longer plans (e.g.
year-long goals), bump the upper bounds there.

## Re-running onboarding
A learner can edit their profile by visiting `/onboarding` again — the upsert
respects `learner_id` as a UNIQUE key and clobbers in place. To force a plan
rebuild, call `POST /api/plans/generate` (idempotent: replaces the active plan).
For onboarding-speed rebuild after diagnostic, use `POST /api/plans/generate?fast=1`.
