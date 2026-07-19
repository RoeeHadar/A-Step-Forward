#!/usr/bin/env node
/**
 * run-migration-0020.mjs
 * Applies migration 0020_weekly_quiz_rotation directly via the @neondatabase/serverless
 * client (the web Neon path, when Alembic is behind Vercel's DB).
 *
 * Adds the `rotation` dimension to `weekly_quizzes_ai` (ADR-0010 Stream B, anti-gaming):
 * each weekly-gate retake gets its own cached quiz so retakes present FRESH items
 * (the learner can't memorize answer positions). Rotation = the number of gate attempts
 * already recorded for the plan week; reloads within a rotation stay cached.
 *
 * NOTE: The application (apps/web/src/lib/weekly-quiz.ts) also performs this same
 * idempotent DDL lazily on the first weekly-quiz load and degrades gracefully, so the
 * feature works before this runs. Running this migration just gives the canonical,
 * indexed, Alembic-tracked version and pre-warms the schema (no index swap mid-test).
 *
 * Idempotent — safe to re-run. Run: DATABASE_URL=... node scripts/run-migration-0020.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}
const sql = neon(url);

console.log('Applying migration 0020_weekly_quiz_rotation...');

// One statement per call — the Neon HTTP driver rejects multi-statement strings.
const statements = [
  [
    'weekly_quizzes_ai table (ensure exists)',
    `CREATE TABLE IF NOT EXISTS weekly_quizzes_ai (
      id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id     TEXT NOT NULL,
      week_start  DATE NOT NULL,
      plan_id     TEXT,
      week_num    INT,
      locale      TEXT NOT NULL DEFAULT 'he',
      questions   JSONB NOT NULL,
      created_at  TIMESTAMPTZ DEFAULT NOW()
    )`,
  ],
  [
    'rotation column',
    `ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS rotation INT NOT NULL DEFAULT 0`,
  ],
  [
    'drop legacy 5-col unique index',
    `DROP INDEX IF EXISTS weekly_quizzes_ai_user_week_plan_locale_idx`,
  ],
  [
    'drop legacy unique constraint',
    `ALTER TABLE weekly_quizzes_ai DROP CONSTRAINT IF EXISTS weekly_quizzes_ai_user_id_week_start_key`,
  ],
  [
    'rotation-aware unique index',
    `CREATE UNIQUE INDEX IF NOT EXISTS weekly_quizzes_ai_user_week_plan_locale_rot_idx
     ON weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale, rotation)`,
  ],
];

try {
  for (const [label, stmt] of statements) {
    await sql(stmt);
    console.log(`  \u2713 ${label}`);
  }

  await sql`
    INSERT INTO alembic_version (version_num)
    VALUES ('0020_weekly_quiz_rotation')
    ON CONFLICT DO NOTHING
  `;
  console.log('  \u2713 alembic_version updated');

  console.log('\nMigration 0020 complete!');
} catch (err) {
  console.error('Migration failed:', err instanceof Error ? err.message : err);
  process.exit(1);
}
