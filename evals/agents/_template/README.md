# evals/agents/_template

Copy this directory to `evals/agents/<agent>/` when creating an eval suite for a new agent. See `skills/run-evals/SKILL.md`.

Required files:

- `capability.yaml` — promptfoo matrices (positive cases).
- `safety.yaml` — refusal + safety cases.
- `citation.py` — DeepEval for faithfulness + citation accuracy (skip for agents that don't cite).
- `thresholds.yaml` — per-metric pass thresholds.
- `baseline.json` — last green baseline (promoted via `chore(evals): promote …` PR).
