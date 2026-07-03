---
concept_id: "uni_applications_integrals"
name: "Applications of Integrals"
name_he: "יישומי אינטגרלים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "integrals_applications"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/integrals_applications.json
prerequisites: ["uni_integration_techniques"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Applications of Integrals

**HE:** יישומי אינטגרלים

## Lesson overview

**Lesson:** Applications of Integration
**HE:** יישומי אינטגרציה

Applications of the definite integral: area between curves, volume of revolution by disk, washer, and shell methods.

> יישומי האינטגרל המסויים: שטח בין עקומות, נפח סביבת ציר בשיטות דיסק, מכבסה וקליפה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_integration_techniques|uni_integration_techniques]]

## Skill atoms

- Area between curves: ∫(top−bottom)dx on [a,b]
- Find intersection points as integration limits; split when curves cross
- Area with horizontal slices: integrate with respect to y
- Disk method: V=π∫[f(x)]² dx (rotation about x-axis)
- Washer method: V=π∫(R²−r²)dx (outer minus inner radius squared)
- Shell method: V=2π∫x·h(x)dx (rotation about y-axis)
- Choose disk/washer vs shell by axis of rotation vs integration variable
- Rotation about shifted axis y=k or x=k (radius as distance to axis)
- Set up integral from sketch with labeled intersections and radii
- Net signed area vs total area between curves

## Level scope

- **calc1:** Geometry-heavy calc-1 applications; sketch-first workflow with intersection finding and method naming before antiderivatives.

## Lesson sections

- **intro:** What Can Integration Measure?
- **definition:** Area and Volume Formulas
- **theory:** Finding Intersection Points and Choosing Method
- **worked_example:** Worked Example 1 — Area Between Curves
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Volume by Disk Method
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Shell Method and Washer Comparison (Exam Level)
- **method_guide:** Method Guide — Applications of Integration
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/integrals_polynomial_rational|integrals_polynomial_rational]]
- [[concepts/areas_between_curves|areas_between_curves]]
- [[concepts/volumes_of_revolution_basic|volumes_of_revolution_basic]]
- [[concepts/volumes_of_revolution|volumes_of_revolution]]
- [[concepts/double_integrals|double_integrals]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/integrals_applications.json` _(alias from `uni_applications_integrals`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
