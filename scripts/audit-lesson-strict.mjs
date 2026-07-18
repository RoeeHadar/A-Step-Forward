#!/usr/bin/env node
/**
 * Strict lesson validation for NEW / pilot-quality lessons.
 *
 * The default seed validator (validateLesson) stays permissive so the 207
 * grandfathered lessons keep seeding. This runner applies the higher bar
 * (validateLessonStrict): structured agent_hints, >=1 skill_atom per question,
 * non-broken answer payloads, >=3 question kinds, and every taught atom
 * exercised. Scope it to the pilot set with --pilot <file> or --only <ids>.
 *
 * Usage:
 *   node scripts/audit-lesson-strict.mjs --only=derivatives_rules,integrals_intro
 *   node scripts/audit-lesson-strict.mjs --pilot=scripts/seed_data/pilot-bagrut-math-5.json
 *   node scripts/audit-lesson-strict.mjs            # all files (report only)
 *   node scripts/audit-lesson-strict.mjs --strict   # exit 1 on any violation
 */
import fs from 'node:fs';
import path from 'node:path';
import { normalizeLesson, validateLessonStrict } from './lib/normalize-lesson.mjs';

const args = new Map();
for (const arg of process.argv.slice(2)) {
  if (!arg.startsWith('--')) continue;
  const [k, v] = arg.slice(2).split('=');
  args.set(k, v ?? 'true');
}

const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const strict = args.get('strict') === 'true';

/** Resolve the target concept-id set from --only or --pilot, else all files. */
function resolveTargets() {
  const only = args.get('only');
  if (only && only !== 'true') return new Set(only.split(',').filter(Boolean));
  const pilot = args.get('pilot');
  if (pilot && pilot !== 'true') {
    const parsed = JSON.parse(fs.readFileSync(pilot, 'utf8'));
    const ids = Array.isArray(parsed) ? parsed : parsed.concept_ids ?? [];
    return new Set(ids);
  }
  return null; // all
}

const targets = resolveTargets();
const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith('.json'))
  .filter((f) => !targets || targets.has(f.replace(/\.json$/, '')))
  .sort();

console.log(`Strict lesson audit — ${files.length} file(s)${targets ? ' (scoped)' : ''}`);
console.log('='.repeat(60));

let totalViolations = 0;
let lessonsWithViolations = 0;

for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  const data = normalizeLesson(raw, file);
  const errors = validateLessonStrict(file, data);
  if (errors.length) {
    lessonsWithViolations += 1;
    totalViolations += errors.length;
    console.log(`\n[${file}] ${errors.length} violation(s):`);
    for (const e of errors) console.log(`  - ${e}`);
  }
}

console.log('\n' + '='.repeat(60));
console.log(`Lessons with violations: ${lessonsWithViolations}/${files.length}`);
console.log(`Total violations: ${totalViolations}`);

if (strict && totalViolations > 0) {
  console.error('\n[audit-lesson-strict] STRICT: violations present');
  process.exit(1);
}
console.log('\n[audit-lesson-strict] OK');
