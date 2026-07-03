---
concept_id: "simple_harmonic_motion"
name: "Simple Harmonic Motion (SHM)"
name_he: "תנועה הרמונית פשוטה"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "simple_harmonic_motion"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/simple_harmonic_motion.json
prerequisites: ["newton_laws", "work_energy"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Simple Harmonic Motion (SHM)

**HE:** תנועה הרמונית פשוטה

## Lesson overview

**Lesson:** SHM Energy Analysis and the Pendulum
**HE:** ניתוח אנרגיה של SHM ומטוטלת

In SHM, total mechanical energy E = ½kA² is conserved and continuously exchanges between kinetic (½mv²) and potential (½kx²) forms. The simple pendulum for small angles is exactly an SHM system with T = 2π√(L/g), independent of mass and amplitude. Energy analysis is the fastest route to finding speeds at arbitrary positions.

> ב-SHM, האנרגיה המכנית הכוללת $E=\frac{1}{2}kA^2$ מתשמרת ועוברת ללא-הרף בין קינטית ($\frac{1}{2}mv^2$) לפוטנציאלית ($\frac{1}{2}kx^2$). מטוטלת פשוטה לזוויות קטנות היא בדיוק מערכת SHM עם $T=2\pi\sqrt{L/g}$, ללא תלות במסה או במשרעת.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/newton_laws|newton_laws]], [[concepts/work_energy|work_energy]]

## Skill atoms

- Definition of SHM: F = -kx
- Spring-mass system
- Period: T = 2π√(m/k)
- Simple pendulum: T = 2π√(L/g)
- Amplitude, frequency, angular frequency
- Position, velocity, acceleration as functions of time
- Energy in SHM: KE + PE = constant
- x(t) = A·cos(ωt+φ)

## Level scope

- **hs_physics:** Spring-mass and simple-pendulum period formulas (T = 2π√(m/k), T = 2π√(L/g)) appear in mechanics; SHM also bridges to AC circuits. Questions ask for period, amplitude, or energy exchange at turning points — no differential equations required.

## Lesson sections

- **intro:** Energy in SHM — The Constant-Sum Story
- **definition:** SHM Energy and the Simple Pendulum
- **theory:** Derivation of the Pendulum Equation of Motion
- **worked_example:** Worked Example 1 — Maximum Speed from Energy Conservation
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Fraction of Energy that is Kinetic at x = A/2
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Derive the Pendulum Equation and T = 2π√(L/g)
- **method_guide:** Method Guide — SHM Energy Analysis Decision Table
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes in SHM Energy Analysis and Pendulum
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Sheet & Exam Patterns
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/harmonic_oscillation|harmonic_oscillation]]
- [[concepts/uni_oscillations|uni_oscillations]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/simple_harmonic_motion.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
