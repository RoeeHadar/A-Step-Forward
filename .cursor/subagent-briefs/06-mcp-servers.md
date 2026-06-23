# 06 — MCP Servers

## Goal
Build the four custom MCP servers under `mcp-servers/` (memory, graphrag, curriculum, progress) on top of the services in `services/`. Each MCP shares Pydantic schemas with the gateway and exposes the smallest, sharpest tool surface needed by agents.

## In-scope files
- `mcp-servers/**`

## Out-of-scope
- Service internals (04, 05, 07).
- Agents that consume them (03).

## Required tools per MCP

### memory
- `memory.write(input)` → MemoryRecord
- `memory.search(query, types, k, agent_id, learner_id)` → list[MemoryRecord]
- `memory.timeline(learner_id, since, until)` → episodic list
- `memory.update(id, patch)`
- `memory.delete(id)` (soft)
- `memory.dream_now(learner_id)` — admin/internal
- `memory.consolidate(learner_id)`
- `memory.compact_context(messages, target_tokens)` → compacted context

### graphrag
- `kg.search`, `kg.walk`, `kg.hybrid`, `kg.personalized`
- `kg.related_concepts`, `kg.prereqs`, `kg.next_topics`, `kg.explain_path`

### curriculum
- `curriculum.list_courses`, `curriculum.get_course`, `curriculum.get_lesson`
- `curriculum.find_for_concept`, `curriculum.suggest_path(learner_id, goal_id)`

### progress
- `progress.snapshot(learner_id)`, `progress.gaps(learner_id)`, `progress.streak(learner_id)`
- `progress.update_mastery(learner_id, concept_id, score)`

## Required reading
1. `PLAN.md` §7, §3.3.
2. `.cursor/rules/20-python-style.mdc`, `60-testing.mdc`.
3. `skills/build-an-mcp-server/SKILL.md`.

## Acceptance criteria
- Each server launches via `python -m <package>.server` and registers in `.cursor/mcp.json`.
- Tool schemas are typed Pydantic models; descriptions are short + LLM-friendly.
- Pytest coverage ≥ 80%.
- Each tool has at least one eval in `evals/retrieval/` or `evals/memory/`.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§7, §3.3),
  .cursor/rules/20-python-style.mdc, 60-testing.mdc,
  skills/build-an-mcp-server/SKILL.md,
  .cursor/subagent-briefs/06-mcp-servers.md (this file).
Implement the four servers in order: memory, graphrag, curriculum, progress.
One PR per server. Add an evals fixture per server.
```
