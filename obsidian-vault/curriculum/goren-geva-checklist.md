---
type: checklist
source: .cursor/subagent-briefs/22-content-writer.md
skills:
  - author-lesson
  - expand-lesson-theory
  - expand-lessons-cursor
---

# Goren/Geva Section Checklist

Mandatory pedagogical sequence from brief `22-content-writer.md`. Use when staging lesson content in vault before JSON export.

## Section order

| # | Kind | Required | Notes |
|---|------|----------|-------|
| 1 | `intro` | Usually | Bagrut/university exam context |
| 2 | `definition` | Usually | Formal definition or governing law |
| 3 | `theory` | Yes | Max 2 paragraphs before first example |
| 4 | `worked_example` (easy) | Yes | 4–5 explicit steps, full LaTeX |
| 5 | `checkpoint` | After easy | Student must solve before continuing |
| 6 | `worked_example` (medium) | Yes | Multi-step twist |
| 7 | `checkpoint` | After medium | Medium difficulty |
| 8 | `worked_example` (hard) | Yes | Exam-level |
| 9 | `method_guide` | Yes | Decision flowchart / technique table |
| 10 | `exercise_set` | Yes | 8–15 in `exercises[]`: 4 easy, 5 medium, 4 hard |
| 11 | `pitfall` | Yes | Top 3–5 mistakes |
| 12 | `before_exam` | Yes | Formula table, exam patterns |
| 13 | `summary` | Yes | 3–5 bullet takeaways |

## Always required (even for short topics)

- `worked_example` (with difficulty) + `checkpoint`
- `exercise_set`
- `before_exam`

## Schema drift note

Current `author-lesson` validator and `audit-lesson-depth.mjs` enforce a **subset** of this list. When adding new section kinds to JSON, update:

- `scripts/lib/bilingual-utils.mjs` (`MIN_WORDS`, `EXPAND_SECTION_KINDS`)
- `apps/web/src/lib/lesson-types.ts`
- `apps/web/src/components/lesson-reader.tsx`

## Workflow

1. Draft sections in `curriculum/drafts/<concept_id>.md` using [[templates/lesson-draft|lesson draft template]]
2. Validate prose depth against `skills/expand-lessons-cursor/SKILL.md` word gates
3. Export to `scripts/seed_data/lessons/<concept_id>.json`
4. Run `node scripts/audit-lesson-depth.mjs --strict --phase=4`
5. Mark complete: `node scripts/cursor-expansion-queue.mjs --mark <concept_id>`
