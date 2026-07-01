#!/usr/bin/env node
/**
 * Run lesson depth enrichment phases sequentially.
 *
 * Usage:
 *   node scripts/enrich-lessons.mjs --phase=1 [--dry-run] [--only=combinatorics]
 *   node scripts/enrich-lessons.mjs --phase=all
 *   node scripts/enrich-lessons.mjs --phase=all --validate
 */
import fs from 'node:fs';
import path from 'node:path';
import { normalizeLesson, validateLesson } from './lib/normalize-lesson.mjs';
import { enrichPhase1 } from './lib/enrich-lesson-phase1.mjs';
import { enrichPhase2 } from './lib/enrich-lesson-phase2.mjs';
import { enrichPhase3 } from './lib/enrich-lesson-phase3.mjs';
import { enrichPhase4 } from './lib/enrich-lesson-phase4.mjs';
import {
  lessonMetrics,
  phase1Gates,
  phase2Gates,
  phase3Gates,
  phase4Gates,
} from './lib/lesson-depth.mjs';

const args = new Map();
for (const arg of process.argv.slice(2)) {
  if (!arg.startsWith('--')) continue;
  const [k, v] = arg.slice(2).split('=');
  args.set(k, v ?? 'true');
}

const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const phase = args.get('phase') ?? 'all';
const dryRun = args.get('dry-run') === 'true';
const only = args.get('only');
const validate = args.get('validate') === 'true';

const PHASES = {
  1: enrichPhase1,
  2: enrichPhase2,
  3: enrichPhase3,
  4: enrichPhase4,
};

function runPhases(raw, selected) {
  let out = raw;
  for (const p of selected) {
    out = PHASES[p](out);
  }
  return out;
}

function selectedPhases() {
  if (phase === 'all') return [1, 2, 3, 4];
  return phase.split(',').map((x) => Number.parseInt(x.trim(), 10)).filter((n) => PHASES[n]);
}

const files = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith('.json'))
  .filter((f) => !only || f.replace(/\.json$/, '') === only || f === only)
  .sort();

if (files.length === 0) {
  console.error('[enrich-lessons] no files matched');
  process.exit(1);
}

const phasesToRun = selectedPhases();
console.log(`[enrich-lessons] ${files.length} files, phases: ${phasesToRun.join(',')}, dry-run=${dryRun}`);

let updated = 0;
const errors = [];
const metricsBefore = [];
const metricsAfter = [];

for (const file of files) {
  const fp = path.join(dir, file);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(fp, 'utf8'));
  } catch (e) {
    errors.push(`${file}: parse ${e.message}`);
    continue;
  }

  metricsBefore.push(lessonMetrics(raw));
  const enriched = runPhases(raw, phasesToRun);
  const normalized = normalizeLesson(enriched, file);
  const errs = validateLesson(file, normalized);
  if (errs.length) {
    errors.push(`${file}: ${errs.join('; ')}`);
    continue;
  }

  metricsAfter.push(lessonMetrics(normalized));

  const changed = JSON.stringify(raw) !== JSON.stringify(enriched);
  if (changed && !dryRun) {
    fs.writeFileSync(fp, `${JSON.stringify(enriched, null, 2)}\n`, 'utf8');
    updated += 1;
  }
}

console.log(`[enrich-lessons] updated ${updated}/${files.length} files`);
if (errors.length) {
  console.error(`[enrich-lessons] ${errors.length} errors:`);
  for (const e of errors.slice(0, 20)) console.error(`  ${e}`);
  process.exit(2);
}

if (validate || phase === 'all') {
  const lastPhase = phasesToRun[phasesToRun.length - 1];
  let gates = null;
  if (lastPhase === 1) gates = phase1Gates(metricsAfter);
  else if (lastPhase === 2) gates = phase2Gates(metricsAfter);
  else if (lastPhase === 3) gates = phase3Gates(metricsAfter);
  else if (lastPhase === 4) gates = phase4Gates(metricsAfter);
  else if (phase === 'all') gates = phase4Gates(metricsAfter);

  if (gates) {
    console.log('[enrich-lessons] validation gates:', JSON.stringify(gates, null, 2));
    if (!gates.pass) {
      console.error('[enrich-lessons] validation FAILED');
      process.exit(3);
    }
    console.log('[enrich-lessons] validation PASSED');
  }
}
