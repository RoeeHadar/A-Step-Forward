#!/usr/bin/env node
/**
 * Regenerate:
 *   - apps/web/src/lib/lessons-index.generated.json  (lightweight catalog)
 *   - apps/web/src/lib/lessons-bundle.generated.json   (full lesson payloads for DB fallback)
 *
 * Usage: node scripts/generate-lessons-artifacts.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { normalizeLesson, validateLesson } from './lib/normalize-lesson.mjs';

const LESSONS_DIR = 'scripts/seed_data/lessons';
const INDEX_OUT = 'apps/web/src/lib/lessons-index.generated.json';
const BUNDLE_OUT = 'apps/web/src/lib/lessons-bundle.generated.json';

const files = fs.readdirSync(LESSONS_DIR).filter((f) => f.endsWith('.json')).sort();
const index = [];
const bundle = {};
const errors = [];

for (const file of files) {
  const fp = path.join(LESSONS_DIR, file);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch (e) {
    errors.push({ file, error: `JSON parse: ${e.message}` });
    continue;
  }

  const data = normalizeLesson(raw, file);
  const validationErrors = validateLesson(file, data);
  if (validationErrors.length) {
    errors.push({ file, error: validationErrors.join('; ') });
    continue;
  }

  index.push({
    id: data.concept_id,
    title_en: data.title_en,
    title_he: data.title_he,
    est_minutes: data.est_minutes,
    estimated_minutes: data.est_minutes,
    duration_min: data.est_minutes,
    subject: data.subject,
    level_min: data.level,
    type: 'interactive',
    math_track: data.math_track,
  });

  bundle[data.concept_id] = {
    lesson: {
      id: data.concept_id,
      concept_id: data.concept_id,
      subject: data.subject,
      level: data.level,
      math_track: data.math_track,
      title_en: data.title_en,
      title_he: data.title_he,
      summary_en: data.summary_en,
      summary_he: data.summary_he,
      sections: data.sections,
      agent_hints: data.agent_hints,
      est_minutes: data.est_minutes,
      author: data.author,
      version: data.version,
      level_focus: data.level_focus,
      skill_atom_bank: data.skill_atom_bank,
    },
    questions: data.questions.map((q, i) => ({
      id: q.id ?? `${data.concept_id}-q${i + 1}`,
      lesson_id: data.concept_id,
      ord: q.ord,
      kind: q.kind,
      difficulty: q.difficulty,
      stem_en: q.stem_en,
      stem_he: q.stem_he,
      options_en: q.options_en ?? null,
      options_he: q.options_he ?? null,
      correct_index: q.correct_index ?? null,
      correct_answer: q.correct_answer ?? null,
      answer_payload: q.answer_payload ?? null,
      rubric_en: q.rubric_en ?? null,
      rubric_he: q.rubric_he ?? null,
      explanation_en: q.explanation_en,
      explanation_he: q.explanation_he,
      skill_atoms: q.skill_atoms ?? [],
      points_level_min: q.points_level_min ?? null,
    })),
  };
}

index.sort((a, b) => a.id.localeCompare(b.id));

fs.writeFileSync(INDEX_OUT, `${JSON.stringify(index, null, 2)}\n`, 'utf-8');
fs.writeFileSync(BUNDLE_OUT, `${JSON.stringify(bundle, null, 2)}\n`, 'utf-8');

console.log(`[generate-lessons-artifacts] index=${index.length} bundle=${Object.keys(bundle).length} errors=${errors.length}`);
if (errors.length) {
  for (const e of errors.slice(0, 20)) console.error(`  [skip] ${e.file}: ${e.error}`);
  if (errors.length > 20) console.error(`  ... and ${errors.length - 20} more`);
  process.exit(1);
}
