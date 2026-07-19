# Diagnostic + plan fixes (Jul 2026)

Status: **WORKING** — bare SQL bootstrap (`1d44e8cc`+). Plan creates after onboarding.

Full trial-and-error log lives in the skill (authoritative for agents):

→ [[../../.cursor/skills/diagnostic-plan-golden-path/SKILL|.cursor/skills/diagnostic-plan-golden-path/SKILL.md]]

(Repo path: `.cursor/skills/diagnostic-plan-golden-path/SKILL.md`)

## TL;DR for future agents

1. First plan = **`onboarding-plan-bootstrap.ts` only** — never `neon-db` on submit.
2. **2 weeks × ≤4 concepts**; roll forward later with `advanceRollingPlanWindow`.
3. No post-onboarding diagnostic gate; calibrate while learning.
4. Symptom `FUNCTION_INVOCATION_TIMEOUT` on plan create → you reintroduced the monolith, locks, or a huge calendar. Undo that; do not add more retries.

## Chronology (compressed)

| Phase | What happened |
|-------|----------------|
| A | Diagnostic broken (serve-time stems, stale resume, `question_idx`) → fixed with 6 Q + answer-time dedupe |
| B | Plan timer 60s+ / never redirects → fast path, poll, kickoff, 2-week cap — **still timed out** |
| C | Removed diagnostic; sync create via neon-db — **still `FUNCTION_INVOCATION_TIMEOUT`** |
| D | Thin bootstrap (no kg-data, no advisory locks) — **worked in production** |

## Failed approaches (do not retry)

- neon-db / kg-data on onboarding critical path  
- Advisory lock + `1/0` Neon HTTP transactions for first plan  
- Full exam-horizon week materialization  
- Client poll while server never commits  
- Long sleep-retries inside submit  
- Pre-serve stem reservation / resume-as-complete  

## Works

- `bootstrapOnboardingPlan` + `/api/plans/bootstrap`  
- Client abort → `/plan-setup` fallback  
- Verify `has_plan` before `/app`  
