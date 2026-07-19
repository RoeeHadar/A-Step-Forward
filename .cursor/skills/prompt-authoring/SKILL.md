---
name: prompt-authoring
description: How to author and version system prompts for runtime agents under prompts/. Read BEFORE creating or editing any prompt.
---

# Prompt Authoring

## Layout
```
prompts/<agent>/
  v1.md     # the system prompt as currently shipped at version 1
  v2.md     # add when changing semantics; never edit a shipped vN.md in place
  README.md # rationale, change log per version
```

## Anatomy of a good system prompt
1. **Role + mission** (2–3 lines).
2. **Audience constraints** (age-appropriate, language, accessibility).
3. **Operating principles** (Socratic, cite, refuse unsafe, prefer worked examples, etc.).
4. **Tool catalog** (1-line per tool — *describe the contract, not the implementation*).
5. **Memory protocol** (when to recall, when to commit, what types).
6. **Style guide** (markdown, length, formality).
7. **Refusal & safety policy** (clear lines + redirection script).
8. **Output schema** (concrete; agents return structured outputs).
9. **Few-shots** (rare, only when essential; prefer evals to teach behaviors).

## Versioning rules
- A shipped `vN.md` is immutable. Bump to `vN+1.md` and update `agent.prompt_version`.
- Every prompt change requires:
  - PR with eval results for capability + safety + refusal + citation.
  - No regression vs. previous baseline (within `thresholds.yaml` slack).
- Use the `eval` commit type for prompt-only PRs.

## Prompt caching
- Keep stable preamble at the top so providers (Anthropic prompt caching) can cache.
- Avoid date/randomness in cached portion.

## Pitfalls
- Don't try to encode routing logic in a prompt; that belongs in the orchestrator.
- Don't list every tool the system has; only the ones this agent can use.
- Don't hard-code dates or learner IDs; inject via the `Input` model.
- Don't fix a single failing eval with another sentence; understand the root cause first.
