# Hacker News — Show HN draft

**Title (≤ 80 chars):**

> Show HN: A Step Forward – An AI learning center with memory that compounds

**Body:**

Hi HN,

A Step Forward is an open-source AI-native learning center. Instead of one
catch-all chatbot, you get a small team of specialised agents — a Tutor that
asks Socratic questions, a Mentor for goals and habits, a Coach that drills
you with FSRS-style reviews, a Reviewer for code and essays, a Researcher with
web + KG search — coordinated by an orchestrator.

The two ideas I'm proudest of:

1. **Multi-layered, self-healing memory.** Episodic, semantic, procedural,
   and affective layers, written through redaction + encryption, with a
   nightly "dreaming" job that consolidates, decays, and resolves conflicts.
   Every memory is inspectable and editable — there's a Memory Inspector
   panel in the UI.
2. **GraphRAG over a personal knowledge graph.** Lessons, notes, and uploads
   are chunked, embedded, and resolved into a per-learner KG. Retrieval is a
   hybrid (BM25 + dense + graph traversal + Cohere/Voyage rerank). Every
   claim links back to its source chunk.

Stack: Next.js 15 + Tailwind v4 + Clerk on the frontend; FastAPI + Pydantic v2
+ SQLAlchemy 2 async on the backend; Postgres+pgvector, Redis, Neo4j;
LangGraph orchestration; Claude primary with GPT + Gemini fallbacks;
Langfuse + Sentry + OTel for observability; promptfoo + DeepEval gating every
prompt and agent in CI.

Honest status: Phase 1 is live (signup, dashboard, Tutor chat, lesson view,
Memory Inspector, progress dashboards, GraphRAG seeded with a small math
course). Phase 2 (full Memory backend on Postgres+pgvector, Agents Phase 3,
Backend Phase 2 wiring) is in flight. The repo's "Round 2 resume briefs" walk
through the remaining streams.

License is MIT. Self-hosting docs are in `docs/infra/local-dev.md`. Privacy
docs in `docs/security/threat-model.md`. ADRs in `docs/adr/`.

I'd love feedback on the memory architecture (`ARCHITECTURE.md` §6,
`docs/adr/0002-memory-architecture.md`) and on whether the agent contract in
`packages/agents/agents/base/agent.py` is a sane base.

— Roee
