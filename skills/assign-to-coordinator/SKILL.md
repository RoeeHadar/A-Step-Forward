---
name: assign-to-coordinator
description: >
  Standard operating procedure for the manager/supervisor (Opus) when handing off
  a new batch of tasks to the Coordinator agent. Read this skill BEFORE updating
  .cursor/subagent-briefs/15-coordinator-directive.md and producing a handoff prompt.
---

# Assign to Coordinator

## When to use
- After any architectural decision, major phase completion, or significant blocker is resolved.
- When the current coordinator directive is stale (tasks completed or priorities shifted).
- When the user asks "what's next?" or asks you to give tasks to the coordinator.

## What this skill does NOT do
You (the manager) do not write code, do not open branches, and do not merge PRs.
You set direction, resolve architectural ambiguity, and approve high-risk migrations.
Everything else goes to the coordinator.

---

## Step 1 — Assess the current state

Before writing anything, confirm:
1. What phases / tasks are **done** (CI passing, merged to main)?
2. What is **in-flight** (open PR, branch exists)?
3. What is **blocked** (dependency missing, secret not set, architectural question)?
4. What is the next highest-value thing to ship?

Read the following to assess state:
- `git status` (untracked / modified files signal in-flight work)
- `.cursor/subagent-briefs/15-coordinator-directive.md` (previous directive)
- `.cursor/subagent-briefs/RESUME-README.md` (overall progress)
- Recent GitHub Actions runs for CI status

---

## Step 2 — Write the coordinator directive

Update `.cursor/subagent-briefs/15-coordinator-directive.md`.

### Directive structure (always follow this template)

```markdown
# Coordinator Directive — Round N (YYYY-MM-DD)

Read `14-adaptive-learning-architecture.md` for the full vision.

## Current state
| Item | Status |
|------|--------|
| Live frontend URL | ... |
| Live backend URL | ... |
| Last merged phase | ... |
| Databases | ... |

## Task list
### TASK 1 — <title> [P0 — <Stream> agent]
**Goal**: one sentence.
Steps: numbered, concrete, no ambiguity.
Branch: `feat/<stream>/<name>`
PR title: `<type>(<scope>): <subject>`
Acceptance: what does "done" look like?

### TASK 2 — ...
...

## Rules for all agents
(copy from previous directive, update only if rules change)

## Coordinator responsibilities
- Sequencing constraints between tasks
- When to escalate to manager
```

### Priority labels
- **P0** — site is broken or a user-facing flow is blocked; fix before anything else
- **P1** — core feature for the next user-visible milestone
- **P2** — major phase work, not yet user-visible
- **P3** — parallel or lower priority; can be assigned to an agent with spare capacity
- **P4** — housekeeping; assign only if no P0-P3 work is available

### Task granularity rules
- One task = one branch = one PR.
- If a task requires touching both frontend and backend, split into two sub-tasks with explicit interface contract between them.
- Always name the **agent stream** responsible: `Frontend`, `Backend`, `Agents`, `Memory`, `GraphRAG`, `MCP`, `Curriculum`, `Evals`, `Infra`, `Security`.

---

## Step 3 — Produce the coordinator handoff prompt

After updating the directive, give the user the **exact text** to paste into a new Cursor chat
(model: **Composer 2.5** or **Cursor Auto**) for the coordinator.

### Coordinator prompt template

```
You are the Coordinator for "A Step Forward" AI learning platform.

Read these files in order before doing anything else:
1. `PLAN.md`
2. `ARCHITECTURE.md`
3. `AGENTS.md`
4. `.cursor/subagent-briefs/00-README.md`
5. `.cursor/subagent-briefs/15-coordinator-directive.md`  ← your task list
6. `skills/coordinator-dispatch/SKILL.md`               ← your operating procedure

Then follow the coordinator-dispatch skill to assign each task in the directive
to the correct specialized agent. For each task, produce the full starter prompt
that the specialized agent should receive (use the templates in coordinator-dispatch/SKILL.md).

Do not write code yourself. Your job is to read, plan, and produce prompts.
```

Customize the prompt only if there is a specific first task to highlight or a blocker to mention.

---

## Step 4 — Update RESUME-README.md

After the directive is written, update `.cursor/subagent-briefs/RESUME-README.md`:
- Mark completed phases ✅
- Note the current round number and date
- List the active branch(es)
