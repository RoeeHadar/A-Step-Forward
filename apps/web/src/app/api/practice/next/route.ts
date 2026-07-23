/**
 * POST /api/practice/next — continue after feedback (or skip to next without grading).
 * Prefer submit with give_up for honest mastery; this loads another item when session still active.
 */
import { auth } from '@clerk/nextjs/server';
import { advancePracticeItem } from '@/lib/practice-queue';
import {
  getPracticeSessionForLearner,
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

  const advanced = await advancePracticeItem({
    learnerId: userId,
    conceptFilter: session.concept_filter,
    seenIds: session.seen_ids,
    recentCorrect: session.recent_correct,
    generatedCount: session.generated_count,
    previousDifficulty: session.current_item?.difficulty,
  });
  if (!advanced) {
    return Response.json({ error: 'no_items' }, { status: 503 });
  }

  const seen = [...session.seen_ids];
  if (advanced.item.question_id) seen.push(advanced.item.question_id);
  seen.push(advanced.item.id);

  const updated = await updatePracticeSession(userId, sessionId, {
    current_item: advanced.item,
    hint_step: 0,
    focus_concept_id: advanced.focusConceptId,
    seen_ids: seen,
    generated_count:
      advanced.item.source === 'generated'
        ? session.generated_count + 1
        : session.generated_count,
  });

  return Response.json({
    session: toPracticeSessionPublic(updated ?? session),
    ended: false,
  });
}
