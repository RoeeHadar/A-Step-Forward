# ADR 0015: Agent Chat Recovery

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product owner + Composer (grill-me + recovery plan)
- **Related:** [ADR-0011](0011-agent-communication-quality.md), [ADR-0012](0012-agent-context-under-pressure.md), [ADR-0014](0014-coach-hybrid-tools-solver.md)

## Context

Live website agents (Tutor, Mentor, Coach, Reviewer) answered simple questions with unrelated plan/status dumps, broken Hebrew, and invented ASF mappings. Root causes: chat hard-routed to a single cheap 8B model; always-on oversized context; Tutor intent contracts leaking to other agents; anxiety false positives on math stems; mid-stream whitespace trim; soft repair appended **after** bad text was already shown; evals mostly mock-only.

## Decision

1. **Quality-first model policy** for learner answers (`resolveChatModelChain` → primary quality chain). Escape hatch: `CHAT_MODEL_POLICY=cheap|volume`. Classifiers/background keep cheap 8B via `resolveClassifierModelChain`.
2. **Hybrid knowledge:** general model knowledge by default; injected ASF plan/profile/mastery/curriculum authoritative when present and relevant. Cite ASF only when packs were used.
3. **Relevance-gated context** via `buildContextNeeds` — status/active-week/XP/profile/mastery skipped on pure teach turns. Tutor THIS TURN overlays only for Tutor.
4. **Deterministic language** per turn: explicit request → latest substantive message → profile → UI locale (`chat-response-language.ts`).
5. **Buffered quality gate:** score full draft; one compact repair retry; then chunk-emit. No post-display repair appends. Stream strip uses `trim: false`.
6. **Typed section budgeting** (`chat-context-builder.ts` + `fitSystemSections`): whole packs drop under budget; core identity never dropped mid-instruction.
7. **Trust hierarchy:** current message > verified profile/plan/mastery > recent turns > inferred persona/notes > handoff digests. Notes relevance-filtered.
8. **Rollout:** flags (`CHAT_MODEL_POLICY`); canary on pilot account; human HE/EN transcript review; rollback by env flag without reverting learner data.

## Consequences

**Positive:** Ordinary questions answered in the learner's language; less context hijacking; stronger multilingual model by default; failed drafts not shown.

**Risks:** Higher latency/cost on quality models; over-aggressive gating may omit useful profile on borderline turns — tune via needs router + evals.

## Alternatives considered

- Keep corpus-only answers — rejected (breaks ordinary Q&A and caused refusals/hallucinated mappings).
- Stream-then-append soft repair — rejected (learner already saw bad text).
- Cheap-only chat with better prompts — rejected (Hebrew coherence insufficient).

## Canary / rollback

1. Ship with `CHAT_MODEL_POLICY` unset (quality default).
2. Canary pilot account; compare HE/EN transcripts vs pre-change.
3. Rollback: set `CHAT_MODEL_POLICY=cheap` on Vercel (no data migration).
4. Production-shaped vitest fixtures under `apps/web/src/lib/chat-*.test.ts`; promptfoo matrix in `evals/agents/tutor/chat_recovery.yaml`.
