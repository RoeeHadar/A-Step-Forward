/**
 * Server-side queue + item sourcing for the practice arena (ADR-0013 v2).
 */
import 'server-only';
import {
  buildHintLadder,
  isPracticeArenaKind,
  isPracticeExamWorthyItem,
  isPracticeOpenKind,
  nextDifficulty,
  practiceExamWorthinessScore,
  practiceItemFingerprint,
  PRACTICE_MAX_GENERATED_PER_SESSION,
  stemLooksVagueOrMeta,
  type PracticeDifficulty,
  type PracticeItemSealed,
  type PracticeQueueMode,
} from '@/lib/practice-arena';
import { conceptIdsForTopics } from '@/lib/practice-topics';
import {
  fetchLessonByConceptId,
  getConceptMastery,
  getLearnerProfile,
  type LessonQuestionRow,
} from '@/lib/neon-db';
import { buildPracticeDrillItem } from '@/lib/practice-drill-builder';
import {
  isPracticeFingerprintSeen,
  listPracticeFingerprintsSeen,
} from '@/lib/practice-session';
import { listRecentTestSourceQuestionIds } from '@/lib/practice-test-overlap';
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
  if (!isPracticeArenaKind(q.kind)) return null;
  // Prefer open / constructed; skip MCQ/TF for v2 default bank use.
  if (q.kind === 'mcq' || q.kind === 'true_false') return null;
  const labels = conceptLabel(conceptId);
  const payload = q.answer_payload as PracticeItemSealed['answer_payload'];
  const fingerprint = practiceItemFingerprint({
    conceptId,
    stemEn: q.stem_en,
    stemHe: q.stem_he,
    questionId: q.id,
  });
  return {
    id: newItemId(),
    source: 'authored',
    lesson_id: lessonId,
    question_id: q.id,
    fingerprint,
    kind: q.kind === 'fill_blank' ? 'short_answer' : (q.kind as PracticeItemSealed['kind']),
    difficulty: q.difficulty,
    concept_id: conceptId,
    skill_atoms: Array.isArray(q.skill_atoms) ? q.skill_atoms : [],
    stem_en: q.stem_en,
    stem_he: q.stem_he,
    options_en: null,
    options_he: null,
    correct_index: null,
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
    rubric_en: q.explanation_en || '',
    rubric_he: q.explanation_he || '',
    model_answer_en: q.explanation_en || q.correct_answer || '',
    model_answer_he: q.explanation_he || q.correct_answer || '',
    points_available: isPracticeOpenKind(q.kind) ? 20 : 5,
    hints: buildHintLadder({
      conceptLabelEn: labels.en,
      conceptLabelHe: labels.he,
      skillAtoms: q.skill_atoms ?? [],
    }),
  };
}

export async function pickPracticeFocusConcept(opts: {
  learnerId: string;
  conceptFilter?: string | null;
  topicIds?: string[];
  queueMode?: PracticeQueueMode;
}): Promise<string | null> {
  if (opts.conceptFilter && kgById[opts.conceptFilter]) {
    return opts.conceptFilter;
  }

  const topicConcepts = conceptIdsForTopics(opts.topicIds ?? []).filter((id) => kgById[id]);
  if (topicConcepts.length) {
    const mastery = (await getConceptMastery(opts.learnerId).catch(
      () => ({}),
    )) as Record<string, number>;
    const ranked = [...topicConcepts].sort((a, b) => {
      const ma = typeof mastery[a] === 'number' ? mastery[a]! : 0.5;
      const mb = typeof mastery[b] === 'number' ? mastery[b]! : 0.5;
      return ma - mb;
    });
    return ranked[Math.floor(Math.random() * Math.min(3, ranked.length))] ?? ranked[0]!;
  }

  const [profile, mastery] = await Promise.all([
    getLearnerProfile(opts.learnerId).catch(() => null),
    getConceptMastery(opts.learnerId).catch(() => ({}) as Record<string, number>),
  ]);
  const masteryMap = mastery as Record<string, number>;
  const weak = Object.entries(masteryMap)
    .filter(([, s]) => typeof s === 'number')
    .sort((a, b) => a[1] - b[1])[0];
  if (weak && kgById[weak[0]]) return weak[0];

  const subjects = profile?.subjects ?? [];
  const roots = (kg.concepts as KgConcept[]).filter(
    (c) => subjects.length === 0 || subjects.includes(c.subject),
  );
  return roots[0]?.id ?? (kg.concepts as KgConcept[])[0]?.id ?? null;
}

async function pickAuthoredItem(opts: {
  learnerId: string;
  conceptId: string;
  seenIds: string[];
  seenFingerprints: Set<string>;
  difficulty: PracticeDifficulty;
  recentTestQuestionIds: Set<string>;
}): Promise<PracticeItemSealed | null> {
  const lesson = await fetchLessonByConceptId(opts.conceptId).catch(() => null);
  if (!lesson?.questions?.length) return null;

  const candidates = lesson.questions.filter((q) => {
    if (!isPracticeArenaKind(q.kind)) return false;
    if (q.kind === 'mcq' || q.kind === 'true_false') return false;
    if (opts.seenIds.includes(q.id)) return false;
    if (opts.recentTestQuestionIds.has(q.id)) return false;
    if (!q.stem_en || !q.stem_he) return false;
    if (
      !isPracticeExamWorthyItem({
        stemEn: q.stem_en,
        stemHe: q.stem_he,
        explanationEn: q.explanation_en,
        explanationHe: q.explanation_he,
        questionId: q.id,
      })
    ) {
      return false;
    }
    if (stemLooksVagueOrMeta(q.stem_en) || stemLooksVagueOrMeta(q.stem_he)) return false;
    const fp = practiceItemFingerprint({
      conceptId: opts.conceptId,
      stemEn: q.stem_en,
      stemHe: q.stem_he,
      questionId: q.id,
    });
    if (opts.seenFingerprints.has(fp)) return false;
    return true;
  });
  if (!candidates.length) return null;

  const scored = candidates
    .map((q) => ({
      q,
      score:
        practiceExamWorthinessScore(q.stem_he || q.stem_en, q.kind) +
        (q.difficulty === opts.difficulty ? 2 : 0),
    }))
    .sort((a, b) => b.score - a.score);

  const topScore = scored[0]!.score;
  const elite = scored.filter((s) => s.score >= topScore - 2);
  const preferOpen = elite.filter((s) => s.q.kind === 'open' || s.q.kind === 'derivation');
  const pool = preferOpen.length ? preferOpen : elite;
  const pick = pool[Math.floor(Math.random() * pool.length)]!.q;
  return authoredToSealed(pick, opts.conceptId, lesson.lesson.id);
}

async function pickGeneratedItem(opts: {
  learnerId: string;
  conceptId: string;
  generatedCount: number;
  difficulty: PracticeDifficulty;
  seenFingerprints: Set<string>;
}): Promise<PracticeItemSealed | null> {
  if (opts.generatedCount >= PRACTICE_MAX_GENERATED_PER_SESSION) return null;
  for (let attempt = 0; attempt < 3; attempt++) {
    const item = await buildPracticeDrillItem({
      conceptId: opts.conceptId,
      difficulty: opts.difficulty,
      learnerId: opts.learnerId,
      count: 1,
    });
    if (!item) continue;
    if (opts.seenFingerprints.has(item.fingerprint)) continue;
    const already = await isPracticeFingerprintSeen(opts.learnerId, item.fingerprint);
    if (already) continue;
    return item;
  }
  return null;
}

export async function advancePracticeItem(opts: {
  learnerId: string;
  conceptFilter?: string | null;
  topicIds?: string[];
  queueMode?: PracticeQueueMode;
  seenIds: string[];
  recentCorrect: boolean[];
  generatedCount: number;
  previousDifficulty?: PracticeDifficulty;
}): Promise<
  | { item: PracticeItemSealed; focusConceptId: string }
  | { thin_topic: true; focusConceptId: string | null }
  | null
> {
  const seenFingerprints = await listPracticeFingerprintsSeen(opts.learnerId);
  const recentTestQuestionIds = await listRecentTestSourceQuestionIds(opts.learnerId);
  const focusConceptId = await pickPracticeFocusConcept({
    learnerId: opts.learnerId,
    conceptFilter: opts.conceptFilter,
    topicIds: opts.topicIds,
    queueMode: opts.queueMode,
  });
  if (!focusConceptId) return { thin_topic: true, focusConceptId: null };

  const difficulty = nextDifficulty(
    opts.recentCorrect,
    opts.previousDifficulty ?? 'medium',
  );

  const topicPool = conceptIdsForTopics(opts.topicIds ?? []);
  const tryConcepts = [
    focusConceptId,
    ...topicPool.filter((id) => id !== focusConceptId).slice(0, 4),
  ];

  for (const conceptId of tryConcepts) {
    const authored = await pickAuthoredItem({
      learnerId: opts.learnerId,
      conceptId,
      seenIds: opts.seenIds,
      seenFingerprints,
      difficulty,
      recentTestQuestionIds,
    });
    if (authored) return { item: authored, focusConceptId: conceptId };

    const generated = await pickGeneratedItem({
      learnerId: opts.learnerId,
      conceptId,
      generatedCount: opts.generatedCount,
      difficulty,
      seenFingerprints,
    });
    if (generated) return { item: generated, focusConceptId: conceptId };
  }

  return { thin_topic: true, focusConceptId };
}
