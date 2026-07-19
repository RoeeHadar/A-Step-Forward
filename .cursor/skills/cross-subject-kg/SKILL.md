---
name: cross-subject-kg
description: How to extend the knowledge graph with new cross-subject edges (e.g. derivatives → kinematics) and within-subject prerequisites, and how the skill-atom universe is wired into mastery tracking. Read BEFORE editing kg-data.json, kg-cross-edges.json, or anything that touches skill_atoms / kg_edges in Postgres.
---

# Cross-subject KG + Skill Atoms

## Why this exists

A learner who's stuck on `kinematics_1d` is usually NOT stuck on kinematics
itself — they're stuck on `functions_quadratic` ($x(t) = x_0 + v_0 t + \frac12 a t^2$
is a parabola) or on `algebra_basics` (rearranging for $t$). Within-subject
prerequisites don't capture that. We layer **cross-subject edges** on top, and
we go one level finer with **skill atoms** so the planner can name the actual
missing micro-skill, not just the topic.

## The two graphs

### Within-subject — `kg-data.json` (auto-generated)

```
content/knowledge-graph/<subject>-*.yaml      # source of truth
        │
        │  node scripts/build-kg-json.mjs
        ▼
apps/web/src/lib/kg-data.json                 # Vercel-bundled snapshot
```

Edit the YAML, rebuild the JSON. Each concept lists `prerequisites: [...]` —
these are ALL within the same subject by convention.

### Cross-subject + high-leverage — `kg-cross-edges.json` (hand-curated)

```
apps/web/src/lib/kg-cross-edges.json          # source of truth (hand-curated)
        │
        │  scripts/seed-lessons.mjs (during seed) upserts into Postgres
        ▼
Neon `kg_edges` table                         # what the runtime planner queries
```

Edit the JSON, run the seed workflow. Each edge has:

```json
{
  "src": "trigonometry_identities",
  "dst": "ac_circuits",
  "relation": "applies_to",
  "weight": 1.0,
  "note": "Phasors are sine + identities."
}
```

| Field      | Meaning                                                                                              |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| `src`      | Source concept id (must exist in `kg-data.json`).                                                    |
| `dst`      | Destination concept id (must exist).                                                                 |
| `relation` | `prereq` \| `applies_to` \| `generalizes` \| `models` \| `tooling_for`.                              |
| `weight`   | (0, 1]. The planner multiplies edge weight × (1 − mastery) when computing urgency. 1.0 = hard prereq.|
| `note`     | One-line human rationale (shown to authors, not learners).                                           |

The combined graph is what `apps/web/src/lib/learning-plan.ts` walks.

## Skill atoms — the finer granularity

Concepts are too coarse for mastery tracking. A learner can "know" derivatives
in the abstract but never have practiced the **product rule** specifically.
**Skill atoms** are first-class:

```sql
-- Postgres (Neon)
skill_atoms          (atom_id, name, name_he, description_en, description_he, subject, level)
lesson_skill_atoms   (lesson_id, atom_id, role)       -- role = 'teaches' | 'exercises'
skill_practice       (learner_id, atom_id, attempts, correct, last_practiced)
```

How atoms get into the database:

1. Author them implicitly in a lesson's `agent_hints.skill_atoms_unlocked[]`
   (role = `teaches`) and per-question `skill_atoms[]` (role = `exercises`).
2. Re-seed the lessons:
   ```
   gh workflow run "Seed DB (one-shot)" -f target=lessons
   ```
3. The seeder upserts each atom into `skill_atoms` and the (lesson, atom, role)
   tuples into `lesson_skill_atoms`. No manual schema changes needed.

## Naming conventions for atoms

- snake_case, ≤ 32 chars, action-flavoured: `product_rule_apply`, `free_body_diagram_force_sum`, `area_scale_factor`, `rule_out_SSA`.
- Subject-prefix only when ambiguous: `math_proof_by_contradiction` vs `phys_proof_dimensional`.
- Reuse atoms across lessons — that's the WHOLE POINT. The same `area_scale_factor` atom should appear in `triangles_similar`, `circles_area`, `volumes`, and any physics problem that depends on it.

## Adding a new cross-subject edge — workflow

1. Decide the relation:
   - `prereq` — the learner literally cannot understand `dst` without `src` (e.g. `vectors_basics → kinematics_2d`).
   - `applies_to` — `src` is a tool used inside `dst` (e.g. `trig_identities → ac_circuits`).
   - `generalizes` — `src` is the general principle, `dst` is the specific case.
   - `models` — `dst` is modeled mathematically by `src` (e.g. `differential_equations → simple_harmonic_motion`).
   - `tooling_for` — `src` is a computational tool for `dst` (e.g. `complex_numbers → ac_circuits`).
2. Add the entry to `apps/web/src/lib/kg-cross-edges.json` in the appropriate
   section (the file is grouped by topic — keep edges adjacent to siblings).
3. Run the seed workflow: `gh workflow run "Seed DB (one-shot)" -f target=lessons`.
4. Probe the planner: hit `/api/learning-plan/next?goal=<dst>` as a logged-in
   user and verify the new edge shows up in `path[]`.

## Adding a new within-subject prereq

1. Edit the YAML under `content/knowledge-graph/`.
2. Rebuild: `node scripts/build-kg-json.mjs`.
3. Commit both the YAML and the regenerated `kg-data.json`.
4. The seeder picks it up automatically on the next run.

## Pitfalls

- ❌ Adding an edge whose `src` or `dst` doesn't exist in `kg-data.json` — the seeder will warn but NOT fail. Always verify both ids exist first.
- ❌ Cycles. The planner does a BFS with cycle detection (it'll terminate), but cycles imply your prereq model is wrong. Refactor.
- ❌ Authoring a new atom in a lesson but never `exercises`ing it in any question — the planner will see `mastery = 0` forever. Either drop the atom or add ≥ 1 question that exercises it.
- ❌ Per-subject atom duplication (e.g. `math_area_scale_factor` AND `phys_area_scale_factor`). The atom is the same skill — name it once and let both subjects' lessons reference it.
- ❌ Bypassing the seed pipeline to write directly to `kg_edges` or `skill_atoms` in Neon. The JSON files are the source of truth; the DB is a projection.

## What touches what

| Layer                                            | Files / tables                                                            |
| ------------------------------------------------ | ------------------------------------------------------------------------- |
| Within-subject prereqs (source of truth: YAML)   | `content/knowledge-graph/*.yaml` → `apps/web/src/lib/kg-data.json`        |
| Cross-subject edges (source of truth: JSON)      | `apps/web/src/lib/kg-cross-edges.json` → Postgres `kg_edges`              |
| Skill atoms (source of truth: lesson JSONs)      | `scripts/seed_data/lessons/*.json` → Postgres `skill_atoms`, `lesson_skill_atoms` |
| Per-learner mastery                              | Postgres `skill_practice` (written by `/api/lesson/answer`)               |
| Path planning                                    | `apps/web/src/lib/learning-plan.ts` (reads kg JSON + skill_practice)     |
| Agent grounding                                  | `apps/web/src/app/api/chat/route.ts` (injects path snapshot + agent_hints)|
