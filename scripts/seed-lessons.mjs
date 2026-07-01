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
import { normalizeLesson, validateLesson } from './lib/normalize-lesson.mjs';

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

const Q_KINDS = new Set([
  'mcq', 'mcq_multi', 'true_false', 'open', 'short_answer',
  'fill_blank', 'numeric', 'match', 'ordering', 'derivation',
]);

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
      return q.expected_steps ? { expected_steps: q.expected_steps } : null;
    default:
      return q.answer_payload ?? null;
  }
}

const lessons = [];
const validationErrors = [];

for (const file of files) {
  const fp = path.join(dir, file);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch (e) {
    console.error(`[seed-lessons] JSON parse error in ${file}: ${e.message}`);
    process.exit(1);
  }
  const data = normalizeLesson(raw, file);
  const errs = validateLesson(file, data);
  if (errs.length) {
    validationErrors.push({ file, errors: errs });
    continue;
  }
  lessons.push({ file, data });
}

console.log(`[seed-lessons] validated ${lessons.length}/${files.length} lessons`);
if (validationErrors.length) {
  for (const { file, errors } of validationErrors.slice(0, 15)) {
    console.error(`  [invalid] ${file}: ${errors.join('; ')}`);
  }
  if (validationErrors.length > 15) {
    console.error(`  ... and ${validationErrors.length - 15} more invalid files`);
  }
  process.exit(2);
}

if (dryRun) {
  console.log('[seed-lessons] --dry-run: skipping DB writes');
  process.exit(0);
}

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}
const sql = neon(url);

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
        sections, agent_hints, est_minutes, author, version,
        level_focus, skill_atom_bank
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
        ${data.version ?? 1},
        ${data.level_focus ? JSON.stringify(data.level_focus) : null},
        ${data.skill_atom_bank ? JSON.stringify(data.skill_atom_bank) : null}
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
          explanation_en, explanation_he, skill_atoms,
          points_level_min
        ) VALUES (
          ${lessonId}::uuid,
          ${q.ord},
          ${q.kind},
          ${q.difficulty},
          ${q.stem_en},
          ${q.stem_he},
          ${q.options_en ? JSON.stringify(q.options_en) : null}::jsonb,
          ${q.options_he ? JSON.stringify(q.options_he) : null}::jsonb,
          ${q.correct_index ?? null},
          ${q.correct_answer ?? null},
          ${payload ? JSON.stringify(payload) : null}::jsonb,
          ${q.rubric_en ?? null},
          ${q.rubric_he ?? null},
          ${q.explanation_en},
          ${q.explanation_he},
          ${JSON.stringify(q.skill_atoms ?? [])}::jsonb,
          ${q.points_level_min ?? null}
        )
      `;
      questionsInserted += 1;
    }

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
