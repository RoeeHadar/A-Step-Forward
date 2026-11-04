#!/usr/bin/env node
/**
 * Skill-tag accuracy guard (AS-77). Port of the AS-76 scan heuristic
 * (items/AS-76/work/scan.py): a question is a candidate mislabel when every
 * current skill_atom shares 0 tokens with stem_en + verify.expr while another
 * atom from the lesson's agent_hints.skill_atoms_unlocked shares >= 2.
 * Known candidates live in scripts/audit-skill-tags.baseline.json; only NEW
 * candidates fail.
 *
 * Usage:
 *   node scripts/audit-skill-tags.mjs                      # check vs baseline (exit 1 on new)
 *   node scripts/audit-skill-tags.mjs --dir=<lessons dir> --baseline=<file>
 *   node scripts/audit-skill-tags.mjs --write-baseline     # regenerate baseline
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const STOP = new Set(['of', 'the', 'a', 'and', 'to', 'in', 'core', 'skill', 'basic', 'rule', 'find', 'compute', 'solve']);

export function toks(s) {
  const out = new Set();
  for (const w of new Set(String(s).toLowerCase().match(/[a-z]+/g) ?? [])) {
    out.add(w);
    if (w.endsWith('s') && w.length > 3) out.add(w.slice(0, -1));
  }
  for (const w of STOP) out.delete(w);
  return out;
}

/** Candidates for one parsed lesson. */
export function scanLesson(file, d) {
  const rows = [];
  const un = ((d.agent_hints ?? {}).skill_atoms_unlocked ?? []).filter((a) => typeof a === 'string');
  (d.questions ?? []).forEach((q, i) => {
    const expr = (q.verify ?? {}).expr;
    const st = toks(`${q.stem_en ?? ''} ${expr === undefined || expr === null ? '' : String(expr)}`);
    const cur = (q.skill_atoms ?? []).filter((a) => typeof a === 'string');
    if (!cur.length) return;
    const sc = (a) => { let n = 0; for (const t of toks(a.replaceAll('_', ' '))) if (st.has(t)) n++; return n; };
    let best = null; let bs = -1;
    for (const a of un) { const s = sc(a); if (s > bs) { best = a; bs = s; } }
    if (best && cur.every((a) => sc(a) === 0) && bs >= 2 && !cur.includes(best)) {
      rows.push({ file, index: i, ord: q.ord ?? null, current: cur, suggested: best, score: bs });
    }
  });
  return rows;
}

export function scanDir(dir) {
  return fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()
    .flatMap((f) => scanLesson(f, JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'))));
}

export const keyOf = (r) => `${r.file}#${r.index}:${[...r.current].join(',')}`;

export function newCandidates(rows, baseline) {
  const known = new Set(baseline.map(keyOf));
  return rows.filter((r) => !known.has(keyOf(r)));
}

function main() {
  const args = new Map();
  for (const a of process.argv.slice(2)) { if (a.startsWith('--')) { const [k, v] = a.slice(2).split('='); args.set(k, v ?? 'true'); } }
  const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
  const baselinePath = args.get('baseline') ?? 'scripts/audit-skill-tags.baseline.json';
  const rows = scanDir(dir);
  if (args.get('write-baseline') === 'true') {
    fs.writeFileSync(baselinePath, `${JSON.stringify(rows.map(({ score, ...r }) => r), null, 1)}\n`);
    console.log(`[audit-skill-tags] wrote ${rows.length} baseline candidates to ${baselinePath}`);
    return 0;
  }
  const baseline = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
  const fresh = newCandidates(rows, baseline);
  if (fresh.length) {
    for (const r of fresh) console.error(`[audit-skill-tags] NEW ${r.file} q[${r.index}] (ord ${r.ord}): tagged ${r.current.join(',')} but stem matches ${r.suggested} (score ${r.score})`);
    console.error(`[audit-skill-tags] FAIL: ${fresh.length} new candidate(s) (${rows.length} total, ${baseline.length} baselined)`);
    return 1;
  }
  console.log(`[audit-skill-tags] OK (${rows.length} candidates, all baselined)`);
  return 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) process.exitCode = main();
