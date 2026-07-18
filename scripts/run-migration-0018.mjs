#!/usr/bin/env node
/**
 * run-migration-0018.mjs
 * Applies migration 0018_question_store directly via the @neondatabase/serverless
 * client (the web Neon path, when Alembic is behind Vercel's DB).
 *
 * Creates the `question_items` store: composite (multi-part) questions that (a)
 * populate lessons' baked-in questions offline and (b) power the educator-only
 * quiz/test builder. Retrieval is structured-filter-first; the pgvector
 * `embedding` column is nullable and filled offline.
 *
 * Idempotent — safe to re-run. Run: DATABASE_URL=... node scripts/run-migration-0018.mjs
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}
const sql = neon(url);

console.log('Applying migration 0018_question_store...');

// One statement per call — the Neon HTTP driver rejects multi-statement strings.
const statements = [
  ['vector extension', `CREATE EXTENSION IF NOT EXISTS vector`],
  [
    'question_items table',
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
  ],
  ['ix_qi_concept_diff', `CREATE INDEX IF NOT EXISTS ix_qi_concept_diff ON question_items (concept_id, difficulty)`],
  ['ix_qi_subject_level', `CREATE INDEX IF NOT EXISTS ix_qi_subject_level ON question_items (subject, level)`],
  ['ix_qi_verification', `CREATE INDEX IF NOT EXISTS ix_qi_verification ON question_items (verification_status)`],
  ['ix_qi_source', `CREATE INDEX IF NOT EXISTS ix_qi_source ON question_items (source)`],
  ['ix_qi_skill_atoms', `CREATE INDEX IF NOT EXISTS ix_qi_skill_atoms ON question_items USING GIN (skill_atoms)`],
  ['ix_qi_extra_concepts', `CREATE INDEX IF NOT EXISTS ix_qi_extra_concepts ON question_items USING GIN (extra_concept_ids)`],
  ['ix_qi_math_track', `CREATE INDEX IF NOT EXISTS ix_qi_math_track ON question_items USING GIN (math_track)`],
  [
    'ix_qi_embedding_hnsw',
    `CREATE INDEX IF NOT EXISTS ix_qi_embedding_hnsw ON question_items USING hnsw (embedding vector_cosine_ops)`,
  ],
];

try {
  for (const [label, stmt] of statements) {
    await sql(stmt);
    console.log(`  ✓ ${label}`);
  }

  await sql`
    INSERT INTO alembic_version (version_num)
    VALUES ('0018_question_store')
    ON CONFLICT DO NOTHING
  `;
  console.log('  ✓ alembic_version updated');

  console.log('\nMigration 0018 complete!');
} catch (err) {
  console.error('Migration failed:', err instanceof Error ? err.message : err);
  process.exit(1);
}
