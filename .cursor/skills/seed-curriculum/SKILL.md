---
name: seed-curriculum
description: How to author and seed curriculum (courses → units → lessons → objectives → assessments → resources) and connect it to the Knowledge Graph. Read BEFORE adding seed content or authoring tools.
---

# Seed Curriculum

## Content model
See `packages/schemas/curriculum.py`. Hierarchy: `Course → Unit → Lesson`, plus `Objective`, `Assessment`, `Question`, `Resource`. Objectives carry `concepts[]` which are first-class KG nodes.

## Authoring formats
- YAML for structured fields; Markdown for `body_md`.
- Folder per course:
  ```
  infra/seeds/courses/<course-id>/
    course.yaml
    units/
      <unit-id>/
        unit.yaml
        lessons/
          <lesson-id>.md
        assessments/
          <assessment-id>.yaml
    resources/
      <resource-id>.yaml
  ```

## Seeding
```bash
uv run python scripts/seed_curriculum.py --course foundations-of-math
```
This:
1. Validates everything against Pydantic schemas.
2. Upserts into Postgres.
3. Enqueues a GraphRAG ingestion job to project objectives/concepts into the KG.

## Quality bar (Phase 1 seed)
- ≥ 1 full course with 3 units × 3 lessons × 1 assessment each.
- Each lesson has 2–5 objectives at appropriate Bloom's levels.
- Each objective lists 1–3 concepts; concepts have short canonical names.
- Each assessment has a rubric (even for objective questions).
- Resources have license + summary.

## Pitfalls
- Don't conflate **objective** (what the learner should be able to do) with **concept** (what they should understand). One objective can reference multiple concepts.
- Don't author lessons longer than `est_minutes` * 200 words/min as text-only — break into segments.
- Don't link to copyrighted resources without `license` set.
