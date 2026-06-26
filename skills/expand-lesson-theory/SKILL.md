---
name: expand-lesson-theory
description: How any agent (Tutor, Curriculum Designer, Content Curator, Research) can deepen the THEORETICAL content of an authored lesson — more worked examples, more intuition, more cross-subject links — without breaking the schema. Read BEFORE adding sections, examples, derivations, or `why_matters` content to scripts/seed_data/lessons/<concept_id>.json. Pair with `skills/author-lesson/SKILL.md` (full schema) and `skills/author-question-bank/SKILL.md` (questions).
---

# Expand Lesson Theory

## When to use

- A lesson's `sections` are skeletal — only one worked example, no pitfall discussion, no cross-subject link.
- A learner repeatedly asks "but WHY?" questions on a concept that the lesson doesn't answer — the theoretical surface is too narrow.
- The Q&A Explainer keeps falling back to generic knowledge because the authored lesson has no cited material for the question.
- A new cross-subject edge has been added to `kg-cross-edges.json` (e.g. `derivatives_intro → kinematics_1d`) — the source lesson should explicitly mention the application.

## What lives where

```
scripts/seed_data/lessons/<concept_id>.json
        │  → .sections[]    (the theoretical body — what this skill expands)
        │  → .agent_hints   (the runtime grounding — touched only carefully)
```

Re-seeding REPLACES the whole `sections[]` array. Always re-author the full
array; the seeder is not partial-merge.

## The 5 canonical section kinds (additive — you may add more of each)

| Kind             | Purpose                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| `intro`          | One-paragraph hook — concrete situation, not a definition.                                       |
| `definitions`    | 1–4 core terms, each with a precise definition + 1 example.                                      |
| `worked_example` | A single, fully solved problem with each MOVE named (the *thinking*, not just the answer).      |
| `pitfalls`       | 2–4 most common mistakes from the literature, each with a 1-line fix.                            |
| `why_matters`    | Connection to other concepts (`concept:<id>` refs), real-world impact, cross-subject links.      |

To deepen theory, you usually add MORE of: `worked_example` (different difficulty / different solution path), `definitions` (covering an edge case), `pitfalls` (a less-common but high-impact one), and `why_matters` (a new cross-subject link).

## Section shape

```json
{
  "id": "worked_2",
  "kind": "worked_example",
  "title_en": "Worked example: SAS with a missing angle",
  "title_he": "דוגמה פתורה: צ.ז.צ. עם זווית חסרה",
  "body_en": "Markdown with $math$ allowed; use ### subheaders inside if needed.",
  "body_he": "אותו טקסט בעברית מלא, עם $math$."
}
```

- `id` is unique within the file. Use a stable scheme: `worked_2`, `worked_3`, `pitfall_late`, `why_phys`.
- Both `body_en` AND `body_he` are required. A single-language section is a regression — the UI exposes the gap immediately.
- Markdown body: KaTeX in `$...$` / `$$...$$` only. Use `### Subheader` inside the body for internal structure; never use `# H1` (the section title becomes the H2).

## Expansion patterns (recipes)

### Add a second worked example at a higher difficulty

```json
{ "id": "worked_2", "kind": "worked_example",
  "title_en": "Worked example: combining SAS with the law of cosines",
  "title_he": "דוגמה פתורה: שילוב צ.ז.צ. עם משפט הקוסינוסים",
  "body_en": "Given $a=7$, $b=10$, $\\angle C = 35°$, find side $c$ and prove the triangle is unique.\n\n### Move 1: identify the test\nThe pair (a,b) + included angle (C) is exactly the SAS pattern, so this triangle is uniquely determined.\n\n### Move 2: apply law of cosines\n$$c^2 = a^2 + b^2 - 2ab\\cos C$$\nSubstituting: $c^2 = 49 + 100 - 140\\cos(35°) \\approx 34.3$, so $c \\approx 5.86$.\n\n### Move 3: state uniqueness\nBecause SAS, no SSA ambiguity arises — there is exactly one such triangle.",
  "body_he": "נתון $a=7$, $b=10$, $\\angle C = 35°$, מצאו את הצלע $c$ והוכיחו שהמשולש יחיד.\n\n### צעד 1: זיהוי המבחן\n[…]" }
```

Patterns that work well:
- Name each move with a `### Move N:` header. This is what learners and the Coach later reference.
- Show the formula, then the substitution, then the answer. Not just the answer.
- End with a 1-line meta-comment about WHICH solution path you chose and WHY (e.g. "we used law of cosines, not law of sines, because we had two sides + the included angle").

### Add a `pitfalls` section that catches a real, observed misconception

Cross-reference `agent_hints.common_misconceptions[]` so the body text matches the trigger the runtime is already watching for:

```json
{ "id": "pitfall_aaa", "kind": "pitfalls",
  "title_en": "Pitfall: 'AAA proves congruence'",
  "title_he": "מלכודת: ‹זווית-זווית-זווית מוכיח חפיפה›",
  "body_en": "**The mistake.** Students often say: 'All three angles equal → triangles are congruent.'\n\n**Why it's wrong.** AAA only fixes the *shape* (similar), not the *size*. A 30-60-90 triangle with sides 1-√3-2 has the same angles as one with sides 10-10√3-20 — same shape, different sizes.\n\n**The fix.** Whenever you see only angles, write 'similar', not 'congruent'. Congruence requires at least ONE side measurement (SSS, SAS, ASA, AAS).",
  "body_he": "**הטעות.** […]" }
```

### Add a `why_matters` section that builds a cross-subject bridge

Whenever a new `kg-cross-edges.json` edge is added, the SOURCE lesson should grow a `why_matters` section that names the application:

```json
{ "id": "why_phys", "kind": "why_matters",
  "title_en": "Why it matters: physics applications",
  "title_he": "למה זה חשוב: שימושים בפיזיקה",
  "body_en": "Triangle congruence shows up everywhere force diagrams need symmetric assumptions:\n- **Static equilibrium** (`concept:newton_laws`): when two ropes hang at equal angles from a horizontal beam, the SAS test tells you the tensions are equal *before* you write any equations.\n- **Optics, reflection** (`concept:optics_basics`): the law of reflection produces two congruent triangles around the normal; congruence is what guarantees image symmetry.\n\nThe pattern is: whenever you spot a geometric symmetry in a physical setup, congruence is doing the work.",
  "body_he": "[…]" }
```

## Don't touch `agent_hints` from this skill

`agent_hints` (key insights, common_misconceptions, tutor_pacing_hint, diagnostic_signals, skill_atoms_unlocked) is the AGENT-RUNTIME contract. It's owned by `skills/author-lesson/SKILL.md`. If you genuinely need a new agent_hint while expanding theory:

1. Add it via the lesson-authoring skill, in the same PR.
2. Make sure at least one question in the bank `exercises` the new `skill_atoms_unlocked` atom (`skills/author-question-bank/SKILL.md`).

## Re-seed + verify

```bash
gh workflow run "Seed DB (one-shot)" -f target=lessons
# or locally:
DATABASE_URL=... node scripts/seed-lessons.mjs --only=<concept_id>
node scripts/audit-lessons.mjs
```

Then live-probe `/learn/<subject>/<concept_id>` in HE and EN; toggle the language and confirm both sections render with full body content (no half-empty bilingual gaps).

## Pitfalls

- ❌ Pasting a Wikipedia paragraph as `body_en` and Google-translating it to `body_he`. The platform's whole identity is "we author our own bilingual content"; mechanical translations break that.
- ❌ Authoring an English-only section because the Hebrew "will come later". The UI defaults to HE; learners will see the gap on first contact.
- ❌ Putting questions inside section bodies. Questions live in `questions[]`, not in `sections[].body_*`. The QuizPanel won't render them inline; you'll just produce dead text.
- ❌ Letting a section exceed ~400 words. Long sections are skim-killers. Split into two with distinct `id`s and a clear `### subheader` ladder.
- ❌ Forgetting to add a `why_matters` link after introducing a new `kg-cross-edges.json` edge. The planner will route through the edge but the lesson body will silently lack the bridge.

## Suggested authoring prompts (for AI assistants)

> "Read scripts/seed_data/lessons/<concept_id>.json. List its current sections by id+kind. Propose 2 ADDITIONAL sections (worked_example at a higher difficulty + why_matters connecting to <related concept>), in the exact JSON shape of the existing entries, bilingual EN+HE, with KaTeX math in $...$. Do not modify existing sections."

> "For the concept <concept_id>, add a pitfalls section that explicitly addresses the misconception 'X' (already listed in agent_hints.common_misconceptions). Cite the corresponding fix from the agent_hints entry."
