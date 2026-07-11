#!/usr/bin/env node
/**
 * Audit lesson coverage, locale fields, and misleading aliases.
 * Usage: node scripts/audit-lesson-health.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { ALIASES as CONCEPT_ID_ALIASES } from './lib/concept-aliases.mjs';

const LESSONS_DIR = 'scripts/seed_data/lessons';
const INDEX_PATH = 'apps/web/src/lib/lessons-index.generated.json';
const CATEGORIES_PATH = 'apps/web/src/lib/curriculum-categories.ts';

function looksHebrew(text) {
  const he = (text.match(/[\u0590-\u05FF]/g) ?? []).length;
  const lat = (text.match(/[a-zA-Z]/g) ?? []).length;
  return he > lat && he >= 8;
}
function looksEnglish(text) {
  const he = (text.match(/[\u0590-\u05FF]/g) ?? []).length;
  const lat = (text.match(/[a-zA-Z]/g) ?? []).length;
  return lat > he && lat >= 8;
}

const index = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
const indexIds = new Set(index.map((e) => e.id));

const lessonFiles = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json'));
const authoredIds = new Set();
const localeIssues = [];

for (const file of lessonFiles) {
  const data = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, file), 'utf8'));
  const cid = data.concept_id;
  if (cid) authoredIds.add(cid);
  for (const sec of data.sections ?? []) {
    const he = sec.body_he_md?.trim() ?? '';
    const en = sec.body_en_md?.trim() ?? '';
    if (he && looksEnglish(he)) {
      localeIssues.push({ file, section: sec.id, issue: 'body_he_md looks English', concept_id: cid });
    }
    if (en && looksHebrew(en)) {
      localeIssues.push({ file, section: sec.id, issue: 'body_en_md looks Hebrew', concept_id: cid });
    }
    if (!he && en) {
      localeIssues.push({ file, section: sec.id, issue: 'missing body_he_md', concept_id: cid });
    }
    if (!en && he) {
      localeIssues.push({ file, section: sec.id, issue: 'missing body_en_md', concept_id: cid });
    }
  }
}

const badAliases = [];
for (const [from, to] of Object.entries(CONCEPT_ID_ALIASES)) {
  if (from === to) continue;
  const fromHasOwn = authoredIds.has(from) || indexIds.has(from);
  const toHas = authoredIds.has(to) || indexIds.has(to);
  if (!toHas) {
    badAliases.push({ from, to, issue: 'alias target has no lesson' });
  } else if (!fromHasOwn && toHas) {
    badAliases.push({ from, to, issue: 'redirect-only (shows different lesson title)' });
  }
}

// Parse concept_ids from curriculum categories (rough)
const catSrc = fs.readFileSync(CATEGORIES_PATH, 'utf8');
const catalogIds = new Set();
for (const m of catSrc.matchAll(/concept_ids:\s*\[([\s\S]*?)\]/g)) {
  for (const id of m[1].match(/'([^']+)'/g) ?? []) {
    catalogIds.add(id.slice(1, -1));
  }
}

const catalogMissing = [];
for (const id of catalogIds) {
  const alias = CONCEPT_ID_ALIASES[id] ?? id;
  const has =
    authoredIds.has(id) ||
    indexIds.has(id) ||
    authoredIds.has(alias) ||
    indexIds.has(alias);
  if (!has) catalogMissing.push(id);
}

console.log('=== Lesson health audit ===');
console.log(`Authored lessons: ${authoredIds.size}`);
console.log(`Index entries: ${indexIds.size}`);
console.log(`Catalog concept_ids: ${catalogIds.size}`);
console.log(`Catalog with no lesson/alias target: ${catalogMissing.length}`);
if (catalogMissing.length) {
  console.log('  sample:', catalogMissing.slice(0, 20).join(', '));
}
console.log(`Misleading redirect aliases: ${badAliases.length}`);
for (const row of badAliases.slice(0, 30)) {
  console.log(`  ${row.from} → ${row.to} (${row.issue})`);
}
console.log(`Locale field issues in JSON: ${localeIssues.length}`);
for (const row of localeIssues.slice(0, 25)) {
  console.log(`  ${row.concept_id}/${row.section}: ${row.issue}`);
}
if (localeIssues.length > 25) console.log(`  … and ${localeIssues.length - 25} more`);

process.exit(0);
