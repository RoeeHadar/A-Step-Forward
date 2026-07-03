/**
 * Runtime mirror of apps/web/src/lib/concept-aliases.ts for Node scripts.
 * Parses the TS source so we keep a single source of truth.
 */
import fs from 'node:fs';
import path from 'node:path';

const ALIASES_PATH = path.resolve(
  import.meta.dirname,
  '../../apps/web/src/lib/concept-aliases.ts',
);

function parseAliasesFromTs(src) {
  const block = src.match(/CONCEPT_ID_ALIASES[^=]*=\s*\{([\s\S]*?)\n\};/);
  if (!block) return {};
  const aliases = {};
  for (const line of block[1].split('\n')) {
    const m = line.match(/^\s+(?:'([^']+)'|(\w+)):\s+'([^']+)'\s*,?\s*(?:\/\/.*)?$/);
    if (m) aliases[m[1] ?? m[2]] = m[3];
  }
  return aliases;
}

const ALIASES = parseAliasesFromTs(fs.readFileSync(ALIASES_PATH, 'utf8'));

/** KG / syllabus concept id → authored lesson json id */
export function resolveConceptAlias(conceptId) {
  return ALIASES[conceptId] ?? conceptId;
}

/** Reverse index: lesson id → KG concept ids that alias to it */
export function buildReverseAliasIndex() {
  const reverse = new Map();
  for (const [kgId, lessonId] of Object.entries(ALIASES)) {
    if (!reverse.has(lessonId)) reverse.set(lessonId, []);
    reverse.get(lessonId).push(kgId);
  }
  return reverse;
}

export { ALIASES };
