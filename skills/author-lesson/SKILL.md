---
name: author-lesson
description: How to author a new AI-authored bilingual lesson (JSON shape, all 10 question kinds, agent_hints, skill_atoms) and ship it through the seed pipeline to the live site. Read BEFORE writing or modifying any file under scripts/seed_data/lessons/.
---

# Author Lesson

## When to use

- Adding a new authored lesson for a concept in `apps/web/src/lib/kg-data.json`.
- Expanding question coverage (more practice items) on an existing authored lesson.
- Introducing a new question kind across the corpus.
- Tweaking `agent_hints` (key insights, pacing, misconceptions, diagnostics, skill atoms unlocked).

## Where the content lives

```
scripts/seed_data/lessons/<concept_id>.json       # one file per authored lesson
scripts/seed-lessons.mjs                          # validator + idempotent upserter
apps/web/src/lib/lesson-types.ts                  # TS types the UI reads
apps/web/src/components/lesson-reader.tsx         # body renderer
apps/web/src/components/lesson-quiz-panel.tsx     # question renderer (per kind)
```

The seeder runs on every push via the GitHub workflow `Seed DB (one-shot)` with
`target: lessons` and is idempotent on `(concept_id)`. Re-seeding REPLACES the
question set for a lesson — never partial-merges. So always re-seed the whole
file.

## Lesson JSON shape (top-level)

```json
{
  "concept_id": "triangles_congruence",
  "title_en": "Triangle Congruence Tests",
  "title_he": "מבחני חפיפת משולשים",
  "subject": "math",
  "difficulty": "intermediate",
  "estimated_minutes": 25,
  "sections": [
    {
      "id": "intro",
      "kind": "intro",
      "title_en": "Why congruence?",
      "title_he": "למה חפיפה חשובה?",
      "body_en": "Markdown with $math$ allowed",
      "body_he": "Markdown בעברית עם $math$"
    },
    { "id": "defs",        "kind": "definitions",     ... },
    { "id": "worked",      "kind": "worked_example",  ... },
    { "id": "pitfalls",    "kind": "pitfalls",        ... },
    { "id": "why_matters", "kind": "why_matters",     ... }
  ],
  "questions": [ /* see below */ ],
  "agent_hints": { /* see below */ }
}
```

### Sections — what each kind is for

| Kind             | Purpose                                                                      |
| ---------------- | ---------------------------------------------------------------------------- |
| `intro`          | One-paragraph hook — concrete situation, not a definition.                   |
| `definitions`    | The 1–4 core terms with brief, precise definitions.                          |
| `worked_example` | A single, fully solved problem with the moves named (the *thinking*, not just the answer). |
| `pitfalls`       | The 2–4 most common mistakes from the literature, each with a one-line fix. |
| `why_matters`    | Connection to other concepts in the KG (`concept:<id>` references), real-world impact. |

Always author BOTH `body_en` and `body_he`. The UI defaults to HE; an English-
only or Hebrew-only section will make the page feel half-broken.

## Question kinds — all 10

`scripts/seed-lessons.mjs` will reject a lesson if the `kind` is unknown or the
shape doesn't match. Every question has these common fields:

```json
{
  "id": "q1",
  "kind": "<one of below>",
  "difficulty": 3,                 // 1–5
  "skill_atoms": ["area_scale_factor", ...],   // atoms this question exercises
  "stem_en": "Markdown with $math$ allowed",
  "stem_he": "Markdown בעברית עם $math$",
  "answer_payload": { ... },       // shape depends on kind
  "explanation_en": "Why the answer is correct",
  "explanation_he": "..."
}
```

### `mcq` — single correct answer

```json
"answer_payload": {
  "options_en": ["choice A", "B", "C", "D"],
  "options_he": ["...", "...", "...", "..."],
  "correct_index": 2
}
```

### `mcq_multi` — multiple correct answers (all-or-nothing)

```json
"answer_payload": {
  "options_en": [...],
  "options_he": [...],
  "correct_indices": [0, 2, 3]
}
```

### `true_false`

```json
"answer_payload": { "correct": true }
```

### `short_answer` — open text, fuzzy graded

```json
"answer_payload": {
  "accept_en": ["congruent", "the same", "equal"],   // any match (case + whitespace insensitive) passes
  "accept_he": ["חופפים", "שווים"],
  "regex": "^(yes|כן)$"                              // optional, OR with accept lists
}
```

### `numeric`

```json
"answer_payload": {
  "value": 3.14,
  "tolerance": 0.01,
  "unit_en": "m/s",
  "unit_he": "מ׳/שנ׳"
}
```

### `match` — pair items

```json
"answer_payload": {
  "left_en": ["SSS", "ASA", "SAS"],
  "left_he": ["צ.צ.צ.", "ז.צ.ז.", "צ.ז.צ."],
  "right_en": ["3 sides", "angle-side-angle", "side-angle-side"],
  "right_he": ["3 צלעות", "זווית-צלע-זווית", "צלע-זווית-צלע"],
  "pairs": [[0, 0], [1, 1], [2, 2]]
}
```

### `ordering` — put steps in order

```json
"answer_payload": {
  "steps_en": ["Identify givens", "Pick a test", "State pairs", "Conclude"],
  "steps_he": ["...", "...", "...", "..."],
  "correct_order": [0, 1, 2, 3]
}
```

### `derivation` — show the line-by-line steps (self-assessed)

```json
"answer_payload": {
  "steps_en": ["Step 1: …", "Step 2: …", "Step 3: …"],
  "steps_he": ["...", "...", "..."]
}
```

The grader is self-assessment: the learner ticks "I matched" / "I didn't" per
step; the API persists their self-report. The Reviewer agent can re-grade later
if cited.

### `open` — pure free response

```json
"answer_payload": {
  "rubric_en": "Mentions both prereq concepts and one application.",
  "rubric_he": "..."
}
```

Marked correct = self-assessed.

### `free_response` — legacy free text

Same as `open` but without an authored rubric (older lessons only — avoid for new content).

## `agent_hints` — the agent grounding block

```json
"agent_hints": {
  "key_insights": [
    "Two triangles are congruent iff three independent measurements match.",
    "SSA is NOT a valid test (the ambiguous case)."
  ],
  "common_misconceptions": [
    {
      "wrong": "AAA proves congruence",
      "correction": "AAA only proves similarity, not congruence.",
      "detect_phrase_en": "all three angles",
      "detect_phrase_he": "כל שלוש הזוויות"
    }
  ],
  "tutor_pacing_hint": "Show one worked example before naming the four tests.",
  "diagnostic_signals": {
    "asks about scale": "Steer toward similarity, not congruence.",
    "uses SSA": "Gently surface the ambiguous-case counter-example."
  },
  "skill_atoms_unlocked": [
    "identify_congruence_test",
    "state_congruence_conditions",
    "rule_out_SSA"
  ]
}
```

The runtime mines this for tutor / coach / qa_explainer when the learner's
message mentions the concept (id, EN name, or HE name). See `apps/web/src/app/api/chat/route.ts` → `fetchLessonAgentHintsByConceptIds`.

## Skill atoms — how they wire into mastery

- `agent_hints.skill_atoms_unlocked` → lesson `teaches` these atoms (role = `teaches` in `lesson_skill_atoms`).
- Per-question `skill_atoms[]` → question `exercises` these atoms (role = `exercises`).
- When the learner answers a question, `lesson_answers.skill_atoms_practiced` is filled from `exercises`. The `skill_practice` table aggregates per-atom mastery.
- The learning-plan engine reads `skill_practice` to weigh prerequisite urgency. See `skills/use-learning-plan/SKILL.md`.

## Authoring quality bar

- Both EN and HE for **every** section body and question stem. The UI defaults to HE; English-only content reads as "the platform is half-broken".
- Math in `$...$` (inline) or `$$...$$` (display). Hebrew text is RTL but math always renders LTR (CSS in `globals.css` handles this).
- ≥ 1 question per `skill_atoms_unlocked` atom — otherwise the planner can never observe mastery of that atom.
- Mix question kinds. Aim for at least one of: `mcq`, `mcq_multi` OR `true_false`, `short_answer` OR `numeric`, `match` OR `ordering` OR `derivation`.
- Difficulty 1 = warm-up, 5 = stretch.
- No external URLs. Cite siblings as `concept:<id>` or `lesson:<concept_id>`.

## Re-seeding the corpus

```
gh workflow run "Seed DB (one-shot)" -f target=lessons
```

Locally (requires Neon access):

```
DATABASE_URL=postgresql://... node scripts/seed-lessons.mjs
# Validate without writing:
node scripts/seed-lessons.mjs --dry-run
# Single lesson only:
node scripts/seed-lessons.mjs --only=triangles_congruence
```

Validate the whole corpus reports per-lesson stats:

```
node scripts/audit-lessons.mjs
```

## Pitfalls

- ❌ Authoring English-only or Hebrew-only sections — the language toggle will reveal the gap immediately to a real learner.
- ❌ Putting math in `\(\)` or `\[\]` — the renderer is rehype-katex with `$` delimiters only.
- ❌ Forgetting `skill_atoms[]` on a question — it will still seed, but the planner will never see the atom exercised.
- ❌ Adding new question kinds without extending `lesson-quiz-panel.tsx`, `neon-db.ts:gradeLessonAnswer`, AND `seed-lessons.mjs` validation in lockstep.
- ❌ Linking to Khan Academy / Wikipedia. The whole point of the authored corpus is that we're the source of truth — never outsource it.
