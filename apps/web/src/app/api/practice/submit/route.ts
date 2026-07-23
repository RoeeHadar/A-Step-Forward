/**
 * POST /api/practice/submit — grade current item; reveal explanation; update mastery/XP.
 */
import { auth } from '@clerk/nextjs/server';
import { gradePracticeItem, practiceXpSourceId } from '@/lib/practice-arena';
import {
  getPracticeSessionForLearner,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';
import { recordCustomQuizPractice, recordLessonAnswer } from '@/lib/neon-db';
import { awardXp } from '@/lib/learner-xp';
import { XP_REWARDS } from '@/lib/learner-xp-math';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

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
  const graded = gradePracticeItem(item, body.answer);
  const gaveUp = body.give_up === true;
  const correct = gaveUp ? false : graded.correct;

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
    console.warn('[practice/submit] mastery update failed', err);
    return Response.json({ error: 'mastery_update_failed' }, { status: 503 });
  }

  if (correct) {
    void awardXp({
      learnerId: userId,
      amount: XP_REWARDS.correct_answer,
      reason: 'correct_answer',
      sourceId: practiceXpSourceId(sessionId, itemId),
    }).catch(() => undefined);
  }

  const recent = [...session.recent_correct, correct].slice(-8);
  const attempted = session.attempted + 1;
  const correctCount = session.correct_count + (correct ? 1 : 0);

  const feedback = {
    correct,
    gave_up: gaveUp,
    explanation_en: item.explanation_en,
    explanation_he: item.explanation_he,
    correct_index: item.kind === 'mcq' ? item.correct_index : undefined,
    correct_answer:
      item.kind === 'numeric' || item.kind === 'short_answer' || item.kind === 'fill_blank'
        ? item.correct_answer
        : undefined,
    correct_bool: item.kind === 'true_false' ? item.answer_payload?.correct_bool : undefined,
  };

  const hitGoal = attempted >= session.goal_items;
  const nextSession = await updatePracticeSession(
    userId,
    sessionId,
    {
      attempted,
      correct_count: correctCount,
      recent_correct: recent,
      hint_step: 3,
      current_graded: true,
      status: hitGoal ? 'ended' : 'active',
    },
    session.version,
  );
  if (!nextSession) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  return Response.json({
    feedback,
    session: toPracticeSessionPublic(nextSession),
    goal_reached: hitGoal,
  });
}
