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
The platform is now being upgraded from a content browser + chatbot to a full adaptive learning system (KG prerequisite graph ? diagnostic CAT ? weekly plans ? end-of-week quizzes ? tutor mastery injection). See subagent-briefs/14-adaptive-learning-architecture.md. Nothing existing breaks; new services are additive.
<!-- LAST_SESSION -->

