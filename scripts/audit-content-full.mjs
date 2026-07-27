#!/usr/bin/env node
/**
 * One-off broad audit (math + EN/HE language mixup) across ALL learner-facing
 * content, not just scripts/seed_data/lessons (which already has a dedicated
 * CI gate). Walks arbitrary JSON trees, finds every string field whose key
 * ends in _en / _he (or _en_md / _he_md), and:
 *   1. Runs the canonical findMathErrors() on it (same rules as CI).
 *   2. Flags Hebrew characters appearing in an *_en field (outside math).
 *   3. Flags a run of Latin-alphabet prose (2+ words) appearing in an *_he
 *      field (outside math) — i.e. leaked English.
 *   4. Flags likely mojibake (Latin-1-supplement / replacement-char soup
 *      where Hebrew should be).
 *
 * This is a throwaway audit script (not wired into CI); output feeds a
 * manual fix pass. Usage: node scripts/audit-content-full.mjs > report.json
 */
import fs from 'node:fs';
import path from 'node:path';
import { findMathErrors, maskMathSpans, stripCodeSpans } from './lib/katex-check.mjs';

const HEBREW_RE = /[\u0590-\u05FF]/;
const MOJIBAKE_RE = /[\uFFFD\u0080-\u009F]|[ÀÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ]{2,}/;
// English prose leak inside a Hebrew field: 3+ consecutive Latin words (a real
// phrase/sentence fragment, not just an isolated loanword/acronym like
// "post-hoc" or "chi-square" that Israeli academic Hebrew commonly borrows).
const ENGLISH_PROSE_RE = /\b[A-Za-z]{3,}\b(?:[\s,.'-]+\b[A-Za-z]{2,}\b){2,}/;
// Allow-list of short Latin tokens / loanwords that legitimately appear in
// Hebrew technical text (brand/acronyms/units/stats jargon/intentional
// MoE-scope-scrub replacement phrases — see scripts/moe-5pt-scope-remediation.mjs
// and scripts/scrub-track-scope-voice.mjs, which deliberately rename named
// theorems to generic English phrases even inside Hebrew lesson bodies).
const ALLOWED_LATIN_TOKENS = new Set([
  'AI', 'PDF', 'GPS', 'URL', 'CEO', 'USA', 'UK', 'GB', 'MB', 'KB', 'kg', 'km', 'cm', 'mm',
  'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'min', 'max', 'GPA', 'IQ', 'DNA', 'RNA', 'pH',
  'post', 'hoc', 'chi', 'square', 'MoE', 'SSB', 'SSW', 'MSB', 'MSW', 'ANOVA', 'Calc',
]);
const ALLOWED_PHRASES = [
  'continuity craft', 'endpoint comparison', 'average-rate idea', 'limit-closeness',
  'A Step Forward', 'Step Forward',
];

function collectStringFields(obj, pathPrefix, out) {
  if (obj == null) return;
  if (typeof obj === 'string') {
    out.push([pathPrefix, obj]);
    return;
  }
  if (Array.isArray(obj)) {
    obj.forEach((v, i) => collectStringFields(v, `${pathPrefix}[${i}]`, out));
    return;
  }
  if (typeof obj === 'object') {
    for (const [k, v] of Object.entries(obj)) {
      collectStringFields(v, pathPrefix ? `${pathPrefix}.${k}` : k, out);
    }
  }
}

// Only fields actually rendered as markdown/prose to the learner (via
// MarkdownMath / react-markdown) are worth checking for math-notation and
// language-mixup bugs. Grading-only fields (acceptable_answers, regex,
// correct_answer, unit_en/he, accept_en/he, ids, metadata, …) are displayed
// verbatim in a <code> tag or never displayed at all — LaTeX-looking text or
// short Latin tokens there are not bugs.
const RENDERED_BASE_NAMES = new Set([
  'stem', 'explanation', 'options', 'rubric', 'steps', 'left', 'right',
  'body', 'solution', 'checkpoint_solution', 'title', 'summary',
  'instructions', 'sample_solution', 'expected_steps', 'prompt', 'question',
  'detect_phrase', 'correction', 'hint', 'feedback', 'answer', 'stimulus',
  'context', 'scenario', 'intro', 'description', 'label', 'note', 'tip',
  'misconception', 'why_matters', 'pitfall',
]);

function baseFieldName(lastSeg) {
  return lastSeg.replace(/(_en|_he)(_md)?$/, '');
}

function isRenderedField(lastSeg) {
  return RENDERED_BASE_NAMES.has(baseFieldName(lastSeg));
}

function isEnField(lastSeg) {
  return (/(^|[_.])en(_md)?$/.test(lastSeg) || /_en$/.test(lastSeg)) && isRenderedField(lastSeg);
}
function isHeField(lastSeg) {
  return (/(^|[_.])he(_md)?$/.test(lastSeg) || /_he$/.test(lastSeg)) && isRenderedField(lastSeg);
}
// Math notation only matters where it's actually rendered as markdown, OR in
// answer_payload.acceptable_answers-adjacent fields that ARE rendered
// (options/steps/rubric/left/right) — but NOT the plain-text grading arrays.
const MATH_SKIP_BASENAMES = new Set([
  'acceptable_answers', 'correct_answer', 'accept', 'regex', 'unit',
]);
function isMathCheckedField(lastSeg) {
  const base = baseFieldName(lastSeg);
  if (MATH_SKIP_BASENAMES.has(base)) return false;
  return isRenderedField(lastSeg);
}

function checkEnglishProseLeak(text) {
  let prose = maskMathSpans(stripCodeSpans(text));
  for (const p of ALLOWED_PHRASES) prose = prose.split(p).join(' '.repeat(p.length));
  const m = prose.match(ENGLISH_PROSE_RE);
  if (!m) return null;
  const tokens = m[0].split(/[\s,.'-]+/).filter(Boolean);
  const meaningful = tokens.filter((t) => t.length >= 3 && !ALLOWED_LATIN_TOKENS.has(t));
  if (meaningful.length < 3) return null;
  return m[0].slice(0, 80);
}

function checkHebrewLeak(text) {
  const prose = maskMathSpans(stripCodeSpans(text));
  if (HEBREW_RE.test(prose)) {
    const idx = prose.search(HEBREW_RE);
    return prose.slice(Math.max(0, idx - 20), idx + 30);
  }
  return null;
}

function checkMojibake(text) {
  const hits = text.match(MOJIBAKE_RE);
  if (!hits) return null;
  const idx = text.search(MOJIBAKE_RE);
  return text.slice(Math.max(0, idx - 20), idx + 30);
}

function auditFile(filePath, label) {
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    return [{ file: label, path: '(parse)', type: 'json-parse-error', detail: String(e.message || e) }];
  }
  const fields = [];
  collectStringFields(raw, '', fields);
  const issues = [];
  for (const [key, text] of fields) {
    if (typeof text !== 'string' || !text.trim()) continue;
    const lastSegRaw = key.split('.').pop() || key;
    const lastSeg = lastSegRaw.replace(/\[\d+\]$/, '');

    if (isMathCheckedField(lastSeg)) {
      for (const err of findMathErrors(text, key)) {
        issues.push({ file: label, path: key, type: 'math', detail: err });
      }
    }

    if (isEnField(lastSeg)) {
      const heLeak = checkHebrewLeak(text);
      if (heLeak) issues.push({ file: label, path: key, type: 'hebrew-in-en', detail: heLeak });
    }
    if (isHeField(lastSeg)) {
      const enLeak = checkEnglishProseLeak(text);
      if (enLeak) issues.push({ file: label, path: key, type: 'english-in-he', detail: enLeak });
      const moji = checkMojibake(text);
      if (moji) issues.push({ file: label, path: key, type: 'mojibake', detail: moji });
    }
  }
  return issues;
}

function walkDir(dir, exts = ['.json']) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkDir(full, exts));
    else if (exts.some((e) => entry.name.endsWith(e))) out.push(full);
  }
  return out;
}

const targets = [
  ...walkDir('scripts/seed_data/lessons').map((f) => [f, path.relative(process.cwd(), f)]),
  ...walkDir('content/question-store/generated').map((f) => [f, path.relative(process.cwd(), f)]),
  ['content/question-store/items.json', 'content/question-store/items.json'],
  ...walkDir('apps/web/src/lib/mock-exams').map((f) => [f, path.relative(process.cwd(), f)]),
  ['apps/web/src/lib/exam-style-corpus.generated.json', 'apps/web/src/lib/exam-style-corpus.generated.json'],
].filter(([f]) => fs.existsSync(f));

const allIssues = [];
for (const [file, label] of targets) {
  allIssues.push(...auditFile(file, label));
}

const byType = {};
for (const issue of allIssues) {
  byType[issue.type] = (byType[issue.type] || 0) + 1;
}

const report = { totalFiles: targets.length, totalIssues: allIssues.length, byType, issues: allIssues };
const outPath = process.argv[2] || 'audit-report.json';
fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf8');
console.log(`Wrote ${outPath}: ${allIssues.length} issues across ${targets.length} files`);
console.log(JSON.stringify(byType, null, 2));
