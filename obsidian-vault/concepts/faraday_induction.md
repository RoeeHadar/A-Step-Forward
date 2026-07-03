---
concept_id: "faraday_induction"
name: "Faraday's Law & Induction"
name_he: "חוק פארדי והשראה"
subject: physics
level: high_school
bagrut_chapter: electricity
points_levels: ["hs_physics"]
expansion_status: todo
data_completeness: full
lesson_id: "electromagnetic_induction"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/electromagnetic_induction.json
prerequisites: ["magnetic_force", "electromagnetic_induction"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Faraday's Law & Induction

**HE:** חוק פארדי והשראה

## Lesson overview

**Lesson:** Electromagnetic Induction
**HE:** השראה אלקטרומגנטית

Faraday's law: $\mathcal{E} = -d\Phi/dt$. Lenz's law gives the direction of the induced EMF. A rotating coil generates an alternating EMF $\mathcal{E} = NBA\omega\sin(\omega t)$.

> חוק פרדיי: $\mathcal{E} = -d\Phi/dt$. חוק לנץ נותן את כיוון הכ"א המושרה. סליל מסתובב מייצר כ"א מתחלף $\mathcal{E} = NBA\omega\sin(\omega t)$.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/magnetic_force|magnetic_force]], [[concepts/electromagnetic_induction|electromagnetic_induction]]

## Skill atoms

- Magnetic flux Φ = B·A·cosθ
- Faraday law: EMF = -ΔΦ/Δt
- Lenz law (direction of induced current)
- EMF of moving rod EMF = BLv
- Self-inductance EMF = -L·dI/dt
- Transformer V₁/V₂ = N₁/N₂

## Level scope

- **hs_physics:** Electricity — flux change induces EMF; Lenz direction is exam favourite

## Lesson sections

- **intro:** From Magnetism to Electricity: Induction
- **definition:** Faraday's Law, Lenz's Law, and Moving Conductor EMF
- **theory:** Rotating Coil Generator, Transformers, and Lenz's Law Applications
- **worked_example:** Worked Example 1 — EMF from Changing Flux
- **checkpoint:** Stop & Practice — Easy
- **worked_example:** Worked Example 2 — Moving Conductor in a Magnetic Field
- **checkpoint:** Stop & Practice — Medium
- **worked_example:** Worked Example 3 — Rotating Coil Generator: Deriving the EMF Formula
- **method_guide:** Step-by-Step Approach for Induction Problems
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes in Electromagnetic Induction
- **why_matters:** Why it matters
- **before_exam:** Exam Preparation — Electromagnetic Induction
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/maxwell_equations|maxwell_equations]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/electromagnetic_induction.json` _(alias from `faraday_induction`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
