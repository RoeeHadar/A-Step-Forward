# Repo Memory Snapshot

> Loaded by the `agentStart` Cursor hook. Keep it short and current.

## Project

**A Step Forward** — AI-native learning center. See `PLAN.md` (master plan).

## Phase

**Phase 1/2 — Stream sub-agents in flight.** Round 1 (Phase 0) landed the
foundation. Round 2 is now active: each stream has a *resume brief* at
`.cursor/subagent-briefs/NN-<stream>-resume.md` — that is the paste-and-go
prompt for the matching Composer 2.5 sub-agent. A new **Release Captain**
stream (`11-release-captain-resume.md`) coordinates merges, deploys, and
launch. **Read `.cursor/subagent-briefs/RESUME-README.md` first** — its
locked decisions are project policy; sub-agents must not stop to ask the user.

## Key invariants

- Every memory R/W goes through `MemoryService` (or the `memory` MCP).
- Every agent extends `packages/agents/agents/base/agent.Agent`, has a versioned
  prompt under `prompts/<agent>/v<n>.md`, declares `memory_policy`, and ships an
  eval suite under `evals/agents/<agent>/`.
- Every prompt change requires updated evals — CI blocks regressions.
- Never bypass `SafetyModeration.pre()` / `.post()`.
- Sub-agents stay inside the brief's in-scope files.

## Working areas this week

See `docs/sprint.md`.

<!-- LAST_SESSION -->
## Last done (2026-07-07)

Retrieve this block for “what we just finished” on architecture reviewer fixes + CI.

| Item | Status | Where |
|------|--------|--------|
| Architecture Steward + Code Reviewer agents (skills, briefs 24/25) | Done | `skills/architecture-review/`, `skills/code-review/`, `.cursor/subagent-briefs/24|25-*.md` |
| Architecture assessment L1–L4 | Done | `docs/architecture/assessments/2026-07-05-platform-overview.md` |
| First Code Review (R1–R7) | Done | `docs/reviews/2026-07-05-coordinator-fixes.md` |
| R1–R2 transactional xact locks (plan + consolidate) | Done | `apps/web/src/lib/neon-db.ts` (`pg_try_advisory_xact_lock` + `sql.transaction`) |
| R3–R4 dashboard/memory 503 + `NeonQueryFailedError` | Done | `apps/web/src/app/api/dashboard/route.ts`, `…/memory/route.ts` |
| R5 mapper/lock unit tests | Done | `apps/web/src/lib/neon-db-mapper.test.ts` |
| Keep Render warm no longer fails main | Done | `ff021ca9` — `.github/workflows/keep-warm.yml` always `exit 0`, 90s timeout |
| Cron/warm workflows `permissions: contents: read` | Done | `ff021ca9` — keep-warm + cron-dreaming/decay/consolidate |

**Still open (not this slice):** planner unification (`buildLearningPlan` authority), concurrency integration tests in assessment checklist, full `permissions:` pass on deploy/lint workflows.

**Commits:** `362f813b` (neon-direct + locks + agent groundwork), `ff021ca9` (CI keep-warm + read permissions).

Prior (2026-06-25): PR #15/#16 Render `EmailStr` / API import smoke lessons remain valid.

Adhoc note: chat/agent traffic about ProServAI / Gong / scorg.org is **out of scope** for this monorepo — no such code exists here.
<!-- LAST_SESSION -->

