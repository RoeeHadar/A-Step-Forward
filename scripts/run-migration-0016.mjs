#!/usr/bin/env node
/**
 * run-migration-0016.mjs
 * Applies migration 0016_adaptive_levels directly via the @neondatabase/serverless client.
 * Run: DATABASE_URL=... node scripts/run-migration-0016.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) { console.error('DATABASE_URL not set'); process.exit(1); }
const sql = neon(url);

console.log('Applying migration 0016_adaptive_levels...');

try {
  // 1. lessons: add level_focus and skill_atom_bank
  await sql`ALTER TABLE lessons ADD COLUMN IF NOT EXISTS level_focus JSONB`;
  await sql`ALTER TABLE lessons ADD COLUMN IF NOT EXISTS skill_atom_bank JSONB`;
  console.log('  ✓ lessons columns added');

  // 2. lesson_questions: add points_level_min and answer_payload
  await sql`ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS points_level_min TEXT`;
  await sql`ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS answer_payload JSONB`;
  await sql`CREATE INDEX IF NOT EXISTS ix_lq_level_min ON lesson_questions (points_level_min)`;
  console.log('  ✓ lesson_questions columns added');

  // 3. diagnostic_items: add points_levels
  await sql`ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS points_levels TEXT[]`;
  await sql`CREATE INDEX IF NOT EXISTS ix_diag_points_levels ON diagnostic_items USING GIN (points_levels)`;
  console.log('  ✓ diagnostic_items.points_levels added');

  // 4. Backfill diagnostic_items
  const r1 = await sql`
    UPDATE diagnostic_items
    SET points_levels = ARRAY['5pt']
    WHERE points_levels IS NULL AND (
      topic ILIKE '%calculus%' OR topic ILIKE '%derivative%' OR
      topic ILIKE '%integral%' OR topic ILIKE '%limit%'
    )
  `;
  console.log(`  ✓ backfilled 5pt diagnostic items: ${r1.rowCount ?? 0} rows`);

  const r2 = await sql`
    UPDATE diagnostic_items
    SET points_levels = ARRAY['3pt', '4pt', '5pt']
    WHERE points_levels IS NULL AND (
      topic ILIKE '%linear%' OR topic ILIKE '%fraction%' OR
      topic ILIKE '%ratio%' OR topic ILIKE '%percent%'
    )
  `;
  console.log(`  ✓ backfilled 3pt+ diagnostic items: ${r2.rowCount ?? 0} rows`);

  // 5. Record in alembic_version table
  await sql`
    INSERT INTO alembic_version (version_num)
    VALUES ('0016_adaptive_levels')
    ON CONFLICT DO NOTHING
  `;
  console.log('  ✓ alembic_version updated');

  console.log('\nMigration 0016 complete!');
} catch (err) {
  console.error('Migration failed:', err.message);
  process.exit(1);
}
