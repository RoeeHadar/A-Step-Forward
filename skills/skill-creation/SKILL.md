---
name: skill-creation
description: >-
  Author, review, and audit Agent Skills for this repo following Anthropic's
  "Complete Guide to Building Skills for Claude". Use when creating a new skill,
  editing a SKILL.md, or auditing existing skills under skills/ for correct
  frontmatter, discoverable descriptions, progressive disclosure, and structure.
---

# Skill Creation

This skill teaches how to build and audit **Agent Skills** the way Anthropic's
_Complete Guide to Building Skills for Claude_ prescribes. Use it to create a new
skill, fix an existing one, or run a conformance audit across `skills/`.

## Core mental model

A skill is a **folder** whose behavior is driven by three progressive-disclosure levels:

| Level | What | When it loads |
|-------|------|---------------|
| 1 — Frontmatter | `name` + `description` (YAML) | Always, in the system prompt. It is how the agent decides to load the skill. |
| 2 — SKILL.md body | Full instructions | When the agent judges the skill relevant. |
| 3 — Linked files | `references/`, `scripts/`, `assets/` | Only when the body points to them and the task needs them. |

Three properties every skill must keep: **progressive disclosure** (don't front-load
detail), **composability** (works alongside other skills; never assumes it's the only
one), **portability** (no dependence on machine-specific state).

## The three levels in practice

- Keep level-1 (`description`) rich in trigger terms so the skill loads on the right queries.
- Keep level-2 (`SKILL.md`) focused and skimmable; move deep reference into level-3 files.
- Link level-3 files **one level deep** from `SKILL.md` (e.g. `references/foo.md`), never nested.

## Non-negotiable rules (from the guide)

1. File is named exactly `SKILL.md` (case-sensitive).
2. YAML frontmatter present, opened and closed with `---`.
3. `name`: kebab-case, no spaces, no capitals, no underscores, ≤64 chars, **matches the folder name**.
4. `description`: states **WHAT** it does **and WHEN** to use it (trigger phrases); ≤1024 chars.
5. **No XML angle brackets (`<` `>`) anywhere in the frontmatter** — it is injected into the system prompt.
6. Name must not contain `claude` or `anthropic` (reserved).
7. **No `README.md` inside a skill folder** — all docs go in `SKILL.md` or `references/`.
8. Use forward-slash paths (`scripts/x.py`), never Windows backslashes.
9. Keep `SKILL.md` focused — target under ~500 lines / 5,000 words; use progressive disclosure past that.

## Writing the description (the highest-leverage field)

Formula: **[What it does] + [When to use it / trigger phrases] + [key file types or scopes]**.

- Third person, declarative ("Analyzes…", "Adds…"), never "I can…" or "You can…".
- Include the concrete phrases a user would actually say, and relevant file types / paths.
- If a sibling skill is easy to confuse with, add a **negative trigger** ("Do NOT use for X — use `other-skill`").

```yaml
# Good
description: >-
  Adds a Next.js 15 route under apps/web using App Router, RSC, Tailwind v4 +
  shadcn/ui. Use when creating or modifying any page in apps/web/.

# Bad — vague, no trigger, first person
description: I help you with frontend pages.
```

## Authoring workflow

Copy this checklist and track progress:

```
- [ ] 1. Define 2-3 concrete use cases (trigger → steps → result)
- [ ] 2. Pick category: (1) asset/content creation, (2) workflow automation, (3) MCP enhancement
- [ ] 3. Choose folder name (kebab-case) = name field
- [ ] 4. Write the description (WHAT + WHEN + triggers)
- [ ] 5. Draft SKILL.md body: quick start, steps, examples, pitfalls
- [ ] 6. Move deep detail into references/; keep links one level deep
- [ ] 7. Add scripts/ for fragile or repeated deterministic operations
- [ ] 8. Run the conformance audit (references/audit-checklist.md)
```

**Match freedom to fragility:** high freedom (prose) for judgement tasks, medium (templates/pseudocode)
for preferred patterns, low (a script the agent runs) for fragile, consistency-critical operations.

## Body structure that works

```markdown
# Skill Name
## When to use            ← restate triggers for the agent that already opened the file
## Quick start / Steps     ← numbered, actionable, with expected output
## Examples                ← concrete input → output, not abstract description
## Pitfalls / Troubleshooting  ← error → cause → fix
## Additional resources    ← links to references/ (one level deep)
```

Put critical instructions **at the top**. Prefer bullets and numbered steps over prose.
For deterministic validation, bundle a script rather than trusting language ("code is
deterministic; language interpretation isn't").

## Testing a skill

- **Triggering:** it loads on obvious + paraphrased requests, and does NOT load on unrelated ones.
- **Functional:** it produces correct output and handles the edge/error cases it claims to.
- **Comparison:** with the skill enabled the task needs fewer corrections / tokens than without.

Debug under-triggering by adding trigger keywords to the description; debug over-triggering
by adding negative triggers and narrowing scope.

## Anti-patterns (reject these in review)

- No frontmatter, or `name` ≠ folder name.
- Vague names (`helper`, `utils`, `tools`) or vague descriptions ("helps with X").
- Time-sensitive notes ("before August, use…") — use a "deprecated" section instead.
- Inconsistent terminology (pick one term and keep it).
- "You can use A, or B, or C…" — give one default plus a documented escape hatch.
- Nested references (`references/deep/deeper/x.md`) — keep one level deep.

## Auditing existing skills

To review the skills in this repo against this standard, follow the rubric in
[references/audit-checklist.md](references/audit-checklist.md). Report each skill as
PASS / FIX with `file:line` evidence, then apply the smallest fix that makes it conform —
most commonly **adding the missing YAML frontmatter** without rewriting the body.
