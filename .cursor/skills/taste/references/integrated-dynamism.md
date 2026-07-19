# Integrated dynamism — not pasted decoration

Use this when adding **unique, dynamic** feel to `apps/web`. The warm editorial
redesign (`199ddd9d`) is the baseline. Dynamism must feel **native** to that
system — not stickers on top of it.

## What went wrong (anti-patterns — do not repeat)

The reverted `36b5e75` pass failed the squint test because it **added a second
visual language** on top of the slick one:

| Pasted add-on | Why it felt wrong |
|---------------|-------------------|
| Corner SVG motifs (`GrowthPathMotif`, `MemoryConstellation`) | Decorative stickers unrelated to layout grid; different opacity/scale per page |
| Orbiting agent chips around hero demo | Widget chrome; breaks the matte `iridescent-border` card |
| Cycling `LivingAgentDemo` + progress dots | Demo became the focal point instead of the headline + CTA |
| Extra "What makes us different" section | Repeated messaging already in hero subtitle + agent cards |
| `agent-card` hover glows + bento spans | Competed with `card-punch`; uneven grid vs rest of site |
| New CSS animation families (`orbit-drift`, `path-draw`) | Motion vocabulary unrelated to existing `orb-float` / `card-punch` |

**Rule:** If you can delete the new component and the page still reads the same
at a glance, it was probably pasted — not integrated.

## Integration compass

Dynamism belongs in **layers the architecture already has**:

```
globals.css tokens + utilities  →  canvas breathes (one system)
layout shells (root, app, learn) →  ambient depth everywhere, same recipe
shared components (card-punch, PageHeader, SiteHeader, agent surfaces) →  interaction
product surfaces (dashboard, chat, progress, memory) →  uniqueness = real data/UX
```

Do **not** introduce parallel motif components unless they replace an existing
utility (e.g. extend `.mesh-gradient`, don't add `.growth-path-stroke`).

## Where uniqueness actually lives (ASF-specific)

The product is already unique. Surface that through **behavior and data**, not
hero clipart:

1. **Persistent memory** — `/app/memory`, persona settings, agent chat context
2. **Multi-agent team** — sidebar roster, per-agent colors (`agentColors`), chat routes
3. **Mastery-aware paths** — dashboard weekly plan, progress widgets, `/learn` catalog
4. **Bilingual HE-default** — typography rhythm, RTL logical properties (already core)

Marketing dynamism should **preview** these truths in the existing hero card —
not narrate them again in a new section.

## Approved integration strategies (ranked)

### 1. Canvas layer — extend existing utilities (`globals.css`)

- Slow drift on **existing** `orb-float` / `mesh-gradient` (already on canvas)
- Scroll-linked opacity on `AmbientBackground` via CSS `@supports` + `animation-timeline`
  or a single thin `useScroll` hook **inside** `ambient-background.tsx` only
- Grain + dot-grid: subtle opacity pulse (one keyframe, shared with `card-punch` timing)
- Theme transition: smooth `--background` / `--primary` crossfade on `.dark` toggle

**No new SVG assets in page corners.**

### 2. Interaction layer — upgrade shared primitives

| Primitive | Integrated dynamism |
|-----------|---------------------|
| `card-punch` | Agent-scoped `border-inline-start` tint via `--agent-color` CSS var on parent |
| `MotionCard` | Use site-wide for catalog/agent grids instead of one-off framer wrappers |
| `PageHeader` | Sticky hairline brightens on scroll (same gradient rule already there) |
| `SiteHeader` | `backdrop-blur` + border opacity increases after `scrollY > 8` |
| Buttons / links | Existing hover brightness + `group-hover` arrow nudge (already on CTA) |
| `AnimatedCounter` | Keep for stats; no extra motif behind numbers |

Motion: **150–250ms**, `prefers-reduced-motion` safe. One easing curve site-wide.

### 3. Layout shells — one ambient recipe

- `AmbientBackground` in `app/(app)/app/layout.tsx` and public pages (`learn`) —
  same `variant` rules, no per-page corner art
- Optional `variant="hero"` only on landing above-the-fold — stronger orbs, not new shapes
- Root `body::before` grain stays fixed; never duplicate grain per section

### 4. Hero — deepen the existing structure (landing-hero.tsx)

Keep: serif headline, matte demo card, stats strip, agent grid, how-it-works, CTA band.

Integrated upgrades only:

- Typing demo **inside** the existing card (already there) — optional slow agent name
  crossfade in the **card header only** (no orbit chips, no second card)
- Stats strip: keep symmetric 4-up OR subtle size contrast — not a second bento language
- Agent grid: keep uniform `card-punch` + top accent rule — featured span only if the
  **whole site** uses the same bento grammar (dashboard, learn)

### 5. Product chrome — agent identity without widgets

- `agentColors` → set `--agent-accent` on chat layout, sidebar active item, dashboard cards
- Chat bubbles: user = `primary`, agent = `surface-2` (already correct)
- No floating emoji orbits; identity = color + name in header

## Implementation checklist (before shipping dynamism)

- [ ] Change touches **≤3 integration points** (usually `globals.css`, one shell, one shared component)
- [ ] No new top-level marketing sections for messaging that exists elsewhere
- [ ] No corner SVGs or floating chips outside the layout grid
- [ ] Motion reuses `tokens.motion` durations from `design-tokens.ts`
- [ ] Light + dark + RTL + reduced-motion verified
- [ ] Squint test: page still reads as one designed system, not base + stickers

## Suggested next pass (when user approves)

**Small, architectural** — not another hero rewrite:

1. Scroll-aware `SiteHeader` border opacity (one file)
2. `AmbientBackground`: tie orb opacity to scroll (one file)
3. Agent-scoped `--agent-accent` on dashboard + chat shells via `agentColors` (2–3 files)
4. Optional: wrap learn/catalog cards in existing `MotionCard` for consistent hover

Total: ~5 files, zero new motif components, zero new landing sections.
