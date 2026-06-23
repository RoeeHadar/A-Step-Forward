# Contributing — Sub-Agent Playbook

You are most likely a **Composer 2.5** or **Cursor Auto** sub-agent picking up work. Follow these rules.

## 1. Before you write any code

1. Read `PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md`.
2. Read your assigned brief in `.cursor/subagent-briefs/NN-<stream>.md`.
3. Read every project skill that brief points to (under `skills/`).
4. Check `.cursor/rules/` — these apply globally.
5. Pull latest `main` and create a branch `feat/<stream>/<short-name>` or `fix/<stream>/<short-name>`.

## 2. While you work

* Stay inside the **in-scope files** listed in your brief. If you need to touch something out-of-scope, leave a note in the PR description; do **not** sprawl.
* Honor the contracts: typed Pydantic schemas, agent base classes, memory APIs. Never bypass the Memory Service to read/write rows.
* No `any` in TypeScript, no untyped functions in Python. Use Zod / Pydantic everywhere.
* If you change a prompt or agent, add/update its eval in `evals/`. Prompt PRs without an eval are blocked.
* Use conventional commits: `feat(memory): add decay sweep`.
* Run `ruff format`, `ruff check`, `mypy`, `prettier`, `eslint`, and the local test suite before pushing.

## 3. Tests & evals

* Unit tests live next to the code (`tests/` per package).
* Integration tests live under the top-level `tests/`.
* Agent evals: `evals/agents/<agent>/*.yaml` (promptfoo) and `evals/agents/<agent>/*.py` (DeepEval).
* Retrieval evals: `evals/retrieval/`.
* Memory evals: `evals/memory/` (consolidation, decay, conflict-resolution, dreaming quality).

## 4. PRs

* Title: conventional commit.
* Body: link to the brief, list acceptance criteria checked, paste eval summary, screenshots/GIFs for UI.
* CI must be green (lint, types, unit, integration, evals).
* Use the `review-bugbot` skill on every PR; `review-security` on PRs touching auth, memory, PII, payment, or RBAC.

## 5. Sub-agent etiquette

* Don't escalate to Opus unless you hit a *real* architectural decision not covered by the plan. Otherwise stay in lane.
* Prefer **many small PRs** (use the `split-to-prs` skill) over giant ones.
* When stuck for more than ~15 min, write a short note in `docs/sessions/<YYYY-MM-DD>-<stream>.md` and ask in the PR description.
* Honor cost budgets. Cache. Avoid Opus in runtime hot paths unless the eval shows it's required.

## 6. Local quickstart

```bash
docker compose -f infra/docker-compose.yml up -d
# Backend
cd apps/api && uv sync && uv run alembic upgrade head && uv run uvicorn app.main:app --reload
# Frontend
cd apps/web && pnpm install && pnpm dev
# Evals
cd evals && uv run promptfoo eval -c agents/tutor/basic.yaml
```
