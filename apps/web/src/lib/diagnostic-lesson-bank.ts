/**
 * Runtime fallback: pick diagnostic MCQs from the static lessons bundle when
 * Neon diagnostic_items is sparse or stale (common on fresh deploys).
 */
import 'server-only';

import { createHash } from 'node:crypto';
import { getBundledLesson } from '@/lib/lesson-bundle';
import { resolveConceptAlias, resolveConceptAliasCanonical } from '@/lib/concept-aliases';
import { resolveCorrectBool } from '@/lib/answer-normalize';
import type { DiagnosticItem, LearnerProfileRow, LessonQuestionRow } from '@/lib/neon-db';
import { isTemplateDiagnosticStem } from '@/lib/neon-db';
import {
  stemAllowedForProfile,
  stemMatchesSlotKind,
  type DiagnosticSlotKind,
} from '@/lib/diagnostic-stem-filter';
import { stemAlreadyAsked } from '@/lib/diagnostic-stem-dedupe';

const KEY_ORDER = ['A', 'B', 'C', 'D'];

function difficultyNumeric(raw: string | number | undefined): number {
  if (typeof raw === 'number' && Number.isFinite(raw)) {
    return Math.min(10, Math.max(1, raw));
  }
  const map: Record<string, number> = {
    easy: 3,
    medium: 5,
    hard: 7,
    very_hard: 9,
  };
  return map[String(raw ?? 'medium').toLowerCase()] ?? 5;
}

function stableItemId(conceptId: string, stem: string): string {
  const hash = createHash('sha256').update(`diag:${conceptId}:${stem}`).digest('hex');
  return `${hash.slice(0, 8)}-${hash.slice(8, 12)}-4${hash.slice(13, 16)}-8${hash.slice(17, 20)}-${hash.slice(20, 32)}`;
}

function buildOptions(
  q: LessonQuestionRow,
): { options: DiagnosticItem['options']; options_he: DiagnosticItem['options_he'] } | null {
  if (q.kind === 'true_false') {
    const correctBool = resolveCorrectBool(q.answer_payload, {
      correct_answer: q.correct_answer,
    });
    if (correctBool == null) return null;
    const correct = correctBool ? 'A' : 'B';
    return {
      options: { choices: ['True', 'False'], correct },
      options_he: { choices: ['נכון', 'לא נכון'], correct },
    };
  }
  if (q.kind !== 'mcq') return null;
  const choicesEn = (q.options_en ?? []).slice(0, 4);
  if (choicesEn.length < 2) return null;
  const choicesHe = (q.options_he ?? choicesEn).slice(0, 4);
  const idx = Math.max(
    0,
    Math.min(choicesEn.length - 1, q.correct_index ?? 0),
  );
  const correct = KEY_ORDER[idx] ?? 'A';
  return {
    options: { choices: choicesEn, correct },
    options_he: { choices: choicesHe, correct },
  };
}

function questionToItem(
  conceptId: string,
  subject: string,
  q: LessonQuestionRow,
): DiagnosticItem | null {
  const stem = q.stem_en?.trim();
  if (!stem || isTemplateDiagnosticStem(stem)) return null;
  const built = buildOptions(q);
  if (!built) return null;
  return {
    id: stableItemId(conceptId, stem),
    topic: conceptId,
    subject,
    difficulty: difficultyNumeric(q.difficulty),
    stem,
    options: built.options,
    source_concept: conceptId,
    stem_he: q.stem_he?.trim() || null,
    options_he: built.options_he,
    explanation_he: q.explanation_he?.trim() || null,
  };
}

function relatedConceptIds(conceptId: string): string[] {
  const canonical = resolveConceptAliasCanonical(conceptId);
  return [...new Set([conceptId, canonical, resolveConceptAlias(conceptId)])];
}

export function pickDiagnosticItemFromLessonBank(
  conceptId: string,
  profile: LearnerProfileRow,
  excludeItemIds: string[],
  targetDifficulty: number,
  slotKind: DiagnosticSlotKind,
  excludeStemKeys: string[] = [],
): DiagnosticItem | null {
  const exclude = new Set(excludeItemIds);
  const subjects = profile.subjects?.length ? profile.subjects : ['math'];
  const target = Math.max(1, Math.min(10, targetDifficulty));

  const candidates: DiagnosticItem[] = [];

  for (const cid of relatedConceptIds(conceptId)) {
    const lesson = getBundledLesson(cid);
    if (!lesson) continue;
    const subject = lesson.lesson.subject === 'physics' ? 'physics' : 'math';
    if (!subjects.includes(subject)) continue;

    for (const q of lesson.questions) {
      const item = questionToItem(cid, subject, q);
      if (!item || exclude.has(item.id) || stemAlreadyAsked(item.stem, excludeStemKeys)) continue;
      if (!stemAllowedForProfile(item.stem, profile)) continue;
      candidates.push(item);
    }
  }

  if (candidates.length === 0) return null;

  const kindMatches = candidates.filter((c) => stemMatchesSlotKind(c.stem, slotKind));
  const pool = kindMatches.length > 0 ? kindMatches : candidates;

  pool.sort(
    (a, b) =>
      Math.abs(a.difficulty - target) - Math.abs(b.difficulty - target) ||
      a.stem.length - b.stem.length,
  );

  return pool[0] ?? null;
}
