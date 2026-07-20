#!/usr/bin/env node
/**
 * audit-lesson-facets — facet checklist gate for piloted concept families.
 *
 * For each family glob in curriculum-track-contract.facet_pilot_families,
 * every matching lesson must evidence each required facet via:
 *   - question.facets[] tags, and/or
 *   - section/body keyword hits from facet_evidence
 *
 * Usage:
 *   node scripts/audit-lesson-facets.mjs
 *   node scripts/audit-lesson-facets.mjs --strict
 *   node scripts/audit-lesson-facets.mjs --only=functions_quadratic
 *   node scripts/audit-lesson-facets.mjs --json
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const CONTRACT_PATH = path.join(ROOT, 'scripts/seed_data/curriculum-track-contract.json');

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const strict = args.has('strict');
const asJson = args.get('json') === 'true';
const only = args.get('only') && args.get('only') !== 'true'
  ? new Set(args.get('only').split(',').map((s) => s.trim()))
  : null;

function loadContract() {
  return JSON.parse(fs.readFileSync(CONTRACT_PATH, 'utf8'));
}

function loadLessons() {
  return fs
    .readdirSync(LESSONS_DIR)
    .filter((f) => f.endsWith('.json'))
    .map((f) => {
      const lesson = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, f), 'utf8'));
      return { file: f, id: lesson.id || f.replace(/\.json$/, ''), lesson };
    });
}

function globToRegExp(glob) {
  // "functions_*" → /^functions_.*$/ ; also match variant suffixes after base
  const escaped = glob.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*');
  return new RegExp(`^${escaped}$`);
}

function familyMatches(familyGlob, lessonId, conceptId) {
  const re = globToRegExp(familyGlob);
  if (re.test(lessonId) || re.test(conceptId)) return true;
  // variants: functions_quadratic__5pt should match functions_*
  const base = String(lessonId).replace(/__(?:3pt|4pt|5pt|uni|university)$/, '').replace(/_(?:3pt|4pt|5pt|uni|university)$/, '');
  return re.test(base);
}

function flattenText(lesson) {
  const parts = [];
  const push = (v) => {
    if (v == null) return;
    if (typeof v === 'string') parts.push(v);
    else if (typeof v === 'number' || typeof v === 'boolean') parts.push(String(v));
    else if (Array.isArray(v)) v.forEach(push);
    else if (typeof v === 'object') Object.values(v).forEach(push);
  };
  push(lesson);
  return parts.join('\n');
}

function collectFacetTags(lesson) {
  const tags = new Set();
  for (const q of lesson.questions || []) {
    for (const f of q.facets || []) tags.add(String(f));
  }
  for (const f of lesson.facets || []) tags.add(String(f));
  return tags;
}

function evidenceFacet(facetId, evidence, lesson, text, tags) {
  const spec = evidence[facetId] || {};
  const tagHits = (spec.facet_tags || []).some((t) => tags.has(t)) || tags.has(facetId);
  if (tagHits) return { ok: true, via: 'tag' };
  const keywords = spec.section_keywords || [];
  for (const kw of keywords) {
    if (kw && text.toLowerCase().includes(String(kw).toLowerCase())) {
      return { ok: true, via: 'keyword', keyword: kw };
    }
  }
  return { ok: false };
}

function audit(contract, entries) {
  const errors = [];
  const warnings = [];
  const families = contract.facet_pilot_families || Object.keys(contract.facet_checklists || {});
  const checklists = contract.facet_checklists || {};
  const evidence = contract.facet_evidence || {};

  for (const family of families) {
    const required = checklists[family] || [];
    if (!required.length) continue;

    for (const { id, file, lesson } of entries) {
      if (only && !only.has(id) && !only.has(lesson.concept_id)) continue;
      const conceptId = lesson.concept_id || id;
      if (!familyMatches(family, id, conceptId)) continue;
      // Skip non-math / physics noise if any
      if (lesson.subject && lesson.subject !== 'math') continue;

      const text = flattenText(lesson);
      const tags = collectFacetTags(lesson);
      for (const facetId of required) {
        const hit = evidenceFacet(facetId, evidence, lesson, text, tags);
        if (!hit.ok) {
          errors.push({
            code: 'facet_missing',
            id,
            file,
            family,
            facet: facetId,
            note: `Missing facet "${facetId}" (add section keywords or question facets tags)`,
          });
        }
      }
    }
  }

  return { errors, warnings };
}

function main() {
  const contract = loadContract();
  const entries = loadLessons();
  const { errors, warnings } = audit(contract, entries);

  if (asJson) {
    console.log(JSON.stringify({ errors, warnings, errorCount: errors.length }, null, 2));
  } else {
    console.log(`audit-lesson-facets: ${errors.length} error(s), ${warnings.length} warning(s)`);
    for (const e of errors) {
      console.log(`  [E] ${e.id}: missing ${e.facet} (${e.family})`);
    }
  }

  if (strict && errors.length > 0) process.exit(1);
}

main();
