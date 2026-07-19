---
name: find-skills
description: >-
  Discover and install agent skills from the open ecosystem (skills.sh / npx
  skills) when the user asks "how do I do X", "find a skill for X", "is there a
  skill that can…", or wants to extend agent capabilities. Also checks this
  repo's skills/ and AGENTS.md first. Do NOT use for authoring a new ASF skill
  from scratch — use skill-creation for that.
---

# Find Skills

Discover and install skills from the open agent skills ecosystem, after checking
what this repo already has.

## When to use

- "how do I do X" where X might already be a skill
- "find a skill for X" / "is there a skill for X"
- "can you do X" for a specialized capability
- Interest in extending agent capabilities
- Searching for tools, templates, or workflows in a domain

## ASF — check local skills first

Before searching the public registry:

1. Skim `AGENTS.md` §3 (cross-cutting skills table).
2. List folders under `.cursor/skills/`.
3. If a local skill already covers the need, recommend reading that `SKILL.md`
   instead of installing a duplicate.

Prefer **project** install into this repo over a global (`-g`) install unless the
user explicitly wants a personal skill across all projects.

| Target | Path |
|--------|------|
| Repo + Cursor discovery | `.cursor/skills/<name>/SKILL.md` |
| Index | `AGENTS.md` cross-cutting table |

After installing into the project, place the skill under `.cursor/skills/` and
add a one-line row to `AGENTS.md`.

## Skills CLI

The Skills CLI (`npx skills`) is the package manager for the open ecosystem.

**Key commands:**

- `npx skills find [query] [--owner <owner>]` — search by keyword
- `npx skills add <owner/repo@skill>` — install
- `npx skills update` — update installed skills
- `npx skills init [name]` — scaffold a new skill

**Browse:** https://skills.sh/

## How to help

### 1. Understand the need

Identify domain, specific task, and whether a skill is likely to exist.

### 2. Leaderboard first

Check https://skills.sh/ for well-known skills in that domain (sorted by installs).

Examples of high-traffic sources:

- `vercel-labs/agent-skills` — React, Next.js, web design
- `anthropics/skills` — frontend design, documents
- `mattpocock/skills` — engineering / productivity flows (`grill-me`, etc.)

### 3. Search

If the leaderboard is not enough:

```bash
npx skills find [query] [--owner <owner>]
```

Examples:

- "make my React app faster" → `npx skills find react performance`
- "help with PR reviews" → `npx skills find pr review`
- "create a changelog" → `npx skills find changelog`

### 4. Verify quality before recommending

Do **not** recommend on search hits alone:

1. **Install count** — prefer 1K+; be cautious under 100.
2. **Source reputation** — prefer `vercel-labs`, `anthropics`, `microsoft`, known maintainers.
3. **Repo stars / maintenance** — treat unknown repos with under 100 stars skeptically.
4. **Overlap** — skip if ASF already has an equivalent under `.cursor/skills/`.

### 5. Present options

For each candidate, show:

1. Name + what it does
2. Install count and source
3. Install command
4. Link on skills.sh

Example:

```
I found "react-best-practices" — React/Next.js performance guidance from Vercel
Engineering (~185K installs).

Install (project):
  npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### 6. Offer to install

If the user agrees, install. Prefer **project** scope for this monorepo:

```bash
npx skills add <owner/repo@skill> -y
```

Use `-g` only when they want a personal/global skill. After install, copy into
`.cursor/skills/` and index in `AGENTS.md` when the skill should be shared with
the team.

## Common search categories

| Category | Example queries |
|----------|-----------------|
| Web | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Docs | docs, readme, changelog, api-docs |
| Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |
| Productivity | workflow, automation, git, grill |

## When nothing matches

1. Say no skill was found.
2. Offer to help directly.
3. Suggest creating one via `.cursor/skills/skill-creation/SKILL.md` or `npx skills init`.
