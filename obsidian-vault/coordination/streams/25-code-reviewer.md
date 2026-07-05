# Stream 25 — Code Reviewer

**Cursor sub-agent** for deep code integrity review (not architecture, not evals, not full security audit).

## Brief & skill

| Resource | Path |
|----------|------|
| Sub-agent brief | `.cursor/subagent-briefs/25-code-reviewer.md` |
| Primary skill | `skills/code-review/SKILL.md` |
| Checklists | `skills/code-review/REFERENCE.md` |
| Reports | `docs/reviews/` |

## Scope

- Silent failures, dead code, async races, edge cases
- Clarity, over-engineering, test quality
- BLOCKER / WARN / NIT findings with `file:line` evidence

## Not this stream

- [[24-architecture-steward|Architecture Steward]] — topology & ADRs
- Stream 08 — promptfoo / DeepEval / Playwright
- Stream 10 — security threat model
- Bugbot — quick PR diff (`review-bugbot` skill)

## Status

| Date | Review | Verdict |
|------|--------|---------|
| 2026-07-05 | Groundwork shipped | Skill, brief, template, `docs/reviews/` |

## Review queue

1. [ ] Post-coordinator-fixes pass (`neon-db` locks, API routes, cron)
2. [ ] `apps/web/src/app/api/chat/route.ts` hot path
3. [ ] Plan apply + `generateLearningPlan` module

## Workflow with PRs

1. Bugbot on PR (required)
2. Code Reviewer on same diff if Bugbot WARN+ or large scope
3. Security (10) if auth/memory/RBAC touched
