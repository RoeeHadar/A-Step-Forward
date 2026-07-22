# ADR 0011: Agent communication quality (grounded, anti-filler)

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** Product owner + Composer (grilling session)
- **Extends:** [ADR-0010](0010-assessment-driven-progression.md) (humble readiness). Constrained by [ADR-0006](0006-neon-direct-critical-path.md).
- **Source:** Grilling session 2026-07-22 on live Tutor/Mentor chat failures (status dumps, invented topic bridges, wrong math, filler loops, mid-answer truncation, overconfident bagrut %).

## Context

Live website agents already inject profile, XP, plan weeks, persona, and pacing into the system prompt, and already have brevity / exam-readiness interaction modes. In production chats, learners still received:

1. **Raw field dumps** (XP, ISO dates, repeated gate lines) instead of plain-language answers.
2. **Invented curriculum links** (e.g. geometric series “explains” ∫x²) with no KG edge or authored lesson support.
3. **Wrong “simplified” math** (∫₀¹ x² = 1) after the learner asked for an easier path.
4. **Filler loops** (“אני חושב שזה יעזור”, “אני צריך להסביר זאת בצורה שונה”) and restarts on “המשך”.
5. **Mid-formula truncation** at `CHAT_CONTEXT.maxOutputTokens = 768`, then the same lecture restarted.
6. **Overconfident exam claims** (~100% on the bagrut), contradicting ADR-0010 humble readiness.

Soft prompt poetry alone was insufficient; the same skills already said “answer first, don’t recap context.”

## Decision

### Success bar (v1)

1. **Grounded correctness** — no invented topic bridges; no wrong solutions; no guaranteed exam %.
2. **Anti-filler / answer-the-question** — plain learner language; ban-list stock phrases; continuation without restart.

Tone polish and new MCP/tools are **wave 2**.

### Scope

- Shared bar: all four live agents (Tutor, Mentor, Coach, Reviewer).
- Hard grounding for math/curriculum claims: Tutor + Coach when explaining.
- Mentor framing owns status / XP / plan / readiness narration; no hard agent auto-switch in v1.

### Enforcement (wave 1)

1. Hard behavioral contract in `agent-skills.ts` + chat-route intent blocks (corpus/KG only, or say the corpus does not support the link; redirect over invent).
2. Pre-summarized **bilingual (HE + EN)** learner progress briefing; agents must paraphrase — never paste XP/ISO/raw keys/repeated gate lines.
3. Intent injects `THIS TURN — progress/readiness` (and recovery / continue) blocks; soft Mentor nudge only.
4. Mandatory **recovery protocol** when the learner says too hard / simplify / do I need this: drop failed path, honest plan-scope, simplest *correct* method, optional private note.
5. Adaptive `maxOutputTokens` (default ~768; worked-solution / continue ~1200–1500) + chunked long solutions + truncation “continue from here” UX when `finish_reason=length`.
6. Memory: light private-note guidance only; no dreaming/consolidation changes.
7. Merge gate: promptfoo/unit regression matrix from the transcript cases + HE pilot smoke.

### Explicitly out of wave 1

New MCP tools, math verifier, hard Mentor switch, dreaming pipeline changes, Cursor IDE hooks.

## Consequences

**Positive**

- Agents answer status and teaching questions in learner language with humble readiness.
- Invented bridges and wrong simplifications become evaluable regressions.
- Truncation becomes recoverable instead of a restart loop.

**Costs / risks**

- Larger worked-solution token budget on some turns (cost/latency).
- Intent false positives (mitigate with priority-ordered classifiers + tests).
- Briefing must stay short or it re-creates dump pressure.

## Alternatives considered

- Prompt-only tweaks — rejected (already failed in prod).
- Always auto-switch to Mentor on status — deferred (jarring UX).
- Inline math verifier tool — deferred to wave 2 if evals still fail.
