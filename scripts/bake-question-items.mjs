#!/usr/bin/env node
/**
 * Bake verified question-store items into lessons' `questions[]`.
 *
 * Offline job: for each pilot concept, pull VERIFIED items from `question_items`,
 * select a balanced set (kind diversity + difficulty spread), flatten composite
 * items into the lesson-question shape (see scripts/lib/normalize-lesson.mjs),
 * and write them into the lesson JSON. Dry-run by default.
 *
 * The mapping/selection are pure functions (exported) so they are unit-testable
 * with fixtures and no DB. The CLI wraps them with a Neon fetch + file writes.
 *
 * Usage:
 *   node scripts/bake-question-items.mjs --pilot=scripts/seed_data/pilot-bagrut-math-5.json
 *   node scripts/bake-question-items.mjs --pilot=... --write        # persist
 *   node scripts/bake-question-items.mjs --concept=derivatives_rules --max=8
 */
import fs from 'node:fs';
import path from 'node:path';

/** Combine a shared stem with a part stem for a self-contained baked question. */
function combineStem(sharedStem, partStem, partOrd, totalParts) {
  const shared = (sharedStem ?? '').trim();
  const part = (partStem ?? '').trim();
  if (!shared) return part;
  if (totalParts <= 1) return part || shared;
  const label = String.fromCharCode(96 + partOrd); // 1 -> 'a'
  return `${shared}\n\n(${label}) ${part}`;
}

/** Stringify a numeric/rational answer for the `correct_answer` column. */
function answerToString(v) {
  if (v === null || v === undefined) return null;
  return String(v);
}

/**
 * Map a store item's `answer_payload` onto the CANONICAL top-level fields the
 * seed pipeline (`seed-lessons.mjs` -> `buildAnswerPayload`) and the grader UI
 * (`lesson-quiz-panel.tsx`) read per kind. Leaving answers only in
 * `answer_payload` silently breaks grading for every kind except mcq.
 */
function applyAnswerFields(q, ap) {
  if (!ap || typeof ap !== 'object') return;
  switch (q.kind) {
    case 'mcq':
      if (ap.options_en) q.options_en = ap.options_en;
      if (ap.options_he) q.options_he = ap.options_he ?? ap.options_en;
      if (ap.correct_index !== undefined) q.correct_index = ap.correct_index;
      break;
    case 'mcq_multi':
      if (Array.isArray(ap.correct_indices)) q.correct_indices = ap.correct_indices;
      if (ap.options_en) q.options_en = ap.options_en;
      if (ap.options_he) q.options_he = ap.options_he ?? ap.options_en;
      break;
    case 'true_false': {
      const b = typeof ap.value === 'boolean' ? ap.value : ap.correct_bool;
      if (typeof b === 'boolean') q.correct_bool = b;
      break;
    }
    case 'numeric':
    case 'fill_blank': {
      const val = ap.value ?? ap.answer ?? (Array.isArray(ap.acceptable_answers) ? ap.acceptable_answers[0] : undefined);
      const s = answerToString(val);
      if (s !== null) q.correct_answer = s;
      break;
    }
    case 'short_answer':
      if (Array.isArray(ap.acceptable_answers)) q.acceptable_answers = ap.acceptable_answers;
      q.case_sensitive = Boolean(ap.case_sensitive);
      if (!q.correct_answer && Array.isArray(ap.acceptable_answers)) {
        q.correct_answer = answerToString(ap.acceptable_answers[0]);
      }
      break;
    case 'match':
      if (ap.left_en) q.left_en = ap.left_en;
      if (ap.left_he) q.left_he = ap.left_he;
      if (ap.right_en) q.right_en = ap.right_en;
      if (ap.right_he) q.right_he = ap.right_he;
      if (ap.correct_pairs) q.correct_pairs = ap.correct_pairs;
      break;
    case 'ordering':
      if (ap.steps_en) q.steps_en = ap.steps_en;
      if (ap.steps_he) q.steps_he = ap.steps_he;
      if (ap.correct_order) q.correct_order = ap.correct_order;
      break;
    case 'derivation':
      if (Array.isArray(ap.expected_steps)) q.expected_steps = ap.expected_steps;
      break;
    default:
      break;
  }
}

/** Flatten one composite store item into >=1 lesson-question objects. */
export function itemToLessonQuestions(item) {
  const parts = Array.isArray(item.parts) ? item.parts : [];
  const total = parts.length;
  return parts.map((part) => {
    const ap = part.answer_payload ?? item.answer_payload ?? null;
    const atoms = (part.skill_atoms?.length ? part.skill_atoms : item.skill_atoms) ?? [];
    const q = {
      kind: part.kind ?? item.kind,
      difficulty: part.difficulty ?? item.difficulty,
      stem_en: combineStem(item.stem_en, part.stem_en, part.ord, total),
      stem_he: combineStem(item.stem_he, part.stem_he, part.ord, total),
      explanation_en: part.explanation_en ?? '',
      explanation_he: part.explanation_he ?? '',
      skill_atoms: atoms,
      answer_payload: ap,
      source_item_id: item.id ?? null,
    };
    if (part.rubric_en) q.rubric_en = part.rubric_en;
    if (part.rubric_he) q.rubric_he = part.rubric_he;
    if (item.points_level) q.points_level_min = item.points_level;
    applyAnswerFields(q, ap);
    return q;
  });
}

const DIFF_ORDER = { easy: 0, medium: 1, hard: 2 };

/**
 * Select a balanced subset: maximize distinct kinds first, then spread across
 * difficulty. Deterministic given input order.
 */
export function selectBalanced(questions, max = 8) {
  const seenKinds = new Set();
  const primary = [];
  const rest = [];
  for (const q of questions) {
    if (!seenKinds.has(q.kind)) {
      seenKinds.add(q.kind);
      primary.push(q);
    } else {
      rest.push(q);
    }
  }
  rest.sort((a, b) => (DIFF_ORDER[a.difficulty] ?? 1) - (DIFF_ORDER[b.difficulty] ?? 1));
  return [...primary, ...rest].slice(0, max);
}

/** Pure end-to-end: store items -> baked, balanced lesson questions. */
export function bakeConceptQuestions(items, { max = 8 } = {}) {
  const flattened = items.flatMap(itemToLessonQuestions);
  const selected = selectBalanced(flattened, max);
  const kinds = new Set(selected.map((q) => q.kind));
  return {
    questions: selected,
    warnings: [
      ...(kinds.size < 3 ? [`only ${kinds.size} distinct kinds available (need >=3)`] : []),
      ...(selected.length === 0 ? ['no verified items to bake'] : []),
    ],
  };
}

/* --------------------------------- CLI ------------------------------------ */

function isMain() {
  return import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('bake-question-items.mjs');
}

async function main() {
  const args = new Map();
  for (const a of process.argv.slice(2)) {
    if (!a.startsWith('--')) continue;
    const [k, v] = a.slice(2).split('=');
    args.set(k, v ?? 'true');
  }
  const write = args.get('write') === 'true';
  const max = Number(args.get('max') ?? 8);
  const lessonsDir = args.get('dir') ?? 'scripts/seed_data/lessons';

  let conceptIds = [];
  if (args.get('concept') && args.get('concept') !== 'true') {
    conceptIds = [args.get('concept')];
  } else if (args.get('pilot') && args.get('pilot') !== 'true') {
    const manifest = JSON.parse(fs.readFileSync(args.get('pilot'), 'utf8'));
    conceptIds = manifest.concept_ids ?? [];
  } else {
    console.error('Provide --concept=<id> or --pilot=<manifest.json>');
    process.exit(1);
  }

  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
  if (!url) {
    console.error('DATABASE_URL not set — cannot fetch verified items.');
    process.exit(1);
  }
  const { neon } = await import('@neondatabase/serverless');
  const { queryItemsForBaking } = await import('./lib/question-store-io.mjs');
  const sql = neon(url);

  for (const conceptId of conceptIds) {
    const items = await queryItemsForBaking(sql, { conceptId, gradedOnly: true, max: 100 });
    const { questions, warnings } = bakeConceptQuestions(items, { max });
    console.log(`\n[${conceptId}] verified items=${items.length} -> baked questions=${questions.length}`);
    for (const w of warnings) console.log(`  ! ${w}`);

    if (write && questions.length > 0) {
      const file = path.join(lessonsDir, `${conceptId}.json`);
      if (!fs.existsSync(file)) {
        console.log(`  (skip write: ${file} not found)`);
        continue;
      }
      const lesson = JSON.parse(fs.readFileSync(file, 'utf8'));
      lesson.questions = questions;
      fs.writeFileSync(file, JSON.stringify(lesson, null, 2) + '\n', 'utf8');
      console.log(`  wrote ${questions.length} questions -> ${file}`);
    }
  }
  if (!write) console.log('\n(dry-run — pass --write to persist into lesson JSON)');
}

if (isMain()) {
  main().catch((err) => {
    console.error(err instanceof Error ? err.message : err);
    process.exit(1);
  });
}
