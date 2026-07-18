#!/usr/bin/env node
/**
 * Audit math notation (KaTeX + remark-math) across lessons so nothing renders
 * unreadable on the site. Scans questions AND section bodies.
 *
 * Usage:
 *   node scripts/audit-lesson-math.mjs --pilot=scripts/seed_data/pilot-strict-allowlist.json --strict
 *   node scripts/audit-lesson-math.mjs --only=derivatives_rules
 *   node scripts/audit-lesson-math.mjs            # all lessons (report only)
 */
import fs from 'node:fs';
import path from 'node:path';
import { findMathErrors, questionMathFields } from './lib/katex-check.mjs';

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const strict = args.get('strict') === 'true';

function resolveTargets() {
  const only = args.get('only');
  if (only && only !== 'true') return new Set(only.split(',').filter(Boolean));
  const pilot = args.get('pilot');
  if (pilot && pilot !== 'true') {
    const parsed = JSON.parse(fs.readFileSync(pilot, 'utf8'));
    return new Set(Array.isArray(parsed) ? parsed : parsed.concept_ids ?? []);
  }
  return null;
}

const targets = resolveTargets();
const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith('.json'))
  .filter((f) => !targets || targets.has(f.replace(/\.json$/, '')))
  .sort();

const SECTION_FIELDS = [
  'body_en_md', 'body_he_md', 'checkpoint_solution_en', 'checkpoint_solution_he',
];

let total = 0;
let filesWith = 0;
for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  const errs = [];
  (raw.sections ?? []).forEach((s, i) => {
    for (const f of SECTION_FIELDS) errs.push(...findMathErrors(s[f], `section[${i}].${f}`));
    (s.exercises ?? []).forEach((ex, j) => {
      errs.push(...findMathErrors(ex.body_en, `section[${i}].exercises[${j}].body_en`));
      errs.push(...findMathErrors(ex.body_he, `section[${i}].exercises[${j}].body_he`));
    });
  });
  (raw.questions ?? []).forEach((q, i) => {
    for (const [text, label] of questionMathFields(q, i)) errs.push(...findMathErrors(text, label));
  });
  if (errs.length) {
    filesWith += 1;
    total += errs.length;
    console.log(`\n[${file}] ${errs.length} math issue(s):`);
    for (const e of errs.slice(0, 40)) console.log(`  - ${e}`);
    if (errs.length > 40) console.log(`  ... and ${errs.length - 40} more`);
  }
}

console.log('\n' + '='.repeat(60));
console.log(`Files with math issues: ${filesWith}/${files.length}`);
console.log(`Total issues: ${total}`);
if (strict && total > 0) {
  console.error('\n[audit-lesson-math] STRICT: math issues present');
  process.exit(1);
}
console.log('\n[audit-lesson-math] OK');
