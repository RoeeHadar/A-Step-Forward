# Last done

> Short, retrievable log of completed Coordinator / reviewer work.
> Agents and humans: read this (and `MEMORY_SNAPSHOT.md` `<!-- LAST_SESSION -->`) before re-deriving status.

## 2026-07-07 — Code-review fixes + CI noise

**Goal:** Land remaining review findings and stop scheduled red X’s on `main`.

| Checkpoint | Done? | Evidence |
|------------|:-----:|----------|
| Architecture Steward groundwork (skill + brief 24) | [x] | `.cursor/skills/architecture-review/`, `.cursor/subagent-briefs/24-architecture-steward.md` |
| Code Reviewer groundwork (skill + brief 25) | [x] | `.cursor/skills/code-review/`, `.cursor/subagent-briefs/25-code-reviewer.md` |
| Platform architecture assessment | [x] | `docs/architecture/assessments/2026-07-05-platform-overview.md` |
| Coordinator-fixes code review (R1–R7 written) | [x] | `docs/reviews/2026-07-05-coordinator-fixes.md` |
| R1 — xact advisory lock (Neon HTTP-safe) | [x] | `neon-db.ts` `pg_try_advisory_xact_lock` inside `sql.transaction` |
| R2 — plan DELETE+INSERT transactional | [x] | `generateLearningPlan` persist batch in one `transaction` |
| R3 — `dbConfigured === false` → 503 | [x] | `/api/dashboard`, `/api/memory` |
| R4 — DB errors logged + 503 via `NeonQueryFailedError` | [x] | same routes + snapshot helpers |
| R5 — unit tests (mapper / lock helpers) | [x] | `apps/web/src/lib/neon-db-mapper.test.ts` |
| Keep Render warm never fails the schedule | [x] | `ff021ca9` best-effort `exit 0`, 90s timeout |
| Cron/warm jobs declare `permissions: contents: read` | [x] | keep-warm, cron-dreaming, cron-decay, cron-consolidate |

**Commits**

- `362f813b` — neon-direct routes, transactional locks, agent review groundwork
- `ff021ca9` — keep-warm exit policy + read-only permissions on cron/warm workflows

**Not in scope / not started**

- Dual planner unification (ADR-0007 follow-up)
- Adding `permissions:` to *every* deploy/lint workflow
- Anything named ProServAI / Gong / scorg — **not this repository**

## How to load next session

1. Open `docs/reviews/LAST_DONE.md` (this file).
2. Open `MEMORY_SNAPSHOT.md` block between `<!-- LAST_SESSION -->` markers (also loaded by `agentStart` hooks).
3. Open `obsidian-vault/_active-context.md` for product next steps.
