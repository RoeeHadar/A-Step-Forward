/**
 * GET /api/practice/history — list finished/active practice sessions for the learner.
 * GET ?session_id= — one session (learner-owned).
 */
import { auth } from '@clerk/nextjs/server';
import {
  getPracticeSessionForLearner,
  listPracticeSessionsForLearner,
  toPracticeSessionPublic,
} from '@/lib/practice-session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const sessionId = url.searchParams.get('session_id');
  if (sessionId) {
    const row = await getPracticeSessionForLearner(userId, sessionId);
    if (!row) return Response.json({ error: 'not_found' }, { status: 404 });
    return Response.json({ session: toPracticeSessionPublic(row) });
  }

  const rows = await listPracticeSessionsForLearner(userId, 40);
  return Response.json({
    sessions: rows.map((r) => ({
      session_id: r.id,
      status: r.status,
      topic_ids: r.topic_ids,
      attempted: r.attempted,
      correct_count: r.correct_count,
      created_at: r.created_at,
      ended_at: r.ended_at,
      summary: r.summary,
    })),
  });
}
