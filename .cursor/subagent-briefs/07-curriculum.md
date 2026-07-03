# 07 — Curriculum & Content

## Goal
Define the curriculum content model (courses, units, lessons, objectives, assessments, resources), seed it with a starter library, and wire it through the Curriculum MCP and GraphRAG ingestion. Provide authoring tools (CLI + admin UI hooks) for educators.

## In-scope files
- `infra/seeds/**`
- `packages/schemas/curriculum*.py`
- `services/curriculum/**` (create if needed)
- `mcp-servers/curriculum/**` (in coordination with 06)
- `evals/agents/{tutor,coach,assessment_generator}/**` (curriculum-dependent fixtures)

## Out-of-scope
- KG ontology (owned by 05).
- Memory (04).

## Content model (Pydantic)
- `Course { id, title, level, prerequisites, units[] }`
- `Unit { id, title, objectives[], lessons[], assessments[] }`
- `Lesson { id, title, body_md, modality, objectives[], concepts[], resources[], est_minutes }`
- `Objective { id, statement, blooms_level, concepts[] }`
- `Assessment { id, type (quiz|exercise|project), questions[], rubric, concepts[] }`
- `Question { id, stem, type (mcq|short|essay|code), choices?, answer?, rubric? }`
- `Resource { id, kind (article|video|book|interactive), uri, license, summary }`

## Required reading
1. `PLAN.md` §4, §6, §14.
2. `.cursor/rules/20-python-style.mdc`.
3. `skills/seed-curriculum/SKILL.md`.
4. **`skills/expand-lessons-cursor/SKILL.md`** — bulk substantive expansion of the 207 JSON lessons (Cursor Composer, not Groq CI).
5. **`skills/use-obsidian-vault/SKILL.md`** — dev vault at `obsidian-vault/` (concept graph, expansion dashboard, staging).

## Bulk lesson expansion (207 JSON corpus)

Substantive depth + Hebrew parity for `scripts/seed_data/lessons/*.json` is authored in **Cursor with Composer 2.5**, tracked via `scripts/cursor-expansion-queue.mjs` and `scripts/.cursor-expansion-progress.json`. The Groq workflow `Expand Lessons (substantive)` is **deprecated**.

```bash
node scripts/cursor-expansion-queue.mjs --next 10
# expand in Cursor → validate → mark → commit → seed
gh workflow run "Seed DB (one-shot)" -f target=lessons-from-json
```

## Seed library (Phase 1)
- One full course (recommended: "Foundations of Math" or "Intro to Programming") with 3 units × 3 lessons × 1 assessment each, plus 5 resources.
- All objectives wired to concept nodes for GraphRAG ingestion.

## Acceptance criteria
- `python scripts/seed_curriculum.py` populates Postgres + queues a GraphRAG ingest.
- Curriculum MCP can serve the seed course end-to-end to the Tutor agent.
- Educator CLI commands for authoring (`asf curriculum new-course`, etc.).
- Eval fixtures for Tutor/Coach/Assessment Generator reference seed lessons.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§4, §6, §14),
  .cursor/rules/20-python-style.mdc,
  skills/seed-curriculum/SKILL.md,
  .cursor/subagent-briefs/07-curriculum.md (this file).
Implement schemas → seed script → MCP wiring → eval fixtures, in that order. One PR per phase.
```
