# Repo Memory Snapshot

> Loaded by the `agentStart` Cursor hook. Keep it short and current.

## Project

**A Step Forward** — AI-native learning center. See `PLAN.md` (master plan).

## Phase

**Phase 0 — Foundation laid by Opus (this session).** Implementation is delegated
to Composer 2.5 / Cursor Auto sub-agents per `.cursor/subagent-briefs/`.

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
Last session: 2026-06-23 (opus)
<!-- LAST_SESSION -->
