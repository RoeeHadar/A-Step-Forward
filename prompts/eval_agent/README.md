# prompts/eval_agent

Versioned system prompts for the `eval_agent` agent.

- `v1.md` is the current shipped prompt.
- Never edit a shipped `vN.md` in place. Bump to `vN+1.md` and update `agent.prompt_version`.
- Each prompt change requires updated evals under `evals/agents/eval_agent/` and no regressions vs. baseline.

See `skills/prompt-authoring/SKILL.md` for the full guide.
