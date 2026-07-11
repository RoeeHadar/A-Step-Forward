#!/usr/bin/env node
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import katex from 'katex';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIR = join(ROOT, 'scripts/seed_data/lessons');

const LEARNER_KEYS = new Set([
  'body_en_md',
  'body_he_md',
  'checkpoint_solution_en',
  'checkpoint_solution_he',
  'stem_en',
  'stem_he',
  'explanation_en',
  'explanation_he',
  'body_en',
  'body_he',
  'solution_en',
  'solution_he',
]);

function stripDisplay(md) {
  return md.replace(/\$\$[\s\S]*?\$\$/g, ' ');
}

function extractMathSegments(md) {
  const segments = [];
  for (const m of md.matchAll(/\$\$([\s\S]*?)\$\$/g)) {
    segments.push({ expr: m[1], display: true });
  }
  for (const m of stripDisplay(md).matchAll(/\$([^$\n]+)\$/g)) {
    segments.push({ expr: m[1], display: false });
  }
  return segments;
}

function checkText(text, path) {
  if (!text) return [];
  const found = [];
  for (const { expr, display } of extractMathSegments(text)) {
    const trimmed = expr.trim();
    if (!trimmed) continue;
    try {
      katex.renderToString(trimmed, { throwOnError: true, displayMode: display });
    } catch (err) {
      found.push({ path, expr: trimmed.slice(0, 100), err: err.message.slice(0, 120) });
    }
  }
  return found;
}

function walk(obj, base, out) {
  if (typeof obj === 'string') {
    checkText(obj, base).forEach((x) => out.push(x));
    return;
  }
  if (Array.isArray(obj)) {
    if (base.endsWith('options_en') || base.endsWith('options_he')) {
      obj.forEach((v, i) => checkText(v, `${base}[${i}]`).forEach((x) => out.push(x)));
      return;
    }
    obj.forEach((v, i) => walk(v, `${base}[${i}]`, out));
    return;
  }
  if (!obj || typeof obj !== 'object') return;
  for (const [k, v] of Object.entries(obj)) {
    if (LEARNER_KEYS.has(k)) {
      checkText(v, `${base}.${k}`).forEach((x) => out.push(x));
    } else if (k === 'options_en' || k === 'options_he') {
      (v ?? []).forEach((opt, i) =>
        checkText(opt, `${base}.${k}[${i}]`).forEach((x) => out.push(x)),
      );
    } else {
      walk(v, `${base}.${k}`, out);
    }
  }
}

const all = [];
for (const file of readdirSync(DIR).filter((f) => f.endsWith('.json')).sort()) {
  walk(JSON.parse(readFileSync(join(DIR, file), 'utf8')), file, all);
}

const byFile = {};
for (const item of all) {
  const file = item.path.split('.')[0] + '.json';
  (byFile[file] ??= []).push(item);
}

console.log(`Learner-field KaTeX errors: ${all.length} in ${Object.keys(byFile).length} files`);
for (const [file, items] of Object.entries(byFile).sort((a, b) => b[1].length - a[1].length)) {
  console.log(`${items.length}\t${file}`);
}

writeFileSync(
  join(ROOT, 'scripts/.math-audit-errors.json'),
  JSON.stringify(all, null, 2),
  'utf8',
);
