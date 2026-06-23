---
name: memory-operations
description: How to use MemoryService and the memory MCP correctly — types, writes, reads, policies, audit, provenance. Read BEFORE you touch any code that reads or writes learner memory.
---

# Memory Operations

## Memory types
- **working** — current conversation context.
- **episodic** — events (sessions, lessons, quizzes).
- **semantic** — facts about the learner.
- **procedural** — how the learner learns (pace, modality, habits).
- **affective** — emotional signals (motivation, frustration).
- **context** — device, time-of-day, environment.
- **reflective** — agent-generated insights/hypotheses.
- **source** — external docs/links/files referenced.

Choose the narrowest correct type. When in doubt, write episodic + let the Dreamer promote.

## Writing (Python)
```python
from services.memory.memory_service.api import MemoryService
from schemas.memory import MemoryWriteInput, MemoryType, Provenance

await mem.write(MemoryWriteInput(
    learner_id=ctx.learner_id,
    type=MemoryType.EPISODIC,
    content="Learner asked for a worked example of long division.",
    tags=["math", "long-division"],
    importance_hint=0.4,            # optional hint, service still scores
    provenance=Provenance(
        kind="chat", id=turn_id, agent="tutor", model="claude-sonnet-4-5",
    ),
))
```

## Writing (Agent via MCP)
Use the `memory.write` tool. Pass the same fields. The service handles redaction, embedding, scoring, conflict resolution, and audit.

## Reading
- Use `memory.search(query, types, k, agent_id, learner_id)` — hybrid retrieval, rerank, policy filter.
- For timeline UIs use `memory.timeline`.
- Never iterate `SELECT * FROM episodic_memories` in feature code.

## Updates / corrections / deletes
- `memory.update(id, patch)` — patch with reason; original version retained.
- `memory.delete(id)` — soft delete; learner-initiated deletes cascade to embeddings + KG.
- Conflict resolution is automatic: new contradicting memory sets `superseded_by` on the old.

## Policies
- Pass `agent_id` on every read. The service applies the agent's `memory_policy`.
- Child mode blocks affective writes; respect it.

## Audit & privacy
- Every read/write is logged in `audit_memory_events`. Don't disable.
- PII is redacted pre-write. Don't bypass.

## Dreaming / consolidation
- Don't trigger dreaming inline from an HTTP request unless it's an admin/MemoryInspector flow. Use the Celery job `memory.dream_learner(learner_id)`.

## Pitfalls
- Don't use semantic memory for one-off events (use episodic).
- Don't write reflective memories from learner-facing flows — that's the Dreamer's job.
- Don't store raw PII in `content` thinking the redactor will catch it later.
- Don't manually compute embeddings; the service does it.
