/**
 * Server-side queue + item sourcing for the practice arena (ADR-0013).
 */
import 'server-only';
import {
  buildHintLadder,
  isPracticeClosedKind,
  nextDifficulty,
  PRACTICE_MAX_GENERATED_PER_SESSION,
  type PracticeDifficulty,
  type PracticeItemSealed,
} from '@/lib/practice-arena';
import { pickPressureNextStep } from '@/lib/pressure-next-step';
import {
  fetchLessonByConceptId,
  getConceptMastery,
  getCurrentPlan,
  getDueReviews,
  getLearnerProfile,
  type LessonQuestionRow,
} from '@/lib/neon-db';
import { buildPracticeDrillItem } from '@/lib/practice-drill-builder';
import kg from '@/lib/kg-data.json';

type KgConcept = {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
};

const kgById = Object.fromEntries(
  (kg.concepts as KgConcept[]).map((c) => [c.id, c]),
);

function conceptLabel(id: string): { en: string; he: string } {
  const c = kgById[id];
  return {
    en: c?.name || id,
    he: c?.name_he || c?.name || id,
  };
}

function newItemId(): string {
  return (
    globalThis.crypto?.randomUUID() ||
    `pr_${Date.now()}_${Math.random().toString(36).slice(2)}`
  );
}

function authoredToSealed(
  q: LessonQuestionRow,
  conceptId: string,
  lessonId: string,
): PracticeItemSealed | null {
  if (!isPracticeClosedKind(q.kind)) return null;
  const labels = conceptLabel(conceptId);
  const payload = q.answer_payload as PracticeItemSealed['answer_payload'];
  return {
    id: newItemId(),
    source: 'authored',
    lesson_id: lessonId,
    question_id: q.id,
    kind: q.kind,
    difficulty: q.difficulty,
    concept_id: conceptId,
    skill_atoms: Array.isArray(q.skill_atoms) ? q.skill_atoms : [],
    stem_en: q.stem_en,
    stem_he: q.stem_he,
    options_en: q.options_en,
    options_he: q.options_he,
    correct_index: q.correct_index,
    correct_answer: q.correct_answer,
    answer_payload: payload
      ? {
          correct_bool: (payload as { correct_bool?: boolean }).correct_bool,
          acceptable_answers: (payload as { acceptable_answers?: string[] })
            .acceptable_answers,
          case_sensitive: (payload as { case_sensitive?: boolean }).case_sensitive,
        }
      : null,
    explanation_en: q.explanation_en || '',
    explanation_he: q.explanation_he || '',
    hints: buildHintLadder({
      conceptLabelEn: labels.en,
      conceptLabelHe: labels.he,
      skillAtoms: q.skill_atoms ?? [],
      explanationEn: q.explanation_en,
      explanationHe: q.explanation_he,
    }),
  };
}

export async function pickPracticeFocusConcept(opts: {
  learnerId: string;
  conceptFilter?: string | null;
  queueMode?: 'default' | 'due';
}): Promise<string | null> {
  if (opts.conceptFilter && kgById[opts.conceptFilter]) {
    return opts.conceptFilter;
  }

  if (opts.queueMode === 'due') {
    const due = await getDueReviews(opts.learnerId).catch(() => []);
    const dueConcept = due.find((d) => d.concept_id && kgById[d.concept_id]);
    if (dueConcept) return dueConcept.concept_id;
  }

  const [profile, mastery, plan] = await Promise.all([
    getLearnerProfile(opts.learnerId).catch(() => null),
    getConceptMastery(opts.learnerId).catch(() => ({}) as Record<string, number>),
    getCurrentPlan(opts.learnerId).catch(() => null),
  ]);

  const masteryMap = mastery as Record<string, number>;
  const activeWeek =
    plan?.weeks.find((w) => w.status === 'active') ?? plan?.weeks[0];

  if (activeWeek?.concepts?.length) {
    const pick = pickPressureNextStep({
      activeWeekConcepts: activeWeek.concepts.map((c) => ({
        conceptId: c.concept_id,
        nameHe: c.name_he,
        nameEn: c.name,
        mastery: masteryMap[c.concept_id] ?? null,
      })),
    });
    if (pick) return pick.conceptId;
  }

  // Weakest measured concepts, then subject bootstrap from KG.
  const weak = Object.entries(masteryMap)
    .filter(([, s]) => typeof s === 'number')
    .sort((a, b) => a[1] - b[1])[0];
  if (weak) return weak[0];

  const subjects = profile?.subjects ?? [];
  const roots = (kg.concepts as KgConcept[]).filter(
    (c) => subjects.length === 0 || subjects.includes(c.subject),
  );
  return roots[0]?.id ?? (kg.concepts as KgConcept[])[0]?.id ?? null;
}

async function pickAuthoredItem(opts: {
  conceptId: string;
  seenIds: string[];
  difficulty: PracticeDifficulty;
}): Promise<PracticeItemSealed | null> {
  const lesson = await fetchLessonByConceptId(opts.conceptId).catch(() => null);
  if (!lesson?.questions?.length) return null;

  const closed = lesson.questions.filter(
    (q) =>
      isPracticeClosedKind(q.kind) &&
      !opts.seenIds.includes(q.id) &&
      q.stem_en &&
      q.stem_he,
  );
  if (!closed.length) return null;

  const prefer = closed.filter((q) => q.difficulty === opts.difficulty);
  const pool = prefer.length ? prefer : closed;
  const q = pool[Math.floor(Math.random() * pool.length)]!;
  return authoredToSealed(q, opts.conceptId, lesson.lesson.id);
}

async function pickGeneratedItem(opts: {
  conceptId: string;
  generatedCount: number;
  difficulty: PracticeDifficulty;
}): Promise<PracticeItemSealed | null> {
  if (opts.generatedCount >= PRACTICE_MAX_GENERATED_PER_SESSION) return null;
  return buildPracticeDrillItem({
    conceptId: opts.conceptId,
    difficulty: opts.difficulty,
    count: 1,
  });
}

export async function advancePracticeItem(opts: {
  learnerId: string;
  conceptFilter?: string | null;
  queueMode?: 'default' | 'due';
  seenIds: string[];
  recentCorrect: boolean[];
  generatedCount: number;
  previousDifficulty?: PracticeDifficulty;
}): Promise<{ item: PracticeItemSealed; focusConceptId: string } | null> {
  const focusConceptId = await pickPracticeFocusConcept({
    learnerId: opts.learnerId,
    conceptFilter: opts.conceptFilter,
    queueMode: opts.queueMode,
  });
  if (!focusConceptId) return null;

  const difficulty = nextDifficulty(
    opts.recentCorrect,
    opts.previousDifficulty ?? 'medium',
  );

  const authored = await pickAuthoredItem({
    conceptId: focusConceptId,
    seenIds: opts.seenIds,
    difficulty,
  });
  if (authored) return { item: authored, focusConceptId };

  const generated = await pickGeneratedItem({
    conceptId: focusConceptId,
    generatedCount: opts.generatedCount,
    difficulty,
  });
  if (generated) return { item: generated, focusConceptId };

  // Last resort: allow re-use of authored (ignore seen) so the arena never hard-stops.
  const lesson = await fetchLessonByConceptId(focusConceptId).catch(() => null);
  const any = lesson?.questions.find((q) => isPracticeClosedKind(q.kind));
  if (any && lesson) {
    const sealed = authoredToSealed(any, focusConceptId, lesson.lesson.id);
    if (sealed) return { item: sealed, focusConceptId };
  }
  return null;
}
