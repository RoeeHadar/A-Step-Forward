# 06 — MCP Servers — Resume Brief (Round 2)

## Current state

You shipped a 4-branch stack on top of `mcp-stack-base`:
- `mcp-stack-base`: removed Phase-0 stubs and laid the FastMCP base.
- `feat/mcp/01-memory`: Memory MCP (FastMCP) with full tool set + tests (200 lines of tests).
- `feat/mcp/02-graphrag`: GraphRAG MCP (FastMCP) + tests (124 lines).
- `feat/mcp/03-curriculum`: Curriculum MCP (FastMCP) + tests (99 lines).
- `feat/mcp/04-progress`: Progress MCP (FastMCP) + tests (80 lines).

Nothing merged to `main` yet. The Phase-3 cross-stream WIP further refactored the MCP tools (preserved on `wip/agents-phase3-snapshot`) — coordinate with stream 09 to land the right version cleanly.

## What's left

1. **Merge the stack** to `main` in the right order: `mcp-stack-base` → `feat/mcp/01-memory` → `02-graphrag` → `03-curriculum` → `04-progress`. PR per branch, `review-bugbot`, squash.
2. **Reconcile with `wip/agents-phase3-snapshot`** — diff your MCP tool implementations against that snapshot; cherry-pick the better refactor where applicable (keep tests + schemas as the source of truth).
3. **Schema-validated I/O** for every tool — Pydantic schemas from `packages/schemas/`; convert via JSON Schema in the FastMCP descriptor.
4. **Auth context** plumbing: tools must accept the `agent_id` + `learner_id` headers from the calling agent and apply memory/RBAC policy.
5. **Rate limits + cost telemetry**: middleware that tags tool calls with `(agent_id, tool_name)` and reports to Langfuse.
6. **Docker images** + `infra/docker/mcp/*.Dockerfile` so they can be deployed alongside the API (coordinate with stream 09).
7. **Cursor `mcp.json` updates**: confirm the project-side MCPs (`memory-project`, `graphrag-project`) point at the deployed staging URLs once Release Captain deploys them.

## Locked decisions

- Use **FastMCP** for all four servers (already aligned). No bespoke stdio frameworks.
- Tools accept + enforce `agent_id`, `learner_id`, `request_id` from headers — never trust body claims.
- Tool names are stable; bump via `v2_` prefix only with an ADR.
- Each server has its own `README.md`, `pyproject.toml`, `tests/`.

## Done when

- All four MCP servers merged to `main`.
- All tool calls auth-aware, schema-validated, telemetry-tagged.
- Servers deployable as Fly Machines / containers.
- `mcp.json` updated to point at deployed staging URLs.
- Tests + smoke tests green in CI.

## Required reading

- `PLAN.md` §7; `ARCHITECTURE.md` §7.
- `skills/build-an-mcp-server/SKILL.md`.
- `.cursor/rules/{20,30,40,50,60}-*.mdc`.
- `.cursor/subagent-briefs/06-mcp-servers.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the MCP Servers sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/06-mcp-servers-resume.md
  3. .cursor/subagent-briefs/06-mcp-servers.md
  4. PLAN.md §7; ARCHITECTURE.md §7
  5. skills/build-an-mcp-server/SKILL.md
  6. .cursor/rules/{20,30,40,50,60}-*.mdc

Then:
  A. Merge the stack to main, in order: mcp-stack-base → feat/mcp/01-memory →
     feat/mcp/02-graphrag → feat/mcp/03-curriculum → feat/mcp/04-progress.
     PR per branch, review-bugbot, squash.
  B. Reconcile with wip/agents-phase3-snapshot — pull the better refactor where it
     improves the tools, keep tests + schemas as the source of truth.
  C. Add schema-validated I/O + auth-context plumbing + rate limits + Langfuse
     telemetry to every tool.
  D. Add Dockerfiles under infra/docker/mcp/*.Dockerfile (coord stream 09).
  E. Update .cursor/mcp.json project-MCP URLs to the deployed staging hosts
     once Release Captain confirms them.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs. review-bugbot on each. review-security for memory MCP.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: four production MCP servers live, used by every agent in the
deployed website.
```
