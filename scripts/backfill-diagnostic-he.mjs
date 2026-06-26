/**
 * Backfill Hebrew translations on existing `diagnostic_items` rows.
 *
 * The starting diagnostic seeder (`scripts/seed_diagnostic_items.py`) was
 * EN-only originally — it generated template stems like
 *   "[Difficulty 6/10] Which statement best describes **Functions — Intro**?"
 * with four English options. The 0015 migration added `stem_he`,
 * `options_he`, `explanation_he` columns; this script populates them in
 * parallel by mirroring the template in Hebrew, using each concept's
 * `name_he` from `apps/web/src/lib/kg-data.json`.
 *
 * The HE translation is a faithful mirror of the EN template — same option
 * structure, same correct key (B). The Python seeder is updated to emit
 * both languages going forward; this script catches the legacy rows.
 *
 * Usage:
 *   DATABASE_URL=... node scripts/backfill-diagnostic-he.mjs
 *   DATABASE_URL=... node scripts/backfill-diagnostic-he.mjs --dry-run
 *   DATABASE_URL=... node scripts/backfill-diagnostic-he.mjs --force   (re-translate even if HE already set)
 *
 * Idempotent: skips rows that already have `stem_he IS NOT NULL` unless
 * `--force`.
 */
import { neon } from '@neondatabase/serverless';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const dryRun = process.argv.includes('--dry-run');
const force = process.argv.includes('--force');

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}
const sql = neon(url);

const kg = JSON.parse(
  readFileSync(join(ROOT, 'apps/web/src/lib/kg-data.json'), 'utf8'),
);
const heByConcept = Object.fromEntries(
  kg.concepts.map((c) => [c.id, c.name_he || c.name]),
);

function templateHe(conceptId, difficulty) {
  const name = heByConcept[conceptId] ?? conceptId.replace(/_/g, ' ');
  const d = Math.round(Number(difficulty));
  return {
    stem: `[רמת קושי ${d}/10] איזה משפט מתאר בצורה הטובה ביותר **${name}**?`,
    options: {
      choices: [
        `עובדה כללית ולא קשורה לגבי ${name}`,
        `תכונה ליבה ומדויקת של ${name}`,
        `תפיסה שגויה נפוצה לגבי ${name}`,
        `טענה פשטנית מדי שמתעלמת מהדרישות הקודמות של ${name}`,
      ],
      correct: 'B',
    },
    explanation: `התשובה הנכונה מבטאת תכונה מהותית של ${name}.`,
  };
}

const where = force ? sql`` : sql`WHERE stem_he IS NULL`;
const rows = await sql`
  SELECT id::text, topic, difficulty, options
  FROM diagnostic_items
  ${where}
`;

console.log(
  `Found ${rows.length} diagnostic_items needing HE backfill${force ? ' (forced)' : ''}.`,
);

let updated = 0;
for (const r of rows) {
  const he = templateHe(r.topic, r.difficulty);
  // Preserve the original `correct` key in case it differs from B (some
  // hand-authored rows may have rotated the answer).
  he.options.correct = r.options?.correct ?? 'B';
  if (dryRun) {
    if (updated < 3) {
      console.log(`would update ${r.id}: topic=${r.topic} → stem_he="${he.stem.slice(0, 60)}…"`);
    }
    updated += 1;
    continue;
  }
  await sql`
    UPDATE diagnostic_items
    SET stem_he = ${he.stem},
        options_he = ${JSON.stringify(he.options)}::jsonb,
        explanation_he = ${he.explanation}
    WHERE id = ${r.id}::uuid
  `;
  updated += 1;
}

console.log(`${dryRun ? '[dry-run] would update' : 'updated'} ${updated} rows.`);
