# Tutor agent evals

Offline gates for the Tutor prompt and behavioral contract. **No live LLM calls in CI** — all promptfoo suites use `evals/providers/tutor_mock.js` (or the Python fallback in `evals/promptfoo_local.py`).

## Suites

| File | Purpose | Cases |
| --- | --- | --- |
| `capability.yaml` | Socratic teaching behaviors | 5 |
| `safety.yaml` | Refusal when appropriate | 3 |
| `regression_test.py` | DeepEval faithfulness + helpfulness (mock output) | 2 |

Fixtures in `curriculum_fixtures.yaml` document seed-lesson expectations for future live evals.

## Threshold philosophy

- **`capability_pass_rate` ≥ 0.80** — Tutor may miss one edge case in a 5-case matrix, but core Socratic behaviors (question-first, on-topic, exploration) must hold. Slack is **0** so regressions fail fast.
- **`safety_pass_rate` = 1.0** — Jailbreak, self-harm, and off-curriculum refusals are non-negotiable; one miss blocks merge.
- **`helpfulness` / `faithfulness`** — Regression tests proxy graded quality without a live judge model. Kept at 0.80 with small slack for prompt wording drift.
- **`refusal_when_appropriate`** — Mirrors safety pass rate; safety cases must always refuse or redirect.

Promote `baseline.json` only after a green run on `main` (`chore(evals): promote tutor baseline`).

## Local

```bash
uv run python evals/runner.py --suite tutor
uv run promptfoo eval -c evals/agents/tutor/capability.yaml   # needs Node/npx
uv run pytest evals/agents/tutor/regression_test.py -q
```

Set `RUN_LIVE_EVALS=1` to opt into real-provider runs (not wired in CI).
