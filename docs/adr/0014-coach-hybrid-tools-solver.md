# ADR 0014: Coach hybrid tools + shared Tutor/Coach solver

- **Status:** Accepted
- **Date:** 2026-07-24
- **Deciders:** Product owner + Composer (grill-me session)
- **Related:** [ADR-0011](0011-agent-communication-quality.md), [ADR-0012](0012-agent-context-under-pressure.md), [ADR-0013](0013-intensive-practice-arena.md)

## Context

Live web agents (Tutor, Mentor, Coach, Reviewer) were differentiated mainly by persona/skills text while the chat path has no LLM tool-calling API (`llmStream` / `llmComplete` are text-only). Coach/Tutor still produced wrong finals on arithmetic and dumped solutions too early. We need **real allowlists + memory policy** and a **tool-backed solver** without inventing a full MCP surface on day one.

## Decision

1. **Uniqueness** via tool/data allowlists + memory policies (not more costume prompts alone).
2. **Hybrid tools**: server-side authoritative **tool packs** injected into the system prompt, plus post-stream `[[ASF_*]]` markers. No OpenAI-style `tools` on the LLM provider in wave 1.
3. **Proof bar**: shadow logging + soft citation (`[[ASF_CITE:…]]`) now; hard eval gates later.
4. **Memory**: layered always-on context + **handoff digests** (not raw cross-agent note dumps) + on-demand **`memory.expand`** pack when the turn needs more.
5. **Persona writes**: role-gated in skills (Mentor wellbeing, Tutor explanation-style, Coach drill prefs; Reviewer rare) + Memory Steward consolidate as backstop.
6. **Coach first** for drill packs: `get_due_queue`, `get_weak_atoms`, `memory.expand`.
7. **Shared solver** for Tutor + Coach: `curriculum.get_worked_example` + `solver.verify_numeric` (deterministic soft repair on verify miss).
8. **Method choice**: corpus/canonical method first; persona only as tie-break among valid authored methods.
9. **Reveal policy**: hint ladder; explicit “full solution” does **not** skip. After **N=2** varied hint/attempt cycles in chat → **offer → confirm**. Practice arena stays stricter (Resign = sealed escape).
10. **Verify fail**: soft repair now; promote to hard-block after evals.

### Wave 1 out of scope

Full MCP tool sprawl; inventing alternate methods beyond authored corpus; all-four digests as the primary ship (Coach/Tutor digests first); model-callable `mark_atom_practiced`; hard reply-blocking verify day one.

## Consequences

**Positive:** Replies can cite real pack IDs; arithmetic mistakes get a visible recheck; Coach drills stay grounded in due/weak-atom data.

**Risks:** Pack latency/token cost — keep packs small; soft repair only covers patterns we can parse deterministically.

## Alternatives considered

- Full LLM tool-calling loop — rejected (provider/fallback stack is text-only today).
- Coach-only solver — rejected (Tutor shares the same arithmetic wound).
- Hard-block verify day one — deferred until evals prove repair quality.
