# Evals coverage / gap report — 2026-07-21-adr0010-building

| Field | Value |
|-------|-------|
| Round | `2026-07-21-adr0010-building` |
| Mode | **PLAN + REPORT ONLY** (no suite execution this iteration) |
| Suite focus | Pilot + ADR-0010 |
| Target env | `local` |
| Seed variant | `building` (locked; matches `docs/qa/rounds/current.json`) |
| Crew | ASF Evals Tester (scout → executor → reporter) |
| Status | Coverage/gap only — **no baseline promote** |

Labels: **PLANNED** = scouted / recommended for a later execute iteration; **EXECUTED** = not run this round (plan-report-only).

---

## 0. Seed lock

`docs/qa/rounds/current.json` → `seed_variant: building`, `mode: plan-report-only`. Scout did not switch variants.

Fingerprint for `building`: readiness mock-capped ~70%, multi-week plan, rich interactive start (`docs/qa/adr-0010-manual-test-plan.md` cases 2–3, 9–14, 16).

---

## 1. Scout — coverage matrix

### 1.1 Layout vs brief (`08-evals-qa` / `run-evals`)

| Area | Expected | Present | Notes |
|------|----------|---------|-------|
| `evals/agents/<agent>/` | capability, safety, refusal, citation, thresholds, baseline | Partial | 12 agents + `_template`; most lack DeepEval, baseline, refusal-dedicated files |
| `evals/retrieval/` | memory + KG recall@k / MRR | Partial | KG suite + MCP YAMLs; no dedicated `memory_recall.yaml` |
| `evals/memory/` | dreaming, consolidation, decay, conflict, PII | Present | Hygiene YAMLs + `run_hygiene_evals.py`; baseline + thresholds |
| `evals/e2e/` | Playwright | **Absent** | Dir missing; Playwright lives under `apps/web` (out of this harness) |
| `evals/runner.py` | Aggregate + `--touched` + baseline check | Present | Discovers agent YAMLs / `*.py` / memory cases; GraphRAG via `retrieval/kg` |
| Online / shadow | 1% prod → Langfuse + `eval_online` | **Not wired** | Deferred (active-context: no live learners yet) |

### 1.2 Agent roster × eval assets

| Agent | capability | safety | DeepEval / pytest | thresholds | baseline | CI gate | ADR-0010 relevance |
|-------|:----------:|:------:|:-----------------:|:----------:|:--------:|:-------:|--------------------|
| Tutor | ✓ | ✓ | regression (+ stale citation pyc) | ✓ | ✓ | Soft (`evals.yml` continue-on-error) + `evals-tutor.yml` | Exam-readiness intent tests live in **web unit**, not promptfoo |
| Coach | ✓ | ✓ | — | ✓ | — | No | Weak-atom / FSRS drills — no ADR gate suite |
| Q&A Explainer | ✓ | ✓ | citation_test.py | ✓ | — | No | Citation only |
| Mentor | — | — | — | — | — | No | **Gap:** at-risk triage / day-before anxiety (ADR D/F) |
| Reviewer | — | — | — | — | — | No | **Gap:** open-response milestone/final grading (ADR B deferred) |
| Note-Taker / Engagement / Accessibility | — | — | — | — | — | No | Out of pilot critical path |
| Grader | ✓ | ✓ | — | ✓ | — | No | Prompt-contains only; **no rubric/judge fidelity for gates** |
| Assessment Generator | ✓ | ✓ | — | ✓ | — | No | Thin; **no bank-first / anti-MCQ / corpus-depth cases** |
| Curriculum Designer | ✓ | ✓ | — | ✓ | — | No | No learning-plan authority / gate-remediation cases |
| Progress Analyzer | ✓ | ✓ | — | ✓ | — | No | No blocking-atoms / gate-fail root-cause cases |
| Orchestrator | ✓ | ✓ | routing_test.py | ✓ | — | No | Routing only |
| Safety / Moderation | ✓ | ✓ | — | ✓ | — | No | Generic safety |
| Research / KG Builder / Content Curator | ✓ | ✓ | research citation | ✓ | — | No | Low for this round |
| Memory Steward | — | — | — | — | — | No | Consolidation covered under `evals/memory/` hygiene, not agent persona |

**Baselines on disk:** `evals/agents/tutor/baseline.json`, `evals/memory/baseline.json`, `evals/retrieval/kg/baseline.json` only.

### 1.3 ADR-0010 / pilot — where truth lives today

ADR-0010 behavior is primarily guarded by **Vitest unit tests in `apps/web`**, not by `evals/` LLM harness:

| ADR theme | Automated guard (local) | In `evals/` harness? |
|-----------|-------------------------|----------------------|
| Hard gate + critical floor (`evaluateGatePass`) | `plan-pacing.test.ts`, `assessment-calibration.test.ts`, `assessment-grading-logic.test.ts` | **No** |
| Lesson ≠ advancement / exposure | Covered indirectly via pacing/lesson-complete logic + manual case 9 | **No** promptfoo |
| Readiness mock-cap / concave / never 100% | `readiness.test.ts`, `assessment-calibration.test.ts` | **No** |
| Gate bank-first / format_version / MCQ cap | `gate-question-bank.test.ts`, `weekly-quiz.test.ts` | **No** |
| Soft override / retake rotation | Unit + manual cases 12–14 | **No** end-to-end eval |
| Wellbeing eases load, not pass bar | Manual case 16 + pacing units | **No** dedicated eval |
| Mentor day-before / at-risk | Manual cases 5, 7 | **No** agent suite |
| Seed variant `building` journey | `docs/qa/adr-0010-manual-test-plan.md` + `seed-pilot-demo.mjs` | **Manual only** |

Active-context deferred item (truthful): *full promptfoo/DeepEval harness incomplete for live learners* — confirmed.

### 1.4 CI gate status

| Workflow | What runs | Blocking? |
|----------|-----------|-----------|
| `.github/workflows/evals.yml` | Tutor capability + safety via `npx promptfoo` | **No** (`continue-on-error: true`) |
| `.github/workflows/evals-tutor.yml` | `uv run python evals/runner.py --suite tutor` (mock LLM) | Path-filtered; Tutor-only |
| Lint & Test | Web units (includes ADR calibration) | Yes for web |
| Touched-agent full matrix | `runner.py --touched` TOUCH_MAP only maps tutor / memory / graphrag | **Incomplete** vs roster |

Last recorded `evals/report.md`: 2026-06-23 GraphRAG-only PASS — **stale**; not a current ADR-0010 attestation.

### 1.5 Top gaps (priority for pilot + ADR-0010)

1. **No `evals/` suite for assessment-driven progression** (gate pass/fail, mock readiness cap, soft override) — only web units + manual plan.
2. **Missing live-site agent suites:** Mentor, Reviewer (critical for ADR streams D/B deferred paths).
3. **Assessment Generator / Grader** suites are prompt-string asserts against live Anthropic IDs — flake/API-key risk; no mocks; no gate-item or rubric fidelity metrics.
4. **Baselines absent** for every agent except Tutor (+ memory/KG infra) — regression gate cannot fire for grader/assessment paths.
5. **TOUCH_MAP / CI** do not cover planner, readiness, weekly-quiz, or gate-bank paths under `apps/web` — ADR-0010 code can ship without touching `evals/`.
6. **`evals/e2e/` missing**; online shadow evals not implemented.
7. Most agent capability YAMLs need live LLM providers (unlike Tutor’s `tutor_mock.js`) — local full `make evals` will fail or skip without keys.

---

## 2. Executor — planned local checklist (not run)

Mode forbids execution and **forbids baseline promote**. Commands below are for a future execute iteration once live attestation / keys are approved.

### 2.1 Safe / mock-friendly (prefer first)

| # | Command | Expected | If fail | Flake / keys |
|---|---------|----------|---------|--------------|
| 1 | `pnpm --filter @asf/web test -- assessment-calibration plan-pacing readiness gate-question-bank weekly-quiz assessment-grading-logic` | All green — ADR calibration ground truth | **P0** for ADR-0010 math | None (pure units) |
| 2 | `uv run python evals/runner.py --suite tutor` | Pass vs tutor thresholds; mock provider | P1 agent contract | Mock — OK local |
| 3 | `uv run python evals/runner.py --suite memory` | Hygiene cases pass; compare to memory baseline slack | P1 | Needs memory package import path |
| 4 | `uv run python evals/runner.py --suite graphrag` *(or kg run_eval)* | Recall metrics within KG thresholds | P2 for this round | Local fixtures |

### 2.2 Promptfoo / DeepEval (API or incomplete)

| # | Command | Expected | Severity | Notes |
|---|---------|----------|----------|-------|
| 5 | `uv run promptfoo eval -c evals/agents/grader/capability.yaml` | Prompt contract contains | P2 | Needs Anthropic; **not mocked** |
| 6 | Same for `assessment_generator` | Prompt contract contains | P2 | Does **not** assert bank-first / corpus / MCQ caps |
| 7 | `uv run python -m deepeval test run evals/agents/qa_explainer/citation_test.py` | Citation thresholds | P2 | Judge model / keys |
| 8 | Full `make evals` / `uv run python evals/runner.py` | Aggregate report | P1 inventory | Will hit live providers for non-tutor agents |

### 2.3 Pilot / `building` (manual ↔ future automated)

| # | Action | Maps to ADR manual # | Automate later? |
|---|--------|----------------------|-----------------|
| 9 | Seed `building` → assert readiness ≤ ~70% without mock | #2 | Playwright / API eval |
| 10 | Mark lessons complete → week does not advance | #9 | Integration eval |
| 11 | Gate fail on weak critical despite high aggregate | #10 | Unit already; need e2e |
| 12 | Retake → rotated items | #12 | Integration |
| 13 | Soft override after ≥3 attempts | #14 | Integration |

**Do not** run `chore(evals): promote … baseline` this round.

Echo: `seed_variant: building`.

---

## 3. Reporter — findings for coordinator

### Verdict

**PLANNED coverage/gap only — EXECUTED: none.**  
Eval harness exists as scaffolding (Tutor strongest; memory/KG partial). **ADR-0010 pilot risk is covered mainly by web Vitest + manual seed plan, not by promptfoo/DeepEval.** That is an honest gap relative to brief 08 and `60-testing.mdc` (touched-agent evals ≥ thresholds), but matching active-context deferral of the full harness.

### Regression risk (this round’s focus)

| Risk | Level | Why |
|------|-------|-----|
| Gate / readiness parameter drift | Mitigated in CI via web units | Calibration tests pin constants; still no LLM-facing readiness humility eval |
| Gate item quality / anti-gaming | Medium | Bank logic unit-tested; no eval that graders/generators preserve hard open/numeric mix |
| Mentor / Reviewer behavior on at-risk / open response | High if those paths are exercised in pilot | **No suites** |
| Promoting baselines | N/A | Explicitly out of scope — do not promote |
| False green from `evals.yml` | Medium | `continue-on-error: true` on tutor promptfoo job |

### Coordinator actions (no promote)

1. Treat web ADR calibration tests + `adr-0010-manual-test-plan.md` (`building`) as the **binding** QA bar for this round until LLM evals catch up.
2. Queue (later iteration, not this report): eval packages for gate/readiness scenarios; Mentor + Reviewer `_template` clones; mock providers for grader/assessment_generator.
3. Expand `TOUCH_MAP` / CI path filters to `apps/web/src/lib/{plan-pacing,readiness,weekly-quiz,gate-question-bank,lesson-complete}*` so ADR code changes force the right suites.
4. Keep online/shadow evals deferred until live learners exist.
5. Re-run scout after first execute iteration; still **no baseline promote** until Tutor (and any new suites) are green with mocks on local + CI.

### Round artifacts

- This file: `docs/qa/rounds/2026-07-21-adr0010-building/evals.md`
- Manual twin: `docs/qa/adr-0010-manual-test-plan.md`
- Unit ground truth: `apps/web/src/lib/assessment-calibration.test.ts` (+ related)

---

## 5-line summary (coverage gaps)

1. ADR-0010 gate/readiness/mock-cap logic has **no** `evals/` promptfoo/DeepEval suite — only Vitest + manual `building` plan.  
2. **Mentor** and **Reviewer** (pilot-critical for at-risk / open-response) have **zero** eval directories.  
3. Grader / Assessment Generator suites are thin live-LLM prompt checks — no mocks, no bank-first / rubric-fidelity cases.  
4. Baselines exist only for Tutor + memory + KG; CI tutor promptfoo is **non-blocking** (`continue-on-error`).  
5. `evals/e2e/`, online shadow, and TOUCH_MAP coverage of ADR web paths are missing — full harness still deferred per active-context.

---

seed_variant: building  
round_id: 2026-07-21-adr0010-building
