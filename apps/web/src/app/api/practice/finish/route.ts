/**
 * POST /api/practice/finish — end session and return summary.
 */
import { auth } from '@clerk/nextjs/server';
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
    return Response.json({ session: toPracticeSessionPublic(session) });
  }

  const updated = await updatePracticeSession(
    userId,
    sessionId,
    { status: 'ended' },
    session.version,
  );
  if (!updated) {
    return Response.json({ error: 'session_conflict' }, { status: 409 });
  }

  return Response.json({ session: toPracticeSessionPublic(updated) });
}
