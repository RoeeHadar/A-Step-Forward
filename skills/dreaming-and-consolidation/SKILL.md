---
name: dreaming-and-consolidation
description: How the Memory Steward (Dreamer) consolidates short-term memories, applies decay, resolves conflicts, builds hierarchical summaries, and projects insights into the Knowledge Graph. Read BEFORE editing dreaming, consolidation, decay, or KG projection code.
---

# Dreaming & Consolidation

## Purpose
Keep learner memory **healthy at scale** by simulating the cognitive processes that prevent memory degradation: replay, consolidation, decay, conflict resolution, abstraction, and projection into long-term structures.

## When dreaming runs
- **Cron**: nightly at 03:00 learner local time (env `MEMORY_DREAM_CRON`).
- **On-demand**: `POST /v1/memory/dream` (educator/admin) and `memory.dream_now` MCP (internal).
- **After session**: lightweight "micro-dream" pass after a long session (>30 min).

## Pipeline (`services/memory/memory_service/hygiene/dreaming.py`)
1. **Pull** last N hours of episodic memories for the learner.
2. **Cluster** by topic/concept (KG-assisted; cosine + KG-walk distance).
3. **Salience scoring** per cluster (novelty, repetition, emotional weight, teacher tagging).
4. **Pattern extraction** via Claude (`prompts/memory_steward/v1.md`):
   - mastered_concepts[]
   - lingering_misconceptions[]
   - learner_preferences_delta
   - emotional_trends
   - new_goals_or_obstacles
5. **Reflective memory writes** capturing each pattern with provenance.
6. **Semantic + procedural updates** (e.g., "learner prefers visual proofs", mastery deltas).
7. **Consolidation** — merge near-duplicates (cosine ≥ `MEMORY_CONSOLIDATION_DUP_COSINE`) with conflict resolution.
8. **Hierarchical summaries** — refresh today's daily digest, then weekly insight, then monthly profile.
9. **Decay sweep** — recompute effective strength; archive below threshold (don't delete).
10. **KG projection** — for clusters with `salience ≥ MEMORY_KG_PROMOTE_SALIENCE`, write/update KG nodes/edges via the KG Builder agent.
11. **Memory Health report** — write a record listing drift, contradictions, coverage gaps; surfaced in Memory Inspector.

## Conflict resolution
- For each candidate write, find the nearest existing semantic memory with cosine ≥ τ.
- If contradictory (LLM-judge), set `new.superseded_by` or `old.superseded_by` based on `(recency × confidence × user_trust)`.
- Never silently overwrite. Surface high-stakes contradictions in Memory Health for verification.

## Decay
- `strength(now) = salience × exp(-(now - last_accessed) / τ_user)` where `τ_user` adapts to access pattern.
- Each access **reinforces** (`salience += δ`, `last_accessed = now`).
- Below `archive_threshold` → mark `archived_at`, move embedding to cold index. Do **not** hard delete.

## Compression
- Convert verbatim conversations >24h old into structured summaries (`facts`, `decisions`, `open_questions`).
- Keep a layered ladder: verbatim (24h) → daily digest (30d) → weekly insight (1y) → lifetime profile.

## Context-window compaction (orchestrator-side)
- When prompt context > `MEMORY_CONTEXT_COMPACT_RATIO` of model limit, replace older turns with a structured summary block + keep last K verbatim + pinned memories.
- Implemented in `services/memory/memory_service/hygiene/compaction.py`; called by the orchestrator before every LLM call.

## Verification cycle
- Periodically (or for high-stakes facts), MemorySteward enqueues a verification prompt for the next session: "I think you prefer worked examples to definitions first — still true?"

## Evals to keep green
- `evals/memory/dreaming/*` — fidelity (did patterns reflect actual events?), no fabrication.
- `evals/memory/consolidation/*` — no duplicate semantic memories after run; no silent overwrites.
- `evals/memory/decay/*` — synthetic time-travel; archived items match expected curve.
- `evals/memory/conflict/*` — contradictions surface with `superseded_by`.

## Pitfalls
- Don't run dreaming inline on the request path.
- Don't dream over data containing unredacted PII.
- Don't dream over a single session; cluster across the window.
- Don't let salience compound without bound; cap `salience ∈ [0, 1]`.
