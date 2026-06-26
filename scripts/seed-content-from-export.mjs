#!/usr/bin/env node
/**
 * Seed `content_sections` (and copy bagrut PDFs metadata) from a JSON
 * export produced by `scripts/ingest_learning_db.py --export-json …`.
 *
 * Strategy:
 * - Load the JSON.
 * - Group sections by `source_file`.
 * - For each source_file: DELETE existing rows in Neon, then INSERT the
 *   new chunks. This guarantees no stale rows survive when the new ingest
 *   produces a different chunk count or different chunk_indexes.
 * - Bagrut rows are upserted by (subject, source_file).
 *
 * Usage:
 *   DATABASE_URL=postgresql://... node scripts/seed-content-from-export.mjs \
 *     --input "C:\temp\asf-ingest\content_export.json"
 *   add --dry-run to skip writes.
 */
import fs from 'node:fs';
import path from 'node:path';
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}
const sql = neon(url);

const args = new Map();
for (const arg of process.argv.slice(2)) {
  if (!arg.startsWith('--')) continue;
  const [k, v] = arg.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const inputPath = args.get('input') ?? 'scripts/seed_data/content_export.json';
const dryRun = args.get('dry-run') === 'true';

if (!fs.existsSync(inputPath)) {
  console.error(`input not found: ${inputPath}`);
  process.exit(1);
}

console.log(`seed-content: input=${inputPath} dry_run=${dryRun}`);
const raw = fs.readFileSync(inputPath, 'utf-8');
const data = JSON.parse(raw);
const sections = data.sections ?? [];
const bagrut = data.bagrut ?? [];

console.log(`  sections: ${sections.length}`);
console.log(`  bagrut:   ${bagrut.length}`);

// Group sections by (subject, source_file) so we can delete stale rows
// per file before re-inserting the fresh set.
const bySource = new Map();
for (const s of sections) {
  const key = `${s.subject}\u0001${s.source_file}`;
  if (!bySource.has(key)) bySource.set(key, []);
  bySource.get(key).push(s);
}

let deletedFiles = 0;
let inserted = 0;
let errors = 0;
let updatedBagrut = 0;

for (const [key, rows] of bySource) {
  const [subject, source_file] = key.split('\u0001');
  if (!dryRun) {
    try {
      await sql`DELETE FROM content_sections WHERE subject = ${subject} AND source_file = ${source_file}`;
      deletedFiles += 1;
    } catch (err) {
      console.warn(`  ! delete failed for ${source_file}:`, err.message ?? err);
      errors += 1;
      continue;
    }
  }
  for (const r of rows) {
    if (!r.body_md || !r.body_md.trim()) continue;
    if (dryRun) {
      inserted += 1;
      continue;
    }
    try {
      await sql`
        INSERT INTO content_sections
          (id, subject, grade, source_file, chunk_index, title, body_md, page_start, page_end, updated_at)
        VALUES
          (gen_random_uuid(), ${r.subject}, ${r.grade ?? null}, ${r.source_file},
           ${r.chunk_index}, ${r.title}, ${r.body_md},
           ${r.page_start ?? null}, ${r.page_end ?? null}, NOW())
      `;
      inserted += 1;
    } catch (err) {
      console.warn(`  ! insert failed for ${r.source_file}#${r.chunk_index}:`, err.message ?? err);
      errors += 1;
    }
  }
}

for (const b of bagrut) {
  if (dryRun) continue;
  try {
    await sql`
      INSERT INTO bagrut_exams
        (id, subject, exam_type, year, source_file, display_name, file_url)
      VALUES
        (gen_random_uuid(), ${b.subject}, ${b.exam_type}, ${b.year ?? null},
         ${b.source_file}, ${b.display_name}, ${b.file_url})
      ON CONFLICT (subject, source_file) DO UPDATE SET
        exam_type    = EXCLUDED.exam_type,
        year         = EXCLUDED.year,
        display_name = EXCLUDED.display_name,
        file_url     = EXCLUDED.file_url
    `;
    updatedBagrut += 1;
  } catch (err) {
    console.warn(`  ! bagrut insert failed for ${b.source_file}:`, err.message ?? err);
    errors += 1;
  }
}

// Force an ingest-status row so the /learn page can show last-updated timestamp.
if (!dryRun) {
  try {
    await sql`
      INSERT INTO content_ingest_status (id, last_ingest_at, failed_files)
      VALUES (1, NOW(), '[]'::jsonb)
      ON CONFLICT (id) DO UPDATE SET
        last_ingest_at = EXCLUDED.last_ingest_at,
        failed_files = EXCLUDED.failed_files
    `;
  } catch (err) {
    console.warn('  ! ingest-status update failed:', err.message ?? err);
  }
}

console.log(`\nDone:`);
console.log(`  source-files cleared: ${deletedFiles}`);
console.log(`  sections inserted:    ${inserted}`);
console.log(`  bagrut upserted:      ${updatedBagrut}`);
console.log(`  errors:               ${errors}`);
process.exit(errors > 0 ? 1 : 0);
