# Taste — Visual Review Pass

A structured way to judge whether a page/component in `apps/web` looks
**designed**. Use after the build, before shipping. Capture evidence, don't rely on
memory.

## 1. Set up the evidence

Review each surface across the axes that actually break design in this repo:

- **Themes:** light and dark (toggle `.dark`).
- **Direction:** RTL (Hebrew default) and LTR (English).
- **Breakpoints:** mobile (~375px), tablet (~768px), desktop (~1280px).
- **States:** default, hover, focus (keyboard), active, disabled, loading, empty, error.

Take a screenshot of each meaningful combination (use the browser tools). Compare
against the intended focal point and hierarchy.

## 2. Score each principle (from SKILL.md)

For each, mark OK / FIX with a one-line note and the element:

1. Hierarchy — is there exactly one focal point? Does the squint test pass?
2. Spacing rhythm — consistent scale? related grouped, unrelated separated?
3. Typography — ≤3 sizes/weights, real contrast between levels, generous body leading?
4. Color — neutral canvas + one deliberate accent? AA contrast both themes?
5. Depth — subtle elevation; flashy surfaces reserved for focal areas?
6. Motion — 150–250ms, purposeful, safe under reduced-motion?
7. Alignment — shared edges, consistent gutters, baseline-aligned icons?
8. Details — all interaction + empty + loading states designed?

## 3. Token conformance

- No raw hex or arbitrary px — everything resolves to `globals.css` semantic colors
  and `design-tokens.ts` (radius / spacing / motion).
- Radii consistent across sibling elements.
- Agent-scoped UI uses the matching `agentColors` value.

## 4. Bilingual / a11y crosscheck

- RTL layout uses logical properties (`ps/pe`, `ms/me`, `text-start/end`); nothing
  hardcodes `left`/`right`.
- KaTeX math renders LTR inside Hebrew prose.
- Visible focus ring on every interactive element; contrast holds in both themes.
- No external links in learner-facing content.

## 5. Verdict

```
<surface> — SHIP | POLISH | REWORK
  - FIX: <principle> — <what/element> — <suggested change>
  ...
Top 3 highest-leverage polish items:
  1.
  2.
  3.
```

Prefer a few high-leverage changes (spacing rhythm, hierarchy, one accent) over many
tiny tweaks — those are what make a page read as "designed."
