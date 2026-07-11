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
