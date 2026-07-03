---
concept_id: "uni_fluids"
name: "Fluid Mechanics"
name_he: "מכניקת זורמים"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "fluids_bernoulli"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/fluids_bernoulli.json
prerequisites: ["uni_newtonian_mechanics", "uni_work_energy"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Fluid Mechanics

**HE:** מכניקת זורמים

## Lesson overview

**Lesson:** Bernoulli's Equation and Fluid Dynamics
**HE:** משוואת ברנולי ודינמיקת נוזלים

Bernoulli's principle links faster flow to lower pressure. Master continuity, Bernoulli's equation, Torricelli's theorem, and Venturi applications for university fluid dynamics.

> עיקרון ברנולי מקשר זרימה מהירה ללחץ נמוך. שליטה ברציפות, משוואת ברנולי, משפט טוריצ'לי ויישומי ונטורי לדינמיקת נוזלים אוניברסיטאית.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_newtonian_mechanics|uni_newtonian_mechanics]], [[concepts/uni_work_energy|uni_work_energy]]

## Skill atoms

- Continuity equation A₁v₁ = A₂v₂ for incompressible flow
- Bernoulli's equation and energy per unit volume
- Fast flow → lower static pressure (Venturi / lift intuition)
- Torricelli's theorem v = √(2gH)
- Applying continuity first, then Bernoulli for pressures
- Horizontal-pipe Bernoulli simplification (P + ½ρv² = const)
- Pipe narrowing and flow-speed calculation from radii
- Venturi meter and real-world Bernoulli applications
- Unit and sign checks in fluid-energy problems

## Level scope

- **physics1:** Ideal-fluid continuity + Bernoulli at intro-university depth — sequential continuity-then-Bernoulli workflow, Torricelli draining, and the counter-intuitive pressure–speed tradeoff. Viscosity and full hydrostatics are out of scope for this aliased lesson.

## Lesson sections

- **intro:** Fast Fluid, Low Pressure
- **definition:** Key Equations
- **theory:** Derivation and Validity
- **worked_example:** Worked Example 1 — Continuity Equation
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Venturi Meter
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Pipe with Height Change
- **method_guide:** Method Guide
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Card
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/fluids_bernoulli.json` _(alias from `uni_fluids`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
