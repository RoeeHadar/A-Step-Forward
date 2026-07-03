---
concept_id: "uni_thermodynamics"
name: "Thermodynamics"
name_he: "תרמודינמיקה"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "thermodynamics_makhina"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/thermodynamics_makhina.json
prerequisites: ["uni_work_energy"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Thermodynamics

**HE:** תרמודינמיקה

## Lesson overview

**Lesson:** Thermodynamics — Makhina Track
**HE:** תרמודינמיקה — מסלול מכינה

Heat, work and internal energy. Master calorimetry ($Q=mc\Delta T$, latent heat), the first law ($\Delta U=Q-W$), and ideal gas processes.

> חום, עבודה ואנרגיה פנימית. שליטה בקלורימטריה ($Q=mc\Delta T$, חום סמוי), החוק הראשון ($\Delta U=Q-W$), ותהליכי גז אידיאלי.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_work_energy|uni_work_energy]]

## Skill atoms

- Sensible heat Q = mcΔT within a single phase
- Latent heat at phase change Q = mL (plateau regions)
- First law of thermodynamics ΔU = Q − W (sign conventions)
- Ideal gas law PV = nRT with Kelvin temperature
- Isothermal, adiabatic, isochoric, and isobaric process simplifications
- Multi-stage heating curves (heat, melt, heat, boil, …)
- Internal energy change from heat in minus work out
- Water-specific constants (c, L_f, L_v) and unit conversion (g ↔ kg)
- Identifying process type from problem wording
- Temperature-vs-heat graph interpretation (slope vs plateau)

## Level scope

- **physics1:** Makhina-aligned thermodynamics — calorimetry, latent heat, first law, and ideal-gas processes at rigorous SI-unit depth. Multi-stage heating-curve problems and explicit ΔU = Q − W sign discipline are expected; statistical mechanics is out of scope.

## Lesson sections

- **intro:** Energy in thermal systems
- **definition:** Key formulas
- **theory:** Thermodynamic processes
- **worked_example:** Worked Example 1 — heating 2 kg of water from 20°C to 80°C
- **checkpoint:** Quick check
- **worked_example:** Worked Example 2 — 1 kg ice at −10°C → steam at 100°C
- **checkpoint:** Quick check
- **worked_example:** Worked Example 3 — isothermal vs adiabatic compression
- **method_guide:** Method guide
- **exercise_set:** Practice Exercises
- **pitfall:** Common pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/thermodynamics_makhina.json` _(alias from `uni_thermodynamics`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
