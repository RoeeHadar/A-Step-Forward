# 03 — Agents — Resume Brief (Round 2)

## Current state

Phase 1: Tutor stub on `main`; `AGENT_REGISTRY` populated for all 20 agents; orchestrator + declarative router working (Phase-0 smoke test green).

Phase 2: real implementations for `assessment_generator`, `coach`, `curriculum_designer`, `grader`, `progress_analyzer`, `qa_explainer` shipped with capability/safety/thresholds eval YAMLs on `main`. Orchestrator routing test + QA citation test on `main`.

Phase 3 (in-flight, **preserved by Opus** on branch `wip/agents-phase3-snapshot`):
- New agent packages: `research`, `kg_builder`, `content_curator` — each with `agent.py`, `input.py`, `output.py`, `tools.py`, `memory_policy.py`, `budget.py`.
- New evals: `evals/agents/{research,kg_builder,content_curator}/{capability.yaml,safety.yaml,thresholds.yaml}` + `evals/agents/research/citation_test.py`.
- New tests: `packages/agents/tests/test_phase3_agents.py`, `services/orchestrator/tests/test_phase3_smoke.py`.
- Workspace stabilization: `pyproject.toml` cleanup across packages, ruff scoping fix, Alembic migration consolidation (drops `0002_core_tables.py`), `scripts/fix-workspace-sources.ps1`, `uv.lock`.
- Helpers added: `packages/agents/agents/base/{agent_helpers.py,prompts.py}` (referenced by new agents — confirm they exist or land them alongside).

> ⚠️ The Phase-3 snapshot was committed by Opus onto `wip/agents-phase3-snapshot` because it was sitting uncommitted on the wrong branch (`feat/graphrag/04-mcp-evals`). Resume by **cherry-picking the agent pieces** onto a fresh `feat/agents/03-phase3-system-agents` from `main`, **separately** from the workspace-stabilization commits (which belong to stream 09 — coordinate via the Release Captain).

## What's left

1. **Land Phase-3 agents** on their own branch off `main`, with their evals. Open one PR per agent (`feat(agents): add research`, `feat(agents): add kg_builder`, `feat(agents): add content_curator`). Evals must pass.
2. **Remaining Phase-3 agents**: `memory_steward` (Dreamer), `safety_moderation` (real impl, beyond stub), `eval_agent`, `analytics_insights`, `note_taker`, `engagement`, `accessibility`, `reviewer`, `mentor`. Same pattern — one PR per agent + evals.
3. **Wire the orchestrator** to dispatch to each implemented agent (replace placeholder "not implemented" branch in `services/orchestrator/orchestrator/runner.py` with a registry lookup that instantiates and runs the right `Agent` class).
4. **LLM client**: replace `packages/agents/agents/base/llm.py` stub with real Anthropic-primary + OpenAI-fallback calls (using Anthropic prompt caching for stable system prompts, retries via tenacity, Langfuse tracing, per-agent budget enforcement that raises `BudgetExceeded`).
5. **LangGraph upgrade**: move the orchestrator from declarative router to a LangGraph state machine with checkpointing + parallel composition (sub-agent for stream 03 only — keep router compatible).

## Locked decisions

- Default model: `claude-sonnet-4-5`. Deep model: `claude-opus-4-8` (Reviewer, Research, Curriculum Designer only). Cheap model: `claude-haiku-4-5` (Note-Taker, Engagement, KG batch).
- Prompt caching enabled for stable system prompts (Anthropic).
- Agents never call other agents directly; always via Orchestrator.
- Only `KGBuilder` and `MemorySteward` write to the KG.
- Eval gates enforced: no agent PR merges without `capability + safety + thresholds` met.

## Done when

- All 20 agents from `AGENTS.md` have a real `run()`, registered, eval-green.
- Orchestrator runs any of them by name; routes intelligently.
- LLM client uses real providers with retries, caching, tracing, budget enforcement.
- LangGraph orchestrator with checkpointing live; replaces the regex router for non-trivial flows (keep router as fallback).

## Required reading

- `PLAN.md` §3.3, §4, §11; `ARCHITECTURE.md` §2, §6.
- `.cursor/rules/{20,30,40,60}-*.mdc`.
- `skills/build-an-agent/SKILL.md`, `skills/prompt-authoring/SKILL.md`, `skills/run-evals/SKILL.md`.
- `.cursor/subagent-briefs/03-agents.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Agents sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/03-agents-resume.md
  3. .cursor/subagent-briefs/03-agents.md
  4. PLAN.md §3.3, §4, §11; ARCHITECTURE.md §2, §6
  5. skills/{build-an-agent,prompt-authoring,run-evals}/SKILL.md
  6. .cursor/rules/{20,30,40,60}-*.mdc

Then resume work:
  A. git checkout wip/agents-phase3-snapshot ; review the Phase-3 agent code
     for research / kg_builder / content_curator and their evals.
  B. git checkout -b feat/agents/03-phase3-system-agents main
     Cherry-pick (or copy in a new commit) ONLY the agent packages and their
     evals (NOT the pyproject / migration / lockfile changes — those belong
     to stream 09 and the Release Captain will coordinate).
  C. Open one PR per agent (research, kg_builder, content_curator). Each PR
     includes evals + tests. review-bugbot on every PR.
  D. Implement the remaining agents one PR each: memory_steward, safety_moderation,
     eval_agent, analytics_insights, note_taker, engagement, accessibility,
     reviewer, mentor.
  E. Replace the orchestrator runner's "not implemented" placeholders with a
     registry-driven dispatch.
  F. Replace packages/agents/agents/base/llm.py stub with real Anthropic-primary
     + OpenAI-fallback calls (prompt caching, retries, tracing, budget enforcement).
  G. Promote orchestrator to a LangGraph state machine with checkpointing.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. Evals gate every prompt/agent change.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: every agent in AGENTS.md is real and routed, ready for the deployed
website to use them end-to-end.
```
