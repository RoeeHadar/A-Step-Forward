/**
 * POST /api/practice/submit — grade current item (open → process grader); mastery/XP.
 */
import { auth } from '@clerk/nextjs/server';
import { cookies } from 'next/headers';
import {
  gradePracticeItem,
  isPracticeOpenKind,
  practiceSuccessFromProcess,
  practiceXpSourceId,
  type PracticeAttemptLogEntry,
} from '@/lib/practice-arena';
import {
  getPracticeSessionForLearner,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';
import { recordCustomQuizPractice, recordLessonAnswer } from '@/lib/neon-db';
import { awardXp } from '@/lib/learner-xp';
import { XP_REWARDS } from '@/lib/learner-xp-math';
import { gradeOpenItemProcess } from '@/lib/process-grader';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';
import kg from '@/lib/kg-data.json';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

type KgConcept = { id: string; subject: string };

const kgById = Object.fromEntries(
  (kg.concepts as KgConcept[]).map((c) => [c.id, c]),
);

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const sessionId = typeof body.session_id === 'string' ? body.session_id : '';
  const itemId = typeof body.item_id === 'string' ? body.item_id : '';
  if (!sessionId || !itemId) {
    return Response.json({ error: 'session_id and item_id required' }, { status: 400 });
  }

  const session = await getPracticeSessionForLearner(userId, sessionId);
  if (!session || session.status !== 'active' || !session.current_item) {
    return Response.json({ error: 'session_not_found' }, { status: 404 });
  }
  if (session.current_item.id !== itemId) {
    return Response.json({ error: 'item_mismatch' }, { status: 409 });
  }
  if (session.current_graded) {
    return Response.json({ error: 'already_submitted' }, { status: 409 });
  }

  const item = session.current_item;
  const gaveUp = body.give_up === true;
  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);

  let correct = false;
  let processScore: number | null = null;
  let processFeedback: Awaited<ReturnType<typeof gradeOpenItemProcess>> | null = null;
  let gradingUnavailable = false;

  if (gaveUp) {
    correct = false;
    processScore = 0;
  } else if (isPracticeOpenKind(item.kind)) {
    const answerText = typeof body.answer === 'string' ? body.answer : '';
    processFeedback = await gradeOpenItemProcess({
      item_id: item.id,
      stem: locale === 'he' ? item.stem_he : item.stem_en,
      response: answerText,
      rubric: locale === 'he' ? item.rubric_he : item.rubric_en,
      model_answer: locale === 'he' ? item.model_answer_he : item.model_answer_en,
      concept_id: item.concept_id,
      subject: kgById[item.concept_id]?.subject ?? null,
      skill_atoms: item.skill_atoms,
      points_available: item.points_available ?? 20,
      locale,
    });
    if (processFeedback.status === 'failed') {
      // Soft-fail: still unlock solution so the learner can continue.
      gradingUnavailable = true;
      processScore = 0;
      correct = false;
      processFeedback = {
        ...processFeedback,
        status: 'graded',
        strengths:
          locale === 'he'
            ? 'הבדיקה האוטומטית לא הייתה זמינה כרגע.'
            : 'Automatic grading was temporarily unavailable.',
        next_fix:
          locale === 'he'
            ? 'השוו לפתרון המודל למטה והמשיכו לשאלה הבאה.'
            : 'Compare with the model solution below, then continue.',
        process_score: 0,
        points_earned: 0,
      };
    } else {
      processScore = processFeedback.process_score;
      correct = practiceSuccessFromProcess(processScore);
    }
  } else {
    const graded = gradePracticeItem(item, body.answer);
    correct = graded.correct;
    processScore = correct ? 1 : 0;
  }

  try {
    if (item.source === 'authored' && item.lesson_id && item.question_id) {
      await recordLessonAnswer({
        learnerId: userId,
        lessonId: item.lesson_id,
        questionId: item.question_id,
        conceptId: item.concept_id,
        correct,
        skillAtoms: item.skill_atoms,
      });
    } else {
      await recordCustomQuizPractice({
        learnerId: userId,
        conceptId: item.concept_id,
        correct,
        skillAtoms: item.skill_atoms,
      });
    }
  } catch (err) {
    // Mastery must not block feedback / progression.
    console.warn('[practice/submit] mastery update failed (continuing)', err);
  }

  if (correct) {
    void awardXp({
      learnerId: userId,
      amount: XP_REWARDS.correct_answer,
      reason: 'correct_answer',
      sourceId: practiceXpSourceId(sessionId, itemId),
    }).catch(() => undefined);
  }

  const logEntry: PracticeAttemptLogEntry = {
    item_id: item.id,
    concept_id: item.concept_id,
    kind: item.kind,
    difficulty: item.difficulty,
    correct,
    process_score: processScore,
    gave_up: gaveUp,
    stem_en: item.stem_en.slice(0, 240),
    stem_he: item.stem_he.slice(0, 240),
  };

  const recent = [...session.recent_correct, correct].slice(-8);
  const attempted = session.attempted + 1;
  const correctCount = session.correct_count + (correct ? 1 : 0);
  const attempt_log = [...session.attempt_log, logEntry];

  const feedback = {
    correct,
    gave_up: gaveUp,
    grading_unavailable: gradingUnavailable,
    process_score: processScore,
    process: processFeedback
      ? {
          strengths: processFeedback.strengths,
          steps_present: processFeedback.steps_present,
          steps_skipped: processFeedback.steps_skipped,
          logic: processFeedback.logic,
          next_fix: processFeedback.next_fix,
          points_earned: processFeedback.points_earned,
          points_available: processFeedback.points_available,
        }
      : null,
    explanation_en: item.explanation_en || item.model_answer_en || '',
    explanation_he: item.explanation_he || item.model_answer_he || '',
    correct_answer:
      item.kind === 'numeric' || item.kind === 'short_answer' || item.kind === 'fill_blank'
        ? item.correct_answer
        : undefined,
  };

  const nextSession = await updatePracticeSession(
    userId,
    sessionId,
    {
      attempted,
      correct_count: correctCount,
      recent_correct: recent,
      attempt_log,
      hint_step: 3,
      current_graded: true,
      status: 'active',
    },
    session.version,
  );
  if (!nextSession) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  return Response.json({
    feedback,
    session: toPracticeSessionPublic(nextSession),
    goal_reached: attempted >= session.goal_items,
  });
}
