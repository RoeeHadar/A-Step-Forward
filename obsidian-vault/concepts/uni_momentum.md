---
concept_id: "uni_momentum"
name: "Linear & Angular Momentum"
name_he: "תנע לינארי וזוויתי"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "momentum"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/momentum.json
prerequisites: ["uni_newtonian_mechanics", "uni_work_energy"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Linear & Angular Momentum

**HE:** תנע לינארי וזוויתי

## Lesson overview

**Lesson:** Momentum, Impulse, and Collisions
**HE:** תנע, מתקף והתנגשויות

Momentum $\vec{p}=m\vec{v}$ is conserved when net external force is zero. Impulse $\vec{J}=\vec{F}\Delta t=\Delta\vec{p}$. Elastic collisions conserve both momentum and kinetic energy; inelastic collisions conserve only momentum.

> תנע $\vec{p}=m\vec{v}$ נשמר כאשר הכוח החיצוני הנטו אפס. מתקף $\vec{J}=\vec{F}\Delta t=\Delta\vec{p}$. התנגשויות אלסטיות שומרות תנע ואנרגיה קינטית; לא-אלסטיות שומרות רק תנע.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_newtonian_mechanics|uni_newtonian_mechanics]], [[concepts/uni_work_energy|uni_work_energy]]

## Skill atoms

- Linear momentum p = mv (vector quantity)
- Impulse-momentum theorem J = FΔt = Δp
- Conservation of momentum in isolated systems
- Perfectly inelastic collisions (objects stick together)
- Elastic collisions in 1D (momentum and KE both conserved)
- 1D elastic collision velocity formulas
- Impulse with sign reversal (wall bounce, F-t graph area)
- Recoil and explosion problems
- KE loss fraction in inelastic collisions
- Identifying collision type from problem wording

## Level scope

- **physics1:** Linear momentum, impulse, and 1D collisions at university depth — elastic vs inelastic classification, sign conventions, and explicit KE-loss analysis. Angular momentum appears in uni_rigid_body; here the focus is translational p and J.

## Lesson sections

- **intro:** What Is Momentum?
- **definition:** Momentum, Impulse, and Conservation
- **theory:** Why Momentum Is Conserved: Newton's 3rd Law
- **worked_example:** Worked Example 1 — Perfectly Inelastic Collision
- **checkpoint:** Stop & Practice — Easy
- **worked_example:** Worked Example 2 — Bullet Embedding in Block
- **checkpoint:** Stop & Practice — Medium
- **worked_example:** Worked Example 3 — Elastic Collision Between Equal Masses
- **method_guide:** Step-by-Step Approach for Collision and Impulse Problems
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes with Momentum
- **why_matters:** Why it matters
- **before_exam:** Exam Preparation — Momentum
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/momentum_impulse_collisions|momentum_impulse_collisions]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/momentum.json` _(alias from `uni_momentum`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
