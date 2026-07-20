#!/usr/bin/env node
/**
 * Build wave-3 exam-topic-matrix sections for 3pt, hs_physics, makhina, university
 * from curriculum-categories.ts concept lists. Marks topics ok|missing by lesson existence.
 *
 * Usage: node scripts/build-wave3-exam-matrix.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(ROOT, 'apps/web/src/lib/curriculum-categories.ts');
const ALIASES_SRC = path.join(ROOT, 'apps/web/src/lib/concept-aliases.ts');
const LESSONS = path.join(ROOT, 'scripts/seed_data/lessons');
const MATRIX = path.join(ROOT, 'scripts/seed_data/exam-topic-matrix.json');

const src = fs.readFileSync(SRC, 'utf8');
const aliases = {};
for (const m of fs.readFileSync(ALIASES_SRC, 'utf8').matchAll(/^\s*([a-z0-9_]+):\s*'([a-z0-9_]+)'/gm)) {
  aliases[m[1]] = m[2];
}

function lessonExists(id) {
  if (fs.existsSync(path.join(LESSONS, `${id}.json`))) return id;
  if (aliases[id] && fs.existsSync(path.join(LESSONS, `${aliases[id]}.json`))) return aliases[id];
  for (const suf of ['__4pt', '__5pt', '_4pt', '_5pt', '__3pt', '_3pt', '__uni', '_uni']) {
    if (fs.existsSync(path.join(LESSONS, `${id}${suf}.json`))) return `${id}${suf}`;
  }
  return null;
}

/** Extract sections for a category id from the TS source. */
function extractCategory(catId) {
  const marker = `id: '${catId}'`;
  const start = src.indexOf(marker);
  if (start < 0) return null;
  const after = src.slice(start);
  const secStart = after.indexOf('sections: [');
  if (secStart < 0) return null;
  // Find matching closing of sections array — naive brace count from sections: [
  let i = secStart + 'sections: ['.length;
  let depth = 1;
  let inStr = false;
  let strCh = '';
  for (; i < after.length && depth > 0; i++) {
    const ch = after[i];
    if (inStr) {
      if (ch === '\\') {
        i++;
        continue;
      }
      if (ch === strCh) inStr = false;
      continue;
    }
    if (ch === "'" || ch === '"' || ch === '`') {
      inStr = true;
      strCh = ch;
      continue;
    }
    if (ch === '[') depth++;
    else if (ch === ']') depth--;
  }
  const sectionsBlock = after.slice(secStart, i);
  const sections = [];
  const secRe = /id:\s*'([^']+)'[\s\S]*?concept_ids:\s*\[([^\]]*)\]/g;
  let sm;
  while ((sm = secRe.exec(sectionsBlock))) {
    const ids = [...sm[2].matchAll(/'([a-z][a-z0-9_]*)'/g)].map((x) => x[1]);
    if (ids.length) sections.push({ id: sm[1], concept_ids: [...new Set(ids)] });
  }
  return sections;
}

function topicsFromSection(section, maxTopics = 12) {
  // Prefer a representative sample: first N unique concepts that aren't pure aliases to same lesson
  const topics = [];
  const seenLessons = new Set();
  for (const cid of section.concept_ids) {
    if (topics.length >= maxTopics) break;
    const hit = lessonExists(cid);
    if (hit && seenLessons.has(hit)) continue;
    if (hit) seenLessons.add(hit);
    topics.push({
      id: cid,
      catalog_ids: [cid],
      facets: [],
      status: hit ? 'ok' : 'missing',
      lesson: hit || undefined,
    });
  }
  return topics;
}

const TRACK_MAP = [
  { track: '3pt', categoryId: 'high_school_math_3pt', maxPerSection: 8 },
  { track: 'hs_physics', categoryId: 'hs_physics', maxPerSection: 8 },
  { track: 'makhina', categoryId: 'makhina', maxPerSection: 8 },
  { track: 'university', categoryId: 'calculus_1', maxPerSection: 10, also: ['linear_algebra', 'university_physics_1'] },
];

const matrix = JSON.parse(fs.readFileSync(MATRIX, 'utf8'));

for (const spec of TRACK_MAP) {
  const catIds = [spec.categoryId, ...(spec.also || [])];
  const sections = [];
  for (const catId of catIds) {
    const extracted = extractCategory(catId);
    if (!extracted) {
      console.warn('category not found:', catId);
      continue;
    }
    for (const sec of extracted) {
      sections.push({
        id: `${catId}__${sec.id}`,
        label_en: `${catId} / ${sec.id}`,
        topics: topicsFromSection(sec, spec.maxPerSection),
      });
    }
  }
  matrix.tracks[spec.track] = {
    sections,
    notes: `Wave 3 auto-built from curriculum-categories (${catIds.join(', ')})`,
  };
  const missing = sections.flatMap((s) => s.topics.filter((t) => t.status === 'missing'));
  const ok = sections.flatMap((s) => s.topics.filter((t) => t.status === 'ok'));
  console.log(
    `${spec.track}: ${sections.length} sections, ${ok.length} ok, ${missing.length} missing`,
    missing.length ? `e.g. ${missing.slice(0, 5).map((t) => t.id).join(', ')}` : '',
  );
}

// Enforce wave-3 tracks for coverage CI (non-strict still writes queue; strict gates 4pt+5pt+wave3)
matrix.enforced_tracks = ['4pt', '5pt', '3pt', 'hs_physics', 'makhina', 'university'];

fs.writeFileSync(MATRIX, `${JSON.stringify(matrix, null, 2)}\n`);
console.log('wrote', MATRIX);
