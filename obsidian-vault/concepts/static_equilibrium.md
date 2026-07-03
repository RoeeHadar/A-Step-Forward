---
concept_id: "static_equilibrium"
name: "Extended Static Equilibrium"
name_he: "שיווי משקל מורחב"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "static_equilibrium"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/static_equilibrium.json
prerequisites: ["torque"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Extended Static Equilibrium

**HE:** שיווי משקל מורחב

## Lesson overview

**Lesson:** Static Equilibrium — ΣF = 0 and Στ = 0
**HE:** שיווי משקל סטטי — ΣF = 0 ו-Στ = 0

A rigid body is in static equilibrium when it is both translationally at rest (ΣF = 0) and rotationally at rest (Στ = 0). Choosing the pivot point cleverly eliminates unknown forces from the torque equation. The center of mass must lie over the support base for stability.

> גוף קשיח בשיווי משקל סטטי כאשר הוא גם תנועתית נח ($\sum F=0$) וגם סיבובית נח ($\sum\tau=0$). בחירת ציר מרגיל חוסכת מחישוב כוחות לא ידועים. מרכז המסה חייב להיות מעל בסיס התמיכה לצורך יציבות.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/torque|torque]]

## Skill atoms

- Translational equilibrium: ΣF_x = 0 and ΣF_y = 0
- Rotational equilibrium: Στ = 0 about chosen pivot
- Torque τ = r⊥F with consistent CCW/CW sign convention
- Pivot at unknown force to eliminate reaction from Στ
- Hinged beam + cable: solve tension from Στ about hinge
- Two-support beam: reactions from torque balance + ΣF_y = 0
- Non-uniform beam: weight acts at given CM, not geometric center
- Ladder on frictionless wall: minimum μs from Στ at base
- Stability: CM must lie above support base to resist tipping

## Level scope

- **hs_physics:** Extended torque equilibrium beyond single-pivot cases — distributed loads, multi-support beams, and stability/tipping criteria. Less frequent than basic ladder problems but appears as a harder mechanics sub-question.

## Lesson sections

- **intro:** When Nothing Moves — The Two Conditions for Equilibrium
- **definition:** The Two Equilibrium Conditions and Torque Definition
- **theory:** Choosing the Pivot Wisely — Eliminating Unknowns
- **worked_example:** Worked Example 1 — Uniform Beam Hinged at Wall with Cable at 30°
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Non-Uniform Beam with Person at ¾ Position
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Ladder Against Frictionless Wall: Minimum Friction Coefficient
- **method_guide:** Method Guide — Static Equilibrium Decision Table
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes in Static Equilibrium
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Sheet & Exam Patterns
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/fluids_hydrostatics|fluids_hydrostatics]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/static_equilibrium.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
