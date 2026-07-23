# ADR 0013: Intensive practice arena

- **Status:** Accepted (v2 — open exam-style, 2026-07-23 grill)
- **Date:** 2026-07-23
- **Deciders:** Product owner + Composer (grilling sessions)
- **Related:** [ADR-0011](0011-agent-communication-quality.md), [ADR-0012](0012-agent-context-under-pressure.md), custom quiz / process-grader seal pattern

## Context

Learners need a **continuous practice arena** distinct from lessons and timed mock exams: deliberate open exam-style reps on topics they choose, with trustworthy supply, no recycle, Finish → summary, and student/teacher review.

## Decision (v2)

### Product

1. Surface **`/app/practice`**: one item at a time; **no timer**. Soft goals optional; always-visible **Finish training**.
2. **Topic multi-select** from a curated bilingual full-catalog topic list (not limited to the active plan). Remember last selection. Topics locked for the session.
3. **Open-first** (≥~90%): `open` / constructed response; rare closed only when exam-faithful. Typed answers + side KaTeX cheat sheet. Bilingual stems by UI locale; no language mix; math integrity gates.
4. **Exam register** from learner goal (bagrut/uni); difficulty adapts from recent process success (≥~0.6) and light mastery.
5. **No recycle** permanently per learner (authored `question_id` + generated stem fingerprint). Authored-first + gated LLM fill + promote path; honest thin-topic UI — never recycle, never junk MCQ filler.
6. **Hints + Coach**: 3-step ladder + in-panel Coach no-answer until graded.
7. **Grading**: process/rubric for open (partial credit); mastery + XP on success.
8. **Review**: finished sessions persisted; learner history + linked teacher (test-attempts RBAC pattern).

### Replaces wave-1 defaults

Closed-first server queue, due/explore as main modes, and MCQ-as-default are superseded on the same route.

## Consequences

**Positive:** Learners train what they intend; exam thinking + form; durable history for teachers.

**Risks:** Open grading latency/cost; topic bank depth — mitigate with gates + authored expansion.

## Alternatives considered

- Server-picked weak-atom queue only — rejected (learners know what they want).
- Fold into mock exam — rejected (no clock; endless reps).
- Photo upload of work — deferred.
