#!/usr/bin/env node
/**
 * Find catalog cards that would show misleading titles or load wrong lesson content.
 */
import fs from 'node:fs';
import { ALIASES, resolveConceptAlias } from './lib/concept-aliases.mjs';

const index = JSON.parse(
  fs.readFileSync('apps/web/src/lib/lessons-index.generated.json', 'utf8'),
);
const kg = JSON.parse(fs.readFileSync('apps/web/src/lib/kg-data.json', 'utf8'));
const indexById = new Map(index.map((e) => [e.id, e]));
const kgById = kg.byId ?? Object.fromEntries(kg.concepts.map((c) => [c.id, c]));

function resolveCanonical(id) {
  let cur = id;
  const seen = new Set();
  while (ALIASES[cur] && !seen.has(cur)) {
    seen.add(cur);
    cur = ALIASES[cur];
  }
  return cur;
}

function isAlias(id) {
  return id in ALIASES;
}

function dedupe(ids) {
  const keyToPick = new Map();
  for (const id of ids) {
    const key = resolveCanonical(id);
    const current = keyToPick.get(key);
    if (!current) {
      keyToPick.set(key, id);
      continue;
    }
    const idIsAlias = isAlias(id);
    const currentIsAlias = isAlias(current);
    if (!idIsAlias && currentIsAlias) keyToPick.set(key, id);
    else if (id === key && current !== key) keyToPick.set(key, id);
  }
  const picked = new Set(keyToPick.values());
  const seen = new Set();
  const out = [];
  for (const id of ids) {
    if (!picked.has(id)) continue;
    const key = resolveCanonical(id);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(id);
  }
  return out;
}

function hasDirectLesson(id) {
  return Boolean(indexById.get(id));
}

function cardTitle(id) {
  const own = indexById.get(id);
  if (own) return own.title_en;
  const kgNode = kgById[id];
  if (kgNode) return kgNode.name;
  const alias = resolveConceptAlias(id);
  const aliased = indexById.get(alias);
  if (aliased) return `[alias→${alias}] ${aliased.title_en}`;
  return id;
}

function lessonTitle(id) {
  const canon = resolveCanonical(id);
  return indexById.get(canon)?.title_en ?? null;
}

// Parse track concept arrays from curriculum-categories.ts
const catSrc = fs.readFileSync('apps/web/src/lib/curriculum-categories.ts', 'utf8');
const trackBlocks = [...catSrc.matchAll(/id: '([^']+)'[\s\S]*?concept_ids: ([\w_]+)/g)];
const arrays = [...catSrc.matchAll(/const ([A-Z_0-9]+) = \[([\s\S]*?)\];/g)];

const issues = [];
const aliasOnlyClickable = [];
const titleMismatch = [];

for (const [, name, body] of arrays) {
  if (!name.endsWith('_CONCEPTS')) continue;
  const ids = [...body.matchAll(/'([^']+)'/g)].map((m) => m[1]);
  const deduped = dedupe(ids);
  for (const id of deduped) {
    const direct = hasDirectLesson(id);
    const canon = resolveCanonical(id);
    const card = cardTitle(id);
    const lesson = lessonTitle(id);

    if (isAlias(id) && direct) {
      aliasOnlyClickable.push({ track: name, id, canon, card, lesson });
    }

    if (!direct && isAlias(id)) {
      // Soon card — title may show target lesson name
      const aliasTargetTitle = indexById.get(canon)?.title_en;
      const kgName = kgById[id]?.name;
      if (aliasTargetTitle && kgName && aliasTargetTitle !== kgName) {
        titleMismatch.push({
          track: name,
          id,
          kind: 'soon-card-shows-lesson-title',
          kgName,
          shownTitle: card,
        });
      }
    }

    if (direct && canon !== id) {
      issues.push({ track: name, id, canon, issue: 'clickable alias id' });
    }
  }
}

// Alias URLs that would load wrong lesson body
const aliasUrlIssues = [];
for (const [from, to] of Object.entries(ALIASES)) {
  if (from === to) continue;
  if (!indexById.get(to)) continue;
  if (indexById.get(from)) continue;
  const fromKg = kgById[from]?.name;
  const toLesson = indexById.get(to)?.title_en;
  if (fromKg && toLesson && !fromKg.toLowerCase().includes(toLesson.split(' ')[0].toLowerCase())) {
    aliasUrlIssues.push({ from, to, fromKg, toLesson });
  }
}

console.log('=== Catalog lesson mismatch audit ===\n');
console.log(`Clickable alias ids (should be 0): ${issues.length}`);
for (const r of issues.slice(0, 15)) console.log(`  ${r.track}: ${r.id} → ${r.canon}`);

console.log(`\nSoon cards with misleading titles: ${titleMismatch.length}`);
for (const r of titleMismatch.slice(0, 20)) {
  console.log(`  ${r.track}: ${r.id} kg="${r.kgName}" shown="${r.shownTitle}"`);
}

console.log(`\nSemantic alias mismatches (sample): ${aliasUrlIssues.length}`);
for (const r of aliasUrlIssues.slice(0, 30)) {
  console.log(`  ${r.from} (${r.fromKg}) → ${r.to} (${r.toLesson})`);
}
