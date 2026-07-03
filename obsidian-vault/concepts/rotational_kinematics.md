---
concept_id: "rotational_kinematics"
name: "Rotational Kinematics"
name_he: "קינמטיקה סיבובית"
subject: physics
level: high_school
bagrut_chapter: mechanics
points_levels: ["hs_physics"]
expansion_status: done
data_completeness: full
lesson_id: "rotational_kinematics"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/rotational_kinematics.json
prerequisites: ["circular_motion"]
tags:
  - concept/physics
  - status/done
  - completeness/full
---

# Rotational Kinematics

**HE:** קינמטיקה סיבובית

## Lesson overview

**Lesson:** Rotational Kinematics — Angular Motion and Rolling
**HE:** קינמטיקה סיבובית — תנועה זוויתית וגלגול

Rotational kinematics is the exact mirror of linear kinematics: replace x→θ, v→ω, a→α. The four constant-α equations are identical in structure to the constant-a linear equations. The bridge between rotational and linear quantities uses the radius r. Rolling without slipping links ω to the linear velocity of the center.

> קינמטיקה סיבובית היא המראת קינמטיקה לינארית: $x\to\theta$, $v\to\omega$, $a\to\alpha$. ארבע משוואות $\alpha$-קבוע זהות במבנה לארבע משוואות $a$-קבוע. הגשר בין כמויות סיבוביות ולינאריות משתמש ברדיוס $r$. גלגול ללא החלקה מקשר $\omega$ למהירות לינארית של המרכז.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/circular_motion|circular_motion]]

## Skill atoms

- Angular displacement (θ)
- Angular velocity (ω)
- Angular acceleration (α)
- Rotational kinematic equations (analogous to linear)
- Relationship between linear and angular: v=rω, a=rα

## Level scope

- **hs_physics:** Rotational analogues of linear kinematics (θ, ω, α) with v = rω links — tested when combined with rotational dynamics or rolling. Bagrut depth is formula-based conversion, not calculus of rotation.

## Lesson sections

- **intro:** From Linear to Rotational — the Perfect Analogy
- **definition:** Angular Quantities and the Four Kinematic Equations
- **theory:** Connecting Linear and Rotational — Tangential vs Centripetal Acceleration
- **worked_example:** Worked Example 1 — Wheel Spinning from 0 to 120 rpm in 4 s
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Rolling Disk: Center Speed and Contact Point Speed
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Spool Unwinding from Rest: Derive $\omega(t)$
- **method_guide:** Method Guide — Rotational Kinematics Decision Table
- **exercise_set:** Practice Exercises
- **pitfall:** Top Mistakes in Rotational Kinematics
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Formula Sheet & Exam Patterns
- **summary:** Summary — Key Equations


## Links

- Lesson JSON: `scripts/seed_data/lessons/rotational_kinematics.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
