---
concept_id: "rotational_dynamics"
name: "Rotational Dynamics & Angular Momentum"
name_he: "דינמיקה סיבובית ותנע זוויתי"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "rotational_dynamics"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/rotational_dynamics.json
prerequisites: ["rotational_kinematics", "torque"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Rotational Dynamics & Angular Momentum

**HE:** דינמיקה סיבובית ותנע זוויתי

## Lesson overview

**Lesson:** Rotational Dynamics — Torque, Moment of Inertia, and Angular Momentum
**HE:** דינמיקה סיבובית — מומנט כוח, מומנט התמדה ותנע זוויתי

Rotational dynamics is the rotational analog of Newton's second law: τ = Iα. Torque τ plays the role of force, moment of inertia I plays the role of mass, and angular acceleration α plays the role of linear acceleration. Angular momentum L = Iω is conserved when net torque is zero. Rotational kinetic energy ½Iω² adds to translational KE for rolling objects.

> דינמיקה סיבובית היא האנלוג הסיבובי של חוק שני של ניוטון: $\tau=I\alpha$. מומנט כוח $\tau$ — תפקיד הכוח. מומנט התמדה $I$ — תפקיד המסה. תנע זוויתי $L=I\omega$ מתשמר כשהמומנט הנטו הוא אפס. אנרגיה קינטית סיבובית $\frac{1}{2}I\omega^2$ מתווספת ל-KE תנועתית עבור גופים מתגלגלים.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/rotational_kinematics|rotational_kinematics]], [[concepts/torque|torque]]

## Skill atoms

- Moment of inertia I
- Rotational Newton's 2nd law: τ = Iα
- Rotational kinetic energy: ½Iω²
- Angular momentum: L = Iω
- Conservation of angular momentum
- Rolling without slipping

## Level scope

- **hs_physics:** Moment of inertia, τ = Iα, and angular-momentum conservation — including rolling-without-slipping on inclines. A full rotational-dynamics question is less guaranteed than linear mechanics but common in 5-unit mocks.

## Lesson sections

- **intro:** Why Torque? Beyond F = ma for Rotating Systems
- **definition:** Torque, Moment of Inertia, Angular Momentum, Rotational KE
- **theory:** Work–Energy Theorem for Rotation and Angular Momentum Conservation
- **worked_example:** Worked Example 1 — Disk with Net Torque: Angular Acceleration
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Solid Cylinder Rolling Down a 30° Incline
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Yo-Yo: Derive Acceleration of Center of Mass
- **method_guide:** Method Guide — Rotational Dynamics Decision Table
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes in Rotational Dynamics
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Sheet & Exam Patterns
- **summary:** Summary — Key Equations


## Links

- Lesson JSON: `scripts/seed_data/lessons/rotational_dynamics.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
