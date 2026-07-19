#!/usr/bin/env node
/**
 * run-migration-0019.mjs
 * Applies migration 0019_test_attempts directly via the @neondatabase/serverless
 * client (the web Neon path, when Alembic is behind Vercel's DB).
 *
 * Creates `test_attempts`: the durable record of every graded quiz/test a learner
 * takes (ADR-0009). Powers:
 *   (a) the week-gate signal (score vs pass threshold, weak concepts), and
 *   (b) the Tests archive UI (past tests + the learner's answers vs correct + a
 *       `feedback` slot for future Reviewer notes).
 *
 * NOTE: The application code (apps/web/src/lib/test-attempts.ts) also creates this
 * table lazily (CREATE TABLE IF NOT EXISTS) and degrades gracefully if it is
 * absent, so the feature works even before this migration is run. Running this
 * migration just gives the canonical, indexed, Alembic-tracked version.
 *
 * Idempotent — safe to re-run. Run: DATABASE_URL=... node scripts/run-migration-0019.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}
const sql = neon(url);

console.log('Applying migration 0019_test_attempts...');

// One statement per call — the Neon HTTP driver rejects multi-statement strings.
const statements = [
  [
    'test_attempts table',
    `CREATE TABLE IF NOT EXISTS test_attempts (
      id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      learner_id     TEXT NOT NULL,
      kind           TEXT NOT NULL DEFAULT 'weekly_gate',
      plan_id        TEXT,
      week_num       INT,
      quiz_id        TEXT,
      locale         TEXT NOT NULL DEFAULT 'he',
      score          DOUBLE PRECISION NOT NULL DEFAULT 0,
      passed         BOOLEAN NOT NULL DEFAULT FALSE,
      pass_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.75,
      per_topic      JSONB NOT NULL DEFAULT '{}'::jsonb,
      weak_concepts  TEXT[] NOT NULL DEFAULT '{}',
      questions      JSONB NOT NULL DEFAULT '[]'::jsonb,
      answers        JSONB NOT NULL DEFAULT '[]'::jsonb,
      feedback       JSONB,
      created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )`,
  ],
  [
    'ix_test_attempts_learner',
    `CREATE INDEX IF NOT EXISTS ix_test_attempts_learner ON test_attempts (learner_id, created_at DESC)`,
  ],
  [
    'ix_test_attempts_plan_week',
    `CREATE INDEX IF NOT EXISTS ix_test_attempts_plan_week ON test_attempts (learner_id, plan_id, week_num)`,
  ],
  [
    'ix_test_attempts_kind',
    `CREATE INDEX IF NOT EXISTS ix_test_attempts_kind ON test_attempts (learner_id, kind)`,
  ],
];

try {
  for (const [label, stmt] of statements) {
    await sql(stmt);
    console.log(`  \u2713 ${label}`);
  }

  await sql`
    INSERT INTO alembic_version (version_num)
    VALUES ('0019_test_attempts')
    ON CONFLICT DO NOTHING
  `;
  console.log('  \u2713 alembic_version updated');

  console.log('\nMigration 0019 complete!');
} catch (err) {
  console.error('Migration failed:', err instanceof Error ? err.message : err);
  process.exit(1);
}
