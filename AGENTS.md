# Agents (Sub-agent Index)

This file is the index for **both**:

1. **Cursor sub-agents** that build the system (Composer 2.5 / Cursor Auto). See `.cursor/subagent-briefs/`.
2. **Runtime AI agents** that run inside the product. See `packages/agents/` and `prompts/`.

Always read `PLAN.md` first.

---

## 1. Runtime Agent Roster

Each runtime agent must implement the contract in `packages/agents/agents/base/agent.py` and pass the eval suite in `evals/agents/<agent>/`.

### Shared baseline (every agent gets this)

Every runtime agent's system prompt is composed by `apps/web/src/app/api/chat/route.ts` as:

```
buildAgentBaseline()           # apps/web/src/lib/agent-baseline.ts
+ getAgentPersona(agent)       # apps/web/src/lib/agent-prompts.ts
+ [brand-new-learner cue if no profile]
+ [profile]
+ [shared learner persona]                     ← CLAUDE.md-style, every agent
+ [private notes for THIS (learner, agent)]    ← per-agent scratchpad
+ [mastery | relevant curriculum | lesson agent_hints | learning-plan snapshot]
```

The **baseline** tells every agent: the corpus stats (117 KG concepts, 93 cross-subject edges, ~74 authored lessons, ~500 skill atoms), the full agent network roster, and the universal rules (bilingual HE-default, math always LTR in `$...$` / `$$...$$`, no external links, brand-new-learner protocol). This means **a brand-new learner with zero history gets a fully-grounded agent on turn one** — the entire knowledge base is the baseline.

### Per-learner memory layers (storage: Neon, keyed by Clerk `userId`)

| Layer                        | Scope                  | Storage                                  | Writer                                | Reader                                | Skill                                  |
| ---------------------------- | ---------------------- | ---------------------------------------- | ------------------------------------- | ------------------------------------- | -------------------------------------- |
| Shared learner persona       | per-learner            | `learner_profiles.learner_persona`        | Any agent (sparingly) + Memory Steward| Every agent on every turn             | `skills/learner-persona/SKILL.md`      |
| Per-agent private notes      | per-(learner, agent)   | `learner_agent_notes`                    | The owning agent                       | The owning agent (top-K, importance)   | `skills/agent-skill-notes/SKILL.md`    |
| Chat turns (verbatim)        | per-(learner, agent)   | `chat_turns`                              | Chat route                             | Owning agent (last N)                  | `skills/chat-memory-context/SKILL.md`  |
| Concept mastery              | per-(learner, concept) | `concept_mastery`                         | Grader + answer routes                 | Every agent via context                | `skills/use-learning-plan/SKILL.md`    |
| Skill-atom mastery           | per-(learner, atom)    | `skill_practice`                          | Lesson/answer route                    | Learning planner                       | `skills/cross-subject-kg/SKILL.md`     |
| Activity streak / weekly plan | per-learner            | `learning_plans` + `plan_weeks` + derived | Plan generator                         | `/dashboard`                           | `skills/use-learning-plan/SKILL.md`    |

The Clerk `userId` is the single key. There is no separate "storage bucket" for memories — every learner-bound row lives in the same Postgres database as the user identity, RLS-friendly. Lightweight dreaming/consolidation runs against `learner_agent_notes` at `POST /api/agent-memory/dream`; heavy nightly consolidation belongs to the Memory Steward.

### Learner-facing

| Agent              | Folder                                    | Runtime persona                    | Sub-agent prompt           | Tools (web runtime)                                                            | Notes                                |
| ------------------ | ----------------------------------------- | ---------------------------------- | -------------------------- | ------------------------------------------------------------------------------ | ------------------------------------ |
| Tutor              | `packages/agents/agents/learner_facing/tutor/` | `agent-prompts.ts:TUTOR`           | `prompts/tutor/v1.md`      | `memory.*`, `kg.related_concepts`, `curriculum.get_lesson`, `learning_plan.next` | Socratic, adaptive difficulty. Receives lesson `agent_hints` + learning-plan snapshot when concept matches. |
| Mentor             | `packages/agents/agents/learner_facing/mentor/` | `agent-prompts.ts:MENTOR`          | `prompts/mentor/v1.md`     | `memory.*`, `progress.get_summary`, `curriculum.get_path` (read-only)          | Goals, motivation, habits. Hands off to Curriculum Designer for path. |
| Coach              | `packages/agents/agents/learner_facing/coach/`  | `agent-prompts.ts:COACH`           | `prompts/coach/v1.md`      | `memory.*`, `progress.get_due_reviews`, `kg.related_concepts`, `learning_plan.next` | Drills at atom granularity using planner's `weak_atoms`. |
| Q&A / Explainer    | `packages/agents/agents/learner_facing/qa_explainer/` | `agent-prompts.ts:QA_EXPLAINER` | `prompts/qa_explainer/v1.md` | `memory.search`, `kg.*`, `curriculum.get_lesson`, `learning_plan.next`        | Cited answers from authored corpus only. No external links. |
| Reviewer           | `packages/agents/agents/learner_facing/reviewer/` | `agent-prompts.ts:REVIEWER`        | `prompts/reviewer/v1.md`   | `memory.*`, `curriculum.get_lesson`, `kg.related_concepts`                     | Rubric-first feedback on submissions. |
| Note-Taker         | `packages/agents/agents/learner_facing/note_taker/` | `agent-prompts.ts:NOTE_TAKER`     | `prompts/note_taker/v1.md` | `memory.*`, `kg.related_concepts`                                              | Cheap, frequent. Ties notes to `concept:<id>`. |
| Engagement         | `packages/agents/agents/learner_facing/engagement/` | (not on web yet)                  | `prompts/engagement/`      | TBD                                                                            | Bulk nudges. |
| Accessibility      | `packages/agents/agents/learner_facing/accessibility/` | (not on web yet)               | `prompts/accessibility/`   | TBD                                                                            | Multimodal, multi-language. |

### System / internal

| Agent                 | Folder                                            | Sub-agent prompt                  | Key tools                                                                                   | Notes                                  |
| --------------------- | ------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------- |
| Orchestrator / Router | `packages/agents/agents/system/orchestrator/`     | `prompts/orchestrator/v1.md`      | All — it routes                                                                             | LangGraph router. |
| Curriculum Designer   | `packages/agents/agents/system/curriculum_designer/` | `prompts/curriculum_designer/v1.md` | `memory.*`, `curriculum.get_path` / `update_path`, `kg.related_concepts`, **`learning_plan.next` (authoritative path planner)** | `milestones[]` MUST be drawn from `path[]`. See `skills/use-learning-plan/SKILL.md`. |
| Assessment Generator  | `packages/agents/agents/system/assessment_generator/` | `prompts/assessment_generator/v1.md` | Generates all 10 question kinds; reuses skill atoms from `skill_atoms`                  | Creates quizzes/exercises/projects.    |
| Grader                | `packages/agents/agents/system/grader/`           | `prompts/grader/v1.md`            | Rubric + LLM judge; calls `LearnerModelService.get_prerequisites` for root cause            | Authoritative grading; updates `concept_mastery` + `skill_practice`. |
| Progress Analyzer     | `packages/agents/agents/system/progress_analyzer/` | `prompts/progress_analyzer/v1.md`| `memory.*`, `progress.get_mastery`, `kg.related_concepts`, **`learning_plan.next` (root-cause tool)** | `gaps[]` drawn from `blocking_atoms[]`. |
| Content Curator       | `packages/agents/agents/system/content_curator/`  | `prompts/content_curator/v1.md`   | `curriculum.*`, `kg.*`                                                                      | Sources & ranks content (we own the corpus; this checks coverage). |
| Research Agent        | `packages/agents/agents/system/research/`         | `prompts/research/v1.md`          | `kg.retrieve_chunks`, `web.search`                                                          | Deep research; web + RAG + KG.         |
| KG Builder            | `packages/agents/agents/system/kg_builder/`       | `prompts/kg_builder/v1.md`        | LLM extraction → `kg_edges`, `skill_atoms`                                                  | Entity/relation extraction.            |
| Memory Steward (Dreamer) | `packages/agents/agents/system/memory_steward/` | `prompts/memory_steward/v1.md`  | `memory.*` (admin)                                                                          | Dreaming, consolidation, decay, conflict resolution. |
| Safety / Moderation   | `packages/agents/agents/system/safety_moderation/` | `prompts/safety_moderation/v1.md`| Moderation API                                                                              | Pre/post filters, jailbreak defense.   |
| Eval Agent            | `packages/agents/agents/system/eval_agent/`       | `prompts/eval_agent/v1.md`        | `evals/*`                                                                                   | Runs eval suites, regression flags.    |
| Analytics / Insights  | `packages/agents/agents/system/analytics_insights/` | `prompts/analytics_insights/v1.md` | DB read-only                                                                              | Aggregates for educators/admins.       |

---

## 2. Cursor Sub-agent Briefs

| Stream                | Brief                                          | First-run command (in this repo)                  |
| --------------------- | ---------------------------------------------- | ------------------------------------------------- |
| Frontend              | `.cursor/subagent-briefs/01-frontend.md`       | "Read PLAN.md + 01-frontend.md + skills/add-a-frontend-page, then start." |
| Backend API           | `.cursor/subagent-briefs/02-backend-api.md`    | "Read PLAN.md + 02-backend-api.md + skills/add-a-backend-endpoint." |
| Agents framework      | `.cursor/subagent-briefs/03-agents.md`         | "Read PLAN.md + 03-agents.md + skills/build-an-agent + prompts/."  |
| Memory service        | `.cursor/subagent-briefs/04-memory.md`         | "Read PLAN.md + 04-memory.md + skills/memory-operations + skills/dreaming-and-consolidation." |
| GraphRAG              | `.cursor/subagent-briefs/05-graphrag.md`       | "Read PLAN.md + 05-graphrag.md + skills/graphrag-ingestion."       |
| MCP servers           | `.cursor/subagent-briefs/06-mcp-servers.md`    | "Read PLAN.md + 06-mcp-servers.md + skills/build-an-mcp-server."   |
| Curriculum / Content  | `.cursor/subagent-briefs/07-curriculum.md`     | "Read PLAN.md + 07-curriculum.md + skills/seed-curriculum."        |
| Evals / QA            | `.cursor/subagent-briefs/08-evals-qa.md`       | "Read PLAN.md + 08-evals-qa.md + skills/run-evals."                |
| Infra / DevOps        | `.cursor/subagent-briefs/09-infra.md`          | "Read PLAN.md + 09-infra.md + skills/deploy + skills/db-migrations."|
| Security / Safety     | `.cursor/subagent-briefs/10-security-safety.md`| "Read PLAN.md + 10-security-safety.md."           |

**Model**: every Cursor sub-agent runs **Composer 2.5** or **Cursor Auto**, never Opus (Opus is reserved for planning/replanning).

**Run mode**: long, focused sub-agent sessions with `run_in_background: true` are preferred for multi-file work.

---

## 3. Cross-cutting skills (read before touching the relevant code)

| Skill | Read before |
| ----- | ----------- |
| `skills/neon-direct-route/SKILL.md` | Adding/modifying any `apps/web/src/app/api/**` route that touches Neon. The free-tier critical path (onboarding, diagnostic, plans, chat memory, /learn) is Vercel + Neon direct; Render is optional. |
| `skills/chat-memory-context/SKILL.md` | Touching `apps/web/src/app/api/chat/route.ts`, adding a new agent persona, or changing what gets persisted in `chat_turns`. |
| `skills/onboarding-flow/SKILL.md` | Adding an onboarding question, changing plan generation inputs, or adjusting the diagnostic length. |
| `skills/in-house-concept-content/SKILL.md` | Adding bilingual concept explanations to `/learn`, fixing wrong Wikipedia matches, or adding new CC content sources (OpenStax, Wikibooks, etc.). |
| `skills/author-lesson/SKILL.md` | Authoring or modifying an AI-authored lesson under `scripts/seed_data/lessons/` (sections, all 10 question kinds, `agent_hints`, skill atoms). |
| `skills/author-question-bank/SKILL.md` | Adding MORE questions (volume + kind diversity) to an existing authored lesson, or generating drills live. Pair with `author-lesson`. |
| `skills/expand-lesson-theory/SKILL.md` | Adding MORE sections / worked examples / pitfalls / cross-subject `why_matters` to an authored lesson without breaking the schema. |
| `skills/use-learning-plan/SKILL.md` | Adding any "what should I study next?" / "why am I stuck?" feature, or wiring a new agent / UI to the mastery-aware path planner. |
| `skills/cross-subject-kg/SKILL.md` | Adding cross-subject edges to `kg-cross-edges.json`, within-subject prereqs in YAML, or new canonical skill atoms. |
| `skills/learner-persona/SKILL.md` | Reading or writing the shared CLAUDE.md-style learner persona (`learner_profiles.learner_persona`). |
| `skills/agent-skill-notes/SKILL.md` | Reading or writing per-(learner, agent) private notes (`learner_agent_notes`); also see the dreaming endpoint. |
| `skills/dreaming-and-consolidation/SKILL.md` | Any consolidation work — the lightweight web endpoint or the heavy Memory Steward nightly. |
| `skills/coordinator-dispatch/SKILL.md` | Whenever you are operating as the Coordinator. |
| `skills/assign-to-coordinator/SKILL.md` | Whenever you are operating as the Manager and need to hand off a new round of work. |
