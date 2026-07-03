#!/usr/bin/env node
/**
 * Mirror cursor-expansion-queue output to obsidian-vault/curriculum/expansion-queue.md
 *
 * Usage:
 *   node scripts/sync-obsidian-expansion.mjs
 *   node scripts/sync-obsidian-expansion.mjs --dry-run
 */
import fs from 'node:fs';
import path from 'node:path';
import { lessonMetrics } from './lib/lesson-depth.mjs';
import { hebrewBodyWeak, wordCount, MIN_WORDS, EXPAND_SECTION_KINDS } from './lib/bilingual-utils.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const PROGRESS_PATH = path.join(ROOT, 'scripts/.cursor-expansion-progress.json');
const OUT_PATH = path.join(ROOT, 'obsidian-vault/curriculum/expansion-queue.md');

function loadProgress() {
  if (!fs.existsSync(PROGRESS_PATH)) {
    return { completed: [], failed: {}, policy: 'cursor-composer-2.5', updated_at: null };
  }
  return JSON.parse(fs.readFileSync(PROGRESS_PATH, 'utf8'));
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

const dryRun = process.argv.includes('--dry-run');
const progress = loadProgress();
const completed = new Set(progress.completed ?? []);
const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
const queue = [];

for (const file of files) {
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, file), 'utf8'));
  } catch (err) {
    console.warn(`sync-obsidian-expansion: skip corrupt ${file}: ${err.message}`);
    continue;
  }
  const id = raw.concept_id ?? file.replace(/\.json$/, '');
  if (completed.has(id)) continue;
  const { needs, score, reasons } = lessonNeedsWork(raw);
  if (needs) queue.push({ id, score, reasons: reasons.slice(0, 6) });
}

queue.sort((a, b) => b.score - a.score);

const now = new Date().toISOString();
const top20 = queue.slice(0, 20);
const next10 = queue.slice(0, 10);

const lines = [
  '---',
  'type: expansion-queue',
  `generated: ${now}`,
  `policy: ${progress.policy ?? 'cursor-composer-2.5'}`,
  `done: ${completed.size}`,
  `total: ${files.length}`,
  `remaining: ${queue.length}`,
  'tags:',
  '  - curriculum/expansion',
  '---',
  '',
  '# Expansion Queue',
  '',
  '> Auto-generated. Run `node scripts/sync-obsidian-expansion.mjs` to refresh.',
  '',
  '## Summary',
  '',
  `| Metric | Value |`,
  `|--------|-------|`,
  `| Marked done | ${completed.size} / ${files.length} |`,
  `| Need work | ${queue.length} |`,
  `| Policy | ${progress.policy ?? 'cursor-composer-2.5'} |`,
  `| Progress file updated | ${progress.updated_at ?? 'never'} |`,
  '',
  '## Commands',
  '',
  '```bash',
  'node scripts/cursor-expansion-queue.mjs --next 10',
  'node scripts/cursor-expansion-queue.mjs --mark concept_id1,concept_id2',
  'node scripts/sync-obsidian-expansion.mjs',
  'node scripts/sync-obsidian-concepts.mjs',
  '```',
  '',
  '## Next 10 (priority batch)',
  '',
  '| Score | Concept | Reasons | Note |',
  '|------:|---------|---------|------|',
];

for (const q of next10) {
  lines.push(`| ${q.score} | [[concepts/${q.id}]] | ${q.reasons.join(', ')} | |`);
}

lines.push('', '## Top 20', '', '| Score | Concept | Reasons |', '|------:|---------|---------|');

for (const q of top20) {
  lines.push(`| ${q.score} | [[concepts/${q.id}]] | ${q.reasons.join(', ')} |`);
}

lines.push('', '## Completed concepts', '');

if (completed.size === 0) {
  lines.push('_None marked yet._');
} else {
  for (const id of [...completed].sort()) {
    lines.push(`- [[concepts/${id}|${id}]]`);
  }
}

lines.push('');

if (!dryRun) {
  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  fs.writeFileSync(OUT_PATH, lines.join('\n'), 'utf8');
}

console.log(
  `sync-obsidian-expansion: ${queue.length} in queue, ${completed.size} done${dryRun ? ' (dry-run)' : ''} → ${OUT_PATH}`,
);
