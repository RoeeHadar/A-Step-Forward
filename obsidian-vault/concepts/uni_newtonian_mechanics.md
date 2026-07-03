---
concept_id: "uni_newtonian_mechanics"
name: "Newtonian Mechanics"
name_he: "מכניקה ניוטונית"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "newton_laws"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/newton_laws.json
prerequisites: ["uni_kinematics", "uni_vectors"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Newtonian Mechanics

**HE:** מכניקה ניוטונית

## Lesson overview

**Lesson:** Newton's Three Laws of Motion
**HE:** שלושת חוקי ניוטון

Newton's three laws relate force, mass, and acceleration. Free body diagrams (FBDs) are the essential tool for applying Newton's 2nd law to any system.

> שלושת חוקי ניוטון מקשרים בין כוח, מסה ותאוצה. דיאגרמות גוף חופשי (FBD) הן הכלי המהותי ליישום החוק השני.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_kinematics|uni_kinematics]], [[concepts/uni_vectors|uni_vectors]]

## Skill atoms

- Newton's three laws: inertia, F_net = ma, action-reaction pairs
- Free body diagrams for single and connected objects
- Weight, normal force, tension, and applied forces on FBDs
- Component-wise Newton's 2nd law (ΣF_x = ma_x, ΣF_y = ma_y)
- Elevator problems and apparent weight N = m(g ± a)
- Connected blocks and string tension on frictionless surfaces
- Atwood machine — derive and apply a and T formulas
- Inclined plane with friction (N = mg cos θ, f = μN)
- Multi-body systems — internal vs external forces
- Combining Newton's 2nd law with kinematics for distance/speed

## Level scope

- **physics1:** Systematic FBD → ΣF = ma workflow for single bodies, connected masses, elevators, and Atwood machines. University exams expect derived formulas, limiting-case checks, and friction on inclines — not just plug-and-chug F = ma.

## Lesson sections

- **intro:** Force, Mass, and the Laws Governing Motion
- **definition:** Newton's Three Laws
- **theory:** Free Body Diagrams and System Analysis
- **worked_example:** Worked Example 1 — Box on a Frictionless Surface
- **checkpoint:** Stop & Practice — Easy
- **worked_example:** Worked Example 2 — Two Blocks Connected by a String
- **checkpoint:** Stop & Practice — Medium
- **worked_example:** Worked Example 3 — Atwood Machine: Deriving Acceleration and Tension
- **method_guide:** How to Draw a Correct FBD: 5 Steps
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes with Newton's Laws
- **why_matters:** Why it matters
- **before_exam:** Exam Preparation — Newton's Laws
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/newton_laws_general|newton_laws_general]]
- [[concepts/center_of_mass|center_of_mass]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/newton_laws.json` _(alias from `uni_newtonian_mechanics`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
