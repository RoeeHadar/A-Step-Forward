#!/usr/bin/env node
/**
 * Seed external_resources table from content/external-resources.yaml.
 *
 * Usage:
 *   DATABASE_URL=postgresql://... node scripts/seed-external-resources.mjs
 *
 * Idempotent — upserts on (subject, url).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as yaml from 'js-yaml';
import { neon } from '@neondatabase/serverless';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}

const data = yaml.load(
  fs.readFileSync(path.join(ROOT, 'content', 'external-resources.yaml'), 'utf-8'),
);
const items = data.resources ?? [];

const sql = neon(url);

let inserted = 0;
let updated = 0;

for (const r of items) {
  const result = await sql`
    INSERT INTO external_resources (
      id, subject, concept_id, title, url, source, language, description, sort_order, created_at
    )
    VALUES (
      gen_random_uuid(), ${r.subject}, ${r.concept_id ?? null}, ${r.title},
      ${r.url}, ${r.source}, ${r.language ?? 'en'}, ${r.description ?? null},
      ${r.sort_order ?? 0}, NOW()
    )
    ON CONFLICT (subject, url) DO UPDATE SET
      title = EXCLUDED.title,
      source = EXCLUDED.source,
      language = EXCLUDED.language,
      description = EXCLUDED.description,
      sort_order = EXCLUDED.sort_order
    RETURNING (xmax = 0) AS inserted
  `;
  if (result[0]?.inserted) inserted += 1;
  else updated += 1;
}

console.log(`Seeded ${inserted} new + ${updated} updated external resources.`);
