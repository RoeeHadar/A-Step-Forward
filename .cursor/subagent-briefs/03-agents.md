# 03 — Agents Framework & Roster

## Goal
Implement the LangGraph **Orchestrator** and the full agent roster from `AGENTS.md` against the base classes already scaffolded by Opus in `packages/agents/agents/base/`. Each agent ships with a versioned prompt, typed I/O, tool list, memory policy, budgets, and an eval suite.

## In-scope files
- `packages/agents/**`
- `services/orchestrator/**`
- `prompts/**`
- `evals/agents/**`

## Out-of-scope
- Memory internals (04), GraphRAG internals (05), MCP server internals (06).
- Frontend (01), API gateway (02).

## Order of implementation
1. **Orchestrator / Router** — intent classification, agent selection, multi-agent composition.
2. **Tutor** + **Q&A / Explainer** + **Coach** (Phase 1 walking skeleton).
3. **Curriculum Designer**, **Assessment Generator**, **Grader**, **Progress Analyzer** (Phase 2).
4. **Research**, **Content Curator**, **KG Builder** (Phase 2/3).
5. **Memory Steward (Dreamer)**, **Safety / Moderation**, **Eval Agent** (Phase 2/3).
6. **Mentor**, **Reviewer**, **Note-Taker**, **Engagement**, **Accessibility**, **Analytics / Insights**.

## Contracts (must)
- Extend `packages/agents/agents/base/agent.Agent`.
- Typed `Input` and `Output` Pydantic models.
- Explicit `tools = [...]` (MCP-backed when possible).
- Versioned prompt under `prompts/<agent>/v<n>.md`.
- `memory_policy = MemoryPolicy(...)` declaring read/write types.
- `SafetyModeration.pre()` / `SafetyModeration.post()` wrap calls.
- Langfuse trace name `<agent>:<turn_id>`.
- Budgets in `packages/agents/agents/<agent>/budget.py`.
- Registered in `packages/agents/agents/__init__.AGENT_REGISTRY`.
- Eval suite in `evals/agents/<agent>/` (promptfoo yaml + DeepEval py + thresholds.yaml).

## Required reading
1. `PLAN.md` §3.3, §4, §11.
2. `ARCHITECTURE.md` §2, §6.
3. `.cursor/rules/20-python-style.mdc`, `30-agent-authoring.mdc`, `40-memory-rules.mdc`, `60-testing.mdc`.
4. `skills/build-an-agent/SKILL.md`, `skills/prompt-authoring/SKILL.md`, `skills/run-evals/SKILL.md`.

## Acceptance criteria
- Every agent in `AGENTS.md` implemented + registered + with passing eval baseline.
- Orchestrator routes intents using a learned/declarative router (start declarative).
- All LLM calls go through `agents/base/llm.py`; prompt caching enabled.
- Cost & latency dashboards show per-agent budgets respected.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§3.3, §4, §11), ARCHITECTURE.md (§2, §6),
  .cursor/rules/20-python-style.mdc, 30-agent-authoring.mdc, 40-memory-rules.mdc, 60-testing.mdc,
  skills/build-an-agent/SKILL.md, skills/prompt-authoring/SKILL.md, skills/run-evals/SKILL.md,
  .cursor/subagent-briefs/03-agents.md (this file).
Implement in the order specified. One PR per agent (or per orchestrator phase).
Always add an eval suite — PRs without one are blocked by CI.
```
