---
concept_id: "kinematics_2d"
name: "Kinematics in 2D"
name_he: "קינמטיקה בשני ממדים"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "kinematics_2d"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/kinematics_2d.json
prerequisites: ["kinematics_1d", "vectors_basics"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Kinematics in 2D

**HE:** קינמטיקה בשני ממדים

## Lesson overview

**Lesson:** Projectile Motion (2D Kinematics)
**HE:** תנועת קליע (קינמטיקה דו-ממדית)

Projectile motion decomposes into independent x (constant velocity) and y (free fall) components. Key quantities are range, maximum height, and time of flight.

> תנועת קליע מתפרקת לרכיב x עצמאי (מהירות קבועה) ורכיב y (נפילה חופשית). גדלים מרכזיים: טווח, גובה מרבי, וזמן טיסה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/kinematics_1d|kinematics_1d]], [[concepts/vectors_basics|vectors_basics]]

## Skill atoms

- Decompose v₀ into v₀x = v₀cosθ and v₀y = v₀sinθ
- Independent x (constant v) and y (free fall) kinematics
- Horizontal launch from height: time from vertical free fall
- Maximum height H = v₀y²/(2g) at apex (v_y = 0)
- Time of flight T = 2v₀y/g for symmetric ground launch
- Range R = v₀²sin2θ/g from level ground
- Landing speed v = √(v_x² + v_y²) from components
- Relative velocity vector addition (e.g., boat in current)

## Level scope

- **hs_physics:** Bagrut mechanics expects independent x/y motion analysis and relative-velocity setups (e.g., boats, aircraft). Questions combine vector components with 1D kinematic equations rather than calculus.

## Lesson sections

- **intro:** From 1D to 2D — Projectile Motion
- **definition:** Projectile Motion Equations
- **theory:** Parabola, Symmetry, and Optimal Angle
- **worked_example:** Worked Example 1 — Horizontal Launch from a Cliff
- **checkpoint:** Stop & Practice — Easy
- **worked_example:** Worked Example 2 — Angled Launch
- **checkpoint:** Stop & Practice — Medium
- **worked_example:** Worked Example 3 — Goalkeeper's Kick to Score
- **method_guide:** Step-by-Step Approach for Projectile Problems
- **exercise_set:** Practice Exercises
- **pitfall:** Common Mistakes in Projectile Motion
- **why_matters:** Why it matters
- **before_exam:** Exam Preparation — Projectile Motion
- **summary:** Summary — Key Equations

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/vectors_kinematics_2d_3d|vectors_kinematics_2d_3d]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/kinematics_2d.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
