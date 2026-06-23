# A Step Forward — Master Plan

> Owner of this document: **Opus** (planning & foundation).
> Implementation: delegated to **Composer 2.5** / **Cursor Auto** sub-agents per `.cursor/subagent-briefs/`.

This document is the single source of truth for the project's architecture, agent roster, memory system, MCPs, hooks, skills, and how sub-agents should pick up work. Keep it up to date as the project evolves.

---

## 1. Product Vision

**A Step Forward** is an AI-native learning center: a web platform where students of any age engage with a roster of personalized AI agents (tutor, mentor, assessor, researcher, coach) that teach, assess, remember, and evolve with the learner.

Core differentiators:

1. **Persistent, multi-layered memory** of each learner (not just chat history).
2. **GraphRAG** over a domain-and-learner knowledge graph (concepts ↔ mastery ↔ content ↔ events).
3. **Adaptive curriculum** generated and refined per learner, with spaced repetition for retention.
4. **Multi-agent orchestration** — specialized agents collaborate, route, and review each other.
5. **Memory hygiene** — dreaming, consolidation, decay, conflict resolution, and provenance keep memory healthy at scale.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 15 / RSC)                     │
│   - Learner workspace, lessons, chat, dashboards, admin              │
│   - Streams agent responses via SSE / Vercel AI SDK                  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  REST / SSE / WebSocket
┌──────────────────────────────▼───────────────────────────────────────┐
│            API Gateway  (FastAPI, async, Pydantic v2)                │
│   - Auth, rate limit, schema validation, telemetry                   │
└─────┬───────────────┬───────────────┬────────────────┬───────────────┘
      │               │               │                │
      ▼               ▼               ▼                ▼
┌───────────┐  ┌───────────┐  ┌────────────┐  ┌────────────────┐
│ Orchestr. │  │  Memory   │  │  GraphRAG  │  │  Curriculum &  │
│  (LangGr) │  │  Service  │  │  Service   │  │  Progress Svc  │
└─────┬─────┘  └─────┬─────┘  └─────┬──────┘  └────────┬───────┘
      │              │              │                  │
      ▼              ▼              ▼                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                       Storage Layer                                │
│  Postgres + pgvector (relational + embeddings)                     │
│  Redis (cache, queues, pub/sub, rate limits)                       │
│  Neo4j / Memgraph (knowledge graph)                                │
│  Object Storage (S3 / R2 / Supabase) — media, uploads, snapshots   │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                  Background Workers (Celery / RQ)                  │
│   Dreamer · Consolidator · Decay sweeper · KG extractor · Evals    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack — Choices & Justifications

### 3.1 Frontend

| Concern              | Choice                                  | Why                                                              |
| -------------------- | --------------------------------------- | ---------------------------------------------------------------- |
| Framework            | **Next.js 15** (App Router, RSC)        | Best DX + SSR/streaming + edge + AI SDK; huge ecosystem.         |
| Language             | **TypeScript** (strict)                 | Required; pairs with Pydantic schemas via codegen.               |
| Styling              | **Tailwind CSS v4** + **shadcn/ui**     | Fast, accessible, customizable; MCP-supported.                   |
| Components / a11y    | **Radix UI** primitives via shadcn      | Accessible by default.                                           |
| Animation            | **Framer Motion**                       | Best React animation lib.                                        |
| State (client)       | **Zustand**                             | Tiny, fast, no boilerplate.                                      |
| Data fetching        | **TanStack Query** + REST (typed)       | Cache, retries, optimistic UI.                                   |
| AI streaming         | **Vercel AI SDK** (UI hooks)            | Streaming, tool calls, multimodal.                               |
| Forms                | **React Hook Form** + **Zod**           | Schema-validated forms; shares schemas with backend via codegen. |
| Charts / dashboards  | **Recharts** + **Tremor**               | Mastery curves, progress dashboards.                             |
| Editor (lessons/code)| **Monaco** or **CodeMirror 6**          | If teaching programming.                                         |
| Math                 | **KaTeX**                               | Fast LaTeX rendering.                                            |
| Markdown             | **react-markdown** + remark/rehype      | Lesson + chat rendering.                                         |
| Auth                 | **Clerk** (preferred) or NextAuth       | Quickest secure auth, parental controls if needed.               |
| i18n                 | **next-intl**                           | Multi-language.                                                  |
| Testing              | **Vitest** + **Playwright**             | Unit + E2E, with the Playwright MCP for agent-driven tests.      |

### 3.2 Backend (AI/API)

| Concern        | Choice                          | Why                                                  |
| -------------- | ------------------------------- | ---------------------------------------------------- |
| API framework  | **FastAPI** (async)             | Pydantic v2, OpenAPI, fast.                          |
| ORM            | **SQLAlchemy 2.0 async**        | Mature, async, vector-friendly.                      |
| Migrations     | **Alembic**                     | Standard for SQLAlchemy.                             |
| Validation     | **Pydantic v2**                 | Shared schema model.                                 |
| Queue          | **Celery** (Redis broker) or **Arq** | Background dreaming, ingestion, evals.          |
| Cache          | **Redis** + `redis-py` async    | Hot context, embeddings, rate limits.                |
| Auth verify    | **Clerk SDK** or **PyJWT**      | Verify tokens issued by frontend auth.               |
| Observability  | **OpenTelemetry** → **Langfuse** + **Grafana** | Full traces of LLM calls + spans.          |
| Tests          | **pytest** + **pytest-asyncio** | Unit + integration.                                  |
| Lint/format    | **ruff** + **black** + **mypy** | Consistent code quality.                             |

### 3.3 AI / Agents

| Concern             | Choice                                | Why                                                                       |
| ------------------- | ------------------------------------- | ------------------------------------------------------------------------- |
| Orchestration       | **LangGraph**                         | Cyclic graphs, checkpointing, human-in-the-loop, durable state.           |
| LLM primary         | **Anthropic Claude (Sonnet/Opus)**    | Strong reasoning + tool use + prompt caching.                             |
| LLM secondary       | **OpenAI GPT-5.x / Gemini 2.x**       | Diversification, cost optimization, multimodal.                           |
| Embeddings          | **Voyage `voyage-3-large`** or **OpenAI `text-embedding-3-large`** | Top retrieval quality.                       |
| Reranker            | **Cohere Rerank 3** or **Voyage rerank-2** | Improves RAG precision.                                              |
| Structured output   | **`instructor`** library              | Pydantic-validated tool outputs.                                          |
| Prompt management   | **`promptfoo`** + in-repo `prompts/`  | Versioned, testable prompts.                                              |
| Evals               | **DeepEval** + **promptfoo** + custom | Offline + online evals per agent.                                         |
| Tracing             | **Langfuse**                          | OSS, self-hostable, great LLM tracing.                                    |
| Guardrails          | **Guardrails AI** + custom moderation | Safety, PII, child-appropriate.                                           |

### 3.4 Data

| Store         | Choice                                | Use                                            |
| ------------- | ------------------------------------- | ---------------------------------------------- |
| Relational    | **Postgres 16**                       | Users, courses, sessions, memories.            |
| Vectors       | **pgvector** (in Postgres)            | Simpler ops, transactional; switch to Qdrant if scale demands. |
| Graph         | **Neo4j Community** (Memgraph alt.)   | Knowledge graph + GraphRAG.                    |
| Cache / queue | **Redis 7**                           | Ephemeral state, queues, pub/sub.              |
| Object store  | **S3 / R2 / Supabase Storage**        | Media, uploads, KG snapshots, model artifacts. |

### 3.5 DevOps

| Concern         | Choice                                  |
| --------------- | --------------------------------------- |
| Local dev       | **Docker Compose** (Postgres, Redis, Neo4j, Langfuse) |
| Frontend deploy | **Vercel**                              |
| Backend deploy  | **Fly.io** or **Railway** or **Render** |
| Workers         | **Fly Machines** or **Modal**           |
| Secrets         | **doppler** / **Vercel envs** / **.env.local** |
| CI/CD           | **GitHub Actions** (lint, test, eval, deploy) |
| Monitoring      | **Langfuse** (LLM) + **Sentry** (errors) + **Grafana**+ **Prometheus** |

---

## 4. Agent Roster

All agents run on **Composer 2.5** or **Cursor Auto** at the development layer.
At runtime, each agent has a primary LLM (Claude Sonnet default; Opus for heavy reasoning) and a routed fallback.

### 4.1 Learner-Facing Agents

| #  | Agent                | Purpose                                                              |
| -- | -------------------- | -------------------------------------------------------------------- |
| 1  | **Tutor**            | Conducts interactive lessons (Socratic, adaptive).                   |
| 2  | **Mentor**           | Career/motivation, goal setting, accountability.                     |
| 3  | **Q&A / Explainer**  | Ad-hoc questions with cited evidence.                                |
| 4  | **Coach**            | Drills, practice, feedback (skill-building loops).                   |
| 5  | **Reviewer**         | Reviews submissions (code, essays, solutions) with rubric.           |
| 6  | **Note-Taker**       | Generates lesson recaps, study notes, flashcards.                    |
| 7  | **Engagement**       | Re-engages inactive learners via email/in-app nudges.                |
| 8  | **Accessibility**    | Translation, plain-language, dyslexia-friendly, TTS/STT bridge.      |

### 4.2 System / Internal Agents

| #  | Agent                       | Purpose                                                             |
| -- | --------------------------- | ------------------------------------------------------------------- |
| 9  | **Orchestrator / Router**   | Routes user intent → correct agent(s); manages multi-agent flows.   |
| 10 | **Curriculum Designer**     | Builds & maintains personalized learning paths.                     |
| 11 | **Assessment Generator**    | Creates quizzes, exercises, projects from objectives.               |
| 12 | **Grader**                  | Auto-grades (objective) + LLM-judges (subjective) with rubric.      |
| 13 | **Progress Analyzer**       | Spots gaps, predicts at-risk learners, recommends interventions.    |
| 14 | **Content Curator**         | Sources from web / library, ranks quality, attaches to concepts.    |
| 15 | **Research Agent**          | Deep research (web search + RAG + KG); writes citations.            |
| 16 | **KG Builder**              | Extracts entities/relations from content into Neo4j.                |
| 17 | **Memory Steward (Dreamer)**| Periodic dreaming, consolidation, decay, conflict resolution.       |
| 18 | **Safety / Moderation**     | Content safety, age-appropriateness, PII redaction, jailbreak defense. |
| 19 | **Eval Agent**              | Runs eval suites against new prompts/agents/builds.                 |
| 20 | **Analytics / Insights**    | Aggregate learner/system analytics for educators & admins.          |

### 4.3 Agent Contract (every agent must define)

* **Inputs**: typed Pydantic schema (`<Agent>Input`).
* **Outputs**: typed Pydantic schema (`<Agent>Output`).
* **Tools**: explicit list (MCP-backed where possible).
* **System prompt**: versioned file under `prompts/<agent>/v<n>.md`.
* **Memory access policy**: which memory types it may read/write.
* **Guardrails**: safety pre/post filters.
* **Evals**: `evals/<agent>/*.yaml` (promptfoo) + `tests/agents/test_<agent>.py`.
* **Telemetry**: trace name, latency budget, cost budget.

---

## 5. Memory System (Most Important Subsystem)

A learner's memory is what makes A Step Forward valuable. We use a **multi-store, multi-type, healing memory** modeled after cognitive science.

### 5.1 Memory Types

| Type              | Description                                       | Storage                              |
| ----------------- | ------------------------------------------------- | ------------------------------------ |
| **Working**       | Current conversation context (tokens in-window)   | Ephemeral (in-process)               |
| **Episodic**      | Specific events (sessions, lessons, quizzes)      | Postgres `episodic_memories` + embeddings |
| **Semantic**      | Facts about learner & world (preferences, mastery)| Postgres `semantic_memories` + KG     |
| **Procedural**    | How the learner learns (pace, modality, habits)   | Postgres `procedural_memories`        |
| **Affective**     | Emotional signals, motivation, frustration trends | Postgres `affective_memories`         |
| **Spatial/Ctx**   | Device, time-of-day, environment patterns         | Postgres `context_memories`           |
| **Reflective**    | Agent-generated insights, hypotheses              | Postgres `reflective_memories`        |
| **Source/Refs**   | External docs/links/files referenced              | Object store + Postgres + pgvector    |

Each memory row carries: `id`, `learner_id`, `type`, `content`, `embedding`, `salience`, `confidence`, `valence`, `decay_rate`, `last_accessed_at`, `access_count`, `provenance`, `superseded_by`, `tags`, `kg_node_ids`, `created_at`, `expires_at`.

### 5.2 Lifecycle & Hygiene (Degradation Prevention)

```
   ┌───────────┐    ingest     ┌────────────┐   importance   ┌─────────────┐
   │ Raw event ├──────────────►│ Episodic   ├───────────────►│ Reinforce / │
   └───────────┘               │ memory     │                │ decay       │
                               └──────┬─────┘                └──────┬──────┘
                                      │ dream / consolidate         │
                                      ▼                             │
                               ┌────────────┐                       │
                               │ Semantic / │◄──────────────────────┘
                               │ Procedural │
                               └──────┬─────┘
                                      │ project into
                                      ▼
                               ┌────────────┐
                               │ Knowledge  │
                               │ Graph (KG) │
                               └────────────┘
```

#### Mechanisms

1. **Dreaming** (`MemorySteward` agent; nightly + on-demand)
   * Replays the day's episodic memories.
   * Extracts patterns (re-occurring themes, new mastery, mistakes).
   * Promotes high-salience items to semantic/procedural memory.
   * Generates *reflective* memories ("learner struggles with fractions when tired").
   * Writes new/updated nodes & edges to the KG.

2. **Compression / Summarization**
   * Conversations > N tokens collapsed to structured summaries (`facts`, `decisions`, `open_questions`).
   * Hierarchical: verbatim (24h) → daily digest (30d) → weekly insight (1y) → lifetime profile.

3. **Consolidation**
   * Merge near-duplicate semantic memories (cosine ≥ τ) with conflict resolution.
   * Link related memories via KG edges.
   * Strengthen `salience` for memories accessed often.

4. **Selective Forgetting (Decay)**
   * Each memory has a `decay_rate` (Ebbinghaus-inspired).
   * Effective strength = `salience × exp(-(now - last_accessed)/τ)` with reinforcement on access.
   * Below threshold → archived (cold storage), not deleted (auditable).
   * Hard delete only on user request (GDPR).

5. **Conflict Resolution**
   * On contradiction between new and existing memory:
     * If new is higher confidence/recency, mark old as `superseded_by=new`.
     * If unclear, both kept, flagged for `MemorySteward` review or learner clarification.
   * Versioned, never silently overwritten.

6. **Retrieval-Time Filtering**
   * Hybrid retrieval: BM25 + dense + KG-walk.
   * Rerank by `relevance × recency_decay × confidence × user_trust × salience`.
   * Apply policy: agent X can read types {…}; child mode blocks affective; etc.
   * De-dup near-identicals before injection.

7. **Context-Window Compaction**
   * Hook on the orchestrator: when context approaches 80% of model limit, compact older turns into a structured summary block, keep the last K turns verbatim plus pinned memories.

8. **Importance Scoring**
   * Hybrid heuristic + LLM-judge: signals = emotion, novelty, repetition, explicit user importance, teacher tagging.
   * Drives consolidation, decay rate, and rerank weight.

9. **Spaced Repetition (learner content, not system memory)**
   * **FSRS** algorithm for flashcards, quizzed facts, skills.
   * `Coach` and `Assessment` agents schedule reviews; mastery updates flow back into the KG.

10. **Verification Cycle**
    * Periodically (or when stakes are high) re-validate semantic memories with the learner (gentle "is this still true?").

11. **Provenance & Auditability**
    * Every memory stores source (chat id, lesson id, document id, agent that wrote it, model+version).
    * Learner can view, correct, or delete any memory via a "Memory Inspector" UI.

12. **Privacy / PII**
    * Pre-write redaction (Presidio + custom rules).
    * Encryption at rest; per-learner key wrapping.
    * No memory of sensitive categories without explicit consent.

### 5.3 Memory APIs (sketch)

```
POST   /memory                     create
GET    /memory?type=&query=&k=     hybrid search
PATCH  /memory/{id}                update / correct
DELETE /memory/{id}                soft delete
POST   /memory/dream               trigger dreaming for a learner
POST   /memory/consolidate         force consolidation pass
POST   /memory/decay               sweep decay
GET    /memory/timeline            episodic timeline view
```

Exposed both as **REST** (frontend) and as a **Memory MCP server** (agents).

---

## 6. GraphRAG

### 6.1 Ontology (initial)

Nodes:

* `Learner`, `Concept`, `Skill`, `Topic`, `Course`, `Lesson`, `Resource`, `Assessment`, `Question`, `Misconception`, `Goal`, `Event`, `Agent`.

Edges (examples):

* `Concept -[PREREQUISITE_OF]-> Concept`
* `Lesson -[TEACHES]-> Concept`
* `Resource -[COVERS]-> Concept`
* `Learner -[MASTERS {score, last_assessed_at}]-> Concept`
* `Learner -[STUDIED]-> Lesson`
* `Question -[TESTS]-> Concept`
* `Misconception -[OPPOSES]-> Concept`
* `Goal -[REQUIRES]-> Skill`

### 6.2 Pipeline

1. **Ingest** raw content (PDF, HTML, video transcripts).
2. **Chunk + embed** → pgvector.
3. **Extract** entities/relations via LLM (Claude w/ structured outputs).
4. **Resolve** entities (link to existing nodes; create if new).
5. **Write** to Neo4j with provenance.
6. **Verify** with sample queries; flag low-confidence extractions.

### 6.3 Retrieval Modes

* **Local** — vector search → top-k chunks.
* **Global** — community-detection summaries (Microsoft GraphRAG-style).
* **Hybrid** — vector seed + KG walk (1–3 hops) + rerank.
* **Personalized** — bias toward subgraphs touching `Learner` node.

### 6.4 Exposed as

`GraphRAG MCP` server with tools: `kg.search`, `kg.walk`, `kg.related_concepts`, `kg.prereqs`, `kg.next_topics`, `kg.explain_path`.

---

## 7. MCP Servers

### 7.1 Cursor-side MCPs (development) — in `.cursor/mcp.json`

| MCP                   | Why                                                             |
| --------------------- | --------------------------------------------------------------- |
| **filesystem**        | Project file access.                                            |
| **github**            | Issues, PRs, CI.                                                |
| **context7**          | Up-to-date library docs while coding.                           |
| **shadcn**            | Add UI components directly.                                     |
| **playwright**        | Agent-driven E2E test creation.                                 |
| **postgres**          | Inspect local DB during dev.                                    |
| **sequential-thinking** | Helps Composer plan multi-step changes.                       |
| **fetch**             | Light HTTP fetch.                                               |
| **memory** (project)  | Same memory MCP the app uses, for dev/QA introspection.         |

### 7.2 Runtime MCPs (used by agents at inference)

| MCP                   | Provided by                  |
| --------------------- | ---------------------------- |
| **memory**            | Custom (this repo)           |
| **graphrag**          | Custom (this repo)           |
| **curriculum**        | Custom (this repo)           |
| **progress**          | Custom (this repo)           |
| **web search**        | Tavily or Brave MCP          |
| **wikipedia**         | Community MCP                |
| **arxiv**             | Community MCP                |
| **youtube transcripts** | Community MCP              |
| **wolfram**           | Wolfram MCP                  |
| **file/uploads**      | Custom (this repo)           |

### 7.3 Building MCPs

Standardize on the **Python MCP SDK** for in-repo servers (shares Pydantic models with the API). Each MCP lives in `mcp-servers/<name>/` with:
`server.py`, `tools/`, `pyproject.toml`, `README.md`, `tests/`.

---

## 8. Cursor Configuration

### 8.1 Rules — `.cursor/rules/`

* `00-architecture.mdc` — pointers to PLAN.md and ARCHITECTURE.md.
* `10-typescript-style.mdc` — strict TS, no `any`, Zod everywhere.
* `20-python-style.mdc` — ruff/black/mypy, async-first.
* `30-agent-authoring.mdc` — agent contract, prompt versioning, evals required.
* `40-memory-rules.mdc` — every write goes through Memory service; never direct DB.
* `50-security.mdc` — never log PII; never commit secrets; encryption rules.
* `60-testing.mdc` — coverage targets, evals on every prompt change.
* `70-commit-style.mdc` — conventional commits.
* `80-pr-style.mdc` — PR template, eval-on-PR.

### 8.2 Hooks — `.cursor/hooks.json`

* `beforeShellExecution`: block dangerous commands (`rm -rf /`, `git push --force` to main, raw `kubectl delete`, etc.).
* `afterFileEdit`: format (`ruff format` / `prettier`) and lint changed files.
* `agentStart`: load `MEMORY_SNAPSHOT.md` and current sprint goals into context.
* `agentStop`: append session highlights to `docs/sessions/<date>.md`.
* `beforeReadFile`: redact secrets from `.env*` if accidentally read.
* `agentResponse`: log to local eval store (token usage, model, time).

### 8.3 Sub-agent briefs — `.cursor/subagent-briefs/`

One markdown brief per work stream (Frontend, Backend, Agents, Memory, GraphRAG, MCP, Infra, Evals, Curriculum). Each brief defines: goal, in-scope files, out-of-scope, contracts to honor, acceptance criteria, eval commands, and starting prompt to give Composer 2.5.

### 8.4 Skills — `skills/`

Project-level skills (read by sub-agents when they pick up tasks):

* `build-an-agent/SKILL.md`
* `build-an-mcp-server/SKILL.md`
* `add-a-frontend-page/SKILL.md`
* `add-a-backend-endpoint/SKILL.md`
* `memory-operations/SKILL.md`
* `dreaming-and-consolidation/SKILL.md`
* `graphrag-ingestion/SKILL.md`
* `run-evals/SKILL.md`
* `db-migrations/SKILL.md`
* `prompt-authoring/SKILL.md`
* `seed-curriculum/SKILL.md`
* `deploy/SKILL.md`

(Cursor-account-level skills like `canvas`, `babysit`, `create-rule`, `create-hook`, `create-skill`, `split-to-prs`, `loop`, `automate`, `review-bugbot`, `review-security`, `sdk`, `statusline`, `update-cursor-settings` are already available and should be used where they fit.)

---

## 9. Outsourced / Community Leverage

* **Awesome MCP servers** — pick verified ones (Tavily, GitHub, Postgres, Playwright, shadcn, context7, sequential-thinking).
* **LangChain Hub** — vetted prompts as starting points.
* **shadcn/ui registry** — drop-in components via MCP.
* **DeepEval / promptfoo** — eval frameworks; don't reinvent.
* **LightRAG** / **Microsoft GraphRAG** — reference implementations to learn from (we keep our own thin layer).
* **FSRS-rs / py-fsrs** — spaced repetition algorithm.
* **Presidio** — PII detection.
* **Langfuse** — OSS LLM observability.
* **Guardrails AI** — safety rails.
* **Anthropic prompt-caching cookbook** — to cut costs ≥70% on agent system prompts.

---

## 10. Security, Safety, Privacy

* **Auth**: Clerk (OAuth + email/passkey). Role: `learner`, `educator`, `admin`, `parent`.
* **Authorization**: RBAC at API; per-row policy for learner data.
* **Encryption**: TLS in transit; AES-GCM at rest for memory/notes; per-learner KEK.
* **PII**: Presidio + custom rules before any memory write; redaction in logs.
* **Child safety**: age-gating, content filters, no third-party trackers in child mode, COPPA-aware.
* **Jailbreak defense**: system prompt hardening, input/output classifiers, tool-use allowlists.
* **Audit log** for every memory write/read by agents.
* **GDPR**: data export + hard delete endpoints.

---

## 11. Observability & Evals

* **Tracing**: OpenTelemetry → Langfuse (LLM-aware spans).
* **Metrics**: Prometheus (latency, cost, tokens, retrieval recall, eval scores).
* **Logs**: structured JSON; correlation ids.
* **Evals (offline)**: `evals/` with promptfoo + DeepEval; required before merging any prompt/agent change.
* **Evals (online)**: shadow runs, A/B prompts, user thumbs.
* **Alerts**: cost spikes, eval regressions, error rates.

---

## 12. Repository Layout (monorepo)

```
.
├── PLAN.md                       # ← this file
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── README.md
├── AGENTS.md                     # sub-agent index
├── .env.example
├── .gitignore
├── .cursor/
│   ├── mcp.json
│   ├── hooks.json
│   ├── rules/
│   └── subagent-briefs/
├── skills/                       # project-level skills (sub-agent readable)
├── apps/
│   ├── web/                      # Next.js 15 frontend
│   └── api/                      # FastAPI gateway
├── services/
│   ├── memory/                   # memory service (Python)
│   ├── graphrag/                 # GraphRAG service (Python)
│   ├── orchestrator/             # LangGraph orchestrator
│   └── workers/                  # Celery workers (dreamer, decay, ingest, evals)
├── packages/
│   ├── agents/                   # Python agent definitions (LangGraph)
│   ├── schemas/                  # Pydantic + generated TS types
│   └── ui/                       # Shared React UI primitives
├── mcp-servers/
│   ├── memory/
│   ├── graphrag/
│   ├── curriculum/
│   └── progress/
├── prompts/                      # versioned prompts per agent
├── evals/                        # promptfoo + DeepEval suites
├── infra/
│   ├── docker-compose.yml
│   ├── alembic/
│   └── k8s/                      # later
├── scripts/                      # dev scripts (seed, snapshot, dream-now)
├── docs/
│   └── adr/                      # architecture decision records
└── tests/
```

---

## 13. Sub-Agent Work Streams (delegated to Composer 2.5 / Auto)

Each brief is a self-contained ticket for a Composer 2.5 sub-agent.

| Stream                | Brief file                                        | Primary outputs                                    |
| --------------------- | ------------------------------------------------- | -------------------------------------------------- |
| Frontend              | `.cursor/subagent-briefs/01-frontend.md`          | Next.js app, design system, learner workspace.     |
| Backend / API         | `.cursor/subagent-briefs/02-backend-api.md`       | FastAPI gateway, auth, routes, schemas.            |
| Agents framework      | `.cursor/subagent-briefs/03-agents.md`            | LangGraph orchestrator + all agent stubs.          |
| Memory service        | `.cursor/subagent-briefs/04-memory.md`            | Memory tables, services, dreaming, decay.          |
| GraphRAG              | `.cursor/subagent-briefs/05-graphrag.md`          | Neo4j schema, ingestion pipeline, retrieval API.   |
| MCP servers           | `.cursor/subagent-briefs/06-mcp-servers.md`       | Custom MCPs wired to services.                     |
| Curriculum / Content  | `.cursor/subagent-briefs/07-curriculum.md`        | Seed data, content model, lesson templates.        |
| Evals & QA            | `.cursor/subagent-briefs/08-evals-qa.md`          | promptfoo + DeepEval + Playwright suites.          |
| Infra / DevOps        | `.cursor/subagent-briefs/09-infra.md`             | docker-compose, CI/CD, deploy pipelines.           |
| Security / Safety     | `.cursor/subagent-briefs/10-security-safety.md`   | Guardrails, PII, RBAC, audit log.                  |

All sub-agents **must** read `PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`, and the relevant project skill before touching code.

---

## 14. Phased Roadmap

### Phase 0 — Foundation (owned by Opus, this session)

* Plan + repo skeleton + cursor config + skills + sub-agent briefs + service stubs + docker compose + schemas + memory tables + agent base classes + MCP scaffolds.

### Phase 1 — Walking Skeleton (sub-agents)

* End-to-end: learner logs in → sees a lesson → talks to Tutor → memory is written → progress visible. Single course, single agent, no dreaming yet.

### Phase 2 — Memory & GraphRAG online

* Multi-type memory, dreaming, decay, KG ingestion, GraphRAG retrieval, Memory Inspector UI.

### Phase 3 — Multi-agent orchestration

* Orchestrator routes intent across Tutor/Mentor/Coach/Reviewer. Assessment generator + grader. FSRS reviews.

### Phase 4 — Polish, evals, safety

* Full eval gates, safety hardening, observability, accessibility audit.

### Phase 5 — Scale

* Curriculum library, educator dashboards, multi-tenant, mobile.

---

## 15. Success Criteria for the Foundation (Phase 0 exit)

* `PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md` exist and are coherent.
* `.cursor/` configured with rules, hooks, mcp, sub-agent briefs.
* Repo skeleton in place for `apps/`, `services/`, `packages/`, `mcp-servers/`, `infra/`, `prompts/`, `evals/`, `skills/`.
* Memory service has data model, base APIs, and stubs for dreaming/decay/consolidation/conflict-resolution/compaction.
* GraphRAG service has ontology and ingestion pipeline scaffold.
* LangGraph orchestrator + base `Agent` class + at least Tutor agent stub.
* Custom MCP server stubs for memory, graphrag, curriculum, progress.
* Docker compose brings up Postgres+pgvector, Redis, Neo4j locally.
* Every sub-agent has a brief file and knows which skills to read first.

When all of the above is true, sub-agents can be dispatched and start producing real features.
