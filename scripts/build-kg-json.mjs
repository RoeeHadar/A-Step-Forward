#!/usr/bin/env node
/**
 * Build a static JSON snapshot of the prerequisite knowledge graph from
 * the YAML files in content/knowledge-graph/.
 *
 * Output: apps/web/src/lib/kg-data.json
 *
 * Run manually when YAML files change:
 *   node scripts/build-kg-json.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as yaml from 'js-yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const KG_DIR = path.join(ROOT, 'content', 'knowledge-graph');
const OUT_FILE = path.join(ROOT, 'apps', 'web', 'src', 'lib', 'kg-data.json');

const concepts = [];
for (const file of fs.readdirSync(KG_DIR).filter((f) => f.endsWith('.yaml'))) {
  const data = yaml.load(fs.readFileSync(path.join(KG_DIR, file), 'utf-8'));
  const subject = data.subject ?? file.replace('.yaml', '');
  const level = data.level ?? 'general';
  for (const c of data.concepts ?? []) {
    concepts.push({
      id: c.id,
      name: c.name,
      name_he: c.name_he ?? null,
      subject,
      level,
      prerequisites: c.prerequisites ?? [],
    });
  }
}

const byId = Object.fromEntries(concepts.map((c) => [c.id, c]));
const prereqMap = Object.fromEntries(concepts.map((c) => [c.id, c.prerequisites]));

fs.writeFileSync(
  OUT_FILE,
  JSON.stringify({ concepts, prereqMap, byId }, null, 2),
);

console.log(`Wrote ${concepts.length} concepts to ${path.relative(ROOT, OUT_FILE)}`);
