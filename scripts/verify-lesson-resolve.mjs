#!/usr/bin/env node
/**
 * Verify every authored lesson resolves to itself (no alias shadowing).
 */
import fs from 'node:fs';
import { ALIASES } from './lib/concept-aliases.mjs';

const index = JSON.parse(
  fs.readFileSync('apps/web/src/lib/lessons-index.generated.json', 'utf8'),
);

function resolveLessonConceptId(conceptId) {
  if (index.some((e) => e.id === conceptId)) return conceptId;
  return ALIASES[conceptId] ?? conceptId;
}

const errors = [];
for (const entry of index) {
  const resolved = resolveLessonConceptId(entry.id);
  if (resolved !== entry.id) {
    errors.push({
      id: entry.id,
      resolved,
      title: entry.title_en,
      issue: 'dedicated lesson shadowed by alias',
    });
  }
}

// Alias-only slugs that redirect to a different-titled lesson are OK if not clickable.
// Flag alias keys whose target lesson title diverges AND would be clickable (has own index).
for (const [from, to] of Object.entries(ALIASES)) {
  if (from === to) continue;
  const fromEntry = index.find((e) => e.id === from);
  const toEntry = index.find((e) => e.id === to);
  if (fromEntry && toEntry && from !== to) {
    errors.push({
      id: from,
      resolved: to,
      title: fromEntry.title_en,
      issue: 'both have lessons but alias still maps away',
    });
  }
}

console.log('=== Lesson resolve verification ===');
console.log(`Index entries: ${index.length}`);
console.log(`Errors: ${errors.length}`);
for (const e of errors) {
  console.log(`  ${e.id} → ${e.resolved} (${e.issue})`);
}
process.exit(errors.length ? 1 : 0);
