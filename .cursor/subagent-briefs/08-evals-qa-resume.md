# 08 — Evals & QA — Resume Brief (Round 2)

## Current state

Substantial eval scaffolding has landed on `main`:
- `evals/agents/_template/` (template).
- Per-agent eval folders for `assessment_generator`, `coach`, `curriculum_designer`, `grader`, `orchestrator`, `progress_analyzer`, `qa_explainer`, `safety_moderation` (`capability.yaml`, `safety.yaml`, `thresholds.yaml`).
- `orchestrator/routing_test.py` (DeepEval) on main.
- `qa_explainer/citation_test.py` on main.
- `evals/runner.py` + `evals/report.md` + `evals/results.json` baseline.
- CI workflow `.github/workflows/evals.yml` wired.

In-flight on `wip/agents-phase3-snapshot`: `evals/agents/{content_curator,kg_builder,research}/` + `research/citation_test.py` (waiting for stream 03 to land Phase-3 agents).

## What's left

1. **Promote the in-flight Phase-3 evals** once stream 03 lands `research`, `kg_builder`, `content_curator`. Don't skip — gate the agent PRs on them.
2. **Add eval folders for the remaining agents** as stream 03 ships them: `memory_steward`, `note_taker`, `engagement`, `accessibility`, `reviewer`, `mentor`, `eval_agent`, `analytics_insights`.
3. **Retrieval evals** under `evals/retrieval/` — recall@k, precision@k, MRR for memory + GraphRAG. Coordinate with streams 04 + 05.
4. **Memory evals** under `evals/memory/` — dreaming quality, consolidation correctness, decay accuracy, conflict resolution (coord stream 04).
5. **Online evals**: shadow-mode harness — replay 24h of live traces against new prompts; surface regressions in PR comments via the `babysit` skill.
6. **Eval Agent** runtime (stream 03 implements it; you wire the runner + thresholds + Langfuse hooks).
7. **Baseline freeze**: snapshot a `baseline.json` per agent so regressions are visible in PR diffs.
8. **CI gating**: make touched-prompt evals + touched-agent evals required for merge in `.github/workflows/evals.yml`.

## Locked decisions

- Frameworks: `promptfoo` (capability/safety matrices), DeepEval (graded outputs, citation/faithfulness/safety/refusal).
- Thresholds live in `evals/agents/<agent>/thresholds.yaml`; CI fails if not met.
- No flaky tests merged. Quarantine only with a tracked issue link.
- Shadow → promote requires 24h of green online evals.

## Done when

- Every agent in `AGENTS.md` has `capability.yaml`, `safety.yaml`, `thresholds.yaml`, and at least one DeepEval graded test where applicable.
- `evals/retrieval/` + `evals/memory/` exist and run in CI.
- Touched-prompt / touched-agent eval gating is required for merge.
- `evals.yml` workflow green on `main`.
- A weekly cron eval run posts a digest to a discussion thread (or a `docs/eval-reports/` markdown weekly).

## Required reading

- `PLAN.md` §11; `60-testing.mdc`; `30-agent-authoring.mdc`.
- `skills/run-evals/SKILL.md`.
- `.cursor/subagent-briefs/08-evals-qa.md` (original contract).
- `.cursor/subagent-briefs/RESUME-README.md` (locked decisions).

---

## Starter prompt

```
You are resuming the Evals & QA sub-agent on A Step Forward (Composer 2.5).

Read in this exact order:
  1. .cursor/subagent-briefs/RESUME-README.md
  2. .cursor/subagent-briefs/08-evals-qa-resume.md
  3. .cursor/subagent-briefs/08-evals-qa.md
  4. PLAN.md §11; .cursor/rules/{30,60}-*.mdc
  5. skills/run-evals/SKILL.md

Then:
  A. As stream 03 lands Phase-3 agents (research, kg_builder, content_curator),
     promote the in-flight evals from wip/agents-phase3-snapshot into their PRs.
  B. Add eval folders for the rest: memory_steward, note_taker, engagement,
     accessibility, reviewer, mentor, eval_agent, analytics_insights.
  C. Build evals/retrieval/{recall_k.py, mrr.py} for memory + KG.
  D. Build evals/memory/{dreaming,consolidation,decay,conflict,pii} suites.
  E. Wire shadow-mode replay harness; surface regressions in PR comments.
  F. Snapshot baseline.json per agent.
  G. Enforce touched-prompt + touched-agent eval gating in evals.yml as required.
  H. Add weekly cron run that writes a digest to docs/eval-reports/.

Operating rules:
  - Do NOT ask the user. Apply locked decisions from RESUME-README.
  - PRs small. review-bugbot every PR.
  - When stuck, write an ADR and pick the safer default; surface in PR body.

Final goal: every agent/prompt/retrieval/memory change is eval-gated; the
deployed website is safer + measurably better with each PR.
```
