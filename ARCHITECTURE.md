# Architecture

> Companion to `PLAN.md`. This document focuses on **how** components communicate and the **data flows**, while `PLAN.md` covers **what** and **why**.

## 1. Component Topology

```
        ┌─────────────────────────────────────────┐
        │           Next.js 15 (apps/web)         │
        │  RSC + Vercel AI SDK + TanStack Query   │
        └───────────────┬─────────────────────────┘
                        │ HTTPS / SSE / WS
        ┌───────────────▼─────────────────────────┐
        │      FastAPI Gateway (apps/api)         │
        │ auth · validation · rate-limit · trace  │
        └──┬──────────┬──────────┬─────────┬──────┘
           │          │          │         │
           ▼          ▼          ▼         ▼
   Orchestrator  Memory Svc  GraphRAG   Curriculum/Progress
   (LangGraph)   (Python)     (Python)        (Python)
           │          │          │         │
           └────┬─────┴────┬─────┴────┬────┘
                ▼          ▼          ▼
            Postgres   Redis      Neo4j
            +pgvector            (KG)
                ▲
                │
        Workers (Dreamer, Decay, KG ingest, Eval, Notifications)
```

## 2. Request Flow — Learner asks a question

1. Browser sends `POST /api/chat` with learner id + message.
2. Gateway authenticates (Clerk JWT) and forwards to **Orchestrator**.
3. Orchestrator:
   1. Fetches working/episodic/semantic memory snapshot via **Memory Service** (`memory.search`, `memory.timeline`).
   2. Optionally calls **GraphRAG** for relevant concepts/resources.
   3. Routes to the correct agent (Tutor / Q&A / Coach / etc.) using the **Router** policy.
4. Agent runs its LangGraph; tool calls are MCP-backed.
5. Tokens stream back via SSE to the frontend.
6. After the turn:
   * Episodic memory rows are written.
   * Importance scorer enqueues consolidation candidates.
   * Trace shipped to Langfuse.

## 3. Memory Write/Read Path

* All writes go through `MemoryService.write()` which:
  1. Redacts PII (Presidio).
  2. Embeds (Voyage / OpenAI).
  3. Scores importance (heuristic + LLM-judge).
  4. Inserts row with provenance + decay metadata.
  5. Enqueues KG extraction if `salience >= τ_kg`.
* Reads go through `MemoryService.search()`:
  1. Hybrid retrieval (BM25 + dense + KG walk).
  2. Rerank (`relevance × recency × confidence × user_trust × salience`).
  3. Policy filter (agent type, learner age, consent flags).
  4. Returns ranked, deduped memories with citations.

## 4. Dreaming / Consolidation Cycle

* Nightly Celery beat triggers `dream_learner(learner_id)`.
* Steps:
  1. Pull last 24h episodic memories.
  2. Cluster by topic + concept (KG-assisted).
  3. LLM produces `reflective_memories`, updates `semantic` & `procedural`.
  4. Run consolidation (merge near-duplicates with conflict resolution).
  5. Apply decay sweep; archive low-strength items.
  6. Refresh hierarchical summaries (daily/weekly/monthly).
  7. Update KG nodes (mastery deltas, new misconceptions, etc.).
  8. Emit a `MemoryHealth` report (drift, contradictions, coverage).

## 5. Sub-agent Workflow (development)

```
   Opus (planner) ──► Sub-agent brief (.cursor/subagent-briefs/NN.md)
                       │
                       ▼
   Composer 2.5 / Cursor Auto reads brief + relevant skill(s)
                       │
                       ▼
   Implements feature on a branch ──► PR ──► CI evals/lint/tests
                       │
                       ▼
              Bugbot / Security review ──► merge
```

## 6. Failure Modes & Mitigations

| Risk                              | Mitigation                                                        |
| --------------------------------- | ----------------------------------------------------------------- |
| Memory contradicts learner state  | Conflict-resolution + `superseded_by`, verification prompts.       |
| Hallucinated citations            | RAG-only citations; reranker; eval gate on citation accuracy.      |
| Cost runaway                      | Per-agent token budgets, prompt caching, eval-driven model routing.|
| Latency spikes                    | Async + Redis cache + edge SSR; per-agent SLO budgets.             |
| Prompt regressions                | Required offline evals on prompt PRs; shadow runs in prod.         |
| PII leak                          | Pre-write redaction; structured logs only; encryption at rest.     |
| Jailbreaks                        | Layered defense: system hardening, classifier, tool allowlists.    |
| Memory drift over months          | Dreaming + decay + verification cycle + Memory Health reports.     |

## 7. Deployment Targets

* **Frontend**: Vercel (preview per PR).
* **API + services**: Fly.io (regions near users).
* **Workers**: Fly Machines (scheduled + on-demand).
* **DBs**: managed Postgres (Neon/Supabase), managed Redis (Upstash), managed Neo4j (AuraDB) or self-hosted on Fly.
* **Tracing**: self-hosted Langfuse on Fly.

(Detailed infra is `infra/` and the `09-infra.md` sub-agent brief.)
