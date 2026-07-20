# Ops runbook — cohort pilot (production)

Never commit `DATABASE_URL`, Clerk secrets, or filled emails with passwords.

## 0. Roles

| Role | Owns |
|------|------|
| Pilot lead | Recruitment, roster sheet, seeding, P0 triage, synthesis |
| Testers | Stay in persona, checklists, forms |
| Eng on-call | Hotfix P0 only during the week |

## 1. Accounts (Clerk)

1. Create **11 dedicated** emails (not personal long-lived learning accounts).  
2. Sign up at https://a-step-forward-waij.vercel.app  
3. Each user opens `/identity`:  
   - Students → **learner** + username from `username_hint` in roster  
   - Teacher → **educator** + about-me short HE blurb  
4. Fill `email` + `clerk_user_id` in `roster.json` and `roster-sheet.csv`.  
   - Clerk user id: Clerk dashboard, or after sign-in from session / admin tools.

Suggested username pattern: `pilot_s1_math3` … `pilot_teacher_asf`.

## 2. Teacher ↔ students

1. Teacher: `/educator` → invite each student by username.  
2. Student: accept via notifications bell / `/notifications`.  
3. Verify all 10 appear on educator roster before deep sessions.

Friend graph (students): follow [personas.md](./personas.md) — do **not** friend everyone.

## 3. Fresh students (S1–S6)

1. Complete onboarding in Hebrew with persona goal + anxiety + hours.  
2. Goal keys to pick (labels may differ slightly in UI):

| ID | goal_key |
|----|----------|
| S1 | bagrut_math_3 |
| S2 | bagrut_math_4 |
| S3 | bagrut_math_5 |
| S4 | bagrut_physics |
| S5 | university_prep |
| S6 | calculus1 |

3. No seed script — they must feel real first-run friction.

## 4. Seeded students (S7–S10)

1. Sign up + `/identity` as learner.  
2. Optionally skim onboarding once so profile row exists, **or** let seed insert profile.  
3. Put `clerk_user_id` or `email` in `roster.json`.  
4. Seed:

```powershell
cd <repo-root>
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
$env:DATABASE_URL='<prod Neon URL — never commit>'
node scripts/seed-cohort-pilot.mjs --dry-run
node scripts/seed-cohort-pilot.mjs
```

Single:

```powershell
node scripts/seed-pilot-demo.mjs --variant building --goal bagrut_math_5 --user-id user_xxx --anxiety 4 --hours 10
```

5. Hard-refresh `/app`. Expected signals: see `docs/qa/adr-0010-manual-test-plan.md`.

| ID | variant | goal | anxiety |
|----|---------|------|---------|
| S7 | building | bagrut_math_5 | 4 |
| S8 | at-risk | bagrut_math_4 | 9 |
| S9 | near-exam | bagrut_math_5 | 6 |
| S10 | day-before | bagrut_math_5 | 9 |

## 5. Mid-week bugs

1. Tester: screenshot + 1 line → form + P0 channel.  
2. Core-path blocker → stop that path; continue other checklist items.  
3. Non-P0 → note and continue.  
4. Only pilot lead runs Neon resets / re-seeds.  
5. Log in [daily-triage.md](./daily-triage.md).

## 6. Reset / wipe

Full reset (default for pilot):

```powershell
node scripts/reset-learner.mjs --email <pilot@…> --delete-profile
```

Skill: `.cursor/skills/reset-learner-prod/SKILL.md`.

After synthesis: **hold ~2 weeks**, then full reset all 11 (+ optional Clerk delete).

## 7. DATABASE_URL trap (Windows)

`vercel env run` can be overridden by `apps/web/.env.local`. Verify hostname before wipe/seed:

```powershell
cd apps/web
$env:NODE_TLS_REJECT_UNAUTHORIZED='0'
npx.cmd vercel env run --environment production -- node -e "console.log(new URL(process.env.DATABASE_URL||'').hostname||'MISSING')"
```

## 8. Pre-flight

Complete [preflight-checklist.md](./preflight-checklist.md) **before** inviting the cohort. Fix P0s first.
