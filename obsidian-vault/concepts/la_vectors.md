---
concept_id: "la_vectors"
name: "Vectors in R^n"
name_he: "וקטורים ב-R^n"
subject: math
level: university
bagrut_chapter: null
points_levels: ["la"]
expansion_status: done
data_completeness: full
lesson_id: "la_vectors"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/la_vectors.json
prerequisites: ["uni_functions_review"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Vectors in R^n

**HE:** וקטורים ב-R^n

## Lesson overview

**Lesson:** Vectors in ℝⁿ — Operations, Dot Product & Orthogonality
**HE:** וקטורים ב-ℝⁿ — פעולות, מכפלה פנימית ואורתוגונליות

Vectors in ℝⁿ, their addition and scalar multiplication, the dot product, Euclidean norm, unit vectors, the Cauchy-Schwarz inequality, and geometric orthogonality.

> וקטורים ב-ℝⁿ, חיבור וכפל בסקלר, מכפלה פנימית, נורמה אוקלידית, וקטורים יחידה, אי-שוויון קושי-שוורץ ואורתוגונליות גיאומטרית.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_functions_review|uni_functions_review]]

## Skill atoms

- Vector in ℝⁿ as n-tuple; component-wise addition and scalar multiplication
- Dot product u·v=Σuᵢvᵢ (result is a scalar)
- Euclidean norm ||u||=√(u·u)
- Unit vector û=u/||u||
- Orthogonality test: u·v=0
- Cauchy–Schwarz inequality |u·v|≤||u|| ||v||
- Triangle inequality via Cauchy–Schwarz
- Angle between vectors: cos θ=(u·v)/(||u|| ||v||)
- Find vectors ⊥ to k given vectors via homogeneous dot-product system
- Projection component comp_v u=(u·v)/||v||

## Level scope

- **la:** Opening linear-algebra chapter; component arithmetic, dot product, and Cauchy–Schwarz proofs appear on every Israeli university LA final.

## Lesson sections

- **intro:** Why Vectors?
- **definition:** Vectors, Addition, and Scalar Multiplication
- **theory:** Key Theorems
- **worked_example:** Worked Example 1 — Computing the Dot Product
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Vectors Orthogonal to Two Given Vectors
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Proof of Cauchy–Schwarz
- **method_guide:** Method Guide — Dot Product Toolkit
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Summary


## Links

- Lesson JSON: `scripts/seed_data/lessons/la_vectors.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
