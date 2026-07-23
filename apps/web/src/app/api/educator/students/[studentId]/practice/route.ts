/**
 * GET /api/educator/students/[studentId]/practice — list practice sessions for a linked student.
 */
import { auth } from '@clerk/nextjs/server';
import { assertTeacherOfStudent } from '@/lib/social-db';
import { listPracticeSessionsForLearner } from '@/lib/practice-session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ studentId: string }> },
) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { studentId } = await ctx.params;
  const ok = await assertTeacherOfStudent(userId, studentId).catch(() => false);
  if (!ok) return Response.json({ error: 'Forbidden' }, { status: 403 });

  const rows = await listPracticeSessionsForLearner(studentId, 40);
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
