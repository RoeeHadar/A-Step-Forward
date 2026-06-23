# prompts/content_curator

Versioned system prompts for the `content_curator` agent.

- `v1.md` is the current shipped prompt.
- Never edit a shipped `vN.md` in place. Bump to `vN+1.md` and update `agent.prompt_version`.
- Each prompt change requires updated evals under `evals/agents/content_curator/` and no regressions vs. baseline.

See `skills/prompt-authoring/SKILL.md` for the full guide.
