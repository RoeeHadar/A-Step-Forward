#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

function scrubString(s) {
  return s
    .replace(/\$P\(\\text\{הצלחה\}\)=p\$/g, '$P(\\text{success})=p$')
    .replace(/\$P\(\\text\{נכון\}\)=0\.5\$/g, '$P(\\text{correct})=0.5$')
    .replace(/\$P\(\\text\{עבר\}\|\\text\{בוקר\}\)\$/g, '$P(\\text{pass}|\\text{morning})$')
    .replace(/S_\{\\text\{אחרונים\}\}/g, 'S_{\\mathrm{last}}');
}

function walk(v) {
  if (typeof v === 'string') return scrubString(v);
  if (Array.isArray(v)) return v.map(walk);
  if (v && typeof v === 'object') {
    const out = {};
    for (const [k, val] of Object.entries(v)) out[k] = walk(val);
    return out;
  }
  return v;
}

const ids = [
  'probability_bernoulli',
  'probability_trees_tables',
  'sequences_5pt',
  'sequences_arithmetic',
  'sequences_arithmetic__4pt',
  'sequences_geometric',
  'sequences_geometric__4pt',
];

for (const id of ids) {
  const fp = path.join(DIR, `${id}.json`);
  const j = walk(JSON.parse(fs.readFileSync(fp, 'utf8')));
  fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
  console.log('scrubbed math he', id);
}
