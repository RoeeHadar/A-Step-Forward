#!/usr/bin/env node
/**
 * Priority queue for Cursor Composer lesson expansion.
 *
 * Usage:
 *   node scripts/cursor-expansion-queue.mjs
 *   node scripts/cursor-expansion-queue.mjs --next 10
 *   node scripts/cursor-expansion-queue.mjs --mark id1,id2
 *   node scripts/cursor-expansion-queue.mjs --status
 */
import fs from 'node:fs';
import path from 'node:path';
import { lessonMetrics } from './lib/lesson-depth.mjs';
import {
  hebrewBodyWeak,
  wordCount,
  MIN_WORDS,
  EXPAND_SECTION_KINDS,
} from './lib/bilingual-utils.mjs';

const LESSONS_DIR = path.resolve('scripts/seed_data/lessons');
const PROGRESS_PATH = path.resolve('scripts/.cursor-expansion-progress.json');

function loadProgress() {
  if (!fs.existsSync(PROGRESS_PATH)) {
    return { completed: [], failed: {}, updated_at: null, policy: 'cursor-composer-2.5' };
  }
  return JSON.parse(fs.readFileSync(PROGRESS_PATH, 'utf8'));
}

function saveProgress(p) {
  p.updated_at = new Date().toISOString();
  fs.writeFileSync(PROGRESS_PATH, `${JSON.stringify(p, null, 2)}\n`, 'utf8');
}

function lessonNeedsWork(raw) {
  const reasons = [];
  for (const s of raw.sections ?? []) {
    if (!EXPAND_SECTION_KINDS.has(s.kind)) continue;
    const min = MIN_WORDS[s.kind] ?? { en: 90, he: 75 };
    const en = wordCount(s.body_en_md);
    const he = wordCount(s.body_he_md);
    if (en < min.en) reasons.push(`${s.id}:en<${min.en}`);
    if (he < min.he) reasons.push(`${s.id}:he<${min.he}`);
    if (hebrewBodyWeak(s.body_he_md, s.body_en_md)) reasons.push(`${s.id}:he-weak`);
  }
  for (const q of raw.questions ?? []) {
    if (wordCount(q.explanation_en) < 80) reasons.push(`q${q.ord ?? '?'}:expl-en`);
    if (wordCount(q.explanation_he) < 80) reasons.push(`q${q.ord ?? '?'}:expl-he`);
    if (hebrewBodyWeak(q.explanation_he, q.explanation_en)) reasons.push(`q${q.ord ?? '?'}:expl-he-weak`);
  }
  const score =
    reasons.length * 10 +
    (lessonMetrics(raw).heParityFails ?? 0) * 5 +
    Math.max(0, 1200 - lessonMetrics(raw).totalSectionWords);
  return { needs: reasons.length > 0, score, reasons };
}

function parseArgs() {
  const out = { next: 0, mark: null, status: false };
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === '--status') out.status = true;
    else if (a === '--next') out.next = Number(process.argv[++i] ?? 10);
    else if (a === '--mark') out.mark = String(process.argv[++i] ?? '').split(',').filter(Boolean);
  }
  return out;
}

const args = parseArgs();
const progress = loadProgress();
const completed = new Set(progress.completed ?? []);

if (args.mark?.length) {
  for (const id of args.mark) completed.add(id);
  progress.completed = [...completed];
  saveProgress(progress);
  console.log(`Marked ${args.mark.length} complete (${completed.size} total)`);
  process.exit(0);
}

const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
const queue = [];

for (const file of files) {
  const raw = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, file), 'utf8'));
  const id = raw.concept_id ?? file.replace(/\.json$/, '');
  if (completed.has(id)) continue;
  const { needs, score, reasons } = lessonNeedsWork(raw);
  if (needs) queue.push({ id, file, score, reasons: reasons.slice(0, 6) });
}

queue.sort((a, b) => b.score - a.score);

const total = files.length;
const done = completed.size;
const remaining = queue.length;

console.log(`Cursor expansion queue — ${done}/${total} marked done, ${remaining} need work`);
console.log(`Policy: ${progress.policy ?? 'cursor-composer-2.5'}`);
if (progress.updated_at) console.log(`Progress updated: ${progress.updated_at}`);

if (args.status) {
  console.log(JSON.stringify({ done, total, remaining, top: queue.slice(0, 5).map((q) => q.id) }, null, 2));
  process.exit(0);
}

if (args.next > 0) {
  const batch = queue.slice(0, args.next);
  console.log(`\nNext ${batch.length}:`);
  for (const q of batch) {
    console.log(`  ${q.id.padEnd(40)} score=${q.score}  ${q.reasons.join(', ')}`);
  }
  process.exit(0);
}

console.log('\nTop 20 priority:');
for (const q of queue.slice(0, 20)) {
  console.log(`  ${q.score.toString().padStart(5)}  ${q.id.padEnd(40)}  ${q.reasons.join(', ')}`);
}
