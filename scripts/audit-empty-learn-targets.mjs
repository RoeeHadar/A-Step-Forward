#!/usr/bin/env node
/**
 * audit-empty-learn-targets — catalog concept_ids must resolve to a real lesson
 * whose title/skills are not a known wrong-family alias (matrix.wrong_aliases).
 * Usage: node scripts/audit-empty-learn-targets.mjs [--strict]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MATRIX = path.join(ROOT, 'scripts/seed_data/exam-topic-matrix.json');
const LESSONS = path.join(ROOT, 'scripts/seed_data/lessons');
const ALIASES_SRC = path.join(ROOT, 'apps/web/src/lib/concept-aliases.ts');
const CATEGORIES = path.join(ROOT, 'apps/web/src/lib/curriculum-categories.ts');

const strict = process.argv.includes('--strict');
const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));

function loadAliases() {
  const src = fs.readFileSync(ALIASES_SRC, 'utf8');
  const map = {};
  const re = /^\s*([a-z0-9_]+):\s*'([a-z0-9_]+)'/gm;
  let m;
  while ((m = re.exec(src))) map[m[1]] = m[2];
  return map;
}

function lessonExists(id) {
  return fs.existsSync(path.join(LESSONS, `${id}.json`));
}

const aliases = loadAliases();
const catSrc = fs.readFileSync(CATEGORIES, 'utf8');
const catalogIds = new Set();
for (const m of catSrc.matchAll(/'([a-z][a-z0-9_]*)'/g)) {
  catalogIds.add(m[1]);
}

let errors = 0;

for (const wa of matrix.wrong_aliases || []) {
  const target = aliases[wa.catalog_id];
  if (target && (wa.forbidden_targets || []).includes(target)) {
    console.error(`[E] empty/wrong learn target: ${wa.catalog_id} aliases to forbidden ${target}`);
    errors += 1;
  }
  if (!target && !lessonExists(wa.catalog_id)) {
    // Will also be caught as missing until authored
    if (catalogIds.has(wa.catalog_id)) {
      console.error(`[E] catalog id ${wa.catalog_id} has no lesson and no safe alias`);
      errors += 1;
    }
  }
}

// Known stub pattern: alias to unrelated family while catalog label implies laws
const sineAlias = aliases.trigonometry_plane_sine_cosine_law;
if (sineAlias === 'trigonometry_ratios') {
  console.error('[E] trigonometry_plane_sine_cosine_law → trigonometry_ratios (laws page empty/wrong)');
  errors += 1;
}

console.log(`audit-empty-learn-targets: ${errors} error(s)`);
if (strict && errors > 0) process.exit(1);
