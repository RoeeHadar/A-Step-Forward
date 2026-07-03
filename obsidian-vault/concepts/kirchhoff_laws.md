---
concept_id: "kirchhoff_laws"
name: "Kirchhoff's Laws"
name_he: "חוקי קירכהוף"
subject: physics
level: high_school
bagrut_chapter: electricity
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "kirchhoff_laws"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/kirchhoff_laws.json
prerequisites: ["electric_circuits"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Kirchhoff's Laws

**HE:** חוקי קירכהוף

## Lesson overview

**Lesson:** Kirchhoff's Laws
**HE:** חוקי קירכהוף

Kirchhoff's Current Law (KCL) and Voltage Law (KVL). Node and mesh analysis. Solving multi-loop circuits.

> חוק הזרם (KCL) וחוק המתח (KVL). ניתוח צמתים ולולאות. פתרון מעגלים מרובי לולאות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/electric_circuits|electric_circuits]]

## Skill atoms

- KCL junction rule: sum currents in = sum currents out
- KVL loop rule: sum voltage rises and drops = 0
- Assigning branch current directions before writing equations
- Battery − to +: voltage rise; resistor in I direction: drop
- Single-loop KVL with resistors and EMF sources
- Two-loop circuit: (n−1) KCL + mesh KVL equations
- Node analysis: express branch currents at junctions
- Wheatstone bridge balance condition

## Level scope

- **hs_physics:** KCL and KVL for multi-loop and multi-node DC circuits — a hallmark electricity-questionnaire problem type. Students set up junction and loop equations; bridge/Wheatstone configurations appear as harder variants.

## Lesson sections

- **intro:** Beyond Simple Circuits
- **definition:** KCL and KVL — Formal Statements
- **theory:** Solving Multi-Loop Circuits
- **worked_example:** Worked Example 1 — KCL at a Node
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — KVL in a Single Loop
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Two-Loop Circuit
- **method_guide:** Method Guide — Kirchhoff's Laws
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/dc_circuits_kirchhoff|dc_circuits_kirchhoff]]
- [[concepts/uni_dc_circuits|uni_dc_circuits]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/kirchhoff_laws.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
