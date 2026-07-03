---
concept_id: "la_determinants"
name: "Determinants"
name_he: "דטרמיננטות"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_determinants"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_determinants.json
prerequisites: ["la_matrices"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Determinants

**HE:** דטרמיננטות

## Lesson overview

**Lesson:** Determinants — Definition, Properties & Cramer's Rule
**HE:** דטרמיננטות — הגדרה, תכונות וכלל קרמר

The determinant as a signed volume, cofactor expansion, key multiplicative properties (det(AB)=det(A)det(B)), effect of row operations, Cramer's rule, and adjugate formula for the inverse.

> הדטרמיננטה כנפח מכוון, פיתוח לפי מינורים, תכונות כפליות ($\det(AB)=\det A\cdot\det B$), השפעת פעולות שורה, כלל קרמר ונוסחת ההופכי באמצעות הנלווה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_matrices|la_matrices]]

## Skill atoms

- 2×2 determinant ad−bc and signed-area interpretation
- Cofactor (Laplace) expansion along a row or column
- 3×3 determinant with (−1)ⁱ⁺ʲ sign checkerboard
- Row-operation effects: swap flips sign, scale multiplies, add unchanged
- Multiplicativity det(AB)=det(A)det(B)
- Invertibility criterion det(A)≠0
- Scaling law det(cA)=cⁿdet(A) for n×n
- det(A⁻¹)=1/det(A) proof via AA⁻¹=I
- Triangular matrix: det equals product of diagonal entries
- Cramer's rule xᵢ=det(Aᵢ)/det(A) for small systems

## Level scope

- **la:** Determinant properties and computation; cofactor expansion and row-operation shortcuts tested alongside invertibility and Cramer's rule on 2×2/3×3 systems.

## Lesson sections

- **intro:** Why Determinants?
- **definition:** Determinant via Cofactor Expansion
- **theory:** Key Properties
- **worked_example:** Worked Example 1 — 2×2 Determinant
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — 3×3 Determinant by Cofactor Expansion
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Proof: $\det(A^{-1}) = 1/\det(A)$
- **method_guide:** Method Guide — Determinant Toolkit
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/determinants_cramer|determinants_cramer]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/la_determinants.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
