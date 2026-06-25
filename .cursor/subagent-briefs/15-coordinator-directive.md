# Coordinator Directive — Round 5 (2026-06-25 19:54)

Read `14-adaptive-learning-architecture.md` first for the full architectural vision.
This directive is the concrete task list for right now.

---

## State of the world

### Live
- Frontend: https://a-step-forward-waij.vercel.app ✅
- Backend: https://asf-api-q566.onrender.com ✅ (PR #16 fixed startup crash)

### main (clean, CI passing)
- 9 migrations (0001→0009_bookings), 16 tables on Neon
- `/learn` content browser, `/book` booking, agent chat, memory, progress stubs
- Render startup crash fixed (#16: EmailStr + Docker CMD)
- `migrate-neon.yml` workflow fires on push to main touching `infra/alembic/**`

### Current working branch: `feat/adaptive-learning/phase-a`
3 commits ahead of main, 0 behind. Ready to PR.
Contains:
- `infra/alembic/versions/0010_learner_model.py` — 8 new tables (learner_profiles,
  concept_mastery, mastery_snapshots, diagnostic_sessions, diagnostic_items,
  learning_plans, plan_weeks, weekly_quizzes, quiz_responses)
- `content/knowledge-graph/math-high-school.yaml` — full prerequisite graph
- `content/knowledge-graph/math-university.yaml`
- `content/knowledge-graph/physics-high-school.yaml`
- `content/knowledge-graph/physics-university.yaml`
- `scripts/seed_knowledge_graph.py` — reads YAML → writes Neo4j PREREQUISITE_OF edges
- `.github/workflows/migrate-neon.yml` — auto-runs `alembic upgrade head` on push to main

### In-flight branches (need action)

| Branch | +ahead / -behind | Action |
|--------|-----------------|--------|
| `feat/adaptive-learning/phase-a` | +3 / 0 | **PR → main immediately** |
| `chore/deps-gh-actions-batch` | +1 / -1 | **PR → main immediately** (safe dep bumps) |
| `feat/security/10-safety-hardening` | +1 / -1 | **PR → main** (safety_moderation eval matrices) |
| `feat/frontend/hebrew-rtl-default` | +2 / -2 | Assess: does it add value vs main RTL? If yes PR, else archive |
| `chore/infra/workspace-stabilization` | +21 / -21 | Diverged — cherry-pick infra-only commits or archive |
| `feat/agents/03-phase3-system-agents` | +21 / -21 | Diverged — cherry-pick agent improvements or archive |
| `feat/mcp/05-server-improvements` | +21 / -21 | Diverged — cherry-pick MCP improvements or archive |
| `feat/frontend/visual-polish` | 0 ahead | **Delete** (no commits vs main) |

### Blockers requiring human action (in BLOCKED.md)
1. Verify chat gives real AI response (not mock fallback) — test at live URL
2. Resend API key for booking emails → set in Render + Vercel env
3. Key rotation (Groq + Clerk) — deferred by user, skip for now

---

## Priorities — execute in order

### P0 — Merge Phase A (FIRST — everything else depends on it)

```
git checkout feat/adaptive-learning/phase-a
# open PR → main
# title: feat(adaptive-learning): Phase A — learner model DB + prerequisite KG
# run review-bugbot
# merge (squash or merge commit)
```

**After merge:** `migrate-neon.yml` fires automatically and runs `alembic upgrade head`.
Verify by checking the workflow run in GitHub Actions.
If `DATABASE_URL` secret is missing from GitHub, that is the only blocker — add
`DATABASE_URL` to GitHub repo secrets (Settings → Secrets → Actions) from the
Neon dashboard connection string. This unblocks ALL of Phase B, C, D.

**Also merge immediately (safe, no deps):**
- `chore/deps-gh-actions-batch` → PR "chore(deps): batch bump GH Actions"
- `feat/security/10-safety-hardening` → PR "eval(security): safety_moderation matrices"

---

### P1 — Learner Model Service (start after P0 merges)

Create `services/learner_model/` — the single source of truth for what a learner knows.

**Branch:** `feat/adaptive-learning/phase-a-services`

```
services/learner_model/
  pyproject.toml               # package: learner-model-service
  learner_model_service/
    __init__.py
    api.py                     # LearnerModelService protocol (ABC)
    settings.py                # pydantic-settings
    default_service.py         # in-memory stub for tests
    postgres_service.py        # real impl using SQLAlchemy 2.0 async
    stores/
      models.py                # ORM models for 0010_learner_model tables
      repository.py            # CRUD: upsert_mastery, get_student_model,
                               #       snapshot_week, get_prerequisites
```

Key methods (all async):
```python
async def get_student_model(learner_id: str) -> StudentModel
async def upsert_mastery(learner_id: str, concept_id: str, score: float, data_points: int = 1) -> None
async def get_prerequisites(concept_id: str) -> list[str]   # Neo4j traversal
async def snapshot_week(learner_id: str, week_start: date) -> None
async def create_profile(learner_id: str, profile: LearnerProfileInput) -> LearnerProfile
async def get_profile(learner_id: str) -> LearnerProfile | None
```

Add `StudentModel` Pydantic schema to `packages/schemas/schemas/learner_model.py`:
```python
class StudentModel(BaseModel):
    learner_id: str
    profile: LearnerProfile | None
    mastery: dict[str, float]          # concept_id → 0.0–1.0
    weak: list[str]                    # concept_ids with score < 0.4
    developing: list[str]             # 0.4–0.7
    strong: list[str]                  # > 0.7
    last_active: datetime | None
```

Wire into `apps/api/app/main.py`. Add `GET /v1/learners/me/model` route.

---

### P2 — Onboarding API + frontend (start after P1)

**Branch:** `feat/adaptive-learning/phase-b-onboarding`

#### Backend
`apps/api/app/routers/onboarding.py`:
- `POST /v1/onboarding/submit` — creates `learner_profile`, seeds initial
  `concept_mastery` from `self_scores` (1–10 → 0.1–0.9 linear map), returns `{ok: true}`
- `GET /v1/onboarding/status` (auth) → `{complete: bool}`

#### Frontend gate (middleware)
In `apps/web/src/middleware.ts`, add: if user is signed in AND
`GET /v1/onboarding/status` returns `{complete: false}`, redirect to `/onboarding`.
Exempt: `/onboarding`, `/sign-in`, `/sign-out`, `/api/*`, `/book`, `/learn`.

#### Frontend page `apps/web/src/app/onboarding/page.tsx`
3-step wizard (client component, state machine):

**Step 1 — Goals** (שאלות פתיחה):
- "What is your learning goal?" — dropdown: "Pass Bagrut 5pt Math" | "Pass Bagrut 4pt Math" |
  "Pass Bagrut 3pt Math" | "Pass Bagrut Physics" | "Prepare for university" | "Calculus 1" |
  "Linear Algebra" | "Other" + free text
- Subjects: multi-select checkboxes (Math, Physics, Both)
- Grade level: dropdown (7th–12th, University 1st year, University 2nd+ year)
- Points group (if high school math): 3pt / 4pt / 5pt

**Step 2 — Background** (היסטוריה לימודית):
- "How many hours/week can you study?" — slider 1–20, default 5
- "How did you do in your last math/physics class?" — 1–10 slider
- "How would you rate your teacher?" — 1–10 slider (context for pacing)
- "Preferred learning style?" — radio: Theory first / Practice first / Mixed
- "How long can you focus in one sitting?" — radio: 20 min / 45 min / 90 min

**Step 3 — Self-assessment** (הערכה עצמית):
Show relevant concepts (from KG YAML filtered by subject/grade).
For each concept: "Rate your understanding 1–10" — horizontal slider.
Concepts shown: ~8–12 most important for their goal (not all 30+).
E.g. for 5pt Math goal: Algebra, Trig, Functions, Sequences, Limits, Derivatives, Integrals.

On submit → `POST /v1/onboarding/submit` → redirect to `/diagnostic`.

Style: dark glassmorphism, step indicator at top, Hebrew RTL layout, each step
fits one screen without scrolling. "Next" button bottom right.

---

### P3 — Diagnostic engine (start after P1, can parallel P2)

**Branch:** `feat/adaptive-learning/phase-b-diagnostic`

#### New service `services/diagnostic/`
```
services/diagnostic/
  pyproject.toml
  diagnostic_service/
    __init__.py
    engine.py      # CAT algorithm
    scorer.py      # mastery estimation
    api.py         # DiagnosticService protocol
    settings.py
    default_service.py
    stores/
      models.py    # ORM for diagnostic_sessions, quiz_responses
      repository.py
```

**CAT engine (simple, no IRT parameters needed yet):**
```python
START_DIFFICULTY = 5.0
QUESTIONS_TARGET = 18    # stop at 18 or when confidence converges

def next_difficulty(current: float, was_correct: bool) -> float:
    return min(10.0, current + 1.0) if was_correct else max(1.0, current - 1.0)

def confidence_converged(responses: list[Response]) -> bool:
    # Converge if last 4 answers are all correct or all incorrect
    if len(responses) < 4:
        return False
    last = [r.correct for r in responses[-4:]]
    return all(last) or not any(last)

def estimate_mastery(responses: list[Response]) -> float:
    if not responses:
        return 0.5
    # Weighted by difficulty: harder correct answers count more
    num = sum(r.difficulty * int(r.correct) for r in responses)
    den = sum(r.difficulty for r in responses)
    return round(num / den, 4) if den else 0.5
```

#### API routes `apps/api/app/routers/diagnostic.py`
- `POST /v1/diagnostic/start` — `{topics: list[str]}` → creates session, returns first question
- `POST /v1/diagnostic/{session_id}/answer` — `{item_id, chosen}` → scores, returns next question or `{complete: true, results: {...}}`
- `GET /v1/diagnostic/{session_id}` — current state
- On complete: call `LearnerModelService.upsert_mastery()` for each topic

#### Question bank seeder `scripts/seed_diagnostic_items.py`
For each concept in the KG YAML files, generate 5 MCQ questions at difficulties 2, 4, 6, 8, 10
using `AssessmentGeneratorAgent` with structured output. Store in `diagnostic_items`.

This script runs ONCE to bootstrap the bank. Add to Makefile: `make seed-diagnostic`.

#### Frontend `apps/web/src/app/diagnostic/page.tsx`
- Gate: redirect here from `/onboarding` completion
- Progress bar "Question N of ~18"
- One question at a time, LaTeX rendered via KaTeX
- 4 MCQ options as large radio buttons
- "Submit answer" → next question
- On complete: radar chart (Recharts `RadarChart`) of mastery per topic
  - Axes: each topic in the diagnostic
  - Shows current estimate (0–100%)
- CTA button: "Generate my learning plan" → `POST /v1/plan/generate` → redirect `/plan`

---

### P4 — Planning engine (start after P3 complete)

**Branch:** `feat/adaptive-learning/phase-c-planner`

#### New service `services/planner/`
```
services/planner/
  planner_service/
    __init__.py
    generator.py   # plan generation from mastery + KG
    adapter.py     # plan adaptation after quiz
    api.py
    settings.py
    stores/
      models.py    # ORM for learning_plans, plan_weeks
      repository.py
```

**Generator algorithm (topological sort through prerequisite graph):**
```python
async def generate(
    learner_id: str,
    mastery: dict[str, float],
    goal_concepts: list[str],          # from goal → KG traversal
    hours_per_week: float,
) -> LearningPlan:
    # 1. BFS/DFS from goal_concepts backward through PREREQUISITE_OF edges
    # 2. Filter to concepts with mastery < 0.70 (need work)
    # 3. Topological sort (prerequisites first)
    # 4. Pack into weeks: ~2 new concepts + 1 review per week
    #    assuming 45 min per concept per week
    # 5. Assign quiz_due_at = Sunday of each week
```

#### API routes `apps/api/app/routers/planner.py`
- `POST /v1/plan/generate` — generates or regenerates; returns full plan
- `GET /v1/plan` — current plan (all weeks + status)
- `GET /v1/plan/current-week` — this week's concepts, content, quiz deadline
- `POST /v1/plan/adapt` — called after quiz; adapts remaining weeks

#### Frontend `apps/web/src/app/plan/page.tsx`
- Timeline: list of weeks (accordion or vertical scroll)
- Current week: highlighted, shows concepts as cards with mastery badge
- Each concept card: links to `/learn/[subject]/[section]` AND `/app/chat/tutor?context=...`
- Quiz countdown timer (days until end of week)
- Past weeks: score chip (e.g. "78% ✓")
- "Study now" → opens first content section for this week

Add "My Plan" link to sidebar (between Dashboard and Progress).

---

### P5 — End-of-week quiz (start after P4)

**Branch:** `feat/adaptive-learning/phase-d-quiz`

#### Backend `apps/api/app/routers/quiz.py`
- `POST /v1/quiz/start` — generates quiz from current week's concepts (15 questions
  from `diagnostic_items`), sets `time_limit_s = 1800` (30 min), returns items
- `POST /v1/quiz/{quiz_id}/submit` — scores all responses, calls
  `LearnerModelService.upsert_mastery()` + `snapshot_week()` + `planner.adapt()`
- Server enforces time: if `NOW() > started_at + time_limit_s`, mark expired

#### Frontend `apps/web/src/app/quiz/page.tsx`
- Full-screen layout, countdown timer in top bar (MM:SS, goes red < 5 min)
- Question navigator on side (dot per question, green=answered, grey=unanswered)
- One question visible at a time, navigate with prev/next
- "Submit quiz" button (always enabled after Q1 is answered)
- On submit or time-expire: results page
  - Score per topic (bar chart)
  - Mastery change deltas (↑ Limits +12%, ↓ Derivatives -3%)
  - "See updated plan" CTA

Add "Weekly Quiz" link to sidebar, shown only when quiz is pending.

---

### P6 — Tutor v2 prompt + student model injection (after P1, parallel with P3+)

**Branch:** `feat/adaptive-learning/phase-e-tutor-v2`

1. Create `prompts/tutor/v2.md`:
   - Same as v1 but add:
     ```
     ## Student mastery context (injected per session)
     The orchestrator will inject a `## Learner mastery` section at the top of
     each conversation with the learner's current mastery snapshot. Use it to:
     - Identify which prerequisite is likely causing confusion
     - Calibrate explanation depth (strong → challenge, weak → scaffold)
     - Never explain a concept without first checking a prerequisite

     ## Socratic protocol (MANDATORY for new topics)
     Before explaining any NEW concept:
     1. Ask exactly ONE question: "What do you already know about [concept]?"
        OR "Why did you choose that approach?"
     2. Wait for the answer. Then adapt.
     Do NOT skip this for any new topic, even if the learner asks directly.
     If the learner says "just tell me", acknowledge warmly then ask anyway.

     ## next_step expansion
     `generate_exercise` — trigger exercise generation for the current concept
     `assess_prerequisite` — ask a targeted diagnostic question on the prerequisite
     `flag_for_planner` — this concept needs more time; alert the planner
     ```

2. In `services/orchestrator/orchestrator/runner.py`, before dispatching to Tutor:
   - Call `LearnerModelService.get_student_model(learner_id)`
   - Build mastery summary string:
     ```
     ## Learner mastery
     Strong (>70%): Algebra (92%), Functions (81%)
     Developing (40–70%): Derivatives (58%), Sequences (45%)
     Weak (<40%): Limits (28%), Integration (15%)
     ```
   - Inject into `AgentContext.extra["student_model_summary"]`
   - Update `TutorAgent._build_system_prompt()` to include it

3. Update `TutorAgent.prompt_version = "v2"` only after eval gate passes.

4. Eval gate: add `evals/agents/tutor/socratic_test.py` (DeepEval):
   - Test: when given a new concept, tutor asks a question before explaining
   - Test: when mastery shows "weak in limits", tutor offers to review prerequisites
   - Threshold: both pass in ≥ 80% of runs

---

### P7 — Branch cleanup (parallel with everything)

Delete these remote branches (all either 0 commits ahead, or fully superseded):

```bash
git push origin --delete feat/frontend/visual-polish
git push origin --delete feat/frontend/01-foundation
git push origin --delete feat/frontend/02-landing
git push origin --delete feat/frontend/03-auth
git push origin --delete feat/frontend/04-dashboard
git push origin --delete feat/frontend/05-chat
git push origin --delete feat/frontend/06-lessons
git push origin --delete feat/frontend/07-memory
git push origin --delete feat/frontend/08-progress
git push origin --delete feat/frontend/09-educator-admin
git push origin --delete feat/graphrag/01-ontology-migration
git push origin --delete feat/graphrag/02-ingestion-pipeline
git push origin --delete feat/graphrag/03-retrieval-modes
git push origin --delete feat/graphrag/04-mcp-evals
git push origin --delete feat/mcp/01-memory
git push origin --delete feat/mcp/02-graphrag
git push origin --delete feat/mcp/03-curriculum
git push origin --delete feat/mcp/04-progress
git push origin --delete mcp-stack-base
git push origin --delete split/baseline
git push origin --delete split/frontend-base
git push origin --delete wip/agents-phase3-snapshot
```

For the diverged branches (+21/-21), assess each:
- `chore/infra/workspace-stabilization`: cherry-pick infra/pyproject edits not on main
- `feat/agents/03-phase3-system-agents`: check if Research/KG Builder agents are better than main's stubs; cherry-pick if yes
- `feat/mcp/05-server-improvements`: check for auth-context/telemetry improvements; cherry-pick if yes
- If nothing new to salvage: delete

---

## Dependency graph

```
P0 (merge Phase A) ──────────────────────────────────────────────────┐
                                                                       │
    ├── P1 (LearnerModelService) ──────────────────────────────────────┤
    │         │                                                         │
    │         ├── P2 (Onboarding API + page)                           │
    │         │         │                                               │
    │         ├── P3 (Diagnostic engine) ───────── P5 (Quiz)           │
    │         │         │                                               │
    │         └── P4 (Planner) ────────────────── P5 (Quiz)            │
    │                                                                   │
    └── P6 (Tutor v2 + mastery injection)                              │
                                                                        │
P7 (cleanup) ── parallel, no deps ─────────────────────────────────────┘
```

P1 is the critical bottleneck — dispatch it immediately after P0 merges.
P2, P3, P6 can be dispatched in parallel once P1 is in review.
P4 starts after P3 is green.
P5 starts after P4 is green.

---

## Non-negotiable rules

1. **`npx next lint --dir src` must pass before every frontend push.** Zero ESLint errors.
2. **`npx tsc --noEmit` must pass locally.** Don't rely on Vercel to catch type errors.
3. **No new ESM packages without adding to `transpilePackages` in `next.config.mjs`.**
4. **No Phase B/C/D API routes until `0010_learner_model` is confirmed on Neon** (check
   `migrate-neon` GH Actions run after P0 merges).
5. **Tutor v2 prompt ships ONLY after `evals/agents/tutor/socratic_test.py` passes.**
6. `review-bugbot` on every PR. `review-security` on onboarding, mastery, diagnostic routes.
7. Many small PRs. One feature per PR. No giant PRs.

---

## What the human will do (their only actions)

1. Check `DATABASE_URL` is in GitHub repo secrets (needed for `migrate-neon.yml`).
   If missing: add it from the Neon dashboard. Without this, `0010_learner_model` won't run.
2. After `/onboarding` is live: go through it themselves to validate the flow.
3. After `/diagnostic` is live: complete a diagnostic to confirm mastery profile appears.
4. Resend API key for booking emails (optional, non-blocking).
