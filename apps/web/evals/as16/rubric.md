# AS-16 rubric: metrics, targets, scoring (spec only, not run)
Sources: agents/memory/RAG from items/AS-15/asf-coder.md §1 (summary table, Tutor section); models from apps/web/src/lib/llm-provider.ts:84-95,152-154,261 @9ecf599; requirements /workspace/asf/backlog.md t188u phase 2, t189u (read 2026-11-04).
Targets are proposed baselines (UNVERIFIED until the first run; recalibrate after the baseline run).

| id | metric | target | deterministic check | judge check |
|---|---|---|---|---|
| MEM-R | recall of the right items (misconception, plan position) in a later session | ≥0.8 of the MEM.recall checkpoints | the learner_agent_notes row exists after the session (DB read on dev, by Orchestrator only); a note tag `[[ASF_MEMORY_NOTE` was parsed (chat-memory-persist.ts:11 per AS-15) | judge: did the reply use the remembered fact correctly? 0/1 |
| MEM-F | wrong-thing forgetting: no stale or cross-topic or other-student facts | ≤5% of turns contaminated | grep the reply for planted decoy facts from other personas | judge 0/1 |
| PLAN-A | plan update after a relevant event, with an audit trail | ≥0.9 of events produce a change with a linked evidence turn id | the propose_plan_change call appears in the trace with a reason; the plan diff exists | judge: is the reason consistent with the evidence? |
| PLAN-F | no flip-flop | 0 reversals within 2 sessions without new evidence; mood-only turns cause 0 plan rebuilds (J6 s3) | diff the plan versions | — |
| ADAPT | difficulty/strategy follows the work and changing behaviour | ≥0.8 of the ADAPT checkpoints | the practice difficulty value moves in the expected direction | judge: was the strategy changed rather than repeated? |
| ROLE | role adherence + method distinctness | adherence ≥0.9; blind classifier identifies the agent from its reply ≥0.75 accuracy (4-way) | tutor gives no final answer before an attempt (regex for the final value); reviewer does not rewrite whole solutions | judge with persona specs from agent-prompts.ts:13,32,50,68 |
| RAG | groundedness: no invented facts or Bagrut content (years, question numbers, exam dates) | 0 invented Bagrut items; ≥0.95 claims supported | each cited chunk id exists in the retrieved set (trace); if kg_chunks is empty, mark the run RAG-NA (AS-15: an empty table is silently a no-op) | judge given the retrieved chunks: list unsupported claims |
| HAND | handoff coherence (digest/notes across agents) | ≥0.85 | the digest (agent-handoff-digest.ts:83 per AS-15) contains the prior misconceptions | judge: does agent B contradict agent A? |
| SITE | the decision shows up in the right site element | ≥0.9 of the SITE checkpoints | UI/DB assertion per the decision→element map (t189u phase 1 map; UNVERIFIED whether it exists yet) via Playwright on preview | — |
| SAT | simulated-student satisfaction | student-agent ≥3.5/5 AND independent judge ≥3.5/5; gap ≤1.0 | — | two separate prompts, with different models where possible |
| LAT | latency per turn | p50 ≤4 s, p95 ≤10 s to first token | Langfuse span timings | — |
| COST | cost per turn | ≤$0.003 per agent turn on Groq (see cost-estimate.md) | Langfuse token usage × price table | — |

## Judge prompt outline
System: "You are an impartial evaluator of a tutoring system. You get: persona, session transcript, retrieved chunks, memory notes before/after, plan before/after, and checkpoint list. For each checkpoint output JSON {id, pass:0|1, score_1to5?, evidence_quote, reason≤30 words}. Do not reward fluency; penalise invented exam facts." Run at temperature 0, 2 samples, disagreement → third sample.
Student-agent: plays the persona, follows the scripted turns, may improvise only within `behaviour`, and rates the session at its end on 1-5 for helpfulness, felt-understood and would-return.

## Langfuse use
Each journey run = one Langfuse session; each turn = a trace tagged {journey, lang, session, agent, release_sha}. The scorer reads from the traces: tool calls (retrieve, propose_plan_change), retrieved chunk ids, token usage and latency. Scores are written back as Langfuse scores per checkpoint, and the dataset = journeys.yaml for run comparison across releases. (Langfuse env var NAMES are UNVERIFIED at 9ecf599; not checked.)

## Regression
Every metric is a gate: a release fails if any metric drops >5 points below the stored baseline or misses a hard zero target (RAG invented-Bagrut, PLAN-F). Re-run after every agent/memory/prompt change (t189u).
