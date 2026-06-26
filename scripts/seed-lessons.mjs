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
const Q_KINDS = new Set([
  'mcq',
  'mcq_multi',
  'true_false',
  'open',
  'short_answer',
  'fill_blank',
  'numeric',
  'match',
  'ordering',
  'derivation',
]);
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
    } else if (q.kind === 'mcq_multi') {
      if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) fail(file, `q[${i}] mcq_multi needs options_en/he`);
      if (q.options_en.length !== q.options_he.length) fail(file, `q[${i}] options length mismatch`);
      if (!Array.isArray(q.correct_indices) || q.correct_indices.length === 0) {
        fail(file, `q[${i}] mcq_multi needs correct_indices: int[]`);
      }
      for (const idx of q.correct_indices) {
        if (typeof idx !== 'number' || idx < 0 || idx >= q.options_en.length) {
          fail(file, `q[${i}] correct_indices contains out-of-range index ${idx}`);
        }
      }
    } else if (q.kind === 'true_false') {
      if (typeof q.correct_bool !== 'boolean') fail(file, `q[${i}] true_false needs correct_bool: boolean`);
    } else if (q.kind === 'open' || q.kind === 'derivation') {
      if (!q.rubric_en || !q.rubric_he) fail(file, `q[${i}] ${q.kind} needs rubric_en/he`);
    } else if (q.kind === 'short_answer') {
      if (!Array.isArray(q.acceptable_answers) || q.acceptable_answers.length === 0) {
        fail(file, `q[${i}] short_answer needs acceptable_answers: string[]`);
      }
    } else if (q.kind === 'match') {
      if (!Array.isArray(q.left_en) || !Array.isArray(q.left_he) ||
          !Array.isArray(q.right_en) || !Array.isArray(q.right_he)) {
        fail(file, `q[${i}] match needs left_en/he + right_en/he arrays`);
      }
      if (q.left_en.length !== q.left_he.length || q.right_en.length !== q.right_he.length) {
        fail(file, `q[${i}] match left/right EN-HE length mismatch`);
      }
      if (!Array.isArray(q.correct_pairs) || q.correct_pairs.length !== q.left_en.length) {
        fail(file, `q[${i}] match needs correct_pairs: int[] with one entry per left item`);
      }
      for (const idx of q.correct_pairs) {
        if (typeof idx !== 'number' || idx < 0 || idx >= q.right_en.length) {
          fail(file, `q[${i}] correct_pairs contains out-of-range index ${idx}`);
        }
      }
    } else if (q.kind === 'ordering') {
      if (!Array.isArray(q.steps_en) || !Array.isArray(q.steps_he)) {
        fail(file, `q[${i}] ordering needs steps_en/he`);
      }
      if (q.steps_en.length !== q.steps_he.length) {
        fail(file, `q[${i}] ordering steps EN-HE length mismatch`);
      }
      if (!Array.isArray(q.correct_order) || q.correct_order.length !== q.steps_en.length) {
        fail(file, `q[${i}] ordering needs correct_order: int[] permutation of step indices`);
      }
    } else {
      // fill_blank / numeric
      if (typeof q.correct_answer !== 'string' || !q.correct_answer.trim()) {
        fail(file, `q[${i}] ${q.kind} needs correct_answer`);
      }
    }
    if (!Array.isArray(q.skill_atoms)) fail(file, `q[${i}].skill_atoms must be array`);
  }
}

// ---------- answer_payload extraction ------------------------------------
// For each question kind, builds the structured-answer JSONB blob the grader
// reads from `lesson_questions.answer_payload`. Legacy `correct_index` /
// `correct_answer` columns are kept populated for backward-compat with
// existing `mcq` and `numeric` grading code paths.
function buildAnswerPayload(q) {
  switch (q.kind) {
    case 'mcq_multi':
      return { correct_indices: [...q.correct_indices].sort((a, b) => a - b) };
    case 'true_false':
      return { correct_bool: q.correct_bool };
    case 'short_answer':
      return { acceptable_answers: q.acceptable_answers, case_sensitive: Boolean(q.case_sensitive) };
    case 'match':
      return {
        left_en: q.left_en, left_he: q.left_he,
        right_en: q.right_en, right_he: q.right_he,
        correct_pairs: q.correct_pairs,
      };
    case 'ordering':
      return {
        steps_en: q.steps_en, steps_he: q.steps_he,
        correct_order: q.correct_order,
      };
    case 'derivation':
      // Derivation is rubric-graded server-side; payload optionally lists
      // expected-step keywords the LLM-judge can look for.
      return q.expected_steps ? { expected_steps: q.expected_steps } : null;
    default:
      return null;
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
      const payload = buildAnswerPayload(q);
      await sql`
        INSERT INTO lesson_questions (
          lesson_id, ord, kind, difficulty,
          stem_en, stem_he, options_en, options_he,
          correct_index, correct_answer, answer_payload,
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
          ${payload ? JSON.stringify(payload) : null},
          ${q.rubric_en ?? null},
          ${q.rubric_he ?? null},
          ${q.explanation_en},
          ${q.explanation_he},
          ${JSON.stringify(q.skill_atoms ?? [])}
        )
      `;
      questionsInserted += 1;
    }

    // Backfill the first-class `skill_atoms` and `lesson_skill_atoms` tables.
    // Each atom from either the lesson's `skill_atoms_unlocked` list (the
    // lesson teaches it) or any of its questions' `skill_atoms` arrays (the
    // questions exercise it). Subject defaults to the lesson's subject.
    const taughtAtoms = new Set(data.agent_hints?.skill_atoms_unlocked ?? []);
    const exercisedAtoms = new Set();
    for (const q of data.questions) for (const a of q.skill_atoms ?? []) exercisedAtoms.add(a);
    const allAtoms = new Set([...taughtAtoms, ...exercisedAtoms]);

    for (const atom of allAtoms) {
      await sql`
        INSERT INTO skill_atoms (id, subject, difficulty)
        VALUES (${atom}, ${data.subject}, 'medium')
        ON CONFLICT (id) DO NOTHING
      `;
    }
    // Clear previous links for this lesson, then re-insert.
    await sql`DELETE FROM lesson_skill_atoms WHERE lesson_id = ${lessonId}::uuid`;
    for (const atom of taughtAtoms) {
      await sql`
        INSERT INTO lesson_skill_atoms (lesson_id, skill_atom, role)
        VALUES (${lessonId}::uuid, ${atom}, 'teaches')
        ON CONFLICT DO NOTHING
      `;
    }
    for (const atom of exercisedAtoms) {
      if (taughtAtoms.has(atom)) continue;
      await sql`
        INSERT INTO lesson_skill_atoms (lesson_id, skill_atom, role)
        VALUES (${lessonId}::uuid, ${atom}, 'exercises')
        ON CONFLICT DO NOTHING
      `;
    }

    inserted += 1;
    console.log(`  [ok] ${data.concept_id} (${data.questions.length} q, ${allAtoms.size} atoms)`);
  } catch (err) {
    console.error(`  [fail] ${file}: ${err.message}`);
    errors.push({ file, error: err.message });
  }
}

// ---------- KG cross-edges backfill --------------------------------------
// Read the curated cross-subject edges JSON and upsert into kg_edges so the
// path planner has a single SQL surface to query against. Idempotent.
try {
  const crossEdgesPath = 'apps/web/src/lib/kg-cross-edges.json';
  if (fs.existsSync(crossEdgesPath)) {
    const crossEdges = JSON.parse(fs.readFileSync(crossEdgesPath, 'utf-8'));
    const edges = crossEdges.edges ?? [];
    let edgesUpserted = 0;
    for (const e of edges) {
      if (!e.src || !e.dst || !e.relation) continue;
      await sql`
        INSERT INTO kg_edges (src_concept, dst_concept, relation, weight, note)
        VALUES (${e.src}, ${e.dst}, ${e.relation}, ${e.weight ?? 1.0}, ${e.note ?? null})
        ON CONFLICT (src_concept, dst_concept, relation)
        DO UPDATE SET weight = EXCLUDED.weight, note = EXCLUDED.note
      `;
      edgesUpserted += 1;
    }
    console.log(`[seed-lessons] kg_edges upserted=${edgesUpserted}`);
  }
} catch (err) {
  console.warn(`[seed-lessons] kg_edges backfill failed (non-fatal): ${err.message}`);
}

console.log(
  `[seed-lessons] Done: lessons inserted=${inserted}/${lessons.length}, questions inserted=${questionsInserted}, errors=${errors.length}`,
);
if (errors.length) process.exit(3);
