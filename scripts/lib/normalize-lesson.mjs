/**
 * Shared normalization + validation for authored lesson JSON.
 * Used by seed-lessons.mjs and generate-lessons-artifacts.mjs.
 */

import { normalizeLessonLatex } from './normalize-latex.mjs';

export const SECTION_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'checkpoint',
  'method_guide',
  'exercise_set',
  'pitfall',
  'before_exam',
  'exam_problems',
  'practice_tip',
  'summary',
  'why_matters',
]);

export const Q_KINDS = new Set([
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

export const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

const DIFFICULTY_MAP = { 1: 'easy', 2: 'medium', 3: 'hard', easy: 'easy', medium: 'medium', hard: 'hard' };

function inferLevel(raw) {
  if (raw.level) return raw.level;
  if (raw.level_min) return raw.level_min;
  const d = String(raw.difficulty ?? '').toLowerCase();
  if (d === 'beginner' || d === 'easy') return 'high_school';
  if (d === 'intermediate') return 'high_school';
  if (d === 'advanced' || d === 'hard') return 'university';
  return 'high_school';
}

function normalizeSection(section) {
  const s = { ...section };
  if (!s.body_en_md?.trim() && s.body_en?.trim()) s.body_en_md = s.body_en;
  if (!s.body_he_md?.trim() && s.body_he?.trim()) s.body_he_md = s.body_he;
  s.title_en = s.title_en ?? '';
  s.title_he = s.title_he ?? s.title_en ?? '';
  s.body_en_md = s.body_en_md ?? '';
  s.body_he_md = s.body_he_md ?? '';
  return s;
}

function normalizeQuestion(q, index) {
  const out = { ...q };
  out.ord = typeof out.ord === 'number' ? out.ord : index + 1;
  const diff = DIFFICULTY_MAP[out.difficulty] ?? 'medium';
  out.difficulty = diff;

  if (out.answer_payload && typeof out.answer_payload === 'object') {
    const p = out.answer_payload;
    if (out.kind === 'mcq' && p.options_en && p.correct_index !== undefined) {
      out.options_en = out.options_en ?? p.options_en;
      out.options_he = out.options_he ?? p.options_he ?? p.options_en;
      out.correct_index = out.correct_index ?? p.correct_index;
    }
  }

  out.stem_en = out.stem_en ?? '';
  out.stem_he = out.stem_he ?? out.stem_en ?? '';
  out.explanation_en = out.explanation_en ?? '';
  out.explanation_he = out.explanation_he ?? out.explanation_en ?? '';
  out.skill_atoms = Array.isArray(out.skill_atoms) ? out.skill_atoms : [];
  return out;
}

/** Normalize raw lesson JSON into a DB-ready shape. */
export function normalizeLesson(raw, fileBase) {
  const conceptId = raw.concept_id ?? raw.id ?? fileBase.replace(/\.json$/, '');
  const titleEn = raw.title_en ?? conceptId.replace(/_/g, ' ');
  const titleHe = raw.title_he ?? titleEn;

  const sections = (raw.sections ?? []).map(normalizeSection);
  const questions = (raw.questions ?? []).map(normalizeQuestion);

  const lesson = {
    concept_id: conceptId,
    subject: raw.subject ?? 'math',
    level: inferLevel(raw),
    math_track: Array.isArray(raw.math_track) ? raw.math_track : [],
    title_en: titleEn,
    title_he: titleHe,
    summary_en: raw.summary_en ?? titleEn,
    summary_he: raw.summary_he ?? titleHe,
    sections,
    agent_hints: raw.agent_hints ?? {},
    questions,
    est_minutes: raw.est_minutes ?? raw.estimated_minutes ?? raw.duration_min ?? 20,
    author: raw.author ?? 'cursor-claude-2026',
    version: raw.version ?? 1,
    level_focus: raw.level_focus ?? null,
    skill_atom_bank: raw.skill_atom_bank ?? null,
  };
  return normalizeLessonLatex(lesson);
}

export function validateLesson(file, l) {
  const errors = [];
  if (!l.concept_id) errors.push('missing concept_id');
  if (!l.title_en?.trim()) errors.push('missing title_en');
  if (!l.title_he?.trim()) errors.push('missing title_he');
  if (!Array.isArray(l.sections) || l.sections.length === 0) {
    errors.push('sections must be non-empty array');
    return errors;
  }

  for (const [i, s] of l.sections.entries()) {
    if (!SECTION_KINDS.has(s.kind)) {
      errors.push(`section[${i}].kind invalid: ${s.kind}`);
      continue;
    }
    if (!s.title_en?.trim() || !s.title_he?.trim()) {
      errors.push(`section[${i}] title_en/title_he required`);
    }
    if (s.kind === 'checkpoint') {
      if (!s.body_en_md?.trim() || !s.body_he_md?.trim()) {
        errors.push(`section[${i}] checkpoint body_en_md/body_he_md required`);
      }
      if (!s.checkpoint_solution_en?.trim() || !s.checkpoint_solution_he?.trim()) {
        errors.push(`section[${i}] checkpoint solutions required`);
      }
      continue;
    }
    if (s.kind === 'exercise_set') {
      if (!Array.isArray(s.exercises) || s.exercises.length < 4) {
        errors.push(`section[${i}] exercise_set needs >=4 exercises`);
      } else {
        for (const [j, ex] of s.exercises.entries()) {
          if (!ex.body_en?.trim() || !ex.body_he?.trim()) {
            errors.push(`section[${i}].exercises[${j}] body_en/body_he required`);
          }
        }
      }
      continue;
    }
    if (!s.body_en_md?.trim() || !s.body_he_md?.trim()) {
      errors.push(`section[${i}] body_en_md/body_he_md required`);
    }
  }

  if (!Array.isArray(l.questions)) {
    errors.push('questions must be an array');
  } else {
    for (const [i, q] of l.questions.entries()) {
      if (!Q_KINDS.has(q.kind)) errors.push(`q[${i}].kind invalid: ${q.kind}`);
      if (!DIFFICULTIES.has(q.difficulty)) errors.push(`q[${i}].difficulty invalid: ${q.difficulty}`);
      if (!q.stem_en?.trim() || !q.stem_he?.trim()) errors.push(`q[${i}] stem required`);
    }
  }

  return errors;
}

export function sectionContentScore(sections) {
  if (!Array.isArray(sections) || sections.length === 0) return 0;
  let score = sections.length;
  const kinds = new Set(sections.map((s) => s.kind));
  if (kinds.has('worked_example')) score += 3;
  if (kinds.has('definition')) score += 1;
  if (kinds.has('exercise_set')) score += 2;
  const bodyHe = sections.reduce((n, s) => n + (s.body_he_md?.length ?? 0), 0);
  if (bodyHe > 500) score += 2;
  return score;
}
