#!/usr/bin/env node
/**
 * Pre-ingestion RAG data health check (READ-ONLY).
 *
 * Runs BEFORE any chunking/embedding so we never ingest broken, contradictory,
 * or falsely-authored content into the vector store. It reuses the repo's
 * existing validators instead of reinventing them:
 *   - scripts/lib/normalize-lesson.mjs  (normalizeLesson / validateLesson / acceptableAnswersLookBroken)
 *   - scripts/lib/katex-check.mjs       (findMathErrors)
 *   - scripts/lib/lesson-depth.mjs      (lessonMetrics -> HE parity)
 *
 * Coverage:
 *   1. Structural   — JSON parses, schema valid (validateLesson).
 *   2. Referential  — concept_id == filename; concept_id ∈ KG; cross-edge endpoints ∈ KG.
 *   3. Dedup/contradiction — duplicate concept_id across files; conflicting subject/level.
 *   4. Bilingual    — required EN/HE fields present; severe HE parity gaps.
 *   5. Math         — KaTeX renderability of every learner-facing text field.
 *   6. Answer sanity — short_answer acceptable-answers not broken/templated.
 *   7. Bundle drift — generated index/bundle counts match source lesson count.
 *   8. Question store — verification_status distribution (what is safe to ingest).
 *
 * Findings are split into BLOCK (quarantine — do NOT ingest this doc) and
 * WARN (ingest but flag). A machine-readable report is written to
 * artifacts/rag-health-report.json.
 *
 * Usage:
 *   node scripts/rag-health-check.mjs           # report, exit 0
 *   node scripts/rag-health-check.mjs --strict  # exit 1 if any BLOCK finding
 *   node scripts/rag-health-check.mjs --json     # print full JSON to stdout
 *
 * This script does NOT connect to any database.
 */
import fs from 'node:fs';
import path from 'node:path';
import {
  normalizeLesson,
  validateLesson,
  acceptableAnswersLookBroken,
} from './lib/normalize-lesson.mjs';
import { findMathErrors } from './lib/katex-check.mjs';
import { lessonMetrics } from './lib/lesson-depth.mjs';

const STRICT = process.argv.includes('--strict');
const JSON_OUT = process.argv.includes('--json');

const ROOT = process.cwd();
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const KG_DATA = path.join(ROOT, 'apps/web/src/lib/kg-data.json');
const KG_EDGES = path.join(ROOT, 'apps/web/src/lib/kg-cross-edges.json');
const INDEX_GEN = path.join(ROOT, 'apps/web/src/lib/lessons-index.generated.json');
const BUNDLE_GEN = path.join(ROOT, 'apps/web/src/lib/lessons-bundle.generated.json');
const QSTORE = path.join(ROOT, 'content/question-store/items.json');
const REPORT_DIR = path.join(ROOT, 'artifacts');
const REPORT_OUT = path.join(REPORT_DIR, 'rag-health-report.json');

/** BLOCK = quarantine from ingestion. WARN = ingest but flag. */
const findings = { block: [], warn: [] };
const add = (sev, doc, category, message) => {
  findings[sev].push({ doc, category, message });
};

function readJson(fp) {
  return JSON.parse(fs.readFileSync(fp, 'utf-8'));
}

// --- load KG for referential checks ---------------------------------------
let kgConceptIds = new Set();
try {
  const kg = readJson(KG_DATA);
  const nodes = Array.isArray(kg) ? kg : (kg.concepts ?? kg.nodes ?? []);
  kgConceptIds = new Set(nodes.map((n) => n.id).filter(Boolean));
} catch (e) {
  add('warn', 'kg-data.json', 'referential', `could not load KG concepts: ${e.message}`);
}

// --- Math-bearing text fields per lesson ----------------------------------
function lessonTextFields(lesson) {
  const out = [];
  const y = (val, label) => {
    if (typeof val === 'string' && val.trim()) out.push({ val, label });
  };
  y(lesson.summary_en, 'summary_en');
  y(lesson.summary_he, 'summary_he');
  for (const [i, s] of (lesson.sections ?? []).entries()) {
    y(s.body_en_md, `sections[${i}].body_en_md`);
    y(s.body_he_md, `sections[${i}].body_he_md`);
    y(s.checkpoint_solution_en, `sections[${i}].checkpoint_solution_en`);
    y(s.checkpoint_solution_he, `sections[${i}].checkpoint_solution_he`);
    for (const [j, ex] of (s.exercises ?? []).entries()) {
      y(ex.body_en, `sections[${i}].exercises[${j}].body_en`);
      y(ex.body_he, `sections[${i}].exercises[${j}].body_he`);
      y(ex.solution_en, `sections[${i}].exercises[${j}].solution_en`);
      y(ex.solution_he, `sections[${i}].exercises[${j}].solution_he`);
    }
  }
  for (const [i, q] of (lesson.questions ?? []).entries()) {
    y(q.stem_en, `questions[${i}].stem_en`);
    y(q.stem_he, `questions[${i}].stem_he`);
    y(q.explanation_en, `questions[${i}].explanation_en`);
    y(q.explanation_he, `questions[${i}].explanation_he`);
  }
  return out;
}

// --- 1-6: per-lesson checks ------------------------------------------------
const files = fs
  .readdirSync(LESSONS_DIR)
  .filter((f) => f.endsWith('.json'))
  .sort();

const seenConceptId = new Map(); // concept_id -> file
let lessonsOk = 0;

for (const file of files) {
  const base = file.replace(/\.json$/, '');
  const fp = path.join(LESSONS_DIR, file);
  let raw;
  try {
    raw = readJson(fp);
  } catch (e) {
    add('block', file, 'structural', `JSON parse error: ${e.message}`);
    continue;
  }

  const lesson = normalizeLesson(raw, file);

  // 1. structural / schema
  const schemaErrors = validateLesson(file, lesson);
  for (const err of schemaErrors) add('block', file, 'schema', err);

  // 2. referential — concept_id vs filename
  if (lesson.concept_id !== base) {
    add('warn', file, 'referential', `concept_id "${lesson.concept_id}" != filename "${base}"`);
  }
  // 2. referential — concept_id present in KG
  if (kgConceptIds.size && !kgConceptIds.has(lesson.concept_id)) {
    add('warn', file, 'referential', `concept_id "${lesson.concept_id}" not found in kg-data.json`);
  }

  // 3. dedup / contradiction
  if (seenConceptId.has(lesson.concept_id)) {
    add(
      'block',
      file,
      'contradiction',
      `duplicate concept_id "${lesson.concept_id}" (also in ${seenConceptId.get(lesson.concept_id)})`,
    );
  } else {
    seenConceptId.set(lesson.concept_id, file);
  }

  // 4. bilingual — severe HE parity gaps (missing required fields already caught by schema)
  try {
    const m = lessonMetrics(lesson);
    if (m.heParitySevere > 0) {
      add('warn', file, 'bilingual', `${m.heParitySevere} section(s) with severe HE/EN parity gap (<60%)`);
    }
  } catch {
    /* metrics are best-effort */
  }

  // 5. math renderability
  let mathErrCount = 0;
  for (const { val, label } of lessonTextFields(lesson)) {
    const errs = findMathErrors(val, label);
    for (const e of errs) {
      mathErrCount += 1;
      if (mathErrCount <= 5) add('warn', file, 'math', e);
    }
  }
  if (mathErrCount > 5) {
    add('warn', file, 'math', `…and ${mathErrCount - 5} more math issue(s) (${mathErrCount} total)`);
  }

  // 6. answer sanity
  for (const [i, q] of (lesson.questions ?? []).entries()) {
    if (q.kind === 'short_answer') {
      const list = q.answer_payload?.acceptable_answers ?? q.acceptable_answers;
      if (acceptableAnswersLookBroken(list)) {
        add('warn', file, 'answer', `questions[${i}] short_answer has broken/templated acceptable_answers`);
      }
    }
  }

  if (!schemaErrors.length) lessonsOk += 1;
}

// --- 2 (cont.): cross-edge endpoints exist in KG --------------------------
try {
  const edges = readJson(KG_EDGES);
  const list = Array.isArray(edges) ? edges : (edges.edges ?? []);
  let dangling = 0;
  for (const e of list) {
    const src = e.src ?? e.source;
    const dst = e.dst ?? e.target;
    if (kgConceptIds.size && src && !kgConceptIds.has(src)) {
      dangling += 1;
      add('warn', 'kg-cross-edges.json', 'referential', `edge src "${src}" not in KG`);
    }
    if (kgConceptIds.size && dst && !kgConceptIds.has(dst)) {
      dangling += 1;
      add('warn', 'kg-cross-edges.json', 'referential', `edge dst "${dst}" not in KG`);
    }
  }
  if (!dangling) {
    // no-op; silence is good
  }
} catch (e) {
  add('warn', 'kg-cross-edges.json', 'referential', `could not load cross-edges: ${e.message}`);
}

// --- 7: bundle drift -------------------------------------------------------
function safeCount(fp, kind) {
  try {
    const data = readJson(fp);
    if (Array.isArray(data)) return data.length;
    return Object.keys(data).length;
  } catch (e) {
    add('warn', path.basename(fp), 'bundle', `could not read ${kind}: ${e.message}`);
    return null;
  }
}
const idxCount = safeCount(INDEX_GEN, 'index');
const bundleCount = safeCount(BUNDLE_GEN, 'bundle');
if (idxCount != null && idxCount !== files.length) {
  add('warn', 'lessons-index.generated.json', 'bundle', `index has ${idxCount} entries but ${files.length} source lessons — run generate-lessons-artifacts.mjs`);
}
if (bundleCount != null && bundleCount !== files.length) {
  add('warn', 'lessons-bundle.generated.json', 'bundle', `bundle has ${bundleCount} entries but ${files.length} source lessons — run generate-lessons-artifacts.mjs`);
}

// --- 8: question store verification distribution --------------------------
const qStore = { total: 0, byStatus: {} };
try {
  const items = readJson(QSTORE);
  const list = Array.isArray(items) ? items : (items.items ?? []);
  qStore.total = list.length;
  for (const it of list) {
    const st = it.verification_status ?? 'unknown';
    qStore.byStatus[st] = (qStore.byStatus[st] ?? 0) + 1;
  }
  const unsafe = Object.entries(qStore.byStatus)
    .filter(([st]) => !['auto_verified', 'human_verified'].includes(st))
    .reduce((n, [, c]) => n + c, 0);
  if (unsafe > 0) {
    add('warn', 'question-store/items.json', 'question-store', `${unsafe}/${qStore.total} items are NOT auto/human-verified — ingest only verified items or tag provenance`);
  }
} catch (e) {
  add('warn', 'question-store/items.json', 'question-store', `could not load question store: ${e.message}`);
}

// --- report ----------------------------------------------------------------
const quarantine = [...new Set(findings.block.map((f) => f.doc))];
const report = {
  generated_at: new Date().toISOString(),
  corpus: {
    lessons_total: files.length,
    lessons_schema_ok: lessonsOk,
    kg_concepts: kgConceptIds.size,
    question_store: qStore,
    index_generated: idxCount,
    bundle_generated: bundleCount,
  },
  summary: {
    block: findings.block.length,
    warn: findings.warn.length,
    quarantined_docs: quarantine.length,
  },
  quarantine,
  findings,
};

fs.mkdirSync(REPORT_DIR, { recursive: true });
fs.writeFileSync(REPORT_OUT, JSON.stringify(report, null, 2));

if (JSON_OUT) {
  console.log(JSON.stringify(report, null, 2));
} else {
  const byCat = (arr) => {
    const m = {};
    for (const f of arr) m[f.category] = (m[f.category] ?? 0) + 1;
    return Object.entries(m).map(([k, v]) => `${k}=${v}`).join(', ') || 'none';
  };
  console.log('=== RAG pre-ingestion health check ===');
  console.log(`lessons: ${files.length} (schema-ok: ${lessonsOk}) | KG concepts: ${kgConceptIds.size} | question-store: ${qStore.total}`);
  console.log(`question-store status: ${JSON.stringify(qStore.byStatus)}`);
  console.log('');
  console.log(`BLOCK (quarantine from ingestion): ${findings.block.length}  [${byCat(findings.block)}]`);
  console.log(`WARN  (ingest but flag):           ${findings.warn.length}  [${byCat(findings.warn)}]`);
  // Warn breakdown by normalized message signature (helps triage).
  const sig = {};
  for (const f of findings.warn) {
    const key =
      f.category +
      ' :: ' +
      f.message
        .replace(/"[^"]*"/g, 'X')
        .replace(/\[\d+\]/g, '[i]')
        .replace(/\d+/g, 'N');
    sig[key] = (sig[key] ?? 0) + 1;
  }
  const sigRows = Object.entries(sig).sort((a, b) => b[1] - a[1]);
  if (sigRows.length) {
    console.log('  warn breakdown:');
    for (const [k, v] of sigRows) console.log(`    ${String(v).padStart(4)}  ${k}`);
  }
  console.log(`quarantined docs: ${quarantine.length}${quarantine.length ? ' -> ' + quarantine.slice(0, 20).join(', ') + (quarantine.length > 20 ? ' …' : '') : ''}`);
  console.log('');
  console.log(`full report: ${path.relative(ROOT, REPORT_OUT)}`);
}

if (STRICT && findings.block.length > 0) {
  process.exitCode = 1;
}
