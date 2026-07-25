# Architecture — As-Built Snapshot

> **Maintained by:** Architecture Steward reviews (`.cursor/skills/architecture-review/`).
> **Last updated:** 2026-07-25
>
> This document describes **what runs today**, which may differ from the target
> topology in `PLAN.md` / `ARCHITECTURE.md`. Update after major deploys or ADRs.

---

## 1. Production topology (simplified)

| Layer | Component | Role | Deploy |
|-------|-----------|------|--------|
| UI | `apps/web` (Next.js 15) | Learner app, RSC, API routes | Vercel |
| Auth | Clerk | Identity; `userId` = `learner_id` | SaaS |
| Primary DB | Neon Postgres | Profiles, mastery, plans, chat, notes | Neon |
| LLM | Groq (via `apps/web/src/lib/llm-provider.ts`) | Chat, quiz gen, consolidation | SaaS |
| Optional API | `apps/api` (FastAPI) on Render | Legacy/accelerator routes | Render |
| KG (runtime) | 156 concepts (`kg-data.json`), 93 cross-subject edges (`kg-cross-edges.json`), 306 authored lessons | Bundled on Vercel; planner reads JSON not Postgres `kg_edges`; no Neo4j on hot path | Repo |
| Workers | Cron routes + GitHub Actions | Memory consolidate (both fire Sun 03:00 UTC) | Vercel + GHA |

**Critical path principle:** onboarding, diagnostic, plans, chat memory, `/learn`, progress, and most dashboards read/write **Neon directly** from Vercel (`apps/web/src/lib/neon-db.ts`). Render absence must not break signup → study flows (`.cursor/skills/neon-direct-route/SKILL.md`).

---

## 2. Request paths (verified patterns)

### Chat turn

```
Browser → POST /api/chat (Vercel)
  → buildContextNeeds (relevance gates) + resolveResponseLanguage
  → assembleChatSystemPrompt (whole-section budget via fitSystemSections)
  → Groq quality-first chain (CHAT_MODEL_POLICY escape hatch; maxDuration 60s)
  → buffer draft → scoreResponseQuality → optional one repair → chunk stream
  → Neon: chat_turns, learner_agent_notes, persona reads (no post-display repair append)
  → No MCP tool calls on the Vercel path
```

No Render dependency on the happy path (`apps/web/src/app/api/chat/route.ts`). Agent contracts: hybrid knowledge + answer-first roles (ADR-0015); prompts in `agent-baseline.ts` / `agent-prompts.ts` / `agent-skills.ts`.

### Learner UI pages (Neon-direct SSR)

| Page | Neon entrypoint |
|------|-----------------|
| `/app` | `getCurrentPlan`, `getLearnerProfile`, `getLearnerStreak` |
| `/app/progress` | `getProgressFromNeon` |
| `/app/memory` | `getLearnerMemorySnapshot` |
| `/settings/persona` | `getLearnerPersona`, `countAgentNotes` |

Root `apps/web/src/app/layout.tsx` sets `dynamic = 'force-dynamic'` (most RSC pages inherit).

### Legacy JSON APIs (Neon-direct)

| Route | Source | Misconfig / DB error |
|-------|--------|----------------------|
| `GET /api/dashboard` | `getDashboardSnapshot` → `mapDashboardSnapshotToLearnerDashboard` | 503 |
| `GET /api/memory` | `getMemoryTimelineFromNeon` | 503 |

Primary UI uses server-side Neon helpers on RSC pages. `src/hooks/use-learner-data.ts` targets these JSON routes but has **no importers**.

### Lesson / quiz answer

```
Browser → POST /api/lesson/answer | diagnostic answer routes
  → neon-db: recordLessonAnswer / recordDiagnosticAnswer
  → concept_mastery UPSERT + skill_practice + quiz_responses insert
```

`quiz_responses` has **no `learner_id`**; learner activity from quizzes is inferred via `concept_mastery.last_activity` and paired writes.

### Weekly plan

Two code paths coexist ( **known tension** ):

| Path | Location | Used by |
|------|----------|---------|
| Mastery-aware planner | `apps/web/src/lib/learning-plan.ts` (`buildLearningPlan`) | Agents, `/api/learning-plan/next`, some UI |
| Template weekly generator | `neon-db.ts` (`generateLearningPlan`, `getCurrentPlan`) | Dashboard, onboarding apply, plan weeks in DB |

Unification is an open architectural goal (`obsidian-vault/_active-context.md`).

---

## 3. Modular monolith boundaries (repo)

```
apps/web          — UI + Neon-direct API (TypeScript)
apps/api          — FastAPI gateway (optional in prod)
services/*        — Python domain services (memory, graphrag, orchestrator, workers)
packages/agents   — Runtime agent implementations
packages/schemas  — Shared contracts
mcp-servers/*     — MCP tool servers for agents
prompts/*         — Versioned agent prompts
evals/*           — promptfoo / DeepEval
```

**Not a microservices mesh in production yet.** Most learner traffic is a **Vercel modular monolith** plus Neon.

---

## 4. Data ownership (learner-bound)

| Table / store | Owner writes | Notes |
|---------------|--------------|-------|
| `learner_profiles` | Onboarding, settings | Questionnaire + goals |
| `concept_mastery` | Diagnostic, lesson answer, lesson complete | Score 0–1; UPSERT |
| `learning_plans` / `plan_weeks` | Plan generate/apply | Active plan per learner |
| `chat_turns` | Chat route | Per-agent history |
| `learner_agent_notes` | Agents, consolidate | Per-(learner, agent) |
| `learner_profiles.learner_persona` | Consolidate, agents | Shared persona |
| `skill_practice` | Lesson answers | Atom granularity |

All reads filter by Clerk `userId`; never trust client `learner_id` on reads.

---

## 5. Known coupling & race risks

| Risk | Severity | Notes |
|------|----------|-------|
| Dual planners | P1 | Agents/chat use `buildLearningPlan`; DB weeks from `generateLearningPlan` |
| Plan regen DELETE+INSERT | mitigated | Wrapped in `sql.transaction()` + `pg_try_advisory_xact_lock` (`neon-db.ts`) |
| Consolidation overlap | P1 | Manual `/api/agent-memory/consolidate` + cron; no per-learner lock |
| Legacy `/api/dashboard`, `/api/memory` → Render | P2 | Pages use Neon; JSON APIs still proxy via `data.ts` |
| Duplicate cron triggers | P2 | `vercel.json` crons + `.github/workflows/cron-consolidate-memory.yml` same schedule |
| Plan apply vs chat template redirect | P2 | Product rules in `plan-apply.ts`; scope in `concept-scope.ts` |
| `quiz_responses` without learner_id | P2 | Complicates analytics; paired mastery write mitigates |
| Large `neon-db.ts` (~3.1k lines) | P2 | God-module tendency; split by domain when touching |
| `content-api.ts` Render cache 300s | P3 | `/learn` fallback only; Neon path preferred |
| ADR-001 vs Neon-direct reality | P2 | ADR says Render-primary API; critical path is Neon-direct |

---

## 6. Scalability snapshot (free tier)

- **Vercel:** serverless concurrency, function duration limits; SSE chat long-lived.
- **Neon:** HTTP driver, connection cache; watch concurrent chat + cron.
- **Groq:** rate limits; primary cost/latency lever.
- **Render:** cold start; mitigated by keep-warm workflow; non-critical for core loop.

Horizontal scale first wins: stateless Vercel routes, externalized state in Neon, no in-memory session.

---

## 7. ADR index (accepted decisions)

See `docs/adr/README.md` — hosting, memory layers, auth, Groq, embeddings, security model.

**As-built note:** ADR-001 (Vercel + Render) remains accepted, but production learner loop behavior follows Neon-direct (`.cursor/skills/neon-direct-route/SKILL.md`). Proposed ADR-0006/0007 in `docs/architecture/assessments/2026-07-05-platform-overview.md` would record that drift.

New cross-cutting decisions → propose ADR; Opus accepts.

---

## 8. Review cadence

- **Trigger:** pre-milestone, post-incident, or quarterly.
- **Output:** `docs/architecture/assessments/YYYY-MM-DD-*.md`
- **Latest:** `docs/architecture/assessments/2026-07-05-platform-overview.md`
- **Sub-agent brief:** `.cursor/subagent-briefs/24-architecture-steward.md`
