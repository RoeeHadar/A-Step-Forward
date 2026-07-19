#!/usr/bin/env node
/**
 * Rewrite-bar gate: enforces the PER-LESSON depth floors + archetype breadth from
 * docs/curriculum/lesson-rewrite-scope-map.md on lessons that have completed the
 * rewrite. Opt-in via scripts/seed_data/rewrite-bar-allowlist.json (same pattern
 * as pilot-strict-allowlist) so the grandfathered corpus is not retroactively failed.
 *
 * Usage:
 *   node scripts/audit-lesson-rewrite-bar.mjs --only=derivatives_rules
 *   node scripts/audit-lesson-rewrite-bar.mjs --allowlist=scripts/seed_data/rewrite-bar-allowlist.json --strict
 */
import fs from 'node:fs';
import path from 'node:path';
import { lessonMetrics, phase6PerLesson } from './lib/lesson-depth.mjs';

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}

const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const strict = args.get('strict') === 'true';

function targets() {
  const only = args.get('only');
  if (only && only !== 'true') return new Set(only.split(',').filter(Boolean));
  const list = args.get('allowlist');
  if (list && list !== 'true') {
    const parsed = JSON.parse(fs.readFileSync(list, 'utf8'));
    return new Set(Array.isArray(parsed) ? parsed : parsed.concept_ids ?? []);
  }
  return null;
}

const want = targets();
const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith('.json'))
  .filter((f) => !want || want.has(f.replace(/\.json$/, '')))
  .sort();

let failed = 0;
console.log(`Rewrite-bar audit — ${files.length} lesson(s)`);
console.log('='.repeat(60));
for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  const { pass, reasons } = phase6PerLesson(lessonMetrics(raw));
  if (pass) {
    console.log(`  OK    ${file}`);
  } else {
    failed += 1;
    console.log(`  FAIL  ${file}`);
    for (const r of reasons) console.log(`          - ${r}`);
  }
}

console.log('\n' + '='.repeat(60));
console.log(`Lessons at rewrite bar: ${files.length - failed}/${files.length}`);
if (strict && failed > 0) {
  console.error(`\n[audit-lesson-rewrite-bar] STRICT: ${failed} lesson(s) below the rewrite bar`);
  process.exit(1);
}
console.log('\n[audit-lesson-rewrite-bar] OK');
