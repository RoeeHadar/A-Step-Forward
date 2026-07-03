---
concept_id: "collisions"
name: "Collisions"
name_he: "התנגשויות"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "collisions"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/collisions.json
prerequisites: ["momentum"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Collisions

**HE:** התנגשויות

## Lesson overview

**Lesson:** Collisions — Elastic, Inelastic, and 2D
**HE:** התנגשויות — אלסטיות, לא-אלסטיות ודו-ממדיות

Momentum is always conserved in collisions (no external forces). Kinetic energy is also conserved in perfectly elastic collisions but not in inelastic ones. In perfectly inelastic collisions the objects stick together. In 2D, momentum conservation applies independently to each component. The center-of-mass frame simplifies elastic collision analysis.

> תנע תמיד מתשמר בהתנגשויות (ללא כוחות חיצוניים). אנרגיה קינטית מתשמרת גם ב**התנגשות אלסטית** לגמרי, אך לא בלא-אלסטית. בהתנגשות לא-אלסטית מוחלטת הגופים נדבקים. ב-2D, שימור התנע חל על כל רכיב בנפרד.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/momentum|momentum]]

## Skill atoms

- Elastic collision equations: head-on
- Special case: equal masses
- Coefficient of restitution
- Ballistic pendulum
- 2D collision problems

## Level scope

- **hs_physics:** Focused collision problems — head-on elastic/inelastic, coefficient of restitution, and ballistic-pendulum setups. Bagrut items usually give masses and initial speeds and ask for post-collision velocities or maximum swing height.

## Lesson sections

- **intro:** Why Collisions? Momentum as the Universal Currency
- **definition:** Conservation Laws for Collisions
- **theory:** Center-of-Mass Frame and Coefficient of Restitution
- **worked_example:** Worked Example 1 — Perfectly Inelastic Collision: Final Velocity and Energy Lost
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Elastic 1D Collision: Equal Masses Exchange Velocities
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — 2D Collision: Find Velocity and Angle of the Second Ball
- **method_guide:** Method Guide — Collision Problem Decision Table
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes in Collision Problems
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Sheet & Exam Patterns
- **summary:** Summary — Key Equations


## Links

- Lesson JSON: `scripts/seed_data/lessons/collisions.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
