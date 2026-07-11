#!/usr/bin/env node
/** Remove alias entries that shadow dedicated authored lessons or misroute topics. */
import fs from 'node:fs';
import path from 'node:path';
import { ALIASES } from './lib/concept-aliases.mjs';

const ALIASES_PATH = path.resolve(
  import.meta.dirname,
  '../apps/web/src/lib/concept-aliases.ts',
);

const index = JSON.parse(
  fs.readFileSync('apps/web/src/lib/lessons-index.generated.json', 'utf8'),
);
const lessonIds = new Set(index.map((e) => e.id));

const BAD_SEMANTIC = new Set([
  'capacitors_parallel_plate',
  'photoelectric_effect',
  'normal_distribution_z_scores',
  'normal_distribution_basics',
]);

const remove = new Set();
for (const from of Object.keys(ALIASES)) {
  if (lessonIds.has(from) || BAD_SEMANTIC.has(from)) remove.add(from);
}

const src = fs.readFileSync(ALIASES_PATH, 'utf8');
const lines = src.split('\n');
const out = lines.filter((line) => {
  const m = line.match(/^\s+(?:'([^']+)'|(\w+)):\s+'([^']+)'/);
  if (!m) return true;
  const key = m[1] ?? m[2];
  return !remove.has(key);
});

fs.writeFileSync(ALIASES_PATH, out.join('\n'));
console.log(`Removed ${remove.size} alias entries from concept-aliases.ts`);
