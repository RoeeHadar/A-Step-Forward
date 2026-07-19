# Repo Memory Snapshot

> Loaded by the `agentStart` Cursor hook. Keep it short and current.
> Dreamed / consolidated: 2026-07-16.

## Project

**A Step Forward** — AI-native learning center. Master plan: `PLAN.md`.

## Cursor layout (canonical — do not re-litigate)

```
.cursor/skills/     ← Agent Skills (auto-discovered) — 44 skills live HERE
.cursor/agents/     ← Cursor custom subagents (auto-discovered)
.cursor/rules/      ← *.mdc always-on rules
.cursor/hooks.json + .cursor/hooks/*.py
.cursor/mcp.json
.cursor/subagent-briefs/  ← tickets only (NOT auto-discovered; agents point here)
AGENTS.md           ← KEEP AT REPO ROOT (Cursor auto-loads)
packages/agents/    ← PRODUCT runtime agents (not IDE config)
```

Bare repo `skills/` is **retired** (not a Cursor discovery path). See `.cursor/README.md`.

## Product invariants (hard)

- Free-tier critical path = **Vercel + Neon direct** — never import heavy `neon-db` / kg-data on onboarding or lesson-complete cold paths.
- First plan: thin bootstrap `apps/web/src/lib/onboarding-plan-bootstrap.ts` (2 weeks × ≤4 concepts).
- Lesson complete: thin `apps/web/src/lib/lesson-complete.ts` + mastery ≥0.7 → plan shows Done.
- Plan mutations: Tutor sidebar template only.
- Bilingual HE-default; math LTR in `$...$` / `$$...$$`; no external learner links.
- Auth: Clerk JWT; never trust client `learner_id` / role.

## Last session dream (2026-07-16)

**Shipped / done in this arc**

| Item | Notes |
|------|--------|
| Diagnostic → plan timeouts | Fixed via thin bootstrap; rolling 2-week window; no advisory-lock `1/0` on first plan |
| Lesson complete hang | Thin route; button clears spinner; plan mastery update |
| About-me / HE toggle | Memory persona + style labels + agent blurbs follow locale |
| grill-me + find-skills | Added under `.cursor/skills/` |
| Skills promotion | All project skills moved `skills/` → `.cursor/skills/`; refs updated |
| Cursor agents | 13 defs in `.cursor/agents/`; hooks scripts → `.cursor/hooks/` |

**Deployed commits (earlier):** `d93421f` lesson-complete/i18n; `ab196d1` test mock; `afb204a` grill-me; `03ca744` find-skills.

**Uncommitted (local):** skills move + `.cursor/agents/` + hooks relocation + AGENTS/rules path updates — **commit when user asks**.

**Ops note:** `user-asf-obsidian` MCP was errored last check — use filesystem `obsidian-vault/` fallback.

## Working next

1. Commit/push Cursor layout rearrangement if approved.
2. New Agent chat after layout commit so Cursor rescans skills/agents (this chat is context-heavy).
3. Obsidian MCP re-enable if vault tools needed.

## Do not

- Reintroduce bare `skills/` as a discovery root.
- Put `AGENTS.md` under `.cursor/`.
- Confuse `packages/agents` (product) with `.cursor/agents` (IDE).
<!-- LAST_SESSION -->
Last session: 2026-07-16 (layout + dream consolidation)
<!-- LAST_SESSION -->
