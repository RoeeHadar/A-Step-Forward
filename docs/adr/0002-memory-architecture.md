# ADR-0002 — Multi-type, self-healing memory architecture

## Status

Accepted (2026-06-23).

## Context

A learning platform that "remembers the learner" sets the bar high. Naive
"chat history + RAG" decays badly at scale: duplicates pile up, contradictions
go silent, embeddings drift, privacy regulations bite, and the agents lose
focus on what actually matters for the learner.

## Decision

We adopt the **multi-type, self-healing memory architecture** documented in `PLAN.md` §5, with:

1. **Eight memory types** — working, episodic, semantic, procedural, affective, context, reflective, source.
2. A **single front door** — `MemoryService` — that owns redaction, embedding, importance scoring, conflict resolution, and audit. No feature code touches memory tables directly.
3. A **Memory Steward (Dreamer)** agent + Celery beat that nightly: replays episodes, extracts patterns, promotes to semantic/procedural, consolidates near-duplicates, applies decay/archival, refreshes hierarchical summaries (daily → weekly → lifetime), and projects insights into the KG.
4. **Conflict resolution** via `superseded_by` versioning — never overwrite silently.
5. **Decay** with Ebbinghaus-style strength + access reinforcement; archive (not delete) under threshold.
6. **Context-window compaction** at orchestrator-side before every LLM call.
7. **Retrieval-time policy filter** per agent + child-mode aware.
8. **Verification cycle** for high-stakes facts.
9. **Memory Inspector** UI: learners can view, correct, or delete any memory; deletes cascade to embeddings + KG.

## Consequences

- Higher engineering investment up-front; durable benefits long-term.
- All memory R/W flows through the service — easier to audit, easier to evolve.
- Agents are simpler: they request memory, they don't shape it.
- We need first-class evals for dreaming, consolidation, decay, conflict-resolution, PII (see `evals/memory/`).
