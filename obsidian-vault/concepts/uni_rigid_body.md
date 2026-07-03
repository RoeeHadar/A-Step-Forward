---
concept_id: "uni_rigid_body"
name: "Rigid Body Dynamics"
name_he: "דינמיקת גוף קשיח"
subject: physics
level: university
bagrut_chapter: null
points_levels: ["physics1"]
expansion_status: todo
data_completeness: full
lesson_id: "rigid_body_dynamics"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/rigid_body_dynamics.json
prerequisites: ["uni_momentum", "uni_vectors"]
tags:
  - concept/physics
  - status/todo
  - completeness/full
---

# Rigid Body Dynamics

**HE:** דינמיקת גוף קשיח

## Lesson overview

**Lesson:** Rigid Body Dynamics — Rotation and Rolling
**HE:** דינמיקת גוף נוקשה — סיבוב וגלגול

Real objects have shape, size, and mass distributed through their volume. Rigid body dynamics extends Newton's laws to rotation: moment of inertia replaces mass, torque replaces force, and rolling combines translation with spin.

> לגופים אמיתיים יש צורה, ממדים ומסה המפוזרת בנפח. דינמיקת גוף נוקשה מרחיבה את חוקי ניוטון לסיבוב: מומנט אינרציה מחליף מסה, מומנט סיבוב מחליף כוח, וגלגול משלב תנועה לינארית עם סיבוב.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_momentum|uni_momentum]], [[concepts/uni_vectors|uni_vectors]]

## Skill atoms

- Torque τ = r × F and direction via right-hand rule
- Moment of inertia I for standard shapes (disk, sphere, rod, hoop)
- Newton's 2nd law for rotation τ_net = Iα
- Parallel axis theorem I = I_cm + Md²
- Rolling without slipping condition v = Rω
- Total KE of rolling body (translational + rotational)
- I/(MR²) ratio and ramp-race comparisons
- Combined F = ma and τ = Iα for rolling systems
- Angular momentum L = Iω and conservation with no external torque
- Tabulated I values and when to apply parallel-axis shift

## Level scope

- **physics1:** Rotational dynamics at Physics 1 depth — τ = Iα, standard I formulas, parallel-axis theorem, rolling energy splits, and ramp-race ranking via I/(MR²). Expect simultaneous translation + rotation analysis, not just memorized I tables.

## Lesson sections

- **intro:** Beyond Point Masses
- **definition:** Key Quantities and Formulas
- **theory:** Rolling Without Slipping and Energy
- **worked_example:** Worked Example 1 — Angular Acceleration
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Rolling Down a Ramp
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Atwood Machine with Pulley
- **method_guide:** Method Guide
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Card
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/rigid_body_dynamics.json` _(alias from `uni_rigid_body`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
