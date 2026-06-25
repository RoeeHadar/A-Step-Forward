# Architectural Directive — Adaptive Learning System (2026-06-25)

> **Supervisor directive.** This is a significant strategic upgrade, not a patch.
> Read this document completely before dispatching any sub-agent.
> Do NOT break any existing functionality. Build alongside what works.

---

## What is changing and why

The platform is shifting from "content browser + chatbot" to a genuine adaptive
learning system. The distinguishing loop is:

```
Onboarding questionnaire
       ↓
Adaptive diagnostic (15–20 questions → mastery profile)
       ↓
Personalized weekly plan (KG prerequisite chain + goals + time)
       ↓
Study (free-tier content + premium tutor chat)
       ↓
End-of-week quiz (time-limited)
       ↓
Plan adapts → repeat
```

Every agent operates on the same **Student Model** — the single source of truth
for what a learner knows, how they learn, and where they are in their plan.

---

## What stays exactly as-is

- Agent framework, base classes, LLM client, safety layer
- Memory system (8 types, dreaming, consolidation) — complementary to student model
- GraphRAG content retrieval — extended with prerequisite data, not replaced
- `/learn` content browser and Bagrut PDF viewer
- `/book` private lesson booking
- Clerk auth, RBAC, MCP servers
- Existing DB tables (curriculum, memory_events, content_sections, bookings)

---

## New data layer (Postgres + Neo4j)

### Migration `0010_learner_model.py`

```sql
-- Extended learner profile (created at onboarding)
CREATE TABLE learner_profiles (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id       TEXT NOT NULL UNIQUE,   -- Clerk userId
  goal             TEXT NOT NULL,          -- e.g. "Pass Bagrut 5pt Math"
  grade_level      TEXT,                   -- e.g. "10th", "11th", "university"
  points_group     TEXT,                   -- "3pt" | "4pt" | "5pt" | null
  subjects         TEXT[] NOT NULL,        -- ["math","physics"]
  hours_per_week   NUMERIC(4,1) NOT NULL,
  preferred_style  TEXT,                   -- "theory" | "practice" | "mixed"
  attention_span   INT,                    -- minutes; self-reported initially
  self_scores      JSONB,                  -- {"algebra":7,"trig":4,...} from questionnaire
  background_notes TEXT,                   -- free text (teacher quality, past experience)
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Per-concept mastery (live score, updated after every quiz/exercise)
CREATE TABLE concept_mastery (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id    TEXT NOT NULL,
  concept_id    TEXT NOT NULL,             -- matches Neo4j Concept.canonical_name
  score         NUMERIC(5,4) NOT NULL,     -- 0.0000 – 1.0000
  data_points   INT NOT NULL DEFAULT 1,    -- how many observations
  last_activity TIMESTAMPTZ DEFAULT NOW(),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (learner_id, concept_id)
);

-- Weekly mastery snapshot (for trend detection)
CREATE TABLE mastery_snapshots (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id  TEXT NOT NULL,
  week_start  DATE NOT NULL,
  scores      JSONB NOT NULL,              -- {"algebra":0.9,"limits":0.35,...}
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (learner_id, week_start)
);

-- Diagnostic sessions
CREATE TABLE diagnostic_sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id    TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'active',  -- active | complete
  topics        TEXT[] NOT NULL,                 -- topics being diagnosed
  question_idx  INT NOT NULL DEFAULT 0,
  results       JSONB,                           -- {"algebra":0.9,...} when complete
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  completed_at  TIMESTAMPTZ
);

-- Question bank (seeded + AI-generated)
CREATE TABLE diagnostic_items (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic         TEXT NOT NULL,                   -- e.g. "limits"
  subject       TEXT NOT NULL,                   -- "math" | "physics"
  difficulty    NUMERIC(3,1) NOT NULL,           -- 1.0 – 10.0
  bloom_level   TEXT NOT NULL,                   -- remember|understand|apply|analyze
  stem          TEXT NOT NULL,                   -- question text (Markdown+LaTeX)
  options       JSONB NOT NULL,                  -- [{id:"A",text:"...",correct:true},...]
  explanation   TEXT,                            -- shown after answer
  source_concept TEXT NOT NULL,                  -- concept_id it tests
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly learning plans
CREATE TABLE learning_plans (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id    TEXT NOT NULL UNIQUE,
  goal          TEXT NOT NULL,
  start_date    DATE NOT NULL,
  end_date      DATE,                            -- null = open-ended
  status        TEXT NOT NULL DEFAULT 'active',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Individual weeks within a plan
CREATE TABLE plan_weeks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id       UUID NOT NULL REFERENCES learning_plans(id),
  week_number   INT NOT NULL,
  concepts      TEXT[] NOT NULL,                 -- concept_ids to study this week
  content_ids   UUID[],                          -- content_section ids (optional)
  quiz_due_at   TIMESTAMPTZ,
  status        TEXT NOT NULL DEFAULT 'upcoming', -- upcoming|active|complete|skipped
  UNIQUE (plan_id, week_number)
);

-- End-of-week quizzes
CREATE TABLE weekly_quizzes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id       UUID NOT NULL REFERENCES plan_weeks(id),
  learner_id    TEXT NOT NULL,
  items         JSONB NOT NULL,                  -- list of diagnostic_item ids + order
  time_limit_s  INT NOT NULL DEFAULT 1800,       -- 30 min default
  started_at    TIMESTAMPTZ,
  submitted_at  TIMESTAMPTZ,
  score         NUMERIC(5,4),                    -- 0–1 overall
  per_topic     JSONB,                           -- {"limits":0.4,"derivatives":0.6}
  status        TEXT NOT NULL DEFAULT 'pending'  -- pending|active|submitted|expired
);

-- Individual responses within a quiz or diagnostic
CREATE TABLE quiz_responses (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quiz_id       UUID NOT NULL,                   -- weekly_quiz or diagnostic_session id
  quiz_type     TEXT NOT NULL,                   -- 'weekly' | 'diagnostic'
  item_id       UUID NOT NULL REFERENCES diagnostic_items(id),
  chosen        TEXT NOT NULL,                   -- option id chosen
  correct       BOOLEAN NOT NULL,
  time_spent_s  INT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### Neo4j: prerequisite content files

Create `content/knowledge-graph/` YAML files that define actual prerequisite
relationships between concepts. This is the heart of the system.

**File: `content/knowledge-graph/math-high-school.yaml`**

```yaml
# High-school Math prerequisite graph
# Format: each concept lists what must be mastered BEFORE it
concepts:
  - id: arithmetic
    name: Arithmetic
    name_he: חשבון
    prerequisites: []

  - id: algebra_basics
    name: Algebra Basics
    name_he: יסודות האלגברה
    prerequisites: [arithmetic]

  - id: equations_linear
    name: Linear Equations
    name_he: משוואות מדרגה ראשונה
    prerequisites: [algebra_basics]

  - id: equations_quadratic
    name: Quadratic Equations
    name_he: משוואות ריבועיות
    prerequisites: [equations_linear]

  - id: fractions_algebraic
    name: Algebraic Fractions
    name_he: שברים אלגבריים
    prerequisites: [algebra_basics, equations_linear]

  - id: exponents
    name: Exponents & Roots
    name_he: חזקות ושורשים
    prerequisites: [algebra_basics]

  - id: functions_intro
    name: Functions — Introduction
    name_he: פונקציות — מבוא
    prerequisites: [equations_linear, exponents]

  - id: functions_linear
    name: Linear Functions
    name_he: פונקציה לינארית
    prerequisites: [functions_intro]

  - id: functions_quadratic
    name: Quadratic Functions
    name_he: פונקציה ריבועית
    prerequisites: [functions_linear, equations_quadratic]

  - id: functions_exponential
    name: Exponential Functions
    name_he: פונקציה אקספוננציאלית
    prerequisites: [functions_intro, exponents]

  - id: trigonometry_ratios
    name: Trigonometric Ratios
    name_he: יחסים טריגונומטריים
    prerequisites: [functions_intro]

  - id: trigonometry_identities
    name: Trig Identities
    name_he: זהויות טריגונומטריות
    prerequisites: [trigonometry_ratios]

  - id: trigonometry_equations
    name: Trig Equations
    name_he: משוואות טריגונומטריות
    prerequisites: [trigonometry_identities, equations_quadratic]

  - id: sequences_arithmetic
    name: Arithmetic Sequences
    name_he: סדרות חשבוניות
    prerequisites: [equations_linear]

  - id: sequences_geometric
    name: Geometric Sequences
    name_he: סדרות הנדסיות
    prerequisites: [exponents, sequences_arithmetic]

  - id: statistics_descriptive
    name: Descriptive Statistics
    name_he: סטטיסטיקה תיאורית
    prerequisites: [arithmetic]

  - id: probability_basic
    name: Basic Probability
    name_he: הסתברות בסיסית
    prerequisites: [fractions_algebraic]

  - id: combinatorics
    name: Combinatorics
    name_he: קומבינטוריקה
    prerequisites: [probability_basic]

  # 5-point only concepts:
  - id: limits
    name: Limits
    name_he: גבולות
    prerequisites: [functions_quadratic, trigonometry_identities, sequences_geometric]

  - id: derivatives_intro
    name: Derivatives — Introduction
    name_he: נגזרות — מבוא
    prerequisites: [limits, functions_quadratic]

  - id: derivatives_rules
    name: Derivative Rules
    name_he: כללי גזירה
    prerequisites: [derivatives_intro, functions_exponential, trigonometry_identities]

  - id: derivatives_applications
    name: Applications of Derivatives
    name_he: יישומי נגזרות
    prerequisites: [derivatives_rules]

  - id: integrals_intro
    name: Integrals — Introduction
    name_he: אינטגרלים — מבוא
    prerequisites: [derivatives_rules]

  - id: integrals_techniques
    name: Integration Techniques
    name_he: שיטות אינטגרציה
    prerequisites: [integrals_intro, derivatives_rules]

  - id: integrals_applications
    name: Applications of Integrals
    name_he: יישומי אינטגרלים
    prerequisites: [integrals_techniques]
```

**File: `content/knowledge-graph/physics-high-school.yaml`** — similar structure for:
Kinematics → Dynamics (Newton) → Energy → Momentum → Rotational → Electricity →
Magnetism → Waves → Optics → Nuclear

Write this file fully (all concepts, all prerequisites), following the same format.

**File: `content/knowledge-graph/physics-university.yaml`** — for Physics 1 & 2

**File: `content/knowledge-graph/math-university.yaml`** — for Calculus 1, Linear Algebra

### Script: `scripts/seed_knowledge_graph.py`

Reads the YAML files above and writes to Neo4j:
```cypher
MERGE (a:Concept {canonical_name: $id})
SET a.name = $name, a.name_he = $name_he, a.subject = $subject
WITH a
UNWIND $prerequisites AS prereq_id
MATCH (b:Concept {canonical_name: prereq_id})
MERGE (b)-[:PREREQUISITE_OF {weight: 1.0}]->(a)
```

Idempotent. Add to `Makefile` as `make seed-kg`.

---

## Phase A — Data foundations (implement first, nothing breaks)

### A1: Migration `0010_learner_model.py`
Implement all tables from the "New data layer" section above.
`down_revision = "0009_bookings"`.

### A2: KG prerequisite content files
Write `content/knowledge-graph/math-high-school.yaml`,
`physics-high-school.yaml`, `physics-university.yaml`, `math-university.yaml`.
Then implement `scripts/seed_knowledge_graph.py`.

### A3: Learner Model Service — `services/learner_model/`
```
services/learner_model/
  pyproject.toml
  learner_model_service/
    __init__.py
    api.py           # LearnerModelService protocol
    settings.py
    default_service.py
    stores/
      models.py      # SQLAlchemy ORM for the new tables
      repository.py  # upsert_mastery, get_student_model, snapshot_week
```

Key methods:
- `get_student_model(learner_id) -> StudentModel` — full profile + mastery dict
- `update_mastery(learner_id, concept_id, delta_observations) -> None`
- `get_prerequisites(concept_id) -> list[str]` — traverses Neo4j PREREQUISITE_OF edges
- `snapshot_week(learner_id, week_start)` — writes to `mastery_snapshots`

### A4: Onboarding API
`apps/api/app/routers/onboarding.py`:
- `POST /v1/onboarding/start` → create learner_profile from questionnaire data
- `GET /v1/onboarding/status/{learner_id}` → `{complete: bool, step: int}`

Add `learner_model_service` to `apps/api/app/main.py`.
Add to `pyproject.toml` + Dockerfile.

---

## Phase B — Diagnostic engine

### B1: Diagnostic service — `services/diagnostic/`
```
services/diagnostic/
  diagnostic_service/
    __init__.py
    engine.py        # Adaptive CAT engine
    scorer.py        # mastery estimation from responses
    api.py
    settings.py
```

**Adaptive CAT algorithm (simple):**
```python
def next_difficulty(session: DiagnosticSession, last_correct: bool) -> float:
    current = session.current_difficulty
    if last_correct:
        return min(10.0, current + 1.0)
    return max(1.0, current - 1.0)

def is_complete(session: DiagnosticSession) -> bool:
    # Complete after 15–20 questions OR 5 consecutive correct/incorrect
    return session.question_idx >= 15 or session.confidence_converged

def estimate_mastery(responses: list[Response], topic: str) -> float:
    # Simple: correct% weighted by difficulty
    if not responses:
        return 0.5
    weighted_correct = sum(r.difficulty * r.correct for r in responses)
    weighted_total = sum(r.difficulty for r in responses)
    return weighted_correct / weighted_total if weighted_total else 0.5
```

API routes in `apps/api/app/routers/diagnostic.py`:
- `POST /v1/diagnostic/start` — create session, return first question
- `POST /v1/diagnostic/{session_id}/answer` — submit answer, return next question or results
- `GET /v1/diagnostic/{session_id}` — current state
- `GET /v1/diagnostic/{session_id}/results` — mastery estimates per topic

On session complete: call `LearnerModelService.update_mastery()` for each topic.

### B2: Question bank seeder
Use `AssessmentGeneratorAgent` to generate 20–30 questions per major topic cluster,
store in `diagnostic_items`. Run as `scripts/seed_diagnostic_items.py`.
Questions must have:
- `topic` (concept_id)
- `difficulty` 1–10
- `bloom_level`
- `stem` (Markdown + LaTeX)
- `options` (4 MCQ choices, exactly one correct)
- `explanation`

---

## Phase C — Planning engine

### C1: Planner service — `services/planner/`
```
services/planner/
  planner_service/
    __init__.py
    generator.py   # Weekly plan generator
    adapter.py     # Adapts plan based on quiz results
    api.py
    settings.py
```

**Plan generator algorithm:**
```python
def generate_plan(
    mastery: dict[str, float],
    goal: str,
    hours_per_week: float,
    kg: KnowledgeGraph,
) -> list[PlanWeek]:
    # 1. Identify goal concepts (e.g., all concepts in "integrals_*")
    # 2. Find all transitive prerequisites with mastery < 0.7
    # 3. Topological sort by prerequisite order (KG traversal)
    # 4. Pack into weeks by hours_per_week
    # 5. Each week: max 3 new concepts + 1 review concept
    # Return list of PlanWeek(concepts=[], content_ids=[], quiz_due_at=...)
```

**Plan adapter (runs after each weekly quiz):**
- Score < 0.5 on any concept → add review week for that concept
- Score > 0.85 on all concepts → skip review, advance plan by one week
- Score 0.5–0.85 → continue as planned

### C2: Planning API — `apps/api/app/routers/planner.py`
- `POST /v1/plan/generate` → generates or regenerates a plan from current mastery
- `GET /v1/plan` → current plan (all weeks, current week highlighted)
- `GET /v1/plan/current-week` → this week's concepts + content + quiz deadline
- `POST /v1/plan/adapt` → triggered after quiz submission, returns updated plan

---

## Phase D — End-of-week quiz

### D1: Quiz service integration
In `apps/api/app/routers/quiz.py`:
- `POST /v1/quiz/start` → creates `weekly_quiz` from current week's concepts,
  generates 15 questions from `diagnostic_items`, returns time_limit
- `POST /v1/quiz/{quiz_id}/submit` → scores responses, updates `concept_mastery`,
  calls `planner.adapt()`, saves `mastery_snapshot`
- `GET /v1/quiz/{quiz_id}` → quiz state (pending / active / submitted)

Time limit enforcement: server stores `started_at`; on submit, if
`NOW() - started_at > time_limit_s`, mark as `expired` and score partial answers.

---

## Phase E — Tutor & agent upgrades

### E1: Tutor prompt v2 — `prompts/tutor/v2.md`

Key changes from v1:
1. **Mastery context injected at session start** — orchestrator injects a snapshot:
   ```
   ## Learner's current mastery
   Strong (>70%): Algebra, Functions, Trig Basics
   Developing (40–70%): Derivatives, Sequences
   Weak (<40%): Limits, Integration
   ```
2. **Socratic depth protocol** — before every explanation, ask ONE of:
   - "Why did you choose that approach?"
   - "What do you already know about [concept]?"
   - "Can you show me what you tried first?"
   Never skip this for NEW topics.
3. **Gap detection rule** — if the learner struggles, reason from the KG:
   "Limits require Trig and Functions mastery. Let me check which is the gap."
   Then guide toward the weak prerequisite, not the surface topic.
4. **next_step options expand** to: `continue|assess_prerequisite|generate_exercise|rest|flag_for_planner`
5. **Exercise trigger** — when next_step=`generate_exercise`, the orchestrator
   calls `AssessmentGeneratorAgent` with the current concept and mastery level.

### E2: Orchestrator upgrade
In `services/orchestrator/orchestrator/runner.py`:
- Before dispatching to Tutor, fetch `StudentModel` from `LearnerModelService`
- Inject mastery snapshot into `AgentContext.extra["student_model"]`
- Handle `next_step=generate_exercise` → call `AssessmentGeneratorAgent` → return exercise
- Handle `next_step=assess_prerequisite` → call `DiagnosticAgent` for one targeted question

### E3: Error diagnosis
In `packages/agents/agents/system/grader/agent.py`:
- After scoring a wrong answer, call `LearnerModelService.get_prerequisites(concept_id)`
- For each prerequisite, check if `mastery < 0.5`
- If found: set `root_cause = prerequisite_id`, lower that concept's mastery score
- Output includes `root_cause_concept` and `suggested_review_path`

---

## Frontend: new pages

### `/onboarding` — first-time learner flow
3 steps:
1. **Goals**: "What do you want to achieve?" (dropdown + free text) + subjects + grade
2. **Background**: grade level, points group, years studying, self-rating 1-10 per topic
3. **Preferences**: hours/week, preferred style (theory/practice/mixed), session length

On complete → redirect to `/diagnostic` if onboarding is new, else `/plan`.
Gate: if Clerk user has no `learner_profile`, always redirect to `/onboarding` before `/app/*`.

### `/diagnostic` — adaptive assessment
- Shows one question at a time with LaTeX rendering
- Progress bar: "Question N of ~20"
- On complete: radar chart of mastery per topic (recharts `RadarChart`)
- CTA: "Generate my learning plan" → hits `/v1/plan/generate`

### `/plan` — weekly learning plan
- Timeline view: Week 1, Week 2, ... current week highlighted
- Current week: list of concepts (with mastery badge) + content links + quiz countdown
- Past weeks: score achieved
- "Start studying" opens the first content section for this week

### `/quiz` — end-of-week quiz
- Full-screen, time countdown in header
- One question at a time, can navigate back before submitting
- On submit: show results (correct/incorrect per question, mastery change per topic)
- "See your updated plan" CTA

Update sidebar: add `Plan`, `Diagnostic`, `Quiz` links. Add `Learn` link already there.

---

## What the coordinator must NOT do

- Do NOT change `/learn`, `/book`, existing agent implementations, or auth.
- Do NOT remove the episodic/semantic memory system — it runs alongside the student model.
- Do NOT ship Phase B or C before Phase A migrations are on Neon and verified.
- Do NOT rewrite the tutor prompt (v1 stays); create `v2.md` and update `prompt_version`
  in the agent only when v2 is eval-gated.

---

## Sequencing for sub-agents

Dispatch in this order (some can be parallel):

**Immediate (parallel):**
- **Infra (09)**: Migration `0010_learner_model.py`
- **Curriculum / Content (07)**: KG prerequisite YAML files + `seed_knowledge_graph.py`

**Once A1 lands on Neon:**
- **Backend (02)** + new `learner_model` service: Phase A3+A4
- **Backend (02)**: Diagnostic API (Phase B1)
- **Backend (02)**: Planning API (Phase C1+C2)
- **Backend (02)**: Quiz API (Phase D1)

**Once APIs are green:**
- **Agents (03)**: Tutor prompt v2 + orchestrator student model injection (Phase E1+E2)
- **Agents (03)**: Error diagnosis upgrade (Phase E3)

**In parallel with backend:**
- **Frontend (01)**: `/onboarding`, `/diagnostic`, `/plan`, `/quiz` pages

**After all phases land:**
- **Evals (08)**: eval suites for diagnostic accuracy, plan quality, tutor Socratic adherence

---

## Completion criteria

- A new learner who signs up is redirected to `/onboarding` (blocked from `/app/*` until complete)
- After onboarding, they go through the diagnostic and get a real mastery profile
- After diagnostic, they have a weekly plan visible at `/plan`
- The Tutor knows their mastery snapshot ("Weak in Limits") in every chat session
- End-of-week quiz adapts the plan
- The prerequisite KG is populated (verify with `GET /v1/concepts/limits/prerequisites` → returns Trig + Algebra + Functions)
- All new routes pass integration tests
- ESLint + TypeScript clean; `npx next lint --dir src` → zero errors before any push
