# 07 — Curriculum / Content — Resume Brief (Round 2)

## Current state

Curriculum service skeleton is on `main`:
- `services/curriculum/curriculum_service/{api.py,default_service.py,settings.py}`
- Stores: `database.py`, `models.py`, `repository.py`
- Alembic `infra/alembic/versions/0002_curriculum.py`
- Smoke test `services/curriculum/tests/test_smoke.py`

Evals for `curriculum_designer` and `assessment_generator` already on `main` (capability + safety + thresholds), as well as `coach/curriculum_fixtures.yaml` and `assessment_generator/curriculum_fixtures.yaml`.

`scripts/seed_curriculum.py` is a placeholder.

## What's left

1. **Real schemas + repo** wired against Postgres via the service models (replace any in-memory bits in `default_service.py`).
2. **Phase-1 course content** authored under `content/courses/foundations-of-ai-literacy/` — YAML/MDX:
   - 1 course → 6 units → 4–6 lessons each → objectives, prerequisites, modality, resources, assessment.
   - Bloom-tagged objectives.
   - At least 3 resources per lesson (book chapter, paper, video) with proper `Citation`.
   - At least 1 formative assessment per lesson + 1 summative per unit.
3. **Seed loader** in `scripts/seed_curriculum.py` reads the YAML and upserts into the curriculum tables.
4. **Curriculum MCP endpoints** (`mcp-servers/curriculum`) exposed: `curriculum.search`, `get_lesson`, `next_objective`, `unlock_check`, `recommend_resources` — wire to real data.
5. **Coordinate with stream 05** (GraphRAG): seed loader publishes lessons/objectives → GraphRAG ingests so retrieval works on Day 1.
6. **Coordinate with stream 01** (Frontend) on the lesson page shape (`apps/web/src/app/(app)/app/lessons/[lessonId]/page.tsx`).
7. **Evals**: extend `evals/agents/curriculum_designer/` + add `evals/retrieval/curriculum_recall.py`.

## Locked decisions

- Course path: `content/courses/<slug>/` with `course.yaml`, `units/<unit>.yaml`, `lessons/<unit>/<lesson>.mdx` for body, `assessments/<unit>/<lesson>.yaml`.
- Idempotent seeding: keyed by `(course_slug, unit_slug, lesson_slug)`.
- Default Phase-1 course: **"Foundations of AI Literacy"** (10–14 yo and 14+ tracks).
- Modalities: read, watch, build, practice, project.
- Use `packages/schemas/schemas/curriculum.py` Pydantic models as the source of truth.

## Done when

- Phase-1 course content shipped + seed-loadable.
- Seed runs in CI on a fresh DB and produces a complete graph of units → lessons → objectives → assessments → resources.
- Curriculum MCP returns real data.
- GraphRAG ingestion of the seed corpus succeeds in staging.
- Lessons render in the frontend lesson page.

## Required reading

- `PLAN.md` §13; `AGENTS.md`.
- `skills/seed-curriculum/SKILL.md`.
- `.cursor/rules/{20,60}-*.mdc`.
- `.cursor/subagent-briefs/07-curriculum.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Curriculum sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/07-curriculum-resume.md
  3. .cursor/subagent-briefs/07-curriculum.md
  4. PLAN.md §13; AGENTS.md
  5. skills/seed-curriculum/SKILL.md
  6. .cursor/rules/{20,60}-*.mdc

Then:
  A. Move the curriculum service to real Postgres-backed reads/writes via the
     service models.
  B. Author the Phase-1 course "Foundations of AI Literacy" under
     content/courses/foundations-of-ai-literacy/ (course.yaml, units/, lessons/,
     assessments/) per the locked layout. Aim for 1 course → 6 units → 4–6
     lessons each, Bloom-tagged objectives, ≥3 resources/lesson, ≥1 formative
     per lesson + 1 summative per unit.
  C. Implement scripts/seed_curriculum.py — idempotent upserts keyed by slugs.
  D. Wire Curriculum MCP tools to real data.
  E. Coordinate with stream 05 (GraphRAG) so seed publishes events that trigger
     ingestion on staging.
  F. Extend evals/agents/curriculum_designer/ + add evals/retrieval/curriculum_recall.py.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - Many small PRs (one unit per PR is fine).  review-bugbot on every PR.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: a real, sourced, structured Phase-1 course that the deployed
website can immediately offer to learners on Day 1.
```
