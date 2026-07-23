# ADR 0012: Authoritative learner-facing context under conversational pressure

- **Status:** Accepted
- **Date:** 2026-07-23
- **Deciders:** Product owner + Composer (grilling session)
- **Extends:** [ADR-0011](0011-agent-communication-quality.md)
- **Source:** Post-0011 transcript — anxiety about schedule → agent denied knowing the plan, dumped briefing fields, misread `5pt`, offered a new plan then denied changing it, asked a stressed learner to pick a topic, mixed “at risk” with empty reassurance, broken Hebrew.

## Context

ADR-0011 reduced XP dumps, invented bridges, and filler loops. A new production-like transcript showed the **same underlying disease**: under conversational pressure the model still fails to *comply with injected contracts* — it denies knowledge of injected facts, dumps or misreads them, improvises plans/menus, and contradicts pace data with empty reassurance.

The transcript is a **symptom**; the cure targets the **disease class**: contract non-compliance under pressure (pushback, anxiety, “what now?”, “you’re my teacher”).

## Decision

### Success bar

1. Never claim not to know plan/status when packs are injected.
2. Pressure turns follow a fixed contract: validate → honest status → **one** next action → offer to start it.
3. No inventing a second plan; no topic menus for anxious learners.
4. Learner-facing text is server-authored HE+EN (paraphrase only); natural Hebrew; ban garbage patterns.

### Mechanism

1. **Server-authored learner-facing status packs** (deterministic HE + EN paragraphs) plus structured briefing for the model.
2. **Pressure-family intents**: anxiety, status, readiness, study-next under stress, context challenge (“אתה לא יודע?”), plan ownership (“יש לי כבר תוכנית”).
3. **Next-step picker** (code): lowest-mastery active-week concept → else first active → else planner path[0]. Emitted in the pack as the only default next action.
4. **Hard bans**: deny-knowledge phrases; raw goal keys; “5pt means already learned”; empty “you can do everything” when pace is `at_risk`; known broken-Hebrew patterns.
5. **Eval matrix** for the pressure family (offline + live), not only the single transcript.

### Out of scope

New MCP/tools, model swap, hard Mentor auto-switch, dreaming changes, full persona Hebrew rewrite.

## Consequences

**Positive:** Agents stay grounded when learners push; anxiety gets one clear action; status sounds human.

**Risks:** Intent false positives (mitigate with priority order + tests); packs must stay short or they become dumps again.

## Alternatives considered

- Prompt-only reminders — rejected (0011 already insufficient under pressure).
- LLM-authored status on the hot path — rejected (latency/cost/nondeterminism).
- Hard auto-switch to Mentor — deferred.
