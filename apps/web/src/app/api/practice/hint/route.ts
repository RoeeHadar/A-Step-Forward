/**
 * POST /api/practice/hint — unlock next hint ladder step (never the final answer).
 */
import { auth } from '@clerk/nextjs/server';
import {
  getPracticeSessionForLearner,
  toPracticeSessionPublic,
  updatePracticeSession,
} from '@/lib/practice-session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 30;

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
  if (!session || session.status !== 'active' || !session.current_item) {
    return Response.json({ error: 'session_not_found' }, { status: 404 });
  }
  if (session.current_graded) {
    return Response.json({ error: 'already_submitted' }, { status: 409 });
  }

  const nextStep = Math.min(3, session.hint_step + 1);
  if (nextStep === session.hint_step) {
    return Response.json({
      session: toPracticeSessionPublic(session),
      hint: session.current_item.hints[Math.max(0, nextStep - 1)],
    });
  }

  const updated = await updatePracticeSession(
    userId,
    sessionId,
    {
      hint_step: nextStep,
      hints_used: session.hints_used + 1,
    },
    session.version,
  );
  if (!updated) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  return Response.json({
    session: toPracticeSessionPublic(updated),
    hint: updated.current_item?.hints[nextStep - 1] ?? null,
  });
}
