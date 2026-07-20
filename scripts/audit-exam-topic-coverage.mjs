#!/usr/bin/env node
/**
 * audit-exam-topic-coverage — every matrix topic must resolve to an authored lesson.
 * Usage: node scripts/audit-exam-topic-coverage.mjs [--strict] [--track=4pt,5pt]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MATRIX = path.join(ROOT, 'scripts/seed_data/exam-topic-matrix.json');
const LESSONS = path.join(ROOT, 'scripts/seed_data/lessons');
const ALIASES_SRC = path.join(ROOT, 'apps/web/src/lib/concept-aliases.ts');

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const strict = args.has('strict');
const trackFilter = args.get('track')
  ? new Set(args.get('track').split(',').map((s) => s.trim()))
  : null;

function loadAliases() {
  const src = fs.readFileSync(ALIASES_SRC, 'utf8');
  const map = {};
  const re = /^\s*([a-z0-9_]+):\s*'([a-z0-9_]+)'/gm;
  let m;
  while ((m = re.exec(src))) map[m[1]] = m[2];
  return map;
}

function lessonExists(id) {
  return fs.existsSync(path.join(LESSONS, `${id}.json`));
}

function resolveId(id, aliases) {
  if (lessonExists(id)) return id;
  if (aliases[id] && lessonExists(aliases[id])) return aliases[id];
  for (const suf of ['__4pt', '__5pt', '_4pt', '_5pt']) {
    if (lessonExists(id + suf)) return id + suf;
  }
  return null;
}

const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));
const aliases = loadAliases();
const enforced = new Set(matrix.enforced_tracks || []);
let errors = 0;
const gaps = [];

for (const [track, data] of Object.entries(matrix.tracks || {})) {
  if (trackFilter && !trackFilter.has(track)) continue;
  for (const section of data.sections || []) {
    for (const topic of section.topics || []) {
      const candidates = [topic.id, ...(topic.catalog_ids || [])];
      let hit = null;
      for (const c of candidates) {
        hit = resolveId(c, aliases);
        if (hit) break;
      }
      const status = hit ? (topic.status === 'missing' ? 'authored_pending_status' : topic.status) : 'missing';
      if (!hit) {
        const msg = `[E] missing lesson for ${track}/${section.id}/${topic.id}`;
        console.error(msg);
        errors += 1;
        gaps.push({
          severity: 1,
          kind: 'missing',
          track,
          section: section.id,
          topic: topic.id,
          catalog_ids: topic.catalog_ids || [],
          facets: topic.facets || [],
        });
      } else if (topic.status === 'thin' || topic.status === 'missing') {
        gaps.push({
          severity: topic.status === 'missing' ? 1 : 3,
          kind: topic.status,
          track,
          section: section.id,
          topic: topic.id,
          lesson: hit,
          facets: topic.facets || [],
        });
      }
      // wrong alias check
      for (const wa of matrix.wrong_aliases || []) {
        for (const cid of topic.catalog_ids || []) {
          if (cid !== wa.catalog_id) continue;
          const target = aliases[cid];
          if (target && (wa.forbidden_targets || []).includes(target)) {
            console.error(`[E] wrong_alias ${cid} → ${target}`);
            errors += 1;
            gaps.push({
              severity: 0,
              kind: 'wrong_alias',
              track,
              topic: topic.id,
              catalog_id: cid,
              forbidden_target: target,
            });
          }
        }
      }
      void status;
    }
  }
  if (enforced.has(track) && strict && errors > 0) {
    // counted globally
  }
}

const queuePath = path.join(ROOT, 'scripts/seed_data/curriculum-gap-queue.json');
gaps.sort((a, b) => a.severity - b.severity || String(a.topic).localeCompare(String(b.topic)));
fs.writeFileSync(queuePath, `${JSON.stringify({ generated_at: new Date().toISOString(), gaps }, null, 2)}\n`);
console.log(`audit-exam-topic-coverage: ${errors} error(s); wrote ${gaps.length} gap(s) to curriculum-gap-queue.json`);

if (strict) {
  const enforcedErrors = gaps.filter(
    (g) => (g.kind === 'missing' || g.kind === 'wrong_alias') && enforced.has(g.track),
  ).length;
  if (enforcedErrors > 0) {
    console.error(`STRICT: ${enforcedErrors} enforced-track gap(s)`);
    process.exit(1);
  }
}
