#!/usr/bin/env node
/**
 * run-migration-0013.mjs
 * Creates the lessons, lesson_questions, skill_practice tables and then
 * applies migration 0016 (adds level_focus, skill_atom_bank columns).
 *
 * Run: DATABASE_URL=... node scripts/run-migration-0013.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) { console.error('DATABASE_URL not set'); process.exit(1); }
const sql = neon(url);

console.log('Applying migrations 0013 → 0016...');

// ── 0013: lessons ──────────────────────────────────────────────
await sql`
  CREATE TABLE IF NOT EXISTS lessons (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id    TEXT NOT NULL UNIQUE,
    subject       TEXT NOT NULL,
    level         TEXT NOT NULL,
    math_track    TEXT[] NOT NULL DEFAULT '{}',
    title_en      TEXT NOT NULL,
    title_he      TEXT NOT NULL,
    summary_en    TEXT NOT NULL,
    summary_he    TEXT NOT NULL,
    sections      JSONB NOT NULL,
    agent_hints   JSONB NOT NULL,
    est_minutes   INT  NOT NULL DEFAULT 15,
    author        TEXT NOT NULL DEFAULT 'cursor-claude-2026',
    version       INT  NOT NULL DEFAULT 1,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
  )
`;
await sql`CREATE INDEX IF NOT EXISTS ix_lessons_subject_level ON lessons (subject, level)`;
await sql`CREATE INDEX IF NOT EXISTS ix_lessons_math_track ON lessons USING GIN (math_track)`;
console.log('  ✓ lessons table ready');

await sql`
  CREATE TABLE IF NOT EXISTS lesson_questions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id       UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    ord             INT  NOT NULL,
    kind            TEXT NOT NULL,
    difficulty      TEXT NOT NULL,
    stem_en         TEXT NOT NULL,
    stem_he         TEXT NOT NULL,
    correct_answer  TEXT,
    options_en      TEXT[],
    options_he      TEXT[],
    correct_index   INT,
    rubric_en       TEXT,
    rubric_he       TEXT,
    explanation_en  TEXT NOT NULL DEFAULT '',
    explanation_he  TEXT NOT NULL DEFAULT '',
    skill_atoms     TEXT[] NOT NULL DEFAULT '{}',
    points_level_min TEXT,
    answer_payload  JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
  )
`;
await sql`CREATE INDEX IF NOT EXISTS ix_lq_lesson_id ON lesson_questions (lesson_id)`;
await sql`CREATE INDEX IF NOT EXISTS ix_lq_difficulty ON lesson_questions (difficulty)`;
console.log('  ✓ lesson_questions table ready');

await sql`
  CREATE TABLE IF NOT EXISTS skill_practice (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id     TEXT NOT NULL,
    skill_atom     TEXT NOT NULL,
    attempts       INT  NOT NULL DEFAULT 0,
    successes      INT  NOT NULL DEFAULT 0,
    last_practiced TIMESTAMPTZ,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (learner_id, skill_atom)
  )
`;
await sql`CREATE INDEX IF NOT EXISTS ix_sp_learner ON skill_practice (learner_id)`;
console.log('  ✓ skill_practice table ready');

// ── 0014/0015: concept_mastery table ─────────────────────────────
await sql`
  CREATE TABLE IF NOT EXISTS concept_mastery (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id  TEXT NOT NULL,
    concept_id  TEXT NOT NULL,
    score       NUMERIC(4,3) NOT NULL DEFAULT 0,
    data_points INT NOT NULL DEFAULT 0,
    last_activity TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (learner_id, concept_id)
  )
`;
await sql`CREATE INDEX IF NOT EXISTS ix_cm_learner ON concept_mastery (learner_id)`;
console.log('  ✓ concept_mastery table ready');

// ── 0016: adaptive levels columns ────────────────────────────────
await sql`ALTER TABLE lessons ADD COLUMN IF NOT EXISTS level_focus JSONB`;
await sql`ALTER TABLE lessons ADD COLUMN IF NOT EXISTS skill_atom_bank JSONB`;
await sql`ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS points_level_min TEXT`;
await sql`ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS answer_payload JSONB`;
await sql`CREATE INDEX IF NOT EXISTS ix_lq_level_min ON lesson_questions (points_level_min)`;
console.log('  ✓ adaptive level columns added');

// ── Record in alembic_version ─────────────────────────────────────
for (const v of ['0013_lessons', '0014_concept_mastery', '0015_skill_practice', '0016_adaptive_levels']) {
  await sql`INSERT INTO alembic_version (version_num) VALUES (${v}) ON CONFLICT DO NOTHING`;
}
console.log('  ✓ alembic_version updated');

console.log('\n✅ Migrations applied. Run: node scripts/seed-lessons.mjs');
