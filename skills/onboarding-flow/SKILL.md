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
  ├─ Step 0: Goals + timeline (subjects, grade, next_test_date, final_goal_date)
  ├─ Step 1: Technical background (hours/week, self_rating, teacher_rating, style)
  ├─ Step 2: Mental / motivation (motivation, anxiety, confidence, study time, etc.)
  └─ Step 3: Self-assessment (1-10 per concept)
       POST /api/onboarding/submit
       ↓
       upsertLearnerProfile() writes learner_profiles
       + seeds concept_mastery from self_scores
       ↓
       router.push('/diagnostic')

/diagnostic                apps/web/src/app/diagnostic/page.tsx
  ├─ POST /api/diagnostic/start → 12 questions sampled from diagnostic_items
  ├─ POST /api/diagnostic/[id]/answer per question → updates concept_mastery
  └─ On complete:
       POST /api/plans/generate → generateLearningPlan()
       router.push('/dashboard')

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

`generateLearningPlan()` in `apps/web/src/lib/neon-db.ts`:

1. Pulls mastery from `concept_mastery`.
2. Builds a worklist of weak concepts (mastery < 0.4) and their unmet prerequisites.
3. Picks `numWeeks`:
   - 1–12 weeks based on `next_test_date` (≈ days/7).
   - 2–16 weeks based on `final_goal_date` if no test.
   - Default 4 weeks.
4. Sorts concepts by **prerequisite depth** in the KG (roots first) so the plan
   teaches dependencies before dependents.
5. Round-robins concepts into weeks.
6. Persists `learning_plans` + `plan_weeks` in Neon, replacing any active plan.
7. Hydrates each concept with up to 3 textbook sections + 2 Bagrut exams from
   the matching subject for surface in `LearningPlanDashboard`.

## Diagnostic behavior

`/api/diagnostic/start` samples 12 random items from `diagnostic_items` filtered
to the learner's subjects. **Not** an adaptive CAT — that lives on Render. The
Vercel path is intentionally simpler so it always works.

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
The 4-week default and 12-week cap live in `generateLearningPlan()`. If you
need longer plans (e.g. year-long goals), bump the upper bounds there.

## Re-running onboarding
A learner can edit their profile by visiting `/onboarding` again — the upsert
respects `learner_id` as a UNIQUE key and clobbers in place. To force a plan
rebuild, call `POST /api/plans/generate` (idempotent: replaces the active plan).
