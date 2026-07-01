#!/usr/bin/env node
/**
 * Editorial pass — removes enrichment artifacts and fills missing summaries.
 *
 * Usage:
 *   node scripts/editorial-pass.mjs
 *   node scripts/editorial-pass.mjs --dry-run
 */
import fs from 'node:fs';
import path from 'node:path';
import { editorialCleanup, editorialMetrics } from './lib/editorial-cleanup.mjs';
import { normalizeLesson } from './lib/normalize-lesson.mjs';

const dryRun = process.argv.includes('--dry-run');
const dir = 'scripts/seed_data/lessons';

const files = fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
const before = { boilerplate: 0, heDup: 0, missingSummaryHe: 0 };
const after = { boilerplate: 0, heDup: 0, missingSummaryHe: 0 };
let changed = 0;
let summariesAdded = 0;

for (const file of files) {
  const fp = path.join(dir, file);
  const raw = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const b = editorialMetrics(raw);
  before.boilerplate += b.boilerplate;
  before.heDup += b.heDup;
  before.missingSummaryHe += b.missingSummaryHe ? 1 : 0;

  const hadSummary = !!(raw.summary_he ?? '').trim() && !!(raw.summary_en ?? '').trim();
  const cleaned = normalizeLesson(editorialCleanup(raw));
  const a = editorialMetrics(cleaned);
  after.boilerplate += a.boilerplate;
  after.heDup += a.heDup;
  after.missingSummaryHe += a.missingSummaryHe ? 1 : 0;

  const out = `${JSON.stringify(cleaned, null, 2)}\n`;
  const prev = fs.readFileSync(fp, 'utf8');
  if (out !== prev) {
    changed++;
    if (!hadSummary && cleaned.summary_he && cleaned.summary_en) summariesAdded++;
    if (!dryRun) fs.writeFileSync(fp, out, 'utf8');
  }
}

console.log(`Editorial pass — ${files.length} lessons (${dryRun ? 'dry-run' : 'written'})`);
console.log('='.repeat(60));
console.log(`Files changed:           ${changed}`);
console.log(`Summaries added:         ${summariesAdded}`);
console.log(`Before — lessons w/ boilerplate markers: ${before.boilerplate}`);
console.log(`After  — lessons w/ boilerplate markers: ${after.boilerplate}`);
console.log(`Before — HE/EN duplicate sections:       ${before.heDup}`);
console.log(`After  — HE/EN duplicate sections:       ${after.heDup}`);
console.log(`Before — missing summary_he:             ${before.missingSummaryHe}`);
console.log(`After  — missing summary_he:             ${after.missingSummaryHe}`);
console.log('\n[editorial-pass] OK');
