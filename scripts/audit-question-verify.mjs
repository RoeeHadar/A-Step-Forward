#!/usr/bin/env node
/**
 * Two-tier question-verification gate. Runs the re-derivation / worked-solution
 * checks (scripts/lib/verify-question.mjs) over rewritten lessons.
 *
 * By default scans the rewrite-bar allowlist (only lessons that claim the bar
 * must pass verification). `--all` scans every lesson but only enforces the
 * Tier-1 (verify-block) re-derivation, since the grandfathered corpus predates
 * the needs_review convention.
 *
 * Usage:
 *   node scripts/audit-question-verify.mjs --only=derivatives_rules --strict
 *   node scripts/audit-question-verify.mjs --allowlist=scripts/seed_data/rewrite-bar-allowlist.json --strict
 *   node scripts/audit-question-verify.mjs --all --strict   # Tier-1 only, whole corpus
 */
import fs from 'node:fs';
import path from 'node:path';
import { verifyQuestion } from './lib/verify-question.mjs';

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}

const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const strict = args.get('strict') === 'true';
const scanAll = args.get('all') === 'true';

function allowSet() {
  const only = args.get('only');
  if (only && only !== 'true') return new Set(only.split(',').filter(Boolean));
  const list = args.get('allowlist');
  if (list && list !== 'true') {
    const parsed = JSON.parse(fs.readFileSync(list, 'utf8'));
    return new Set(Array.isArray(parsed) ? parsed : parsed.concept_ids ?? []);
  }
  return null;
}

const allow = allowSet();
const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith('.json'))
  .filter((f) => scanAll || !allow || allow.has(f.replace(/\.json$/, '')))
  .sort();

let failures = 0;
let tier1 = 0;
let questions = 0;
console.log(`Question-verify audit — ${files.length} lesson(s)${scanAll ? ' (Tier-1 only)' : ''}`);
console.log('='.repeat(60));

for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  const qs = Array.isArray(raw.questions) ? raw.questions : [];
  const enforceTier2 = !scanAll; // only enforce needs_review/worked-solution on allowlisted lessons
  const problems = [];
  for (const q of qs) {
    questions += 1;
    const res = verifyQuestion(q);
    if (res.checked) tier1 += 1;
    // In --all mode, only Tier-1 (verify-block) mismatches matter.
    if (!res.ok) {
      if (!res.checked && !enforceTier2) continue;
      problems.push(`${q.id ?? q.ord ?? '?'} [${q.kind}]: ${res.reason}`);
    }
  }
  if (problems.length === 0) {
    if (qs.length) console.log(`  OK    ${file} (${qs.length} q)`);
  } else {
    failures += problems.length;
    console.log(`  FAIL  ${file}`);
    for (const p of problems) console.log(`          - ${p}`);
  }
}

console.log('\n' + '='.repeat(60));
console.log(`Questions scanned: ${questions} | Tier-1 re-derived: ${tier1} | problems: ${failures}`);
if (strict && failures > 0) {
  console.error(`\n[audit-question-verify] STRICT: ${failures} verification problem(s)`);
  process.exit(1);
}
console.log('\n[audit-question-verify] OK');
