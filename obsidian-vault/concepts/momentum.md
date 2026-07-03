---
concept_id: "momentum"
name: "Momentum & Impulse"
name_he: "תנע ומתקף"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "momentum"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/momentum.json
prerequisites: ["newton_laws", "work_energy"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Momentum & Impulse

**HE:** תנע ומתקף

## Lesson overview

**Lesson:** Momentum, Impulse, and Collisions
**HE:** תנע, מתקף והתנגשויות

Momentum $\vec{p}=m\vec{v}$ is conserved when net external force is zero. Impulse $\vec{J}=\vec{F}\Delta t=\Delta\vec{p}$. Elastic collisions conserve both momentum and kinetic energy; inelastic collisions conserve only momentum.

> תנע $\vec{p}=m\vec{v}$ נשמר כאשר הכוח החיצוני הנטו אפס. מתקף $\vec{J}=\vec{F}\Delta t=\Delta\vec{p}$. התנגשויות אלסטיות שומרות תנע ואנרגיה קינטית; לא-אלסטיות שומרות רק תנע.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/newton_laws|newton_laws]], [[concepts/work_energy|work_energy]]

## Skill atoms

- Linear momentum: p = mv
- Impulse: J = F·Δt = Δp
- Newton's 2nd law in terms of momentum
- Conservation of momentum (no external forces)
- Elastic collisions: both KE and p conserved
- Inelastic collisions: only p conserved
- Perfectly inelastic collisions (objects stick together)
- 2D momentum conservation (vector method)
- Explosion problems (recoil)
- Center of mass

## Level scope

- **hs_physics:** Impulse and momentum conservation are tested in mechanics — often linked to collisions or explosions. Questions distinguish elastic vs inelastic outcomes and may require 2D vector momentum components.

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
- [[concepts/uni_momentum|uni_momentum]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/momentum.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
