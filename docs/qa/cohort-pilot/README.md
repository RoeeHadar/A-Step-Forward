# Cohort pilot kit (10 students + 1 teacher)

Human-operated production pilot to collect structured feedback and drive a prioritized improvement wave.

**Site:** https://a-step-forward-waij.vercel.app  
**Locale:** Hebrew for all testers  
**Decisions:** locked in grill-me session 2026-07-20

## Contents

| File | Purpose |
|------|---------|
| [roster.json](./roster.json) | Machine-readable roster (fill `email` / `clerk_user_id` after signup) |
| [roster-sheet.csv](./roster-sheet.csv) | Human spreadsheet template |
| [personas.md](./personas.md) | Persona cards + session checklists |
| [feedback-form-student.md](./feedback-form-student.md) | Student form (copy into Google Form / Notion) |
| [feedback-form-teacher.md](./feedback-form-teacher.md) | Teacher form |
| [ops-runbook.md](./ops-runbook.md) | Accounts, links, seeding, reset, pre-flight |
| [preflight-checklist.md](./preflight-checklist.md) | Core-path smoke before inviting cohort |
| [daily-triage.md](./daily-triage.md) | P0 log during the week |
| [synthesis-template.md](./synthesis-template.md) | Post-pilot 90-minute synthesis |

## Scripts

```powershell
# Seed S7–S10 after roster.json has clerk_user_id or email
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
$env:DATABASE_URL='<prod Neon URL — never commit>'
node scripts/seed-cohort-pilot.mjs --dry-run
node scripts/seed-cohort-pilot.mjs
node scripts/seed-cohort-pilot.mjs --only S7,S8

# Single account (also used by cohort script)
node scripts/seed-pilot-demo.mjs --variant at-risk --goal bagrut_math_4 --email pilot_s8@… --anxiety 9 --hours 3
```

Reset: see `.cursor/skills/reset-learner-prod/SKILL.md` and `scripts/reset-learner.mjs`.

## Success bars (reminder)

| Outcome | Rule |
|---------|------|
| Win | ≥7/10 students avg ≥3.5/5; teacher avg ≥3.5; 0 unresolved core-path blockers |
| Targeted rework | 5–6/10 ≥3.5, or teacher &lt;3.5, or theme ≥3 people |
| Serious rethink | &lt;5/10 ≥3.5, or ≥2 core-path blockers, or teacher can't do ≥2 scripted actions |

Feedback guides changes; it is not sacred. Top 5 changes after synthesis.

## Order of operations

1. Pre-flight smoke ([preflight-checklist.md](./preflight-checklist.md)) — fix P0s  
2. Provision accounts (needs secrets — see [results/STATUS.md](./results/STATUS.md)):

```powershell
# apps/web/.env.local must have CLERK_SECRET_KEY (+ DATABASE_URL for later seed)
node scripts/provision-cohort-accounts.mjs --base-email YOU@gmail.com --password '…' --dry-run
node scripts/provision-cohort-accounts.mjs --base-email YOU@gmail.com --password '…'
```

3. Fill remaining roster fields if needed; teacher + students complete `/identity`  
4. Teacher invites all 10; students accept  
5. Fresh S1–S6: onboarding per persona card  
6. Seeded S7–S10: `node scripts/seed-cohort-pilot.mjs`  
7. Run sessions → write forms into `results/responses/S#.md` / `T1.md`  
8. Daily P0 triage only  
9. Synthesis within 48h of last form  
10. Hold accounts ~2 weeks → full Neon reset  

Live tracker: [results/STATUS.md](./results/STATUS.md)

## Related

- `docs/qa/adr-0010-manual-test-plan.md` — ADR-0010 variant expectations  
- `scripts/seed-pilot-demo.mjs` — variants: `fresh`, `building`, `at-risk`, `near-exam`, `day-before`, `goal-complete`
