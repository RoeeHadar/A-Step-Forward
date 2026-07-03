---
concept_id: "electromagnetic_induction"
name: "Electromagnetic Induction"
name_he: "השראה אלקטרומגנטית"
subject: physics
level: high_school
bagrut_chapter: electricity
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "electromagnetic_induction"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/electromagnetic_induction.json
prerequisites: ["magnetism", "electric_circuits"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Electromagnetic Induction

**HE:** השראה אלקטרומגנטית

## Lesson overview

**Lesson:** Electromagnetic Induction
**HE:** השראה אלקטרומגנטית

Faraday's law: $\mathcal{E} = -d\Phi/dt$. Lenz's law gives the direction of the induced EMF. A rotating coil generates an alternating EMF $\mathcal{E} = NBA\omega\sin(\omega t)$.

> חוק פרדיי: $\mathcal{E} = -d\Phi/dt$. חוק לנץ נותן את כיוון הכ"א המושרה. סליל מסתובב מייצר כ"א מתחלף $\mathcal{E} = NBA\omega\sin(\omega t)$.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/magnetism|magnetism]], [[concepts/electric_circuits|electric_circuits]]

## Skill atoms

- Magnetic flux: Φ = B·A·cosθ
- Faraday's law: EMF = -ΔΦ/Δt
- Lenz's law (direction of induced current)
- EMF of a moving conductor in magnetic field: EMF = BLv
- Self-inductance: EMF = -L·dI/dt
- Energy stored in inductor: U = ½LI²
- Transformer: V₁/V₂ = N₁/N₂

## Level scope

- **hs_physics:** Faraday's law, Lenz's law, motional EMF (BLv), and transformers — core electricity questionnaire content. Questions compute induced EMF/current direction, flux change, and ideal transformer voltage ratios.

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

- [[concepts/faraday_induction|faraday_induction]]
- [[concepts/maxwell_equations|maxwell_equations]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/electromagnetic_induction.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
