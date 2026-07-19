---
name: expand-lessons-cursor
description: Substantive bilingual lesson expansion using Cursor Composer 2.5 locally — NOT Groq CI batch jobs. Read BEFORE bulk-rewriting scripts/seed_data/lessons/ for depth, Hebrew parity, or question explanations. Pair with .cursor/skills/author-lesson/SKILL.md and .cursor/skills/expand-lesson-theory/SKILL.md.
---

# Expand Lessons (Cursor Composer)

## Policy (2026-07-02)

**Bulk substantive lesson expansion runs in Cursor with Composer 2.5**, not via
`expand-lessons-substantive.mjs` / Groq GitHub Actions. Groq free-tier TPM/TPD
limits caused 6+ hour stalls with zero commits. Runtime learner chat may still
use Groq; **corpus authoring does not**.

## When to use

- Deepening sections + question explanations across the 207-lesson JSON corpus.
- Fixing Hebrew parity (`body_he_md` must be full Hebrew prose, not English paste).
- Replacing template filler in explanations with pedagogical depth (Goren/Geva quality).

## Workflow

```bash
# 1. See what still needs work (priority queue)
node scripts/cursor-expansion-queue.mjs
node scripts/cursor-expansion-queue.mjs --next 10

# 2. Expand lessons in Cursor (Composer 2.5)
#    Read .cursor/skills/author-lesson + this file. Edit scripts/seed_data/lessons/<id>.json

# 3. Validate
node scripts/seed-lessons.mjs --dry-run
node scripts/audit-lesson-depth.mjs --strict --phase=4

# 4. Mark progress + commit every 2–5 lessons
node scripts/cursor-expansion-queue.mjs --mark algebra_review,fractions_and_ratios
git add scripts/seed_data/lessons/ scripts/.cursor-expansion-progress.json
git commit -m "feat(curriculum): Cursor expansion batch (N lessons)"

# 5. Seed when a milestone is done
gh workflow run "Seed DB (one-shot)" -f target=lessons-from-json

# 6. Refresh Obsidian vault dashboards
node scripts/sync-obsidian-expansion.mjs
node scripts/sync-obsidian-concepts.mjs
```

Progress file: `scripts/.cursor-expansion-progress.json` (`completed[]`, `updated_at`).
Vault dashboards: `obsidian-vault/curriculum/expansion-queue.md`, `obsidian-vault/concepts/`.
See `.cursor/skills/use-obsidian-vault/SKILL.md`.

## Depth gates (per section)

Use `scripts/lib/bilingual-utils.mjs` `MIN_WORDS`:

| Kind | EN min | HE min |
|------|--------|--------|
| intro | 110 | 90 |
| definition | 130 | 110 |
| theory | 160 | 130 |
| worked_example | 130 | 110 |
| pitfall | 100 | 85 |
| why_matters | 90 | 75 |
| method_guide | 100 | 85 |

Hebrew quality: `hebrewBodyWeak(body_he_md, body_en_md)` must be **false**.
Math stays in `$...$` / `$$...$$` (LTR). Use `### Move N:` (EN) / `### צעד N:` (HE).

## Question explanations

Each `explanation_en` / `explanation_he`: **80–150 words** — why the answer works,
common wrong path, exam tip. No template strings like "Name the rule from this lesson".

## Checkpoint sections

Expand `checkpoint_solution_en` / `checkpoint_solution_he` to show full reasoning.

## Do NOT

- ❌ Run `expand-lessons-substantive.mjs` in CI for bulk work (deprecated).
- ❌ Google-translate EN → HE.
- ❌ Cross-fallback languages in lesson JSON (UI is strict per toggle).
- ❌ Partial-merge sections — always write the full `sections[]` array validly.
- ❌ **Trailing commas** in JSON (invalid JSON — breaks queue + seed). After editing, run `node -e "JSON.parse(require('fs').readFileSync('scripts/seed_data/lessons/<id>.json'))"`.

## Suggested Cursor prompt

> Read `.cursor/skills/expand-lessons-cursor/SKILL.md` and expand
> `scripts/seed_data/lessons/<concept_id>.json`: deepen every section to MIN_WORDS,
> full authentic Hebrew in `body_he_md`, expand all 8 question explanations to
> 80–150 words each language. Preserve schema, LaTeX, skill_atoms, agent_hints.
> Run dry-run seed validate when done.

## Agent runtime note

Runtime agents (Tutor, Q&A Explainer, Content Curator) are told via
`agent-baseline.ts` that the corpus is Cursor-authored at Goren/Geva depth with
strict bilingual sections. Cite lessons as `lesson:<concept_id>`.
