---
concept_id: "limits"
name: "Limits"
name_he: "גבולות"
subject: math
level: high_school
bagrut_chapter: calculus
points_levels: ["5pt"]
expansion_status: done
data_completeness: full
lesson_id: "limits"
lesson_aliased: false
lesson_json: scripts/seed_data/lessons/limits.json
prerequisites: ["functions_quadratic", "trigonometry_identities", "sequences_geometric"]
tags:
  - concept/math
  - status/done
  - completeness/full
---

# Limits

**HE:** גבולות

## Lesson overview

**Lesson:** Limits — Algebraic Techniques
**HE:** גבולות — טכניקות אלגבריות

Master the five core techniques for evaluating limits: direct substitution, factoring and canceling (the 0/0 case), the conjugate method, standard limit identities, and L'Hôpital's rule. Built in the Goren/Geva style with full worked examples, checkpoints, and an exam-prep summary.

> שליטה בחמש הטכניקות המרכזיות לחישוב גבולות: הצבה ישירה, פירוק וצמצום (מקרה 0/0), שיטת הצמוד, גבולות סטנדרטיים, וכלל לופיטל. בנוי בסגנון גורן/גבע עם דוגמאות פתורות מלאות, עצרות ותרגול, ומדריך לפני הבחינה.

_14 sections · 8 questions in authored JSON._


## Prerequisites

[[concepts/functions_quadratic|functions_quadratic]], [[concepts/trigonometry_identities|trigonometry_identities]], [[concepts/sequences_geometric|sequences_geometric]]

## Skill atoms

- Intuitive concept of limit
- Left and right limits
- Limits at infinity (horizontal asymptotes)
- lim sin(x)/x = 1 as x→0
- Limit of rational function (factoring and canceling)
- Indeterminate forms
- Vertical asymptotes from limits

## Level scope

- **5pt:** Conceptual introduction in Bagrut; rigorous ε-δ NOT required; used for asymptotes

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
- [[concepts/uni_limits|uni_limits]]

## Links

- Lesson JSON: `scripts/seed_data/lessons/limits.json`
- Aliases: `apps/web/src/lib/concept-aliases.ts`
- Research: [[research/README|Research index]]
- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]
- Depth guide: `docs/bagrut-math-depth.md` (repo)

## Expansion notes

<!-- Queue reasons, Hebrew parity issues, draft links -->

## QA feedback

<!-- Links to .cursor/qa-loop reports -->
