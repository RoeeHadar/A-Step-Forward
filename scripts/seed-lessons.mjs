#!/usr/bin/env node
/**
 * Seed `lessons` + `lesson_questions` from JSON files written to
 * `scripts/seed_data/lessons/*.json` by the authoring process.
 *
 * Strategy: per-lesson idempotent. For each input file we DELETE the existing
 * row in `lessons` (cascade drops questions), then INSERT the new lesson and
 * its questions in a single transaction.
 *
 * Usage:
 *   DATABASE_URL=... node scripts/seed-lessons.mjs
 *   add --dir <path> to seed from a custom directory
 *   add --dry-run to skip writes (validation only)
 */
import fs from 'node:fs';
import path from 'node:path';
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}
const sql = neon(url);

const args = new Map();
for (const arg of process.argv.slice(2)) {
  if (!arg.startsWith('--')) continue;
  const [k, v] = arg.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const dir = args.get('dir') ?? 'scripts/seed_data/lessons';
const dryRun = args.get('dry-run') === 'true';

if (!fs.existsSync(dir)) {
  console.error(`lessons dir not found: ${dir}`);
  process.exit(1);
}

const files = fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
console.log(`[seed-lessons] ${files.length} lesson files in ${dir}`);

// ---------- validation ----------------------------------------------------
const SECTION_KINDS = new Set([
  'intro',
  'theory',
  'worked_example',
  'pitfall',
  'practice_tip',
  'summary',
]);
const Q_KINDS = new Set(['mcq', 'open', 'fill_blank', 'numeric']);
const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

function fail(file, msg) {
  console.error(`  [invalid] ${file}: ${msg}`);
  process.exit(2);
}

function validateLesson(file, l) {
  const need = ['concept_id', 'subject', 'level', 'title_en', 'title_he',
    'summary_en', 'summary_he', 'sections', 'agent_hints', 'questions'];
  for (const k of need) if (l[k] === undefined) fail(file, `missing field ${k}`);
  if (!Array.isArray(l.sections) || l.sections.length === 0) fail(file, 'sections must be non-empty array');
  if (!Array.isArray(l.questions) || l.questions.length < 4) fail(file, 'questions must be array of >=4');
  for (const [i, s] of l.sections.entries()) {
    if (!SECTION_KINDS.has(s.kind)) fail(file, `section[${i}].kind invalid: ${s.kind}`);
    for (const k of ['title_en', 'title_he', 'body_en_md', 'body_he_md']) {
      if (typeof s[k] !== 'string' || !s[k].trim()) fail(file, `section[${i}].${k} required`);
    }
  }
  const seenOrd = new Set();
  for (const [i, q] of l.questions.entries()) {
    if (!Q_KINDS.has(q.kind)) fail(file, `q[${i}].kind invalid: ${q.kind}`);
    if (!DIFFICULTIES.has(q.difficulty)) fail(file, `q[${i}].difficulty invalid: ${q.difficulty}`);
    if (typeof q.ord !== 'number') fail(file, `q[${i}].ord must be number`);
    if (seenOrd.has(q.ord)) fail(file, `duplicate q.ord ${q.ord}`);
    seenOrd.add(q.ord);
    for (const k of ['stem_en', 'stem_he', 'explanation_en', 'explanation_he']) {
      if (typeof q[k] !== 'string' || !q[k].trim()) fail(file, `q[${i}].${k} required`);
    }
    if (q.kind === 'mcq') {
      if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) fail(file, `q[${i}] mcq needs options_en/he`);
      if (q.options_en.length !== q.options_he.length) fail(file, `q[${i}] options length mismatch`);
      if (typeof q.correct_index !== 'number' || q.correct_index < 0 || q.correct_index >= q.options_en.length) {
        fail(file, `q[${i}] correct_index out of range`);
      }
    } else if (q.kind === 'open') {
      if (!q.rubric_en || !q.rubric_he) fail(file, `q[${i}] open needs rubric_en/he`);
    } else {
      // fill_blank / numeric
      if (typeof q.correct_answer !== 'string' || !q.correct_answer.trim()) {
        fail(file, `q[${i}] ${q.kind} needs correct_answer`);
      }
    }
    if (!Array.isArray(q.skill_atoms)) fail(file, `q[${i}].skill_atoms must be array`);
  }
}

const lessons = [];
for (const file of files) {
  const fp = path.join(dir, file);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch (e) {
    console.error(`[seed-lessons] JSON parse error in ${file}: ${e.message}`);
    process.exit(1);
  }
  validateLesson(file, raw);
  lessons.push({ file, data: raw });
}
console.log(`[seed-lessons] validated ${lessons.length} lessons`);

if (dryRun) {
  console.log('[seed-lessons] --dry-run: skipping DB writes');
  process.exit(0);
}

// ---------- DB writes -----------------------------------------------------
let inserted = 0;
let questionsInserted = 0;
const errors = [];

for (const { file, data } of lessons) {
  try {
    await sql`DELETE FROM lessons WHERE concept_id = ${data.concept_id}`;
    const rows = await sql`
      INSERT INTO lessons (
        concept_id, subject, level, math_track,
        title_en, title_he, summary_en, summary_he,
        sections, agent_hints, est_minutes, author, version
      ) VALUES (
        ${data.concept_id},
        ${data.subject},
        ${data.level},
        ${data.math_track ?? []},
        ${data.title_en},
        ${data.title_he},
        ${data.summary_en},
        ${data.summary_he},
        ${JSON.stringify(data.sections)},
        ${JSON.stringify(data.agent_hints ?? {})},
        ${data.est_minutes ?? 15},
        ${data.author ?? 'cursor-claude-2026'},
        ${data.version ?? 1}
      )
      RETURNING id::text
    `;
    const lessonId = rows[0].id;
    for (const q of data.questions) {
      await sql`
        INSERT INTO lesson_questions (
          lesson_id, ord, kind, difficulty,
          stem_en, stem_he, options_en, options_he,
          correct_index, correct_answer,
          rubric_en, rubric_he,
          explanation_en, explanation_he, skill_atoms
        ) VALUES (
          ${lessonId}::uuid,
          ${q.ord},
          ${q.kind},
          ${q.difficulty},
          ${q.stem_en},
          ${q.stem_he},
          ${q.options_en ? JSON.stringify(q.options_en) : null},
          ${q.options_he ? JSON.stringify(q.options_he) : null},
          ${q.correct_index ?? null},
          ${q.correct_answer ?? null},
          ${q.rubric_en ?? null},
          ${q.rubric_he ?? null},
          ${q.explanation_en},
          ${q.explanation_he},
          ${JSON.stringify(q.skill_atoms ?? [])}
        )
      `;
      questionsInserted += 1;
    }
    inserted += 1;
    console.log(`  [ok] ${data.concept_id} (${data.questions.length} q)`);
  } catch (err) {
    console.error(`  [fail] ${file}: ${err.message}`);
    errors.push({ file, error: err.message });
  }
}

console.log(
  `[seed-lessons] Done: lessons inserted=${inserted}/${lessons.length}, questions inserted=${questionsInserted}, errors=${errors.length}`,
);
if (errors.length) process.exit(3);
