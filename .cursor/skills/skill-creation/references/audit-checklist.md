# Skill Conformance Audit Checklist

Run this rubric against every `skills/*/SKILL.md`. For each skill, record a verdict
(**PASS** or **FIX**) with `file:line` evidence. Apply the smallest change that makes
the skill conform — normally adding frontmatter, never rewriting a working body.

## A. Frontmatter (blocking — a skill with no frontmatter cannot be discovered)

- [ ] `SKILL.md` starts with a `---` line, has a `name:` and `description:`, and closes with `---`.
- [ ] `name` is kebab-case, no capitals / spaces / underscores, ≤64 chars.
- [ ] `name` **exactly equals the folder name**.
- [ ] `name` does not contain `claude` or `anthropic`.
- [ ] `description` states WHAT the skill does.
- [ ] `description` states WHEN to use it (explicit trigger phrases / paths / file types).
- [ ] `description` is third person (no "I…" / "You can…"), ≤1024 chars.
- [ ] No `<` or `>` characters anywhere in the frontmatter block.

## B. Structure

- [ ] Filename is exactly `SKILL.md` (case-sensitive).
- [ ] No `README.md` inside the skill folder.
- [ ] Any linked file is one level deep (`references/x.md`, `scripts/x.py`), not nested deeper.
- [ ] Paths use forward slashes, not backslashes.
- [ ] Body is focused (≈ under 500 lines); heavy detail lives in `references/`.

## C. Content quality

- [ ] Name is specific, not `helper` / `utils` / `tools`.
- [ ] Instructions are actionable (numbered steps, expected outputs), not vague prose.
- [ ] Examples are concrete (input → output).
- [ ] Terminology is consistent throughout.
- [ ] No time-sensitive instructions in the main flow (use a "deprecated" section instead).
- [ ] Where one default exists, it is given with an escape hatch rather than a list of equal options.

## Verdict format

```
<skill-name> — PASS | FIX
  - <finding> (SKILL.md:<line>)
  - Fix applied: <one line>
```

## Common fixes

| Finding | Minimal fix |
|---------|-------------|
| No frontmatter at all | Prepend a `---` block with `name` (= folder) + a WHAT/WHEN `description` derived from the existing body. Do not rewrite the body. |
| `name` ≠ folder | Rename the `name` field to match the folder (renaming the folder risks breaking references). |
| Description missing WHEN | Append "Use when …" with real trigger phrases pulled from the body's "When to use" section. |
| `<`/`>` in frontmatter | Rephrase without angle brackets. |
| README.md in folder | Fold its content into `SKILL.md` or `references/`, then delete the README. |
