#!/usr/bin/env node
/**
 * Audit learner-facing lesson fields for math/LaTeX issues.
 * Run: node scripts/audit-lesson-math.mjs
 */
import { readdirSync, readFileSync } from 'node:fs';
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
  'title_en',
  'title_he',
  'summary_en',
  'summary_he',
]);

function stripDisplayMath(md) {
  return md.replace(/\$\$[\s\S]*?\$\$/g, ' ');
}

function extractMathSegments(md) {
  const segments = [];
  const display = md.matchAll(/\$\$([\s\S]*?)\$\$/g);
  for (const m of display) segments.push({ expr: m[1], display: true });
  const inline = stripDisplayMath(md).matchAll(/\$([^$\n]+)\$/g);
  for (const m of inline) segments.push({ expr: m[1], display: false });
  return segments;
}

function checkText(text, path) {
  if (!text || typeof text !== 'string') return [];
  const found = [];

  if (/\\\\[a-zA-Z]{2,}/.test(text)) {
    found.push({ path, kind: 'double-escaped-latex', detail: text.match(/\\\\[a-zA-Z]{2,}/)?.[0] });
  }
  if (/\\\(|\\\[/.test(text)) {
    found.push({ path, kind: 'wrong-delimiter', detail: text.match(/\\[\(\[]/)?.[0] });
  }

  const naked = text.replace(/\$\$[\s\S]*?\$\$/g, '').replace(/\$[^$\n]+\$/g, '');
  if (/\\(?:frac|sqrt|lim|sum|int|text|mathrm|left|right|dfrac|tfrac)\b/.test(naked)) {
    found.push({
      path,
      kind: 'latex-outside-delimiters',
      detail: naked.match(/.{0,25}\\(?:frac|sqrt|lim|sum|int|text).{0,25}/)?.[0],
    });
  }

  for (const { expr, display } of extractMathSegments(text)) {
    const trimmed = expr.trim();
    if (!trimmed) {
      found.push({ path, kind: 'empty-math', detail: display ? '$$' : '$' });
      continue;
    }
    try {
      katex.renderToString(trimmed, {
        throwOnError: true,
        displayMode: display,
        strict: 'warn',
      });
    } catch (err) {
      found.push({
        path,
        kind: 'katex-error',
        detail: `${trimmed.slice(0, 60)} → ${err.message}`,
      });
    }
  }

  return found;
}

function walk(obj, base, out) {
  if (typeof obj === 'string') {
    out.push(...checkText(obj, base));
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
  const lesson = JSON.parse(readFileSync(join(DIR, file), 'utf8'));
  walk(lesson, file, all);
}

const byKind = {};
for (const i of all) byKind[i.kind] = (byKind[i.kind] ?? 0) + 1;

console.log(`Math audit — ${DIR}`);
console.log('='.repeat(72));
console.log(`Total issues: ${all.length}`);
console.log('By kind:', byKind);

const priority = ['katex-error', 'double-escaped-latex', 'latex-outside-delimiters', 'wrong-delimiter', 'empty-math'];
for (const kind of priority) {
  const items = all.filter((i) => i.kind === kind);
  if (!items.length) continue;
  console.log(`\n## ${kind} (${items.length})`);
  for (const i of items.slice(0, 40)) {
    console.log(`  ${i.path}`);
    console.log(`    ${i.detail}`);
  }
  if (items.length > 40) console.log(`  … (+${items.length - 40} more)`);
}

process.exit(all.some((i) => ['katex-error', 'double-escaped-latex', 'latex-outside-delimiters'].includes(i.kind)) ? 1 : 0);
