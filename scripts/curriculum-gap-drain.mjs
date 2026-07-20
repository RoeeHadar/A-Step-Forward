#!/usr/bin/env node
/**
 * curriculum-gap-drain — list / mark gaps from curriculum-gap-queue.json
 * Usage:
 *   node scripts/curriculum-gap-drain.mjs --list
 *   node scripts/curriculum-gap-drain.mjs --next=5
 *   node scripts/curriculum-gap-drain.mjs --mark=topic_id:ok
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const QUEUE = path.join(ROOT, 'scripts/seed_data/curriculum-gap-queue.json');
const MATRIX = path.join(ROOT, 'scripts/seed_data/exam-topic-matrix.json');

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}

if (!fs.existsSync(QUEUE)) {
  console.error('Run audit-exam-topic-coverage.mjs first to generate the queue.');
  process.exit(1);
}

const queue = JSON.parse(fs.readFileSync(QUEUE, 'utf8'));
const gaps = queue.gaps || [];

if (args.has('list') || args.has('next')) {
  const n = args.has('next') ? Number(args.get('next')) || 5 : gaps.length;
  for (const g of gaps.slice(0, n)) {
    console.log(JSON.stringify(g));
  }
  process.exit(0);
}

if (args.has('mark')) {
  const [topic, status] = String(args.get('mark')).split(':');
  const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));
  let updated = 0;
  for (const track of Object.values(matrix.tracks || {})) {
    for (const section of track.sections || []) {
      for (const t of section.topics || []) {
        if (t.id === topic || (t.catalog_ids || []).includes(topic)) {
          t.status = status || 'ok';
          updated += 1;
        }
      }
    }
  }
  fs.writeFileSync(MATRIX, `${JSON.stringify(matrix, null, 2)}\n`);
  console.log(`marked ${updated} topic(s) as ${status}`);
}
