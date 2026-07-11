# Diagnostic + plan fixes (Jul 2026)

Status: **questions OK**, plan persist fixed with fast path + parallel poll.

## Works

- 6-question diagnostic validation queue (available MCQs only)
- Fresh diagnostic session; pending-only resume on refresh
- Answer-time stem dedupe (not serve-time)
- Client progress from `responses.length` / `diagnosticAnsweredCount`
- Plan: `POST /api/plans/generate?fast=1` + `buildFastPlanConceptOrder`
- Persist plan rows before wellbeing bias write
- Client polls `exists=1` while POST runs

## Failed approaches (avoid)

- 12-question sessions on thin bank
- Resume stale/partial sessions as complete
- Pre-mark stems on serve
- Full `buildLearningPlan` BFS on first plan (60s+ timeout)
- Hydrate textbook/Bagrut before INSERT
- Client-only POST wait with 55s abort

## Skill

Repo: `skills/diagnostic-plan-golden-path/SKILL.md`

## Production verify

After deploy: onboarding → 6 Q → plan redirect < 15s → dashboard week 1.
