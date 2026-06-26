# Agents (Sub-agent Index)

This file is the index for **both**:

1. **Cursor sub-agents** that build the system (Composer 2.5 / Cursor Auto). See `.cursor/subagent-briefs/`.
2. **Runtime AI agents** that run inside the product. See `packages/agents/` and `prompts/`.

Always read `PLAN.md` first.

---

## 1. Runtime Agent Roster

Each runtime agent must implement the contract in `packages/agents/agents/base/agent.py` and pass the eval suite in `evals/agents/<agent>/`.

### Learner-facing

| Agent              | Folder                                    | Prompt                      | Primary model        | Notes                                |
| ------------------ | ----------------------------------------- | --------------------------- | -------------------- | ------------------------------------ |
| Tutor              | `packages/agents/agents/learner_facing/tutor/` | `prompts/tutor/`            | Claude Sonnet (Opus on deep) | Socratic, adaptive difficulty.  |
| Mentor             | `packages/agents/agents/learner_facing/mentor/` | `prompts/mentor/`           | Claude Sonnet        | Goals, motivation, habits.            |
| Coach              | `packages/agents/agents/learner_facing/coach/`  | `prompts/coach/`            | Claude Sonnet        | Drills, practice, FSRS reviews.       |
| Q&A / Explainer    | `packages/agents/agents/learner_facing/qa_explainer/` | `prompts/qa_explainer/` | Claude Sonnet        | Cited answers.                        |
| Reviewer           | `packages/agents/agents/learner_facing/reviewer/` | `prompts/reviewer/`       | Claude Sonnet/Opus   | Code/essay/solution review.           |
| Note-Taker         | `packages/agents/agents/learner_facing/note_taker/` | `prompts/note_taker/`   | Claude Haiku/Sonnet  | Cheap, frequent.                      |
| Engagement         | `packages/agents/agents/learner_facing/engagement/` | `prompts/engagement/`   | GPT-mini / Haiku     | Bulk nudges.                          |
| Accessibility      | `packages/agents/agents/learner_facing/accessibility/` | `prompts/accessibility/` | Gemini / Claude   | Multimodal, multi-language.           |

### System / internal

| Agent                 | Folder                                            | Prompt                          | Notes                                  |
| --------------------- | ------------------------------------------------- | ------------------------------- | -------------------------------------- |
| Orchestrator / Router | `packages/agents/agents/system/orchestrator/`     | `prompts/orchestrator/`         | LangGraph router.                      |
| Curriculum Designer   | `packages/agents/agents/system/curriculum_designer/` | `prompts/curriculum_designer/` | Builds learner paths.                  |
| Assessment Generator  | `packages/agents/agents/system/assessment_generator/` | `prompts/assessment_generator/` | Creates quizzes/exercises/projects.    |
| Grader                | `packages/agents/agents/system/grader/`           | `prompts/grader/`               | Rubric + LLM judge.                    |
| Progress Analyzer     | `packages/agents/agents/system/progress_analyzer/` | `prompts/progress_analyzer/`   | Gap analysis, interventions.           |
| Content Curator       | `packages/agents/agents/system/content_curator/`  | `prompts/content_curator/`      | Sources & ranks content.               |
| Research Agent        | `packages/agents/agents/system/research/`         | `prompts/research/`             | Deep research; web + RAG + KG.         |
| KG Builder            | `packages/agents/agents/system/kg_builder/`       | `prompts/kg_builder/`           | Entity/relation extraction.            |
| Memory Steward (Dreamer) | `packages/agents/agents/system/memory_steward/` | `prompts/memory_steward/`     | Dreaming, consolidation, decay, conflict resolution. |
| Safety / Moderation   | `packages/agents/agents/system/safety_moderation/` | `prompts/safety_moderation/`   | Pre/post filters, jailbreak defense.   |
| Eval Agent            | `packages/agents/agents/system/eval_agent/`       | `prompts/eval_agent/`           | Runs eval suites, regression flags.    |
| Analytics / Insights  | `packages/agents/agents/system/analytics_insights/` | `prompts/analytics_insights/` | Aggregates for educators/admins.       |

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
| `skills/coordinator-dispatch/SKILL.md` | Whenever you are operating as the Coordinator. |
| `skills/assign-to-coordinator/SKILL.md` | Whenever you are operating as the Manager and need to hand off a new round of work. |
