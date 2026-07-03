---
concept_id: "la_orthogonality"
name: "Orthogonality & Least Squares"
name_he: "ישרות וריבועים פחותים"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_orthogonality"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_orthogonality.json
prerequisites: ["la_vector_spaces", "la_eigenvalues"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Orthogonality & Least Squares

**HE:** ישרות וריבועים פחותים

## Lesson overview

**Lesson:** Orthogonality in Inner Product Spaces
**HE:** אורתוגונליות במרחבי מכפלה פנימית

Inner products, orthogonality, orthogonal complement, Gram-Schmidt process, orthogonal projection, and QR decomposition.

> מכפלות פנימיות, אורתוגונליות, משלים אורתוגונלי, תהליך גרם-שמידט, הטלה אורתוגונלית ופירוק QR.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/la_vector_spaces|la_vector_spaces]], [[concepts/la_eigenvalues|la_eigenvalues]]

## Skill atoms

- Standard inner product ⟨u,v⟩=uᵀv in ℝⁿ
- Orthogonality ⟨u,v⟩=0 and norm ||v||=√⟨v,v⟩
- Orthonormal set; QᵀQ=I when Q has ON columns
- Orthogonal complement W⊥ and dim W+dim W⊥=n
- Projection onto a line: proj_a b=(⟨b,a⟩/||a||²)a
- Gram–Schmidt: subtract projections then normalize (never normalize first)
- Projection onto subspace with ONB: Σ⟨b,qⱼ⟩qⱼ
- QR decomposition A=QR via Gram–Schmidt
- Least-squares solution as orthogonal projection onto Col(A)
- Verify residual b−proj is orthogonal to subspace

## Level scope

- **la:** Inner products through least squares; Gram–Schmidt, projection formulas, and QR are high-frequency computation and proof topics.

## Lesson sections

- **intro:** Dot Product and Orthogonality
- **definition:** Inner Product, Orthogonality, Orthogonal Complement
- **theory:** Gram-Schmidt Process
- **worked_example:** Worked Example 1 — Orthogonal Projection onto a Line
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Gram-Schmidt
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Projection onto a Subspace
- **method_guide:** Method Guide — Orthogonality
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/inner_product_gram_schmidt|inner_product_gram_schmidt]]
- [[concepts/orthogonal_matrices|orthogonal_matrices]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/la_orthogonality.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
