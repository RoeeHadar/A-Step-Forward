# Diagnostic + plan fixes (Jul 2026)

Status: **bare SQL bootstrap** (no neon-db monolith) — root cause of FUNCTION_INVOCATION_TIMEOUT.

## Root cause (confirmed)

Onboarding/submit imported `neon-db.ts` → `kg-data.json` (~325KB) + plan-worklist +
advisory-lock Neon transactions. Cold start + lock hack hung until Vercel killed the function.

## Works now

- `onboarding-plan-bootstrap.ts` — thin Neon client, no kg-data, no advisory locks
- `POST /api/onboarding/submit` → bootstrap only (profile + 2 weeks)
- `POST /api/plans/bootstrap` → same path for `/plan-setup` fallback
- Client 25s abort → `/plan-setup` if submit times out
- Rolling 2×4 concepts; advance window later via plans/current

## Failed

- Full exam-horizon plans
- neon-db createOnboardingPlan on submit
- pg_try_advisory_xact_lock + 1/0 in Neon HTTP transactions
- Long retry sleeps inside submit

## Skill

`skills/diagnostic-plan-golden-path/SKILL.md`
