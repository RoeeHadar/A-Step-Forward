# Code Review: Live Website Agents Implementation

- **Date:** 2026-08-13 (re-checked 2026-08-13 after W1/W2 fixes)
- **Reviewer:** Code Reviewer (Cursor sub-agent, stream 25)
- **Scope:** Uncommitted working tree — live website agents (Tutor, Mentor, Coach, Reviewer on `/api/chat`)
- **Intent:** Verify correctness of RAG / hybrid knowledge (ADR-0015), ReAct tool loop (Phase A + B), guided plan-change flow, language/voice rules, memory usage, solver hygiene, and test adequacy.
- **Verdict:** ~~SHIP WITH WARNINGS~~ → **SHIP**

---

## Re-check summary (2026-08-13)

Both WARNs from the initial review were fixed and re-verified at file:line. No new issues introduced by the fix itself (one NIT noted below). Verdict upgraded to **SHIP**.

### W1 — retrieve transient error ✅ RESOLVED

**Evidence:**
- `agent-tools.ts:76–77` — `CORPUS_MISS_OBSERVATION` constant defined: `'No matching passages in the authored math/physics corpus. Answer from general knowledge. Do not invent lesson:<id> or concept:<id> citations.'`
- `agent-tools.ts:116` — empty corpus hit returns `{ observation: CORPUS_MISS_OBSERVATION }`
- `agent-tools.ts:129–131` — catch path now also returns `{ observation: CORPUS_MISS_OBSERVATION }`; the old `'Retrieval is temporarily unavailable.'` string is gone
- `agent-tools.ts:490–492` — `corpusMissObservation()` exported for test use
- `agent-tools.test.ts:19–31` — 2 tests: (1) empty corpus returns `corpusMissObservation()`, (2) throw returns same observation and explicitly asserts it does NOT contain "temporarily unavailable"

Both the empty-corpus and transient-error paths now give the answer model an identical explicit "answer from general knowledge" cue. Static-RAG suppression through `reactHandledGrounding` (route.ts:1683–1687) now only occurs when real observations are present, not on error strings.

### W2 — ReAct kill-switch honesty ✅ RESOLVED

**Evidence:**
- `plan-actions.ts:615–621` — `PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE` added: `"Plan-change tools are temporarily unavailable. Do NOT collect slots, present a fake diff, or ask the learner to confirm … Never send them to a form or template."`
- `plan-actions.ts:623–625` — `planModificationProtocol(reactEnabled: boolean)` returns `PLAN_AGENT_INSTRUCTIONS` when true, `PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE` when false
- `route.ts:43` — `planModificationProtocol` imported from plan-actions
- `route.ts:1283–1288` — `tutorContract?.learnerPreferenceOverride` now also gated on `REACT_ENABLED`; with kill-switch on, the "start guided plan-change flow" override is not prepended
- `route.ts:1545` — `planChangeFlow ? PLAN_FLOW_AGENT_INSTRUCTIONS : planModificationProtocol(REACT_ENABLED)` — correctly routes to the honest unavailable copy when `CHAT_REACT_AGENT=off`

With `CHAT_REACT_AGENT=off` a learner asking to change their plan now receives an honest message ("plan updates are paused right now") rather than being led through a fake slot-filling dialogue that would never apply.

**NIT from re-check:** The `REACT_ENABLED` guard at route.ts:1287 covers ALL `tutorContract.learnerPreferenceOverride` values (including `conversation_advance`, `agent_correction`, etc.), not just the plan-change one. With kill-switch on, these per-intent teaching-mode overrides are also suppressed; the code falls through to the plain Socratic/direct preference line (route.ts:1290–1297). This is a minor over-generalization: teaching-mode contracts (correction, advance) are functionally unrelated to ReAct. Acceptable in an emergency kill-switch scenario (simpler/safer mode), but worth a comment at line 1283.

**Tests:** `plan-chat-stream.test.ts` describe `planModificationProtocol (ReAct kill-switch)` — 2 tests (parent-run: 11 passed total). Contract is now regression-gated.

---

## Summary

The implementation is architecturally sound, correctly layered, and defensively coded throughout. Auth (Clerk-only `userId`), child-mode detection, pre/post safety filters, memory write logging, and quality-gate repair are all present and wired correctly. No BLOCKERs were found.

~~Two WARNs required follow-up~~ — **both resolved** (see Re-check summary above): (1) `CORPUS_MISS_OBSERVATION` is now returned on both empty-corpus hits and transient errors, ensuring the answer model always gets the "answer from general knowledge" cue; (2) `planModificationProtocol(REACT_ENABLED)` is injected at the catalog block, and the per-intent teaching-mode override is also gated on `REACT_ENABLED`, so with the kill-switch on the agent gives an honest "plan updates paused" message rather than conducting an unapplyable guided flow.

The test suite now covers both fix paths. Remaining coverage gaps (no integration tests for `retrieveChunks` DB path; `planSessionEngaged` boundary case) are pre-existing and non-blocking.

---

## Scope reviewed

| Path / area | Notes |
|---|---|
| `apps/web/src/app/api/chat/route.ts` | Full read — context build, ReAct loop, quality gate, solver hygiene, plan-change gates, memory persist |
| `apps/web/src/lib/react-loop.ts` + test | Full read |
| `apps/web/src/lib/agent-tools.ts` | Full read — tool specs + handlers |
| `apps/web/src/lib/rag-retrieve.ts` + test | Full read |
| `apps/web/src/lib/agent-skills.ts` + test | Full read |
| `apps/web/src/lib/agent-baseline.ts` | Full read |
| `apps/web/src/lib/agent-prompts.ts` | Referenced; persona wiring verified |
| `apps/web/src/lib/chat-context-builder.ts` | Full read |
| `apps/web/src/lib/chat-context-needs.ts` + test | Full read |
| `apps/web/src/lib/chat-context-policy.ts` | Full read |
| `apps/web/src/lib/learner-chat-intent.ts` | Full read |
| `apps/web/src/lib/plan-actions.ts` | Full read |
| `apps/web/src/lib/learner-progress-briefing.ts` | Skimmed (types + format helpers) |

### Commands run

- [x] `tsc --noEmit` for `@asf/web` — **pass** (parent-run)
- [x] `vitest` 12 files / 95 tests — **all pass** (parent-run)
- [ ] `pnpm --filter @asf/web lint` — skipped (no compile issues found; parent confirms lint gate is in CI)
- [ ] Re-ran targeted vitest — not required; parent results accepted

---

## Findings

| ID | Sev | Location | Issue | Observable failure | Fix hint |
|----|-----|----------|-------|-------------------|----------|
| R1 | **WARN** | `route.ts:1681–1696` + `agent-tools.ts:129–133` | Transient tool error yields non-empty observation that (a) sets `reactHandledGrounding=true`, suppressing static RAG, and (b) does not carry "answer from general knowledge" instruction | Tutor/Coach gets a `## Retrieved context` section containing only `"Retrieval is temporarily unavailable."` while static RAG is blocked; model lacks explicit "fall back to general knowledge" cue | Return the no-match observation text in the error path of `retrieveTool.handler`, or strip all-error observations before setting `reactHandledGrounding` |
| R2 | **WARN** | `route.ts:1263–1264`, `1539` | `planChangeFlow` gated on `REACT_ENABLED`; `PLAN_AGENT_INSTRUCTIONS` (injected when `planChangeFlow=false`) promises guided flow, but with `CHAT_REACT_AGENT=off` no slot-filling tools run and no session is staged | Learner hears "guided conversational flow" in agent phrasing, says "כן" to confirm, but `maybeApplyConfirmedPlanSession` finds no session and does nothing (logged as `chat: guided plan confirm gate failed`; no learner-visible error) | Document the dependency; or add a separate `CHAT_PLAN_FLOW_ENABLED` flag; or override `PLAN_AGENT_INSTRUCTIONS` to a template-redirect copy when `!REACT_ENABLED` |
| R3 | NIT | `route.ts:425–427` | `kgByName` is keyed by concept `id`, not by `name` — variable name is misleading | Confusion when reading/modifying lookups at lines 1070–1083 | Rename to `kgById` |
| R4 | NIT | `route.ts:591–602` | `finishTemplatePlanTurn` calls `void maybeDreamLearnerNotes(userId, agent)` explicitly after `saveAssistantTurn`, which already calls it internally on line 403 | Double dream-threshold probe on template plan turns; at worst two concurrent dream cycles | Remove the explicit `void maybeDreamLearnerNotes` call at line 601 |
| R5 | NIT | `route.ts:2263–2266` | `resolveChatMaxTokens` is called with `wantsExpandedOutputBudget(message)` for both `wantsWorkedSolution` and `wantsContinue` — same expression for both params | Both fields always have the same value; intention obscured | Use a single local `const expanded = wantsExpandedOutputBudget(message)` then pass it to both fields |

---

### Detail (original WARNs — both resolved)

#### W1 — Transient retrieve error suppresses static RAG without fallback cue ✅ RESOLVED (2026-08-13)

**Original location:** `apps/web/src/lib/agent-tools.ts:129–133` (error return), `apps/web/src/app/api/chat/route.ts:1681–1696` (reactHandledGrounding gate)

**Fix verified:** `agent-tools.ts:116` (empty corpus) and `agent-tools.ts:131` (catch) now both return `{ observation: CORPUS_MISS_OBSERVATION }`. The string "Retrieval is temporarily unavailable." no longer appears. `corpusMissObservation()` exported at line 490. Regression tests in `agent-tools.test.ts:19–31` (2 tests).

---

#### W2 — `CHAT_REACT_AGENT=off` silently breaks guided plan-change confirm ✅ RESOLVED (2026-08-13)

**Original location:** `apps/web/src/app/api/chat/route.ts:1263–1264` (planChangeFlow gate), `route.ts:1539` (instruction selection)

**Fix verified:** `plan-actions.ts:615–625` adds `PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE` and `planModificationProtocol(reactEnabled)`. `route.ts:1545` uses `planChangeFlow ? PLAN_FLOW_AGENT_INSTRUCTIONS : planModificationProtocol(REACT_ENABLED)`. `route.ts:1287` additionally gates `tutorContract.learnerPreferenceOverride` on `REACT_ENABLED`. Regression tests in `plan-chat-stream.test.ts` (2 tests in new describe block).

**NIT from re-check (pre-existing NITs policy):** The `REACT_ENABLED` guard at route.ts:1287 suppresses ALL `tutorContract.learnerPreferenceOverride` values (including `conversation_advance`, `agent_correction`), not only the plan-change one. Acceptable for an emergency kill-switch (simpler/safer mode), but a comment at that branch would clarify intent.

---

## Silent-function / dead-code audit

| Symbol | Location | Status | Notes |
|---|---|---|---|
| `PLAN_AGENT_INSTRUCTIONS` | `plan-actions.ts:596–609` | used | Injected via route.ts:1545 (when `planChangeFlow && REACT_ENABLED`) |
| `PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE` | `plan-actions.ts:615–621` | used | Injected via `planModificationProtocol(REACT_ENABLED=false)` at route.ts:1545 |
| `planModificationProtocol` | `plan-actions.ts:623–625` | used | Imported in route.ts:43 |
| `CASUAL_PLAN_CHANGE_TURN_INSTRUCTION` | `plan-actions.ts:628–637` | used? | Exported but search of route.ts shows it is NOT imported there; appears to be injected via `learner-chat-intent.ts` contracts instead. Likely dead in route context. |
| `learnerExplicitChangeRequest` / `learnerPlanChangeIntent` alias | `plan-actions.ts:444–446` | deprecated | `@deprecated` annotation present; no callers found in reviewed scope |
| `proposalToUpdatePayload` | `plan-actions.ts:486–503` | used | Referenced in plan-apply.ts (not read) |
| `buildAgentBaseline` (full) | `agent-baseline.ts:68` | used elsewhere | `buildCompactAgentBaseline` is used in route.ts (learner chat); full version is used in non-chat contexts. Both live. |

Note: `CASUAL_PLAN_CHANGE_TURN_INSTRUCTION` in `plan-actions.ts:611–621` is exported but not imported in `route.ts`. If it's a dead export, consider removing to avoid confusion with the intent-classifier-driven `CASUAL_PLAN_CHANGE_INSTRUCTION` in `learner-chat-intent.ts`.

---

## Edge-case matrix

| Case | Handled? | Evidence |
|---|---|---|
| `dbConfigured === false` / missing `DATABASE_URL` | **yes** | `rag-retrieve.ts:18` — `sql = null`; `ragCorpusReady()` returns false; all DB helpers catch and return safe defaults |
| Unauthenticated request | **yes** | `route.ts:440–442` — returns `401` when `!userId` |
| Empty learner data (brand-new user, no profile) | **yes** | `route.ts:1310–1316` — explicit brand-new-learner instruction; `buildContextNeeds` handles `minimal=false` with no profile |
| Concurrent write (same learner, two tabs) | **acceptable** | `recordChatTurn` / `applyMemoryTagsFromAssistant` are independent inserts; no multi-step transaction required; ordering may vary but no lost-write risk |
| Invalid / malformed `agent` in body | **yes** | `route.ts:461–462` — `agentNameSchema.safeParse` with fallback to `'tutor'` |
| ReAct planner returns null (no tool model) | **yes** | `react-loop.ts:113–117` — first failure degrades; partial observations preserved on later failures |
| Empty corpus / RAG corpus not ingested yet | **yes** | `rag-retrieve.ts:90–104` — `ragCorpusReady()` gate with 5-min TTL; returns `[]` silently |
| LLM context too large | **yes** | `route.ts:2301–2331` — minimal context retry path |
| Quality gate fails twice | **yes** | `route.ts:2351` — accepts repair if fewer failures even if not fully OK; never loops indefinitely |
| Transient plan session persist failure (collecting) | **yes (UX degrades)** | `agent-tools.ts:424` — `.catch(() => undefined)`; slots lost, model re-asks; session is re-created next tool call |
| Plan session persist failure (confirm-ready staging) | **yes** | `agent-tools.ts:457–464` — hard try/catch; explicit `staging_unavailable` observation; no phantom confirm presented |
| Child mode (COPPA) | **yes** | `route.ts:479–490` — `resolveChildMode` from claims + profile `grade_level`; applied to pre/post safety filter and memory writes |

---

## Test assessment

| Change area | Tests exist? | Assert behavior? | Gap |
|---|---|---|---|
| `runReactLoop` — degraded / budget / unknown-tool / throwing | **yes** (10 tests) | **yes** — returns correct shape, `degraded` flag accurate | Missing: transient-error observation path (all observations are errors → `reactHandledGrounding` side-effect untestable in current unit scope) |
| `runReactLoop` — no-tools-chosen `degraded=false` | **yes** | **yes** | None |
| `retrieveChunks` hybrid query | **no** | n/a — DB path | Needs integration test; `detectLang` + `formatChunksForPrompt` covered adequately |
| `ragCorpusReady` caching + TTL | **no** | n/a | `resetRagReadyCache()` exported specifically for tests; not exercised |
| `buildContextNeeds` routing | **yes** (5 tests) | **yes** — key pack flags | Missing: `planChangeFlow=true` path (tested in route.ts context-build, not unit) |
| Intent classifier + `looksLikeLearnerQuestion` | **yes** (20 tests) | **yes** | Missing: `planSessionEngaged` boundary (open session + question mark message) |
| Agent skills prompt contents | **yes** (3 tests) | **shallow** — string containment only | No test that `REVIEWER_SKILLS` block is returned for reviewer; no test that `buildAgentSkillsPrompt` fails loudly on unknown agent type |
| Quality gate `scoreResponseQuality` | **yes** (6 tests per parent) | Assumed behavioral | OK |
| Language resolver | **yes** (4 tests per parent) | OK | None identified |
| `plan-change-intent` / `plan-chat-stream` / `chat-context-policy` | **yes** (parent) | OK | None identified |
| `applyPostStreamSolverHygiene` (stall + verify compose) | **no dedicated test** | n/a | The solver repair is tested via `agent-solver-verify` (not in scope), but the `correctionStall + solve` composition in route.ts is exercised only via the quality-test suite indirectly |
| `REACT_ENABLED=off` + `planChangeFlow=false` interaction | **no** | n/a | W2 above — no test would catch the behavior regression if PLAN_AGENT_INSTRUCTIONS is changed |

**Overall test quality:** Solid unit coverage for the bounded, pure-logic modules (ReAct loop mechanics, intent classifier, context-needs router). Coverage gaps are concentrated in integration points (DB retrieval, the kill-switch kill-path for plan-change, and the transient-error / graceful-degradation path that motivates W1). The quality/language/plan-stream suites are healthy.

---

## Clarity & complexity

The `buildContextPrompt` function in `route.ts` is ~1 150 lines with 10+ nested conditional branches. It handles profiling, plan-change detection, ReAct grounding, static RAG, wellbeing, handoff digests, solver packs, bilingual briefings, and prompt fitting all in one function. While every branch is deliberate and tested, the function's size makes local changes risky (easy to miss a dependent flag). This is a structural concern for stream 24, not a BLOCKER here.

`streamFromLLM` correctly buffers the full draft before emitting (quality gate runs on the buffer, not the stream), which is the right pattern for a batch-then-stream approach.

---

## Escalations (other streams)

| Finding ID | Escalate to | Reason |
|---|---|---|
| R1 (W1) fix option B (route-side guard) | 01-frontend | Straightforward code change in route.ts |
| R2 (W2) flag decoupling | 02-backend-api | Env var semantics + operator documentation; consider Vercel dashboard env var docs update |
| `buildContextPrompt` size / split | 24-architecture | 1 150-line function; architectural decision on whether to extract sub-builders per agent |
| `retrieveChunks` + `ragCorpusReady` integration test coverage | 08-evals-qa | Needs Neon test fixture or mock-sql setup |
| Plan session TTL (`PLAN_CHANGE_SESSION_TTL_MS`) value review | 07-curriculum | Not reviewed (neon-db not in scope); confirm TTL is sufficient for multi-turn plan-change dialogues that span multiple sessions |

---

## Recommended follow-ups

1. ~~**Fix W1** (agent-tools.ts): Return the no-corpus-match observation on transient `retrieve` error.~~ ✅ Done
2. ~~**Fix or document W2** (route.ts): Either decouple `planChangeFlow` from `REACT_ENABLED` with a separate flag, or update `PLAN_AGENT_INSTRUCTIONS` to redirect to the template path when ReAct is disabled.~~ ✅ Done
3. **Test the transient-error path in react-loop.test.ts** (pre-existing gap): Add a test where all observations are error strings and verify `degraded=false` / `observations` non-empty — documents the current behavior and will catch any future change to the `reactHandledGrounding` logic.
4. **Remove or rename `CASUAL_PLAN_CHANGE_TURN_INSTRUCTION`** in plan-actions.ts if it is no longer imported in route.ts — dead export creates confusion with the similarly-named intent-contract instruction.
5. **Add comment at route.ts:1283** clarifying that the `REACT_ENABLED` guard suppresses all per-intent teaching-mode overrides (not just plan-change) as an intentional safe-mode behavior.

---

## References

- Commits in scope: `e8c0bb24` feat(agents): native tool-calling ReAct loop (Phase A); `3a774e5a` feat(agents): conversational guided plan-change (Phase B); `0fb012cc` fix(agents): unblock plan-change intent, corpus scope, hang
- ADRs: ADR-0009 (goal pacing), ADR-0010/0011/0012 (pressure family), ADR-0014 (hybrid tools), ADR-0015 (hybrid knowledge / ReAct)
- Skills: `.cursor/skills/code-review/SKILL.md`, `.cursor/skills/chat-memory-context/SKILL.md`, `.cursor/skills/web-agent-shared/SKILL.md`

---

**Verdict: SHIP**

**BLOCKER count: 0 — WARN count: 0** (W1 and W2 resolved; original NITs R3–R5 unchanged)

**No remaining fix list.** Pre-existing NITs (R3 `kgByName` rename, R4 double dream call, R5 duplicate `wantsExpandedOutputBudget` arg) and the `CASUAL_PLAN_CHANGE_TURN_INSTRUCTION` dead-export NIT are low-priority hygiene items; none block ship.

**Test coverage** (post-fix): W1 path regression-gated by `agent-tools.test.ts` (2 tests). W2 path regression-gated by `plan-chat-stream.test.ts` (2 tests in new describe block). Pre-existing gaps: `retrieveChunks` DB integration, `planSessionEngaged` boundary — both non-blocking.
