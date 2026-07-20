#!/usr/bin/env node
/**
 * audit-catalog-shelving — flag concepts shelved in the wrong exam section.
 * Reads exam-topic-matrix shelving_rules + curriculum-categories.ts sections.
 * Usage: node scripts/audit-catalog-shelving.mjs [--strict]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MATRIX = path.join(ROOT, 'scripts/seed_data/exam-topic-matrix.json');
const CATEGORIES = path.join(ROOT, 'apps/web/src/lib/curriculum-categories.ts');

const strict = process.argv.includes('--strict');
const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));
const src = fs.readFileSync(CATEGORIES, 'utf8');

let errors = 0;
for (const rule of matrix.shelving_rules || []) {
  // Find section block by id: 'paper1_algebra_5pt'
  const re = new RegExp(
    `id:\\s*'${rule.section_id}'[\\s\\S]*?concept_ids:\\s*\\[([\\s\\S]*?)\\]`,
    'm',
  );
  const m = src.match(re);
  if (!m) {
    console.warn(`[W] section ${rule.section_id} not found in curriculum-categories.ts`);
    continue;
  }
  const block = m[1];
  for (const cid of rule.forbidden_concept_ids || []) {
    if (new RegExp(`'${cid}'`).test(block)) {
      console.error(`[E] shelving: '${cid}' must not appear in section ${rule.section_id}`);
      errors += 1;
    }
  }
}

console.log(`audit-catalog-shelving: ${errors} error(s)`);
if (strict && errors > 0) process.exit(1);
