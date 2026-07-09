---
name: taste
description: >-
  Make apps/web feel deliberately designed rather than defaulted — enforce visual
  taste in layout, spacing rhythm, typography scale, restrained color, hierarchy,
  depth, and motion, on top of Tailwind v4 + shadcn/ui and the project design
  tokens. Use when building or restyling any page or component in apps/web, doing
  a visual/design pass, a "make this look better / feel more polished" request, or
  reviewing UI for design quality. Bilingual HE-default + RTL and dark mode aware.
---

# Taste

Design taste is the difference between UI that _works_ and UI that feels
**intentional**. This skill encodes the opinions that make `apps/web` look
designed. Apply it whenever you create or change anything visual. It sits on top
of `add-a-frontend-page` (which covers the mechanics of RSC, data, a11y).

## When to use

- Building a new page/section or component in `apps/web/`.
- A "make it look better / more polished / more premium" request.
- A dedicated visual pass or design review before shipping UI.

## Ground truth for this project (use these, don't invent)

Colors, radii, spacing, and motion are **tokens**, never hardcoded hexes.

- **Semantic colors** (from `apps/web/src/app/globals.css`): `background`, `surface-1`,
  `surface-2`, `foreground`, `muted`/`muted-foreground`, `border`/`border-bright`,
  `primary` (violet), `accent-cyan`, `accent-magenta`, `accent-amber`, `destructive`,
  `ring`. Use as Tailwind classes (`bg-surface-1`, `text-muted-foreground`, `border-border`).
- **Radii / spacing / motion**: `apps/web/src/lib/design-tokens.ts`
  (`radius.sm|md|lg|xl`, `spacing.page|section|card`, `motion.fast 150ms|normal 250ms|slow 400ms`).
- **Per-agent identity color**: `agentColors` in `design-tokens.ts` (tutor=violet, mentor=purple,
  coach=green, qa=sky, reviewer=orange, note_taker=pink, accessibility=teal).
- **Signature surfaces** (already in `globals.css`, prefer these over ad-hoc effects):
  `mesh-gradient`, `orb-*` + `orb-float`, `bg-dot-grid`, `glass-surface`,
  `iridescent-border`, `card-punch`, `.font-display`.
- **Integrated dynamism** (unique + dynamic without pasted stickers): read
  `skills/taste/references/integrated-dynamism.md` before any motion/motif pass.
  Extend existing utilities and shared primitives — never corner SVGs, orbit widgets,
  or duplicate marketing sections on top of the slick baseline.

## The taste principles

### 1. Hierarchy — one focal point per view
Every screen has a single most-important element. Establish it with **size, weight,
and space**, not with more color. Secondary content recedes via `muted-foreground`
and smaller scale. If everything shouts, nothing is heard.

### 2. Spacing rhythm — space is the design
Most "undesigned" UI is a spacing problem. Use a consistent scale (4/8px based
Tailwind steps). Group related things tight, separate unrelated things generously.
Give content room to breathe — section padding `py-16`+ on marketing, `p-6` cards.
Vertical rhythm should be regular, not random.

### 3. Typography scale — few sizes, clear jumps
Pick a small set of sizes with real contrast between levels (e.g. hero `text-5xl/6xl`,
section `text-2xl/3xl`, body `text-base`, meta `text-sm`). Headings use `.font-display`
(Space Grotesk / Heebo). Body line-height generous (`leading-relaxed`). Constrain
measure to ~`max-w-prose`/65ch for reading. Weight and size carry hierarchy — avoid
more than 2–3 weights.

### 4. Color restraint — neutral canvas, deliberate accent
The canvas is neutral (`background`, `surface-*`, `muted`). Color is a **tool for
meaning**, not decoration: `primary` for the main action, agent colors for identity,
`destructive` only for danger. One accent per surface. Never place two saturated
colors of equal weight side by side. All text must meet AA contrast in both themes.

### 5. Depth & surfaces — layer with intention
Convey elevation with **subtle** borders + soft shadows (`card-punch`) or blur
(`glass-surface`), not heavy drop shadows. Keep radii consistent from the token scale.
Reserve the flashy surfaces (`iridescent-border`, orbs, mesh) for hero / focal moments —
if every card glows, none do.

### 6. Motion — purposeful, fast, respectful
Animate to explain change (enter/leave, state), 150–250ms with ease. Prefer opacity +
small transform over layout-shifting animations. Everything must degrade under
`prefers-reduced-motion` (already globally handled — don't fight it). No gratuitous
autoplay loops except the ambient hero orbs.

### 7. Alignment & grid — everything on a line
Elements share edges and a grid. Optical alignment beats "technically centered."
Consistent gutters; don't mix arbitrary margins. Icons align to text baselines.

### 8. Details — the last 10%
Real hover/focus/active/disabled states (visible focus ring via `ring`). Loading and
**empty states** are designed, not blank. Consistent iconography and sizing. No
orphaned punctuation, no truncation without a tooltip.

## Bilingual + theming (non-negotiable in this repo)

- Hebrew is the **default** learner-facing language; layouts must work in **RTL**
  (`dir="rtl"`) — use logical properties (`ps-*`/`pe-*`, `text-start`) over `left`/`right`.
- Every surface must look intentional in **both light and dark** — verify contrast in each.
- Math always renders **LTR** in `$...$` / `$$...$$`; never restyle `.katex` to inherit RTL.
- No external links in learner-facing content (product policy).

## Pre-ship taste checklist

Copy and verify before calling a UI "done":

```
- [ ] One clear focal point; hierarchy reads at a glance (squint test)
- [ ] Spacing uses the scale; related grouped, unrelated separated
- [ ] ≤3 type sizes/weights per view; headings use .font-display
- [ ] Neutral canvas + one deliberate accent; AA contrast in light AND dark
- [ ] Colors/radii/spacing/motion come from tokens, no raw hex/px magic numbers
- [ ] Elevation via subtle border/shadow/blur; flashy surfaces reserved for focal areas
- [ ] Hover/focus/active/disabled + loading + empty states all designed
- [ ] Works in RTL with logical properties; math stays LTR
- [ ] Motion 150–250ms, purposeful, safe under reduced-motion
- [ ] Aligned to a grid; consistent gutters
```

## Anti-patterns (reject on sight)

- Default/unstyled shadcn straight out of the box with no spacing or hierarchy pass.
- Rainbow surfaces: multiple saturated colors competing for attention.
- Hardcoded hex colors or arbitrary pixel margins instead of tokens.
- Heavy `box-shadow` drop shadows; thick borders; inconsistent radii.
- Centered everything / no clear focal point.
- Blank empty states and unstyled loading spinners.
- `left/right` physical properties that break RTL.

## Deeper review

For a structured visual QA pass (screenshots, per-breakpoint, per-theme), follow
[references/design-review.md](references/design-review.md).
