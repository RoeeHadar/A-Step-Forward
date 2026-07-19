---
name: math-notation-integrity
description: >-
  Keep every math expression on the learner-facing site rendering correctly
  (KaTeX + remark-math): no Hebrew-in-math, no leaking LaTeX, no broken matrix
  row breaks, no unbalanced $. Read BEFORE authoring/editing any lesson math, or
  when a formula renders as a red box, raw backslashes, or a mangled matrix.
  Owns the linter (scripts/lib/katex-check.mjs), the auto-fixer
  (scripts/fix-lesson-math.mjs), and the blocking CI gate.
---

# Math Notation Integrity

The site renders lesson markdown with **remark-math** (`$...$` inline, `$$...$$`
display) + **rehype-katex**. Before KaTeX runs, three normalizers collapse
over-escaped `\\command` → `\command`. Broken math ships as a red error box, raw
`\frac` text, or a corrupted matrix. This skill's job: **make that impossible.**

## The one source of truth

`scripts/lib/katex-check.mjs` `findMathErrors(text)` defines "broken". It is
enforced as a **blocking CI gate** (`.github/workflows/lint-test.yml` →
`node scripts/audit-lesson-math.mjs --strict`) and surfaced live by the
`afterFileEdit` hook. If it returns `[]` for every field, the math is safe.

## Break classes it catches (and what to do)

| Class | Example (broken) | Fix |
|-------|------------------|-----|
| Hebrew/RTL inside math | `$x=\text{מרחק}$` | Move Hebrew out of `$...$`; keep only LTR math inside. Use English or symbols in `\text{}`. |
| LaTeX leaking outside `$` | `the slope is \frac{1}{2}` | Wrap it: `the slope is $\frac{1}{2}$`. |
| Braced sup/sub outside `$` | `### Approximate e^{0.1}` | Wrap: `$e^{0.1}$` (yes, even in headings). |
| Backslash-bracket delimiters | `\(x+1\)` / `\[y=2\]` | Use `$x+1$` / `$$y=2$$` (remark-math ignores `\( \)`). |
| Unbalanced `$` | `half of $x is gone` | Balance the delimiters. |
| `$$` fence metadata | `$$expr\n...more\n$$` | Put `$$` on its own line. |
| Unparseable TeX | `\begin{pmatrix}a&b\c&d` | `\c` is not a command — the row break must be `\\` (see below). |

## The matrix / cases row-break rule (most common historical bug)

`\\` is a **row separator** inside `pmatrix/bmatrix/vmatrix/matrix/cases/aligned/
align/array/…`. In the **JSON source** write it as `\\\\` so it parses to `\\`:

```json
"body_en_md": "$A=\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}$"
```

The normalizers are **environment-aware** — they preserve `\\` inside these
environments and only collapse over-escaped commands outside them. Never write a
row break as a single backslash + letter (`\c`, `\d`, `\x`), and never rely on
the normalizer to "fix" it.

## Things that are NOT broken (do not flag / do not "fix")

- Unicode math glyphs in math or `\text{}` — `$x \le 5$`, `$30°$`, `$\text{T·m/A}$`
  all render fine. Do not normalize them to macros (it corrupts `\text{}`).
- Math inside fenced ```` ``` ```` or inline `` `code` `` — literal, never rendered.
- Escaped `\$` for money — `$\$100$` renders as `$100`.
- Unicode superscript in prose (`x²`) — readable; wrap as `$x^2$` only for polish.

## Workflow

1. Author/edit lesson math in `scripts/seed_data/lessons/*.json`.
2. Auto-fix the safe subset: `node scripts/fix-lesson-math.mjs`
   (converts `\(...\)`→`$...$`, splits `$$` fence metadata — nothing ambiguous).
3. Check strictly: `node scripts/audit-lesson-math.mjs --only=<concept> --strict`
   (or `--strict` for the whole corpus). Fix every reported item by hand.
4. Regenerate the bundle: `node scripts/generate-lessons-artifacts.mjs`.
5. Unit tests: `node --test scripts/lib/katex-check.test.mjs`.

## If you change how math renders

The linter mirrors the site. If you touch `apps/web/src/lib/normalize-latex.ts`
or the KaTeX/remark config in `apps/web/src/components/markdown-math.tsx`, update
BOTH `scripts/lib/normalize-latex.mjs` (bake-time) and
`scripts/lib/katex-check.mjs` (`normalizeLatexEscapes`) to match, and extend
`scripts/lib/katex-check.test.mjs`. All three normalizer copies must stay in sync.

## Never

- Never weaken the gate to make a lesson pass — fix the notation.
- Never auto-translate or auto-rewrite math content; only the deterministic
  `autoFixMath` transforms are safe to apply programmatically.
