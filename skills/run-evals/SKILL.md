---
name: run-evals
description: How to run, write, and gate on evals (promptfoo + DeepEval + custom runner). Read BEFORE changing any prompt, agent, retrieval, or memory hygiene component.
---

# Run Evals

## Layout
```
evals/
  agents/<agent>/
    capability.yaml       # promptfoo matrices
    safety.yaml           # safety + refusal
    citation.py           # DeepEval (faithfulness, citation accuracy)
    thresholds.yaml       # per-metric pass thresholds
    baseline.json         # last green baseline
  retrieval/
    memory_recall.yaml
    kg_recall.yaml
  memory/
    dreaming/*.yaml
    consolidation/*.yaml
    decay/*.yaml
    conflict/*.yaml
  e2e/                    # Playwright
  runner.py               # aggregate runner
```

## Local
```bash
# everything
make evals
# touched-only (default in CI)
uv run python evals/runner.py --touched
# a single suite
uv run promptfoo eval -c evals/agents/tutor/capability.yaml
uv run python -m deepeval test run evals/agents/tutor/citation.py
```

## CI gates
- `lint-test.yml` — lint/types/units always.
- `evals.yml` — touched-prompt + touched-agent suites must pass *and* not regress vs. `baseline.json` within `thresholds.yaml` slack.
- Promote baseline: open a PR with `chore(evals): promote <agent> baseline`. Requires manual review.

## Writing a new suite
- Start from `evals/agents/_template/`.
- Use the seed curriculum + a synthetic learner profile.
- Cover: capability, safety, refusal-when-appropriate, citation accuracy, latency budget, token budget.

## Shadow / online evals
- 1% sample of prod traffic re-graded; results to Langfuse + `eval_online` Postgres table.
- Alerts on metric drift > 5% over a rolling 24h.

## Pitfalls
- Don't relax thresholds to make a PR green — fix the regression or open an ADR.
- Don't write evals that hit live external tools without mocking; flake will block everyone.
- Don't grade with the same model that produced the answer; use a different model as judge (or `gpt`/`claude` cross).
