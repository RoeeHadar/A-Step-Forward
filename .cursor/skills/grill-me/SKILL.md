---
name: grill-me
description: >-
  Relentless one-question-at-a-time interview to stress-test a plan or design
  until shared understanding is confirmed. Use when the user says "grill me",
  "/grill-me", "stress-test this plan", "interrogate this design", or wants to
  sharpen a feature/ADR/product idea before building. Do NOT use for ordinary
  implementation, code review, or architecture review — use code-review /
  architecture-review for those.
---

# Grill Me

Interview the user relentlessly about every aspect of this plan until we reach a
shared understanding. Walk down each branch of the design tree, resolving
dependencies between decisions one-by-one.

## Rules

1. **One question at a time.** Wait for feedback before continuing. Asking
   multiple questions at once is bewildering.
2. **Recommend an answer** with every question (your best default given the
   repo, PLAN.md, and prior answers). The user can accept, reject, or amend.
3. **Facts vs decisions.** If a *fact* can be found by exploring the codebase,
   look it up rather than asking. The *decisions* are the user's — put each one
   to them and wait.
4. **Do not enact the plan** (no implementation, commits, PRs, or file edits
   that ship the design) until the user explicitly confirms shared understanding.
5. **Stay in interview mode** until that confirmation. Summarize only when a
   branch is closed or when the user asks for a recap.

## ASF context (when relevant)

Before grilling product/architecture work in this monorepo, skim as needed:

- `PLAN.md`, `ARCHITECTURE.md`, `docs/architecture/current-state.md`
- Relevant skill under `skills/` (e.g. `neon-direct-route`, `use-learning-plan`,
  `onboarding-flow`, `diagnostic-plan-golden-path`)
- Obsidian active context: `obsidian-vault/_active-context.md`

Prefer grounding recommendations in existing ASF constraints (Vercel+Neon free
tier, bilingual HE-default, no external links in learner content, Clerk auth,
plan/template-only mutations) instead of inventing greenfield options.

## Session close

When the user confirms shared understanding, output a short **decisions log**:

- Goal / non-goals
- Decisions made (bullet list)
- Open questions deferred
- Suggested next skill or stream (if any)

Then stop unless they ask to implement.
