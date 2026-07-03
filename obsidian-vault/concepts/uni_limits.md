---
concept_id: "uni_limits"
name: "Limits & Continuity"
name_he: "גבולות ורציפות"
subject: math
level: university
bagrut_chapter: null
points_levels: ["calc1"]
expansion_status: todo
data_completeness: full
lesson_id: "limits"
lesson_aliased: true
lesson_json: scripts/seed_data/lessons/limits.json
prerequisites: ["uni_functions_review"]
tags:
  - concept/math
  - status/todo
  - completeness/full
---

# Limits & Continuity

**HE:** גבולות ורציפות

## Lesson overview

**Lesson:** Limits — Algebraic Techniques
**HE:** גבולות — טכניקות אלגבריות

Master the five core techniques for evaluating limits: direct substitution, factoring and canceling (the 0/0 case), the conjugate method, standard limit identities, and L'Hôpital's rule. Built in the Goren/Geva style with full worked examples, checkpoints, and an exam-prep summary.

> שליטה בחמש הטכניקות המרכזיות לחישוב גבולות: הצבה ישירה, פירוק וצמצום (מקרה 0/0), שיטת הצמוד, גבולות סטנדרטיים, וכלל לופיטל. בנוי בסגנון גורן/גבע עם דוגמאות פתורות מלאות, עצרות ותרגול, ומדריך לפני הבחינה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/uni_functions_review|uni_functions_review]]

## Skill atoms

- Informal and ε–δ limit definition
- One-sided limits and two-sided limit existence
- Direct substitution when function is continuous at a
- Factor and cancel for polynomial 0/0 limits
- Conjugate rationalization for surd 0/0 limits
- Standard limits: sin x/x, (eˣ−1)/x, ln(1+x)/x
- L'Hôpital's rule for 0/0 and ∞/∞ (differentiate numerator and denominator separately)
- Limit DNE: mismatched one-sided limits or oscillation
- Continuity criterion: lim f(x)=f(a)
- Limits at infinity and horizontal asymptotes

## Level scope

- **calc1:** First calc-1 chapter; exam items reward fast technique selection (substitute → factor → conjugate → standard limits → L'Hôpital) and one-sided limit checks.

## Lesson sections

- **intro:** Why Limits Matter
- **definition:** Definition — What is a Limit?
- **theory:** Theory — The Five Techniques
- **worked_example:** Worked Example 1 — Direct Substitution and Factoring
- **checkpoint:** Stop & Practice ✋
- **worked_example:** Worked Example 2 — The Conjugate Technique
- **checkpoint:** Stop & Practice ✋
- **worked_example:** Worked Example 3 — L'Hôpital + Composition (Two Methods)
- **method_guide:** Method Guide — How to Choose the Right Technique
- **exercise_set:** Exercise Set
- **pitfall:** Top 5 Mistakes — Don't Fall for These!
- **why_matters:** Why it matters
- **before_exam:** Before the Exam — Cheat Sheet
- **summary:** Summary — Limits

## Related KG concepts (same lesson)

_These syllabus concepts alias to the same authored lesson JSON._

- [[concepts/limits_intro|limits_intro]]
- [[concepts/limits_epsilon_delta|limits_epsilon_delta]]
- [[concepts/multivariable_limits|multivariable_limits]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/limits.json` _(alias from `uni_limits`)_
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
