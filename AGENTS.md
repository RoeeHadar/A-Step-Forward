# Agents (Sub-agent Index)

This file is the index for **both**:

1. **Cursor IDE sub-agents** that build the system — definitions in `.cursor/agents/` (auto-discovered); detailed tickets in `.cursor/subagent-briefs/`.
2. **Runtime AI agents** that run inside the product — `packages/agents/` and `prompts/`.

Always read `PLAN.md` first.

**Cursor layout:** see `.cursor/README.md` for what is auto-loaded vs documentation-only.

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

The **baseline** tells every agent: the corpus stats (156 KG concepts, 93 cross-subject edges, 306 authored lessons, ~649 seeded skill atoms), the full agent network roster, and the universal rules (bilingual HE-default, math always LTR in `$...$` / `$$...$$`, no external links, brand-new-learner protocol). This means **a brand-new learner with zero history gets a fully-grounded agent on turn one** — the entire knowledge base is the baseline.

### Per-learner memory layers (storage: Neon, keyed by Clerk `userId`)

| Layer                        | Scope                  | Storage                                  | Writer                                | Reader                                | Skill                                  |
| ---------------------------- | ---------------------- | ---------------------------------------- | ------------------------------------- | ------------------------------------- | -------------------------------------- |
| Shared learner persona       | per-learner            | `learner_profiles.learner_persona`        | Any agent (sparingly) + Memory Steward| Every agent on every turn             | `.cursor/skills/learner-persona/SKILL.md`      |
| Per-agent private notes      | per-(learner, agent)   | `learner_agent_notes`                    | The owning agent                       | The owning agent (top-K, importance)   | `.cursor/skills/agent-skill-notes/SKILL.md`    |
| Chat turns (verbatim)        | per-(learner, agent)   | `chat_turns`                              | Chat route                             | Owning agent (last N)                  | `.cursor/skills/chat-memory-context/SKILL.md`  |
| Concept mastery              | per-(learner, concept) | `concept_mastery`                         | Grader + answer routes                 | Every agent via context                | `.cursor/skills/use-learning-plan/SKILL.md`    |
| Skill-atom mastery           | per-(learner, atom)    | `skill_practice`                          | Lesson/answer route                    | Learning planner                       | `.cursor/skills/cross-subject-kg/SKILL.md`     |
| Activity streak / weekly plan | per-learner            | `learning_plans` + `plan_weeks` + derived | Plan generator                         | `/dashboard`                           | `.cursor/skills/use-learning-plan/SKILL.md`    |

The Clerk `userId` is the single key. There is no separate "storage bucket" for memories — every learner-bound row lives in the same Postgres database as the user identity, RLS-friendly. Lightweight dreaming/consolidation runs against `learner_agent_notes` at `POST /api/agent-memory/dream` (no LLM, on-demand). Heavy LLM-driven consolidation runs at `POST /api/agent-memory/consolidate` (authed, per-learner — also wired to the `Rebuild from notes` button on `/settings/persona`) and `POST /api/cron/consolidate-memory` (CRON_SECRET, weekly sweep — Vercel cron + GitHub Actions backstop). Learners can inspect / edit / redact their shared persona at `/settings/persona`.

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
| Curriculum Designer   | `packages/agents/agents/system/curriculum_designer/` | `prompts/curriculum_designer/v1.md` | `memory.*`, `curriculum.get_path` / `update_path`, `kg.related_concepts`, **`learning_plan.next` (authoritative path planner)** | `milestones[]` MUST be drawn from `path[]`. See `.cursor/skills/use-learning-plan/SKILL.md`. |
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

## 2. Cursor Sub-agents

Cursor discovers custom subagents from **`.cursor/agents/`**. Each agent points
at a detailed ticket in **`.cursor/subagent-briefs/`** (briefs are not
auto-discovered on their own).

| Stream | Agent (`.cursor/agents/`) | Brief |
| ------ | ------------------------- | ----- |
| Frontend | `frontend.md` | `01-frontend.md` |
| Backend API | `backend-api.md` | `02-backend-api.md` |
| Agents framework | `agents-framework.md` | `03-agents.md` |
| Memory service | `memory.md` | `04-memory.md` |
| GraphRAG | `graphrag.md` | `05-graphrag.md` |
| MCP servers | `mcp-servers.md` | `06-mcp-servers.md` |
| Curriculum / Content | `curriculum.md` | `07-curriculum.md` |
| Evals / QA | `evals-qa.md` | `08-evals-qa.md` |
| Infra / DevOps | `infra.md` | `09-infra.md` |
| Security / Safety | `security-safety.md` | `10-security-safety.md` |
| Architecture Steward | `architecture-steward.md` | `24-architecture-steward.md` |
| Code Reviewer | `code-reviewer.md` | `25-code-reviewer.md` |
| Math Notation | `math-notation.md` | skill-driven: `.cursor/skills/math-notation-integrity/SKILL.md` |
| Coordinator | `coordinator.md` | `15-coordinator-directive.md` |

**First-run:** ask the parent agent to use the matching subagent, or open a new
chat with the starter prompt at the bottom of the brief.

**Model**: Composer 2.5 or Cursor Auto for stream work; Opus reserved for planning/replanning.

**Run mode**: long, focused sessions; background multi-file work when sensible.

---

## 3. Cross-cutting skills (read before touching the relevant code)

| Skill | Read before |
| ----- | ----------- |
| `.cursor/skills/neon-direct-route/SKILL.md` | Adding/modifying any `apps/web/src/app/api/**` route that touches Neon. The free-tier critical path (onboarding, diagnostic, plans, chat memory, /learn) is Vercel + Neon direct; Render is optional. |
| `.cursor/skills/chat-memory-context/SKILL.md` | Touching `apps/web/src/app/api/chat/route.ts`, adding a new agent persona, or changing what gets persisted in `chat_turns`. |
| `.cursor/skills/onboarding-flow/SKILL.md` | Adding an onboarding question, changing plan generation inputs, or adjusting the diagnostic length. |
| `.cursor/skills/diagnostic-plan-golden-path/SKILL.md` | Diagnostic session state, post-diagnostic plan persist (`?fast=1`), client poll UX, what worked/failed in onboarding golden path. |
| `.cursor/skills/reset-learner-prod/SKILL.md` | Full/partial production learner reset for pilot testing (plans, memory, onboarding); ops scripts + `/settings/persona` UI. |
| `.cursor/skills/in-house-concept-content/SKILL.md` | Adding bilingual concept explanations to `/learn`, fixing wrong Wikipedia matches, or adding new CC content sources (OpenStax, Wikibooks, etc.). |
| `.cursor/skills/author-lesson/SKILL.md` | Authoring or modifying an AI-authored lesson under `scripts/seed_data/lessons/` (sections, all 10 question kinds, `agent_hints`, skill atoms). |
| `.cursor/skills/author-question-bank/SKILL.md` | Adding MORE questions (volume + kind diversity) to an existing authored lesson, or generating drills live. Pair with `author-lesson`. |
| `.cursor/skills/build-custom-quiz/SKILL.md` | Spinning up an ephemeral, fit-to-purpose AI quiz for one learner via `POST /api/quiz/custom`. Used by the `/app/quiz` page and any agent that wants to drop a mini-assessment into chat. NOT for authoring durable lesson question banks. |
| `.cursor/skills/expand-lessons-cursor/SKILL.md` | **Bulk substantive lesson expansion** in Cursor Composer (replaces deprecated Groq CI batch). |
| `.cursor/skills/use-obsidian-vault/SKILL.md` | Using the `obsidian-vault/` dev knowledge base — concept notes, expansion dashboard, Goren/Geva staging, MCP sync. |
| `.cursor/skills/expand-lesson-theory/SKILL.md` | Adding MORE sections / worked examples / pitfalls / cross-subject `why_matters` to an authored lesson without breaking the schema. |
| `.cursor/skills/use-learning-plan/SKILL.md` | Adding any "what should I study next?" / "why am I stuck?" feature, or wiring a new agent / UI to the mastery-aware path planner. |
| `.cursor/skills/cross-subject-kg/SKILL.md` | Adding cross-subject edges to `kg-cross-edges.json`, within-subject prereqs in YAML, or new canonical skill atoms. |
| `.cursor/skills/learner-persona/SKILL.md` | Reading or writing the shared CLAUDE.md-style learner persona (`learner_profiles.learner_persona`). |
| `.cursor/skills/agent-skill-notes/SKILL.md` | Reading or writing per-(learner, agent) private notes (`learner_agent_notes`); also see the dreaming endpoint. |
| `.cursor/skills/dreaming-and-consolidation/SKILL.md` | Any consolidation work — the lightweight web endpoint or the heavy Memory Steward nightly. |
| `.cursor/skills/memory-steward-consolidate/SKILL.md` | The heavy LLM-driven `POST /api/agent-memory/consolidate` endpoint, the weekly `POST /api/cron/consolidate-memory` sweep, and the `Rebuild from notes` button on `/settings/persona`. |
| `.cursor/skills/deploy/SKILL.md` | **Mandatory after every push to `main`**: run `scripts/verify-deploy.ps1`, poll `Deploy Web (Vercel)` + `Lint & Test`, confirm Vercel deployment `success`, smoke live URL. See `.cursor/rules/65-deploy-vercel.mdc`. |
| `.cursor/skills/coordinator-dispatch/SKILL.md` | Whenever you are operating as the Coordinator. |
| `.cursor/skills/assign-to-coordinator/SKILL.md` | Whenever you are operating as the Manager and need to hand off a new round of work. |
| `.cursor/skills/architecture-review/SKILL.md` | Platform architecture assessments, monolith vs services, coupling/scalability/race analysis, ADR drafts. Architecture Steward sub-agent (brief 24). |
| `.cursor/skills/code-review/SKILL.md` | Deep code integrity review: silent failures, edge cases, async races, clarity, over-engineering, test quality. Code Reviewer sub-agent (brief 25). Pair with `review-bugbot` on PRs. |
| `.cursor/skills/math-notation-integrity/SKILL.md` | Authoring/editing any lesson math, or when a formula renders as a red box / raw backslashes / mangled matrix. Owns the KaTeX linter + auto-fixer + blocking CI gate. Math Notation sub-agent. |
| `.cursor/skills/taste/SKILL.md` | Any visual/design work in `apps/web` — new pages/components, "make it look better" passes, or UI design review. Enforces hierarchy, spacing rhythm, type scale, restrained color, depth, motion on top of the design tokens. Pair with `add-a-frontend-page`. |
| `.cursor/skills/skill-creation/SKILL.md` | Authoring, editing, or auditing any skill under `.cursor/skills/`. Encodes Anthropic's skill-building guide (frontmatter, discoverable descriptions, progressive disclosure) + a conformance audit checklist. |
| `.cursor/skills/grill-me/SKILL.md` | Stress-test a plan or design with a relentless one-question interview before building. User says "grill me" / "/grill-me" / "stress-test this plan". |
| `.cursor/skills/find-skills/SKILL.md` | Discover/install skills from skills.sh (`npx skills find`) after checking local `.cursor/skills/` + AGENTS.md. User asks "find a skill for X" / "is there a skill that…". |
| `.agents/skills/getting-started` (CrewAI) | Scaffold CrewAI Flows/Crews (`crewai create flow`). Used for `crews/asf_qa_flow`. |
| `.agents/skills/design-agent` (CrewAI) | Role/Goal/Backstory + tools for CrewAI Tester agents. |
| `.agents/skills/design-task` (CrewAI) | Single-purpose CrewAI tasks + expected_output + guardrails. |
| `.agents/skills/ask-docs` (CrewAI) | Live CrewAI docs lookup while editing crews. |
| `crews/asf_qa_flow/` | Multi-crew QA Flow: integration, UI, product QA, security, evals Tester teams. |
| `.cursor/skills/web-agent-shared/SKILL.md` | Shared runtime skills for all four live website agents (memory, bilingual, hybrid knowledge ADR-0015, safety, plan protocol). Injected via `apps/web/src/lib/agent-skills.ts`. |
| `.cursor/skills/web-agent-tutor/SKILL.md` | Tutor runtime skills: Socratic + ordinary Q&A (hybrid knowledge). Pair with `web-agent-shared`. |
| `.cursor/skills/web-agent-mentor/SKILL.md` | Mentor runtime skills: goals, habits, wellbeing, plan updates. |
| `.cursor/skills/web-agent-coach/SKILL.md` | Coach runtime skills: drills, FSRS, weak atoms. |
| `.cursor/skills/web-agent-reviewer/SKILL.md` | Reviewer runtime skills: rubric-first submission feedback. |
