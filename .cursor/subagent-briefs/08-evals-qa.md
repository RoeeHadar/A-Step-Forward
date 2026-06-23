# 08 — Evals & QA

## Goal
Build the evals harness, CI gates, online-eval dashboards, and Playwright E2E for **A Step Forward**. Make eval coverage a prerequisite for any prompt/agent/memory PR.

## In-scope files
- `evals/**`
- `tests/**` (cross-cutting)
- `.github/workflows/evals.yml`
- `apps/web/playwright/**`

## Out-of-scope
- Implementing the agents themselves (03).
- Implementing services (02, 04, 05).

## Tools
- **promptfoo** for prompt matrices and regression baselines.
- **DeepEval** for grader-style evals (faithfulness, helpfulness, citation accuracy, safety, refusal).
- **Playwright** for E2E.
- Custom Python harness `evals/runner.py` that aggregates suite results and writes a markdown report + JSON.

## Required suites
- `evals/agents/<agent>/` — capability, safety, refusal, citation, regression.
- `evals/retrieval/` — recall@k, precision@k, MRR for memory & GraphRAG.
- `evals/memory/` — dreaming quality, consolidation correctness, decay accuracy, conflict-resolution correctness, PII redaction.
- `evals/e2e/` — Playwright flows.

## Required reading
1. `PLAN.md` §11.
2. `.cursor/rules/60-testing.mdc`.
3. `skills/run-evals/SKILL.md`.

## Acceptance criteria
- `make evals` runs the full local suite and prints a report.
- CI runs touched-prompt and touched-agent suites on PR; blocks regressions vs. baseline.
- Online shadow-eval pipeline samples 1% of prod traffic and writes to Langfuse + Postgres.
- Playwright smoke test runs on every PR.

## Starter prompt
```
You are a Composer 2.5 sub-agent on the A Step Forward project.
Read in this order:
  PLAN.md (§11),
  .cursor/rules/60-testing.mdc,
  skills/run-evals/SKILL.md,
  .cursor/subagent-briefs/08-evals-qa.md (this file).
Stand up promptfoo + DeepEval harness, write the runner, write CI workflow.
Then add the Phase-1 eval suites for Tutor and the Memory service.
```
