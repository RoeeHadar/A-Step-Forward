#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const NON_VERIFIABLE = new Set(['open', 'derivation']);
let n = 0;
let files = 0;
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith('.json'))) {
  const fp = path.join(DIR, f);
  const j = JSON.parse(fs.readFileSync(fp, 'utf8'));
  let changed = false;
  for (const q of j.questions || []) {
    if (NON_VERIFIABLE.has(q.kind) && q.needs_review !== true) {
      q.needs_review = true;
      changed = true;
      n++;
    }
  }
  if (changed) {
    fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
    files++;
  }
}
console.log(`set needs_review on ${n} question(s) across ${files} file(s)`);
