#!/usr/bin/env node
/**
 * Depth audit for authored lessons — used locally and in CI.
 *
 * Usage:
 *   node scripts/audit-lesson-depth.mjs
 *   node scripts/audit-lesson-depth.mjs --strict
 *   node scripts/audit-lesson-depth.mjs --phase=1
 */
import fs from 'node:fs';
import path from 'node:path';
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
const strict = args.get('strict') === 'true';
const phase = args.get('phase') ?? '4';

const files = fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
const metrics = [];

for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  metrics.push({ file, ...lessonMetrics(raw) });
}

const avg = (key) => metrics.reduce((s, m) => s + m[key], 0) / metrics.length;

console.log(`Lesson depth audit — ${files.length} files`);
console.log('='.repeat(60));
console.log(`Avg section words:     ${avg('totalSectionWords').toFixed(0)}`);
console.log(`Avg questions/lesson:  ${avg('questionCount').toFixed(1)}`);
console.log(`Avg expl words:        ${avg('avgExplanationWords').toFixed(1)}`);
console.log(`Lessons w/ 0 questions: ${metrics.filter((m) => m.questionCount === 0).length}`);
console.log(`Lessons w/ why_matters: ${metrics.filter((m) => m.hasWhyMatters).length}`);
console.log(`Avg HE parity fails:   ${avg('heParityFails').toFixed(2)}`);

const shallow = [...metrics].sort((a, b) => a.totalSectionWords - b.totalSectionWords).slice(0, 10);
console.log('\nShallowest 10 (by section words):');
for (const m of shallow) {
  console.log(`  ${m.totalSectionWords.toString().padStart(5)}  ${m.file}  (q=${m.questionCount})`);
}

const phaseNum = Number.parseInt(phase, 10) || 4;
const gates =
  phaseNum <= 1
    ? phase1Gates(metrics)
    : phaseNum === 2
      ? phase2Gates(metrics)
      : phaseNum === 3
        ? phase3Gates(metrics)
        : phase4Gates(metrics);

console.log(`\nPhase ${phaseNum} gates:`, JSON.stringify(gates, null, 2));

if (strict && !gates.pass) {
  console.error('\n[audit-lesson-depth] STRICT: gates failed');
  process.exit(1);
}

console.log('\n[audit-lesson-depth] OK');
