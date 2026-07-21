---
name: build-custom-quiz
description: >-
  Generate ephemeral, fit-to-purpose AI practice quizzes for a single learner
  from natural-language requirements (kind-mix, time budget, optional topics) via
  POST /api/quiz/custom and buildCustomQuiz. Use when building the /app/quiz page
  or when a runtime agent wants to drop a tailored mini-assessment into chat. Do
  NOT use to author durable lesson question banks — use author-question-bank for that.
---

# Build a Custom AI Quiz

Generate **fit-to-purpose** practice quizzes for one learner from natural-language requirements (kind-mix, time budget, optional topics).

This is the runtime backbone of the `/app/quiz` page and the recommended way for runtime agents (Tutor, Coach, Assessment Generator) to spin up a tailored mini-assessment on demand. **Do not** use this skill to author durable lesson question banks — for that, use `.cursor/skills/author-question-bank/SKILL.md`.

## Why this skill exists

- The corpus of authored lesson questions covers a fixed set of skill atoms per concept; learners frequently want to test themselves on a different cross-section ("just trigonometry word problems, 15 minutes, mixed").
- A single endpoint that takes a kind-mix + time-budget + topic set, and returns a graded-able envelope, gives every consumer (UI, agents) the same predictable building block.
- Quizzes generated this way are **not authored lessons**, but answer keys **are** persisted server-side in Neon `custom_quizzes` (learner-scoped) so grading cannot trust the client. The start response strips solutions/keys; reveal arrives after grading completes. Mastery / skill-practice updates still happen through `/api/lesson/answer` on submit.

## Public surface

### HTTP

```
POST /api/quiz/custom         (authed; learner-scoped)
Body:
{
  "kind_mix":       "closed" | "open" | "mixed",     // required
  "time_limit_min": number,                           // required; clamped to [3, 90]
  "topics":         string[]                          // optional concept_ids
}
```

Returns `CustomQuizEnvelope`:

```jsonc
{
  "quiz_id":       "uuid",            // Neon custom_quizzes.id for this learner
  "kind_mix":      "mixed",
  "time_limit_s":  600,
  "picked_reason": "user_topics" | "weakest_mastery" | "subject_bootstrap",
  "concepts":      [{ "id", "name", "name_he", "subject" }, ...],
  "questions": [
    {
      "ord":             1,
      "kind":            "mcq" | "true_false" | "numeric" | "short_answer" | "open",
      "difficulty":      "easy" | "medium" | "hard",
      "concept_id":      "...",
      "skill_atoms":     ["..."],
      "stem_en":         "...",
      "stem_he":         "...",
      "explanation_en":  "...",
      "explanation_he":  "...",
      // per-kind fields:
      "options_en"?:        string[], "options_he"?: string[], "correct_index"?: number,
      "correct_bool"?:      boolean,
      "correct_answer"?:    string,                 // numeric
      "acceptable_answers"?: string[],              // short_answer
      "rubric_en"?:         string, "rubric_he"?: string  // open
    }
  ],
  "model": "llama-3.3-70b-versatile"
}
```

### TypeScript

```ts
import { buildCustomQuiz } from '@/lib/quiz-builder';
const envelope = await buildCustomQuiz(learnerId, {
  kind_mix: 'mixed', time_limit_min: 10, topics: ['concept-x']
});
```

## When to call

- **UI**: the `/app/quiz` page when the learner clicks "Generate quiz".
- **Tutor agent**: after a chat where the learner says "quiz me on …" — call the builder, then either return the rendered quiz inline (`mixed`, ~5 minutes) or deep-link to `/app/quiz?seed=<topics>`.
- **Coach agent**: spaced-repetition drill — when picking the next short session, call with `kind_mix: 'closed'`, `time_limit_min: 5`, `topics` = the FSRS-due concepts.
- **Assessment Generator agent**: when an educator requests a custom checkpoint, call with the educator-supplied topics and time budget, then attach the envelope to the educator dashboard report.

## When NOT to call

- Authoring a durable, reusable question bank for a concept — write to `lessons.questions` via the seed pipeline instead.
- Generating questions for a learner without authenticating them — the builder needs `learnerId` to pull profile + mastery.
- High-throughput batch generation — this runs synchronously and waits on Groq; batch authoring should use `scripts/generate-bulk-questions.mjs`.

## How concepts are picked

1. If `topics[]` is non-empty and at least one id exists in the KG → use those verbatim. Reason: `user_topics`.
2. Else, sort `concept_mastery` ascending, take the bottom 6. Reason: `weakest_mastery`.
3. Else (brand-new learner with no measured concepts) → take the prerequisite-free roots of the learner's `subjects[]`. Reason: `subject_bootstrap`.

## How question count is sized

| kind_mix | minutes per question | example: 15-min quiz |
| -------- | -------------------- | -------------------- |
| closed   | ~1.2                  | 12 questions         |
| mixed    | ~2.0                  | 7 questions          |
| open     | ~3.5                  | 4 questions          |

Bounds: minimum 3, maximum 20. Hard floor of 3 minutes total.

## Quality bar (what the model must follow)

Hard-coded in the system prompt and enforced by `validateQuestion` + `quiz-solvability.ts`:

- **Bilingual**: every stem / explanation / option / rubric must have both EN and HE.
- **Math LTR inside RTL HE**: rendered via KaTeX; do not translate `$...$`.
- **Skill atoms** must come from the lesson `agent_hints.skill_atoms_unlocked` for that concept where available (otherwise empty array). This is what lets the planner attribute mastery from the answers.
- **Difficulty spread**: ≥1 easy and ≥1 medium when count ≥ 3; ≥1 hard when count ≥ 6.
- **Concept spread**: roughly even across the chosen concepts.
- Stems / explanations / rubrics capped at 600 chars each.
- No real names, schools, emails, phones, or addresses.
- **Solvability (mandatory):** every part must be uniquely solvable from the stem. Reject: proving diagonal bisection on a generic מרובע; ambiguous area of an unspecified quadrilateral; sample solutions that admit "insufficient data / חסרים נתונים".
- **Exam depth:** `difficulty` must be `hard`. Exemplars come from `exam-style-corpus` (original Bagrut/finals multi-part items — never MoE transcripts). Rebuild with `pnpm exam-style:build`.

Any question failing validation is dropped silently. If zero pass validation the endpoint returns **503** so the UI can show a retry CTA.

## Pitfalls

- **Server-held keys.** Start envelope omits `correct_index` / solutions / rubrics. Submit `{ quiz_id, answers[] }` only — never client-supplied `questions[]` with keys.
- **Groq required.** If `GROQ_API_KEY` is missing the endpoint returns 503. Local dev without Groq → use authored lesson quizzes instead.
- **No durable id.** `quiz_id` is a random UUID generated at build time; it's only useful for keying `/api/lesson/answer` writes so the practice pipeline can see them and attribute mastery.
- **Grading is honest for closed kinds, self-reported for open kinds.** The results screen surfaces a 3-way self-assessment (correct / partial / wrong) for open questions; the score reported in the breakdown reflects that choice.

## Files

| File                                                  | Role                                       |
| ----------------------------------------------------- | ------------------------------------------ |
| `apps/web/src/lib/quiz-builder.ts`                    | Server-side builder + Groq prompt + validator. |
| `apps/web/src/app/api/quiz/custom/route.ts`           | Authed HTTP endpoint.                       |
| `apps/web/src/app/(app)/app/quiz/page.tsx`            | Server page; ships KG concept list to client. |
| `apps/web/src/components/quiz-page-client.tsx`        | Single-file bilingual UI (form → runner → results). |

## Related skills

- `.cursor/skills/author-question-bank/SKILL.md` — durable question authoring.
- `.cursor/skills/build-an-agent/SKILL.md` — how agents call this skill from chat.
- `.cursor/skills/chat-memory-context/SKILL.md` — prompt-composition layers the builder injects.
