---
concept_id: "la_matrices"
name: "Matrices & Linear Systems"
name_he: "מטריצות ומערכות לינאריות"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_matrices"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_matrices.json
prerequisites: ["la_vectors"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Matrices & Linear Systems

**HE:** מטריצות ומערכות לינאריות

## Lesson overview

**Lesson:** Matrix Operations — Addition, Multiplication, Transpose & Inverse
**HE:** פעולות על מטריצות — חיבור, כפל, טרנספוז והופכי

Matrix addition, scalar multiplication, matrix multiplication (non-commutativity), the transpose and its algebraic laws, the identity matrix, and the concept of invertibility.

> חיבור מטריצות, כפל בסקלר, כפל מטריצות (אי-קומוטטיביות), טרנספוז וחוקיו, מטריצת היחידה ומושג ההופכי.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_vectors|la_vectors]]

## Skill atoms

- Matrix addition and scalar multiplication (matching dimensions)
- Matrix multiplication dimension check: m×k times k×n
- Entry cᵢⱼ as row i · column j dot product
- Non-commutativity AB≠BA (explicit counterexample)
- Associativity (AB)C=A(BC)
- Transpose laws including (AB)ᵀ=BᵀAᵀ
- Identity matrix Iₙ and AI=IA=A
- 2×2 inverse formula via determinant ad−bc
- Verify candidate inverse by checking AB=I
- Inverse product law (AB)⁻¹=B⁻¹A⁻¹
- Augmented matrix [A|b] for linear systems Ax=b
- Elementary row operations (swap, scale, add multiple)
- Row echelon form and RREF via Gaussian elimination
- Classify unique, infinite, or inconsistent solutions from RREF
- Free variables and parametric solution families

## Level scope

- **la:** Matrix arithmetic plus Gaussian elimination on augmented systems; RREF classification and parametric solutions are tested alongside 2×2 inversion.

## Lesson sections

- **intro:** Why Matrices?
- **definition:** Matrices and Basic Operations
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Multiplying a 2×3 by a 3×2 Matrix
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Counterexample to Commutativity
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Proof: $(AB)^T = B^T A^T$
- **method_guide:** Method Guide — Matrix Operations Checklist
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/linear_systems_gaussian_elimination|linear_systems_gaussian_elimination]]
- [[concepts/matrix_operations_inverse|matrix_operations_inverse]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/la_matrices.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
