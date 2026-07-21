import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { assertTeacherOfStudent } from '@/lib/social-db';
import { getTestAttempt } from '@/lib/test-attempts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** Teacher reads a student's attempt with full keys + agent feedback (pre/post release). */
export async function GET(
  req: Request,
  { params }: { params: Promise<{ studentId: string; attemptId: string }> },
) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  const { studentId, attemptId } = await params;
  const ok = await assertTeacherOfStudent(userId, studentId);
  if (!ok) return Response.json({ error: 'Forbidden' }, { status: 403 });

  const attempt = await getTestAttempt(studentId, attemptId, { forEducator: true });
  if (!attempt) return Response.json({ error: 'not_found' }, { status: 404 });
  return Response.json({ attempt });
}
