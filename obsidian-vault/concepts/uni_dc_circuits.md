---
concept_id: "uni_dc_circuits"
name: "DC Circuits"
name_he: "מעגלי זרם ישר"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "kirchhoff_laws"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/kirchhoff_laws.json
prerequisites: ["uni_potential", "uni_capacitance"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# DC Circuits

**HE:** מעגלי זרם ישר

## Lesson overview

**Lesson:** Kirchhoff's Laws
**HE:** חוקי קירכהוף

Kirchhoff's Current Law (KCL) and Voltage Law (KVL). Node and mesh analysis. Solving multi-loop circuits.

> חוק הזרם (KCL) וחוק המתח (KVL). ניתוח צמתים ולולאות. פתרון מעגלים מרובי לולאות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_potential|uni_potential]], [[concepts/uni_capacitance|uni_capacitance]]

## Skill atoms

- Ohm's law V = IR and power P = IV
- Resistors in series and parallel
- Kirchhoff's junction rule (current in = out)
- Kirchhoff's loop rule (ΣΔV = 0)
- Multi-loop circuit analysis with sign conventions
- RC charging/discharging qualitative behavior

## Level scope

- **physics1:** DC circuit analysis via Kirchhoff rules; multi-loop sign discipline and equivalent resistance are standard exam skills.

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

## Links

- Lesson JSON: `scripts/seed_data/lessons/kirchhoff_laws.json` _(alias from `uni_dc_circuits`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
