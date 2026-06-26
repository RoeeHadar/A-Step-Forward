---
name: author-question-bank
description: How any agent (Assessment Generator, Tutor, Coach, Content Curator) can add MORE practice questions to an existing authored lesson without breaking the schema. Read BEFORE generating questions in bulk for a concept, building a drill set, or proposing a question PR. Pair with `skills/author-lesson/SKILL.md` for the full lesson shape.
---

# Author Question Bank

## When to use

- The current question count for a concept is too low to support sustained practice (we target ≥ 12 questions per authored lesson, with ≥ 1 question per `skill_atom` the lesson teaches).
- The existing questions skew toward the easy end or one kind (e.g. mostly `mcq`) — the bank lacks Bloom or kind diversity.
- A learner consistently scores ≥ 80% on the current set: the planner has run out of useful signal.
- An agent (Coach, Assessment Generator) wants to generate a fresh drill on-the-fly for the live tutor flow.

This skill is the **authored-question** counterpart to `assessment_generator`'s synthesised exercises. Authored questions are persisted, peer-reviewed, and become part of the canonical corpus; synthesised ones are ephemeral.

## Coverage targets (per lesson)

| Dimension      | Target                                                                                |
| -------------- | ------------------------------------------------------------------------------------- |
| **Volume**     | ≥ 12 questions total per authored lesson (current minimum: 8; pilot lessons have 12). |
| **Atom coverage** | ≥ 1 question per `agent_hints.skill_atoms_unlocked[]` atom, so the planner can observe per-atom mastery. |
| **Kind mix**   | At least 4 distinct kinds. Aim for: 2× `mcq` or `mcq_multi`, 1× `true_false`, 1× `short_answer` or `numeric`, 1× `match` or `ordering`, 1× `derivation` or `open`. |
| **Difficulty** | Bloom-ish 1..5; ≥ 2 questions at each of {1–2, 3, 4–5}. Avoid all-3s. |
| **Bilingual**  | Every question MUST have `stem_en`, `stem_he`, `explanation_en`, `explanation_he`, and the language-specific `answer_payload` fields where applicable. |

## Where the bank lives

```
scripts/seed_data/lessons/<concept_id>.json
        │  → .questions[]  (the bank for ONE authored lesson)
scripts/seed-lessons.mjs        (validator + idempotent upserter; rejects bad kinds)
apps/web/src/components/lesson-quiz-panel.tsx   (renderer per kind)
apps/web/src/lib/neon-db.ts:gradeLessonAnswer   (server-side grader per kind)
apps/web/src/app/api/lesson/answer/route.ts     (records answer + updates skill_practice)
```

Answers are NOT persisted to a per-(learner, question) table; instead `recordLessonAnswer()` inserts a `quiz_responses` row + upserts `concept_mastery` and `skill_practice` for the affected concept / atoms. The planner reads from those rollups, so re-seeding a question never breaks a historical answer (the rollup persists).

Re-seeding replaces the whole question set for a lesson. So always re-author the whole `questions[]` array; never partial-merge.

## Question shape — common fields

```json
{
  "id": "q7",
  "kind": "mcq",
  "difficulty": 3,
  "skill_atoms": ["area_scale_factor"],
  "stem_en": "...",
  "stem_he": "...",
  "answer_payload": { /* per-kind shape */ },
  "explanation_en": "...",
  "explanation_he": "..."
}
```

The 10 supported `kind` values, per-kind `answer_payload` shapes, and rendering / grading rules are documented exhaustively in `skills/author-lesson/SKILL.md` — read that file before writing new questions.

## Author-mode workflow (any agent)

1. **Read the lesson JSON** at `scripts/seed_data/lessons/<concept_id>.json`. Note the existing question kinds, difficulty distribution, and skill atoms covered.
2. **Identify the gap.** Run `node scripts/audit-lessons.mjs` for a current snapshot of kind / difficulty / atom coverage. Pick what's missing.
3. **Generate N new questions** following the per-kind schema. Maintain:
   - Same `concept_id` (implied by file location).
   - Mix of kinds + difficulties to close the coverage gap.
   - At least one new question per under-served `skill_atom`.
   - Both languages, fully grammatical (not a dollar-store machine translation).
4. **Append to `questions[]`**, keep ids unique within the file (`q1`, `q2`, ...). Do not rewrite existing questions — only add.
5. **Validate**: `node scripts/seed-lessons.mjs --dry-run --only=<concept_id>`. Fix any schema errors before opening the PR.
6. **Audit**: `node scripts/audit-lessons.mjs` again. Coverage should improve, not regress.
7. **PR**: `content(curriculum): +N questions for <concept_id> (kind: <kinds>, atoms: <atoms>)`. Body should paste the before/after audit deltas.

## Live-mode workflow (Coach / Assessment Generator)

For ephemeral drills inside a chat session (not persisted to `lessons`):

1. Get the learner's weak atoms from `learning_plan.next(goal).blocking_atoms`.
2. Pick atom A with lowest mastery.
3. Generate one question whose `skill_atoms = [A]` at difficulty matching the learner's current band (start at the median of their successful difficulty for related atoms ± 1).
4. Render via `lesson-quiz-panel.tsx`'s per-kind UI.
5. After the learner answers, `POST /api/lesson/answer` to record + update `skill_practice`.
6. Optionally promote a successful ephemeral question into the authored bank via this skill's author-mode workflow.

## Quality bar (per question)

- **Stem** is a single, unambiguous prompt. No nested questions. No "all of the above" / "none of the above" in MCQ.
- **Distractors** are plausible. Each should correspond to a known misconception (cross-reference `agent_hints.common_misconceptions[]`) or a typical computational slip.
- **Math** in `$...$` (inline) and `$$...$$` (display). KaTeX delimiters; never `\(\)` / `\[\]`.
- **Explanation** names the WHY for the correct answer and (when relevant) identifies the misconception that the wrong answer maps to.
- **No external links** in stems / explanations. Cite `concept:<id>` or `lesson:<concept_id>` for cross-references.

## Pitfalls

- ❌ Authoring 6 new questions that all exercise the same atom — the planner can already see mastery on it, you've added zero new signal.
- ❌ Adding only easy questions — the diagnostic / weekly quiz needs hard ones to discriminate strong learners.
- ❌ Hebrew that's a literal word-for-word translation — math conventions, idioms, and sentence order differ. Translate the SENSE, not the words.
- ❌ Forgetting `skill_atoms[]` on a new question. It will seed, but the planner will never see the atom exercised.
- ❌ Reusing question `id`s. The seeder will reject the file.
- ❌ Editing existing questions in place (without bumping the difficulty / explanation). Re-seeding REPLACES the whole question set, so any external `lesson_answers` rows that referenced the old `(lesson_id, question_id)` will now point to a different stem.

## Suggested authoring prompts (for AI assistants)

> "Read scripts/seed_data/lessons/<concept_id>.json. List the current kind, difficulty, and skill-atom distribution. Then propose 6 NEW questions that close the biggest gaps, in the exact JSON shape used by the existing entries, bilingual EN+HE. Do not rewrite existing questions."

> "For the atom <atom_id> on lesson <concept_id>, generate one mcq + one short_answer + one derivation question. Cite the matching misconception from agent_hints.common_misconceptions where appropriate."

## Bulk-generation script

For a fleet-wide top-up there is a Groq-backed script that automates the
authoring workflow above. It enforces kind + difficulty mix, restricts
`skill_atoms` to the lesson's `agent_hints.skill_atoms_unlocked` set,
validates each question against the same schema as the seeder, and
writes back to the JSON files:

```
GROQ_API_KEY=… node scripts/generate-bulk-questions.mjs \
  --target 12   # add up to this many per lesson
  --limit 25    # process at most this many lessons
  --only <csv>  # restrict to specific concept_ids
  --dry-run     # do everything except writing back
```

Also exposed as the `generate-bulk-questions` target in the
`Seed DB (one-shot)` GitHub workflow. After a run, inspect the diff,
PR it, then re-run the `lessons-from-json` target to push the new
questions to Neon.
