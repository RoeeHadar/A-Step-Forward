# Code Review Reports

Structured outputs from the **Code Reviewer** sub-agent (stream 25).

**Session log:** start at [`LAST_DONE.md`](./LAST_DONE.md) for the latest completed fix checklist (also mirrored in `MEMORY_SNAPSHOT.md` under `<!-- LAST_SESSION -->`).

## Naming

```
YYYY-MM-DD-<kebab-scope>.md
```

Examples:

- `2026-07-05-coordinator-fixes.md`
- `2026-07-10-pr-142-neon-api-routes.md`

## Template

Copy from `skills/code-review/templates/code-review-report.md`.

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **SHIP** | No BLOCKERs; safe to merge |
| **SHIP WITH WARNINGS** | No BLOCKERs; WARNs tracked for follow-up |
| **DO NOT SHIP** | At least one unresolved BLOCKER |

## Relationship to other review tools

| Tool | When |
|------|------|
| **Bugbot** (`review-bugbot` skill) | Fast PR diff on every PR (required by PR style rules) |
| **Code Reviewer (25)** | Deep integrity pass — silent failures, edges, races, clarity |
| **Security Review (10)** | Auth, secrets, RBAC, CSP |
| **Architecture Steward (24)** | System topology and ADRs |

Reports are informational until the Coordinator or stream owner implements fixes.
