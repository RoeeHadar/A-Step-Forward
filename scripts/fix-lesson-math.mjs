#!/usr/bin/env node
/**
 * Fix KaTeX-breaking patterns in lesson JSON (conservative passes).
 * Run: node scripts/fix-lesson-math.mjs
 */
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIR = join(ROOT, 'scripts/seed_data/lessons');

const MD_KEYS = new Set([
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
  'title_en',
  'title_he',
  'summary_en',
  'summary_he',
  'rubric_en',
  'rubric_he',
]);

function fixPmatrixRowBreaks(text) {
  return text.replace(/\\begin\{(pmatrix|bmatrix|vmatrix|matrix)\}([\s\S]*?)\\end\{\1\}/g, (full, env, body) => {
    const fixed = body.replace(/([0-9a-z+\-\)\}])\\([a-z0-9])/gi, (match, before, after, offset, str) => {
      const tail = str.slice(offset + match.length - after.length);
      const cmd = ['geq', 'leq', 'neq', 'cdot', 'cos', 'sin', 'tan', 'log', 'ln', 'exp', 'end', 'begin', 'text', 'frac', 'sqrt', 'sum', 'int', 'lim', 'det', 'left', 'right', 'pm', 'mp', 'to', 'in', 'not'].find((c) => tail.startsWith(c));
      if (cmd) return match;
      if (match.startsWith('\\\\')) return match;
      return `${before}\\\\${after}`;
    });
    return `\\begin{${env}}${fixed}\\end{${env}}`;
  });
}

function fixCasesRowBreaks(text) {
  return text.replace(/x<1\\x/g, 'x<1\\\\ x');
}

function fixString(text) {
  if (!text || typeof text !== 'string') return text;
  let out = text;

  // \$ inside $...$ breaks remark-math delimiters
  out = out.replace(/\\\$/g, '');

  out = fixCasesRowBreaks(out);
  out = fixPmatrixRowBreaks(out);

  out = out.replace(/\\\[([\s\S]*?)\\\]/g, '$$$$1$$');
  out = out.replace(/\$e\^x'\s*=\s*e\^x\$/g, '$(e^x)\' = e^x$');
  out = out.replace(/\\ln\(\s*\\text\{non-positive\}\}\}/g, '\\ln(\\text{non-positive})');
  out = out.replace(/\\ln\(\s*\\text\{לא-חיובי\}\}\}/g, '\\ln(\\text{לא-חיובי})');
  out = out.replace(/A_\\max\b/g, 'A_{\\max}');
  out = out.replace(
    /\$a=R\\alpha\\Rightarrow f=\\tfrac\{1\}\{2\}ma\. \\quad \(3\)\$\$/g,
    '$$a=R\\\\alpha\\\\Rightarrow f=\\\\tfrac{1}{2}ma. \\\\quad (3)$$',
  );
  out = out.replace(/\\arcsinh\b/g, '\\operatorname{arcsinh}');
  out = out.replace(
    /x = C_\{\\text\{rung in series with \(C_\{rail\} in parallel with x\)\}\}/g,
    'C_{\\text{eq}}',
  );
  out = out.replace(/\\boxed\{(\d+)\\text\{\s*ס"מ\}(?!\})/g, '\\boxed{$1\\,\\text{cm}}');
  out = out.replace(/\\boxed\{(\d+)\\text\{\s*ס"מ\}\}/g, '\\boxed{$1\\,\\text{cm}}');
  out = out.replace(/\\(Rightarrow|Leftarrow|Leftrightarrow)([a-zA-Z])/g, '\\$1 $2');

  return out;
}

function walk(obj) {
  if (typeof obj === 'string') return fixString(obj);
  if (Array.isArray(obj)) return obj.map((item) => walk(item));
  if (!obj || typeof obj !== 'object') return obj;
  const out = {};
  for (const [key, value] of Object.entries(obj)) {
    if (
      typeof value === 'string' &&
      (MD_KEYS.has(key) ||
        key.endsWith('_md') ||
        key.endsWith('_he') ||
        key.endsWith('_en') ||
        key.includes('solution'))
    ) {
      out[key] = fixString(value);
    } else if (Array.isArray(value) && (key === 'options_en' || key === 'options_he')) {
      out[key] = value.map((v) => (typeof v === 'string' ? fixString(v) : walk(v)));
    } else {
      out[key] = walk(value);
    }
  }
  return out;
}

let filesChanged = 0;
for (const file of readdirSync(DIR).filter((f) => f.endsWith('.json')).sort()) {
  const path = join(DIR, file);
  const before = JSON.parse(readFileSync(path, 'utf8'));
  const after = walk(structuredClone(before));
  if (JSON.stringify(before) !== JSON.stringify(after)) {
    writeFileSync(path, JSON.stringify(after, null, 2) + '\n', 'utf8');
    filesChanged += 1;
  }
}

console.log(`fix-lesson-math: updated ${filesChanged} lesson files`);
