---
concept_id: "uni_integration_techniques"
name: "Integration Techniques"
name_he: "שיטות אינטגרציה"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "integrals_techniques"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/integrals_techniques.json
prerequisites: ["uni_integrals"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Integration Techniques

**HE:** שיטות אינטגרציה

## Lesson overview

**Lesson:** Integration Techniques Overview
**HE:** סקירת שיטות אינטגרציה

Choosing the right integration technique: u-substitution, integration by parts (IBP), partial fractions, and trigonometric substitution. Method guide is the core of this lesson.

> בחירת שיטת האינטגרציה המתאימה: החלפת משתנים (u-sub), אינטגרציה בחלקים (IBP), שברים חלקיים, והצבה טריגונומטרית. מדריך השיטה הוא ליבת השיעור.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_integrals|uni_integrals]]

## Skill atoms

- u-substitution: ∫f(g(x))g'(x)dx=∫f(u)du
- Change u-limits on definite integrals under substitution
- Integration by parts: ∫u dv=uv−∫v du
- LIATE priority for choosing u in IBP
- Repeated/tabular IBP for ∫xⁿeˣ dx and ∫eˣ sin x dx
- Partial fractions for proper rational functions (distinct and repeated factors)
- Polynomial long division before partial fractions when deg P ≥ deg Q
- Trigonometric substitution for √(a²−x²), √(a²+x²), √(x²−a²)
- Choose technique: u-sub vs IBP vs partial fractions vs trig sub
- Combine methods when integrand has nested structure

## Level scope

- **calc1:** Technique-selection chapter; graders award method marks for naming the correct approach before arithmetic.

## Lesson sections

- **intro:** When Basic Rules Are Not Enough
- **definition:** The Four Main Techniques
- **theory:** When to Use Each Technique
- **worked_example:** Worked Example 1 — u-Substitution
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 2 — Integration by Parts
- **checkpoint:** Stop & Practice
- **worked_example:** Worked Example 3 — Trigonometric Substitution (Exam Level)
- **method_guide:** Method Guide — Which Integration Technique?
- **exercise_set:** Practice Exercises
- **pitfall:** Common Pitfalls
- **why_matters:** Why it matters
- **before_exam:** Before the Exam
- **summary:** Take-away

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/integrals_substitution_basic|integrals_substitution_basic]]
- [[concepts/integration_substitution|integration_substitution]]
- [[concepts/integrals_trigonometric|integrals_trigonometric]]
- [[concepts/integration_by_parts|integration_by_parts]]
- [[concepts/integration_partial_fractions|integration_partial_fractions]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/integrals_techniques.json` _(alias from `uni_integration_techniques`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
