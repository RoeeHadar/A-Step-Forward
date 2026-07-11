#!/usr/bin/env node
/**
 * Rebuild diagnostic_items from authored lesson MCQs (real stems/options).
 *
 * Usage:
 *   DATABASE_URL=... node scripts/seed-diagnostic-from-lessons.mjs
 *   add --keep-templates (ignored; full rebuild always runs)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as yaml from 'js-yaml';
import { neon } from '@neondatabase/serverless';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const LESSONS_DIR = path.join(ROOT, 'scripts', 'seed_data', 'lessons');
const KG_ROOT = path.join(ROOT, 'content', 'knowledge-graph');
const KEY_ORDER = ['A', 'B', 'C', 'D'];
const BLOOM_BY_DIFF = {
  2: 'remember',
  3: 'remember',
  4: 'understand',
  5: 'apply',
  6: 'apply',
  7: 'analyze',
  8: 'analyze',
  9: 'evaluate',
  10: 'evaluate',
};

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) {
  console.error('DATABASE_URL must be set');
  process.exit(1);
}

const sql = neon(url);

function mapLessonSubject(subject) {
  const s = String(subject ?? 'math').toLowerCase();
  if (s === 'physics' || s.startsWith('physics_')) return 'physics';
  return 'math';
}

function difficultyNumeric(raw) {
  if (typeof raw === 'number' && Number.isFinite(raw)) return Math.min(10, Math.max(1, raw));
  const map = { easy: 3, medium: 5, hard: 7, very_hard: 9 };
  return map[String(raw ?? 'medium').toLowerCase()] ?? 5;
}

function loadConceptPointsLevels() {
  const out = new Map();
  for (const file of fs.readdirSync(KG_ROOT).filter((f) => f.endsWith('.yaml'))) {
    const data = yaml.load(fs.readFileSync(path.join(KG_ROOT, file), 'utf8')) ?? {};
    for (const concept of data.concepts ?? []) {
      if (concept.id && concept.points_levels) {
        out.set(concept.id, concept.points_levels);
      }
    }
  }
  return out;
}

function isTemplateStem(stem) {
  return /Which statement best describes|A statement that does not apply to/i.test(stem ?? '');
}

function buildMcqOptions(optionsEn, optionsHe, correctIndex) {
  const choicesEn = (optionsEn ?? []).slice(0, 4);
  const choicesHe = (optionsHe ?? choicesEn).slice(0, 4);
  const idx = Math.max(0, Math.min(choicesEn.length - 1, Number(correctIndex ?? 0)));
  const correct = KEY_ORDER[idx] ?? 'A';
  return {
    options: { choices: choicesEn, correct },
    options_he: { choices: choicesHe, correct },
  };
}

function buildTrueFalseOptions(correctBool) {
  const correct = correctBool ? 'A' : 'B';
  return {
    options: { choices: ['True', 'False'], correct },
    options_he: { choices: ['נכון', 'לא נכון'], correct },
  };
}

function extractQuestionsFromLesson(lesson) {
  if (String(lesson.level ?? '').toLowerCase() === 'university') {
    return [];
  }
  const conceptId = lesson.concept_id;
  const subject = mapLessonSubject(lesson.subject);
  const rows = [];

  for (const q of lesson.questions ?? []) {
    if (q.kind === 'mcq') {
      const payload = q.answer_payload ?? {};
      const optionsEn = q.options_en ?? payload.options_en ?? [];
      const optionsHe = q.options_he ?? payload.options_he ?? optionsEn;
      const correctIndex = q.correct_index ?? payload.correct_index ?? 0;
      if (!q.stem_en?.trim() || optionsEn.length < 2) continue;
      const { options, options_he } = buildMcqOptions(optionsEn, optionsHe, correctIndex);
      const diff = difficultyNumeric(q.difficulty);
      rows.push({
        topic: conceptId,
        subject,
        difficulty: diff,
        bloom_level: BLOOM_BY_DIFF[diff] ?? 'apply',
        stem: q.stem_en.trim(),
        options,
        explanation: (q.explanation_en ?? '').trim() || null,
        stem_he: (q.stem_he ?? q.stem_en).trim(),
        options_he,
        explanation_he: (q.explanation_he ?? q.explanation_en ?? '').trim() || null,
        source_concept: conceptId,
      });
    } else if (q.kind === 'true_false') {
      const payload = q.answer_payload ?? {};
      const correctBool = q.correct_bool ?? payload.correct_bool;
      if (typeof correctBool !== 'boolean' || !q.stem_en?.trim()) continue;
      const { options, options_he } = buildTrueFalseOptions(correctBool);
      const diff = difficultyNumeric(q.difficulty);
      rows.push({
        topic: conceptId,
        subject,
        difficulty: diff,
        bloom_level: BLOOM_BY_DIFF[diff] ?? 'understand',
        stem: q.stem_en.trim(),
        options,
        explanation: (q.explanation_en ?? '').trim() || null,
        stem_he: (q.stem_he ?? q.stem_en).trim(),
        options_he,
        explanation_he: (q.explanation_he ?? q.explanation_en ?? '').trim() || null,
        source_concept: conceptId,
      });
    }
  }
  return rows;
}

async function ensureSchema() {
  const alters = [
    `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS stem_he TEXT`,
    `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS options_he JSONB`,
    `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS explanation_he TEXT`,
    `ALTER TABLE diagnostic_items ADD COLUMN IF NOT EXISTS points_levels TEXT[]`,
  ];
  for (const stmt of alters) {
    await sql(stmt);
  }
}

async function main() {
  await ensureSchema();
  const pointsByConcept = loadConceptPointsLevels();

  const lessonFiles = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
  const lessonRows = [];
  for (const file of lessonFiles) {
    let lesson;
    try {
      lesson = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, file), 'utf8'));
    } catch {
      continue;
    }
    lessonRows.push(...extractQuestionsFromLesson(lesson));
  }

  if (lessonRows.length === 0) {
    console.error('No MCQ/true_false questions found in lesson JSON.');
    process.exit(1);
  }

  // Full rebuild keeps CI seed idempotent and drops stale template rows.
  // Clear dependent quiz_responses first — item_id FK has no ON DELETE CASCADE.
  await sql`DELETE FROM quiz_responses WHERE quiz_type = 'diagnostic'`;
  await sql`DELETE FROM diagnostic_items`;
  console.log('Cleared diagnostic_items (and diagnostic quiz_responses) for rebuild.');

  let inserted = 0;
  for (const row of lessonRows) {
    const pointsLevels = pointsByConcept.get(row.topic) ?? null;
    await sql`
      INSERT INTO diagnostic_items (
        topic, subject, difficulty, bloom_level, stem, options, explanation,
        stem_he, options_he, explanation_he, source_concept, points_levels, created_at
      )
      VALUES (
        ${row.topic}, ${row.subject}, ${row.difficulty}, ${row.bloom_level},
        ${row.stem}, ${JSON.stringify(row.options)}::jsonb, ${row.explanation},
        ${row.stem_he}, ${JSON.stringify(row.options_he)}::jsonb, ${row.explanation_he},
        ${row.source_concept}, ${pointsLevels}, NOW()
      )
    `;
    inserted += 1;
  }

  const [{ total }] = await sql`SELECT COUNT(*)::int AS total FROM diagnostic_items`;
  const [{ real }] = await sql`
    SELECT COUNT(*)::int AS real
    FROM diagnostic_items
    WHERE NOT (stem LIKE 'Which statement best describes%')
  `;
  console.log(
    `Inserted ${inserted} lesson-sourced diagnostic items (bank total: ${total}, non-template: ${real}).`,
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
