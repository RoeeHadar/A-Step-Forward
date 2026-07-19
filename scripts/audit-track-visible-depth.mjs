#!/usr/bin/env node
/**
 * audit-track-visible-depth — catches the class of bug where the CURRICULUM
 * CATALOG assigns a concept to a points level (so learners of that track browse
 * it), but the lesson's questions are all gated ABOVE that track — so the track
 * lands on the lesson and sees fewer than the required number of questions.
 *
 * This complements audit-track-scope.mjs, which only reasons from the lesson's
 * own `math_track` and cannot see that the catalog serves a wider audience.
 *
 * Old-track-only concepts (382 calculus deliberately absent from new 372) are
 * excluded — a new-track 3pt learner correctly sees 0 of those.
 *
 * Usage: node scripts/audit-track-visible-depth.mjs [--min=15] [--json]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const CAT_PATH = path.join(ROOT, 'apps/web/src/lib/curriculum-categories.ts');
const ALIAS_PATH = path.join(ROOT, 'apps/web/src/lib/concept-aliases.ts');

const RANK = { '3pt': 0, '4pt': 1, '5pt': 2 };
const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const MIN = Number(args.get('min') ?? 15);
const asJson = args.get('json') === 'true';

const aliasSrc = fs.readFileSync(ALIAS_PATH, 'utf8');
const aliasMap = new Map();
for (const m of aliasSrc.matchAll(/^\s*([a-z0-9_]+):\s*'([a-z0-9_]+)',/gm)) aliasMap.set(m[1], m[2]);
function resolveAlias(id) {
  let cur = id;
  const seen = new Set();
  while (aliasMap.has(cur) && !seen.has(cur)) {
    seen.add(cur);
    cur = aliasMap.get(cur);
  }
  return cur;
}

const catSrc = fs.readFileSync(CAT_PATH, 'utf8');
function extractArray(name, seen = new Set()) {
  if (seen.has(name)) return [];
  seen.add(name);
  const m = catSrc.match(new RegExp(`const ${name} = \\[([\\s\\S]*?)\\];`, 'm'));
  if (!m) return [];
  let out = [...m[1].matchAll(/'([a-z0-9_]+)'/g)].map((x) => x[1]);
  for (const ref of m[1].matchAll(/\.\.\.([A-Z0-9_]+)/g)) out = out.concat(extractArray(ref[1], seen));
  return [...new Set(out)];
}
const LEVEL_ARR = { '3pt': 'MATH_3PT_CONCEPTS', '4pt': 'MATH_4PT_CONCEPTS', '5pt': 'MATH_5PT_CONCEPTS' };
const OLD_TRACK_ONLY = new Set(extractArray('MATH_3PT_OLD_TRACK_ONLY'));

const servedLevels = new Map();
for (const [lvl, arr] of Object.entries(LEVEL_ARR)) {
  for (const id of extractArray(arr)) {
    if (lvl === '3pt' && OLD_TRACK_ONLY.has(id)) continue; // deliberately hidden from new 372
    const canon = resolveAlias(id);
    if (!servedLevels.has(canon)) servedLevels.set(canon, new Set());
    servedLevels.get(canon).add(lvl);
  }
}

const flagged = [];
for (const f of fs.readdirSync(LESSONS_DIR).filter((x) => x.endsWith('.json'))) {
  const d = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, f), 'utf8'));
  if (d.subject !== 'math' || d.level !== 'high_school') continue;
  const levels = servedLevels.get(d.concept_id);
  if (!levels) continue;
  const qs = Array.isArray(d.questions) ? d.questions : [];
  const problems = [];
  for (const lvl of [...levels].sort((a, b) => RANK[a] - RANK[b])) {
    const r = RANK[lvl];
    const visible = qs.filter((q) => !q.points_level_min || RANK[q.points_level_min] <= r).length;
    if (visible < MIN) problems.push({ level: lvl, visible });
  }
  if (problems.length) flagged.push({ concept_id: d.concept_id, served: [...levels], problems });
}

if (asJson) {
  console.log(JSON.stringify({ min: MIN, flagged }, null, 2));
} else {
  console.log(`Track visible-depth audit (min ${MIN} visible questions per catalog-served level)`);
  console.log('='.repeat(70));
  for (const x of flagged) {
    const p = x.problems.map((y) => `${y.level}:${y.visible}`).join(' ');
    console.log(`  ${x.concept_id.padEnd(30)} served=[${x.served.join(',')}]  UNDER: ${p}`);
  }
  console.log('='.repeat(70));
  console.log(flagged.length === 0 ? '[audit-track-visible-depth] OK' : `[audit-track-visible-depth] ${flagged.length} under-served`);
}
process.exit(flagged.length === 0 ? 0 : 1);
