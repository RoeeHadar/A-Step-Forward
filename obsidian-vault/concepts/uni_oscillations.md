---
concept_id: "uni_oscillations"
name: "Oscillations & Waves"
name_he: "תנודות וגלים"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "simple_harmonic_motion"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/simple_harmonic_motion.json
prerequisites: ["uni_newtonian_mechanics", "uni_work_energy"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Oscillations & Waves

**HE:** תנודות וגלים

## Lesson overview

**Lesson:** SHM Energy Analysis and the Pendulum
**HE:** ניתוח אנרגיה של SHM ומטוטלת

In SHM, total mechanical energy E = ½kA² is conserved and continuously exchanges between kinetic (½mv²) and potential (½kx²) forms. The simple pendulum for small angles is exactly an SHM system with T = 2π√(L/g), independent of mass and amplitude. Energy analysis is the fastest route to finding speeds at arbitrary positions.

> ב-SHM, האנרגיה המכנית הכוללת $E=\frac{1}{2}kA^2$ מתשמרת ועוברת ללא-הרף בין קינטית ($\frac{1}{2}mv^2$) לפוטנציאלית ($\frac{1}{2}kx^2$). מטוטלת פשוטה לזוויות קטנות היא בדיוק מערכת SHM עם $T=2\pi\sqrt{L/g}$, ללא תלות במסה או במשרעת.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_newtonian_mechanics|uni_newtonian_mechanics]], [[concepts/uni_work_energy|uni_work_energy]]

## Skill atoms

- SHM total energy E = ½kA² conserved
- KE/PE exchange and speed at position v = ω√(A² − x²)
- Maximum speed v_max = Aω and ω = √(k/m)
- Energy fractions K/E = 1 − x²/A²
- Simple pendulum small-angle SHM equation of motion
- Pendulum period T = 2π√(L/g) and mass independence
- Derivation of pendulum EOM via tangential Newton's 2nd law
- Where kinetic equals potential at x = ±A/√2
- Energy-method protocol for SHM without tracking time
- Distinguishing spring vs pendulum ω relationships

## Level scope

- **physics1:** SHM via energy conservation and small-angle pendulum theory — derive T = 2π√(L/g), compute speeds/energy fractions at arbitrary x, and justify the small-angle approximation. Wave propagation is deferred to later EM/optics concepts.

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

## Links

- Lesson JSON: `scripts/seed_data/lessons/simple_harmonic_motion.json` _(alias from `uni_oscillations`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
