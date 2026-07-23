/**
 * POST /api/practice/next — advance only after the current item was submitted/given up.
 */
import { auth } from '@clerk/nextjs/server';
import { advancePracticeItem } from '@/lib/practice-queue';
import {
  getPracticeSessionForLearner,
  markPracticeFingerprintSeen,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';

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
  if (!sessionId) {
    return Response.json({ error: 'session_id required' }, { status: 400 });
  }

  const session = await getPracticeSessionForLearner(userId, sessionId);
  if (!session) {
    return Response.json({ error: 'session_not_found' }, { status: 404 });
  }
  if (session.status === 'ended') {
    return Response.json({
      session: toPracticeSessionPublic(session),
      ended: true,
    });
  }
  if (session.current_item && !session.current_graded) {
    return Response.json(
      { error: 'submit_required', message: 'Submit or give up before loading the next item.' },
      { status: 409 },
    );
  }

  const advanced = await advancePracticeItem({
    learnerId: userId,
    conceptFilter: session.concept_filter,
    topicIds: session.topic_ids,
    queueMode: session.queue_mode,
    seenIds: session.seen_ids,
    recentCorrect: session.recent_correct,
    generatedCount: session.generated_count,
    previousDifficulty: session.current_item?.difficulty,
  });

  if (!advanced || 'thin_topic' in advanced) {
    const ended = await updatePracticeSession(
      userId,
      sessionId,
      { status: 'ended', current_graded: true },
      session.version,
    );
    return Response.json({
      error: 'thin_topic',
      message: 'No more unused exam-style items for these topics right now.',
      session: ended ? toPracticeSessionPublic(ended) : toPracticeSessionPublic(session),
      ended: true,
    });
  }

  const seen = [...session.seen_ids];
  if (advanced.item.question_id) seen.push(advanced.item.question_id);
  seen.push(advanced.item.id);

  await markPracticeFingerprintSeen({
    learnerId: userId,
    fingerprint: advanced.item.fingerprint,
    conceptId: advanced.item.concept_id,
  });

  const updated = await updatePracticeSession(
    userId,
    sessionId,
    {
      current_item: advanced.item,
      hint_step: 0,
      current_graded: false,
      focus_concept_id: advanced.focusConceptId,
      seen_ids: seen,
      generated_count:
        advanced.item.source === 'generated'
          ? session.generated_count + 1
          : session.generated_count,
    },
    session.version,
  );
  if (!updated) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  return Response.json({
    session: toPracticeSessionPublic(updated),
    ended: false,
  });
}
