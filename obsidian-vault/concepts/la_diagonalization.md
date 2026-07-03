---
concept_id: "la_diagonalization"
name: "Matrix Diagonalization"
name_he: "אלכסון מטריצות"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_diagonalization"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_diagonalization.json
prerequisites: ["la_eigenvalues"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Matrix Diagonalization

**HE:** אלכסון מטריצות

## Lesson overview

**Lesson:** Diagonalization — When Is a Matrix Diagonalizable?
**HE:** אלכסון — מתי מטריצה ניתנת לאלכסון?

The diagonalization criterion (g.m.=a.m. for every eigenvalue), the decomposition A=PDP⁻¹, computing A^n efficiently, and characterisation of 2×2 matrices that cannot be diagonalised over ℝ.

> קריטריון האלכסוניות (ר"ג=ר"א לכל ע"ע), הפירוק $A=PDP^{-1}$, חישוב $A^n$ ביעילות, ואפיון מטריצות $2\times2$ שאינן ניתנות לאלכסון מעל $\mathbb{R}$.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_eigenvalues|la_eigenvalues]]

## Skill atoms

- Diagonalizable criterion: geometric multiplicity equals algebraic multiplicity for every λ
- Defective matrix when g.m.<a.m. (Jordan block intuition)
- Find eigenvalues and linearly independent eigenvectors
- Construct P (eigenvector columns) and D with A=PDP⁻¹
- Compute Aⁿ efficiently via Dⁿ
- Already-diagonal matrix is trivially diagonalizable
- Rotation matrix may have no real eigenvalues (not diagonalizable over ℝ)
- If A=PDP⁻¹ invertible then A⁻¹=PD⁻¹P⁻¹
- Verify diagonalization: check AP=PD
- Use diagonalization to evaluate matrix powers and recurrences

## Level scope

- **la:** Diagonalization criterion and A=PDP⁻¹ construction; computing Aⁿ and deciding non-diagonalizability are standard final-exam capstone problems.

## Lesson sections

- **intro:** Why Diagonalize?
- **definition:** Diagonalizability
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Trivial Diagonalization
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Diagonalize A and Compute A⁵
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Characterise Non-Diagonalizable 2×2 Matrices over ℝ
- **method_guide:** Method Guide — Diagonalization Procedure
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/la_diagonalization.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
