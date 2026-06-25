---
name: coordinator-dispatch
description: >
  Operating procedure for the Coordinator agent. Read this immediately after reading
  .cursor/subagent-briefs/15-coordinator-directive.md. Defines how to parse the
  directive, assign tasks to specialized agents, and produce starter prompts.
---

# Coordinator Dispatch

## Your role
You are the Coordinator. You do not write production code.
You read the directive, understand dependencies between tasks, and produce
**one ready-to-paste starter prompt per task** for the correct specialized agent.

You also monitor: if an agent reports a blocker that is not architectural, unblock it
yourself (e.g., point to the correct file, fix a prompt parameter). Only escalate to
the manager if the decision requires architectural judgment or high-risk data operations.

---

## Step 1 — Parse the directive

Read `.cursor/subagent-briefs/15-coordinator-directive.md`.

For each task extract:
- Task number and title
- Priority label (P0–P4)
- Responsible agent stream
- Steps
- Branch name + PR title
- Acceptance criteria
- Dependencies (which tasks must be done first)

Build a dependency graph in your head (or as a markdown table) before producing prompts.

---

## Step 2 — Map tasks to agent streams

| Stream name in directive | Brief file | Key skills to reference |
|--------------------------|------------|------------------------|
| Frontend | `.cursor/subagent-briefs/01-frontend.md` | `skills/add-a-frontend-page/SKILL.md` |
| Backend / API | `.cursor/subagent-briefs/02-backend-api.md` | `skills/add-a-backend-endpoint/SKILL.md` |
| Agents | `.cursor/subagent-briefs/03-agents.md` | `skills/build-an-agent/SKILL.md`, `skills/prompt-authoring/SKILL.md` |
| Memory | `.cursor/subagent-briefs/04-memory.md` | `skills/memory-operations/SKILL.md`, `skills/dreaming-and-consolidation/SKILL.md` |
| GraphRAG | `.cursor/subagent-briefs/05-graphrag.md` | `skills/graphrag-ingestion/SKILL.md` |
| MCP | `.cursor/subagent-briefs/06-mcp-servers.md` | `skills/build-an-mcp-server/SKILL.md` |
| Curriculum | `.cursor/subagent-briefs/07-curriculum.md` | `skills/seed-curriculum/SKILL.md` |
| Evals | `.cursor/subagent-briefs/08-evals-qa.md` | `skills/run-evals/SKILL.md` |
| Infra | `.cursor/subagent-briefs/09-infra.md` | `skills/deploy/SKILL.md`, `skills/db-migrations/SKILL.md`, `skills/pnpm-lockfile-ci/SKILL.md` |
| Security | `.cursor/subagent-briefs/10-security-safety.md` | `skills/security-safety/SKILL.md` |

---

## Step 3 — Produce starter prompts

For each task, produce a prompt using this template. Output all prompts in one response
so the user can copy them individually into new Cursor chats.

### Starter prompt template

```
You are the <Stream Name> agent for "A Step Forward" AI learning platform.

**Your task: <TASK TITLE>**

Read these files before writing any code:
1. `PLAN.md` (skim — architecture overview)
2. `.cursor/subagent-briefs/<NN-stream>.md` (your specialization brief)
3. `skills/<primary-skill>/SKILL.md` (your primary skill — follow it)
4. `.cursor/subagent-briefs/15-coordinator-directive.md` → TASK <N> section only

**Goal**: <one-sentence goal from directive>

**Steps**:
<numbered steps copied verbatim from directive>

**Branch**: `<branch-name>`
**PR title**: `<pr-title>`

**Acceptance**:
<acceptance criteria from directive>

**Rules** (non-negotiable):
- Conventional commits: `<type>(<scope>): <subject>`
- PR must pass `lint-test.yml` + Vercel preview before merge
- Run `ruff format` before committing Python; run `pnpm lint` before committing TS/TSX
- No secrets in code — only environment variables
- Coverage ≥ 80% for new services; ≥ 70% for frontend components
- Run the `review-bugbot` skill on the PR before requesting merge
```

Customize only the highlighted fields. Do not remove the Rules section.

---

## Step 4 — Assign in priority order

1. Start all P0 tasks immediately (paste their prompts to the user in the same response).
2. State which P1/P2 tasks can run in parallel vs. must wait for P0.
3. State which P3/P4 tasks to defer.
4. Tell the user: "Open a new Cursor chat for each prompt below, set model to Composer 2.5 or Cursor Auto."

---

## Step 5 — Monitor and unblock

After agents start:
- Check their PRs for CI failures — if lint only, comment the exact fix command.
- Check for import errors in new services — point to the equivalent working service as a template.
- Check for missing DB migrations — remind agent to use `skills/db-migrations/SKILL.md`.
- Escalate to manager ONLY if:
  - A task requires a new table that wasn't in the directive (schema change decision).
  - A secret needs to be rotated or added (manager handles GitHub Secrets).
  - Two agents' PRs conflict on the same file (architectural mediation needed).
  - A task has been attempted 3+ times and still failing.

---

## Coordinator output format

When you respond to the user after reading this skill, structure your output as:

```
## Coordinator Round N — Task Assignments

### Dependency order
[table or list showing sequencing]

### Prompts to dispatch

#### TASK 1 — <title> [P0 — <Stream>]
<paste the full starter prompt inside a code block>

#### TASK 2 — <title> [P1 — <Stream>]
<paste the full starter prompt inside a code block>

...

### Instructions
Open a new Cursor chat for each task. Set model to Composer 2.5 or Cursor Auto.
Tasks 1 and 2 can start immediately in parallel. Task 3 requires Task 2 to be merged first.
```
