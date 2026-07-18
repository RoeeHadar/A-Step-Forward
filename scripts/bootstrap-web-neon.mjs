#!/usr/bin/env node
/**
 * Bootstrap web-app tables on Neon when Alembic is stuck behind Vercel's DB.
 * Idempotent — safe to re-run. Does NOT replace full `alembic upgrade head`.
 *
 * Usage (production):
 *   cd apps/web && vercel env run --environment production -- node ../../scripts/bootstrap-web-neon.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}

const sql = neon(url);

/** One statement per entry — Neon HTTP driver rejects multi-statement strings. */
const statements = [
  `CREATE TABLE IF NOT EXISTS learner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL UNIQUE,
    goal TEXT NOT NULL,
    grade_level TEXT,
    points_group TEXT,
    subjects TEXT[] NOT NULL,
    hours_per_week NUMERIC(4,1) NOT NULL,
    preferred_style TEXT,
    attention_span INT,
    self_scores JSONB,
    background_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  )`,
  `CREATE TABLE IF NOT EXISTS learning_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL UNIQUE,
    goal TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  )`,
  `CREATE TABLE IF NOT EXISTS plan_weeks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    week_number INT NOT NULL,
    concepts TEXT[] NOT NULL,
    content_ids UUID[],
    quiz_due_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'upcoming',
    UNIQUE (plan_id, week_number)
  )`,
  `CREATE TABLE IF NOT EXISTS diagnostic_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    topics TEXT[] NOT NULL,
    question_idx INT NOT NULL DEFAULT 0,
    results JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
  )`,
  `CREATE INDEX IF NOT EXISTS ix_diagnostic_sessions_learner ON diagnostic_sessions (learner_id)`,
  `CREATE TABLE IF NOT EXISTS mastery_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL,
    week_start DATE NOT NULL,
    scores JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (learner_id, week_start)
  )`,
  `CREATE TABLE IF NOT EXISTS diagnostic_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    subject TEXT NOT NULL,
    difficulty NUMERIC(3,1) NOT NULL,
    bloom_level TEXT NOT NULL,
    stem TEXT NOT NULL,
    options JSONB NOT NULL,
    explanation TEXT,
    source_concept TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS ix_diagnostic_items_topic ON diagnostic_items (topic, subject)`,
  `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS stem_he TEXT`,
  `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS options_he JSONB`,
  `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS explanation_he TEXT`,
  `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS points_levels TEXT[]`,
  `CREATE INDEX IF NOT EXISTS ix_diag_points_levels ON diagnostic_items USING GIN (points_levels)`,
  `CREATE TABLE IF NOT EXISTS concept_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL,
    concept_id TEXT NOT NULL,
    score NUMERIC(4,3) NOT NULL DEFAULT 0,
    data_points INT NOT NULL DEFAULT 0,
    last_activity TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (learner_id, concept_id)
  )`,
  `CREATE INDEX IF NOT EXISTS ix_cm_learner ON concept_mastery (learner_id)`,
  `CREATE TABLE IF NOT EXISTS quiz_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL,
    quiz_type TEXT NOT NULL,
    item_id UUID NOT NULL REFERENCES diagnostic_items(id),
    chosen TEXT NOT NULL DEFAULT '',
    correct BOOLEAN NOT NULL,
    time_spent_s INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS ix_quiz_responses_quiz ON quiz_responses (quiz_id, quiz_type)`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS next_test_date DATE`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS next_test_name TEXT`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS final_goal_date DATE`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS mental_state JSONB`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS personality_profile JSONB`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS weak_concepts TEXT[]`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS strong_concepts TEXT[]`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS learner_persona TEXT`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS learner_persona_updated_at TIMESTAMPTZ`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS wellbeing_plan_bias JSONB DEFAULT NULL`,
  `ALTER TABLE learner_profiles ADD COLUMN IF NOT EXISTS lessons_completed_count INT NOT NULL DEFAULT 0`,
  `CREATE TABLE IF NOT EXISTS chat_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    session_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS ix_chat_turns_learner_time ON chat_turns (learner_id, created_at DESC)`,
  `CREATE INDEX IF NOT EXISTS ix_chat_turns_session ON chat_turns (session_id, created_at)`,
  `CREATE TABLE IF NOT EXISTS learner_agent_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'observation',
    content TEXT NOT NULL,
    importance INT NOT NULL DEFAULT 3,
    related_concept_id TEXT,
    source_turn_id UUID,
    superseded_by UUID REFERENCES learner_agent_notes(id) ON DELETE SET NULL,
    archived_at TIMESTAMPTZ,
    last_referenced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS ix_lan_learner_agent_time ON learner_agent_notes (learner_id, agent, created_at DESC) WHERE archived_at IS NULL AND superseded_by IS NULL`,
  `ALTER TABLE learning_plans ADD COLUMN IF NOT EXISTS plan_schema_version INT NOT NULL DEFAULT 1`,
  `ALTER TABLE learning_plans ADD COLUMN IF NOT EXISTS plan_adjustment_kind TEXT DEFAULT NULL`,
  `ALTER TABLE learning_plans ADD COLUMN IF NOT EXISTS plan_last_adjusted_at TIMESTAMPTZ DEFAULT NULL`,
  // 0018_question_store — internal question RAG bank (composite items).
  `CREATE EXTENSION IF NOT EXISTS vector`,
  `CREATE TABLE IF NOT EXISTS question_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id          TEXT NOT NULL,
    extra_concept_ids   TEXT[] NOT NULL DEFAULT '{}',
    subject             TEXT NOT NULL,
    level               TEXT NOT NULL,
    math_track          TEXT[] NOT NULL DEFAULT '{}',
    points_level        TEXT,
    kind                TEXT NOT NULL,
    difficulty          TEXT NOT NULL,
    stem_en             TEXT NOT NULL DEFAULT '',
    stem_he             TEXT NOT NULL DEFAULT '',
    parts               JSONB NOT NULL DEFAULT '[]'::jsonb,
    skill_atoms         JSONB NOT NULL DEFAULT '[]'::jsonb,
    answer_payload      JSONB,
    est_seconds         INT,
    source              TEXT NOT NULL DEFAULT 'generated',
    source_ref          TEXT,
    license             TEXT NOT NULL DEFAULT 'generated-original',
    provenance          JSONB,
    display_publicly    BOOLEAN NOT NULL DEFAULT FALSE,
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    verification        JSONB,
    parameter_spec      JSONB,
    answer_formula      JSONB,
    embedding           vector(1024),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS ix_qi_concept_diff ON question_items (concept_id, difficulty)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_subject_level ON question_items (subject, level)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_verification ON question_items (verification_status)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_source ON question_items (source)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_skill_atoms ON question_items USING GIN (skill_atoms)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_extra_concepts ON question_items USING GIN (extra_concept_ids)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_math_track ON question_items USING GIN (math_track)`,
  `CREATE INDEX IF NOT EXISTS ix_qi_embedding_hnsw ON question_items USING hnsw (embedding vector_cosine_ops)`,
];

console.log('Bootstrapping web-app Neon schema…');
for (const stmt of statements) {
  const label = stmt.slice(0, 60).replace(/\s+/g, ' ');
  try {
    await sql(stmt);
    console.log('  ok:', label);
  } catch (err) {
    console.error('  FAIL:', label);
    console.error(' ', err instanceof Error ? err.message : err);
    process.exit(1);
  }
}
console.log('Done.');
