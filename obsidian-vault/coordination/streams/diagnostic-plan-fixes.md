# Diagnostic + plan fixes (Jul 2026)

Status: **diagnostic removed**; **rolling 2-week plan** (timeout root cause fixed).

## Works

- Onboarding steps 0–3 only → sync `createOnboardingPlan`
- Materialize **only 2 weeks** × ≤4 concepts (not full exam horizon)
- Sequential week chunks; horizon `end_date` separate from materialized weeks
- `advanceRollingPlanWindow` on plan fetch when active week past due
- Redirect to `/app` only when `{ has_plan: true }`

## Failed approaches (avoid)

- Building 12–24 weeks on first create → `FUNCTION_INVOCATION_TIMEOUT`
- Full BFS / textbook hydration before INSERT
- Long retry sleeps inside onboarding submit
- Client poll-only plan generation after diagnostic

## Skill

`skills/diagnostic-plan-golden-path/SKILL.md`
