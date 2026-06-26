#!/usr/bin/env node
/**
 * One-shot fix for existing `content_sections` and `bagrut_exams` rows where
 * Hebrew text was extracted from PDFs in visual (reversed) order.
 *
 * Reverses char-order for each line that is predominantly Hebrew, re-reverses
 * Latin/digit runs inside (so "(1744)" survives), strips stray PDF artifacts.
 *
 * Idempotent: each run detects whether a row is already in logical order and
 * skips it. Re-ingesting from source is still preferred for full structure;
 * this script fixes the most painful symptom (unreadable Hebrew).
 *
 * Usage:
 *   DATABASE_URL=postgresql://... node scripts/fix-hebrew-content.mjs
 *   DATABASE_URL=... node scripts/fix-hebrew-content.mjs --dry-run
 *   DATABASE_URL=... node scripts/fix-hebrew-content.mjs --limit=10
 */
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}
const sql = neon(url);

const args = new Map();
for (const arg of process.argv.slice(2)) {
  const [k, v] = arg.startsWith('--') ? arg.slice(2).split('=') : [];
  if (k) args.set(k, v ?? 'true');
}
const dryRun = args.get('dry-run') === 'true';
const limit = Number(args.get('limit') ?? 5000);

// ── Helpers ────────────────────────────────────────────────────────────────
const HEBREW_CHAR = /[\u0590-\u05FF\uFB1D-\uFB4F]/;
const ARTIFACT_CHARS = /[\u200B-\u200F\u202A-\u202E\uFEFF\u00AD]/g;
const STRAY_BULLETS_LINE_START = /^\s*[\u2212\u2013\u2014•▪◦∙·]\s*/gm;
const PAGE_NUMBER_LINE = /^\s*[\u2212\u2013\u2014\-]?\s*\d{1,3}\s*[\u2212\u2013\u2014\-]?\s*$/gm;
const MULTI_BLANK = /\n{3,}/g;

function isHebrewLine(line) {
  const hebrew = (line.match(/[\u0590-\u05FF\uFB1D-\uFB4F]/g) ?? []).length;
  const latin = (line.match(/[a-zA-Z]/g) ?? []).length;
  return hebrew > latin && hebrew > 0;
}

function reverseLineWithLatinCorrection(line) {
  const reversed = [...line].reverse().join('');
  return reversed.replace(/[A-Za-z0-9_]+(?:[.,;:!?][A-Za-z0-9_]+)*/g, (m) =>
    [...m].reverse().join(''),
  );
}

function fixVisualOrderHebrew(text) {
  if (!text) return text;
  return text
    .split('\n')
    .map((line) => (isHebrewLine(line) ? reverseLineWithLatinCorrection(line) : line))
    .join('\n');
}

function cleanText(text) {
  if (!text) return text;
  let t = text.replace(ARTIFACT_CHARS, '');
  t = t.replace(STRAY_BULLETS_LINE_START, '');
  t = t.replace(PAGE_NUMBER_LINE, '');
  t = t.replace(MULTI_BLANK, '\n\n');
  return t.trim();
}

/**
 * A row is "already fixed" if reversing its lines produces text that contains
 * MORE recognizable common Hebrew words (זה, של, את, על, אם, כי, לא, לו).
 *
 * If the *original* string contains many of these, it's already in logical
 * order and we should skip it.
 */
const COMMON_HE_WORDS = ['של ', 'את ', 'על ', 'אם ', 'כי ', 'לא ', ' זה', 'לפי ', 'אך ', 'גם '];
function countCommonHebrew(text) {
  let n = 0;
  for (const w of COMMON_HE_WORDS) {
    let i = 0;
    while ((i = text.indexOf(w, i)) !== -1) {
      n += 1;
      i += w.length;
    }
  }
  return n;
}

function needsReversal(text) {
  if (!text || !HEBREW_CHAR.test(text)) return false;
  const reversed = fixVisualOrderHebrew(text);
  return countCommonHebrew(reversed) > countCommonHebrew(text);
}

function fixCell(text) {
  if (!text) return text;
  const cleaned = cleanText(text);
  if (needsReversal(cleaned)) return fixVisualOrderHebrew(cleaned);
  return cleaned;
}

// ── Main ───────────────────────────────────────────────────────────────────
async function fixContentSections() {
  const rows = await sql`
    SELECT id, title, body_md
    FROM content_sections
    ORDER BY updated_at NULLS LAST
    LIMIT ${limit}
  `;
  let updated = 0;
  let skipped = 0;

  for (const row of rows) {
    const newTitle = fixCell(row.title);
    const newBody = fixCell(row.body_md);
    if (newTitle === row.title && newBody === row.body_md) {
      skipped += 1;
      continue;
    }
    if (!dryRun) {
      await sql`
        UPDATE content_sections
        SET title = ${newTitle}, body_md = ${newBody}, updated_at = NOW()
        WHERE id = ${row.id}
      `;
    }
    updated += 1;
    if (updated <= 5) {
      console.log(`  + fixed: ${String(row.title).slice(0, 60)} → ${String(newTitle).slice(0, 60)}`);
    }
  }
  return { updated, skipped, total: rows.length };
}

async function fixBagrutExams() {
  const rows = await sql`
    SELECT id, display_name
    FROM bagrut_exams
    LIMIT ${limit}
  `;
  let updated = 0;
  for (const row of rows) {
    const newName = fixCell(row.display_name);
    if (newName === row.display_name) continue;
    if (!dryRun) {
      await sql`UPDATE bagrut_exams SET display_name = ${newName} WHERE id = ${row.id}`;
    }
    updated += 1;
  }
  return { updated, total: rows.length };
}

console.log(`fix-hebrew-content: dry_run=${dryRun} limit=${limit}\n`);
const sections = await fixContentSections();
const bagrut = await fixBagrutExams();
console.log(`\ncontent_sections: ${sections.updated}/${sections.total} updated, ${sections.skipped} already-fixed`);
console.log(`bagrut_exams: ${bagrut.updated}/${bagrut.total} updated`);
