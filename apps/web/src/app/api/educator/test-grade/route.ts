import { auth } from '@clerk/nextjs/server';
import { appendLearnerPersonaLine, dbConfigured } from '@/lib/neon-db';
import {
  assertTeacherOfStudent,
  createNotification,
  writeTeacherAudit,
} from '@/lib/social-db';
import { teacherUpdateTestAttempt } from '@/lib/test-attempts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: {
    student_id?: string;
    attempt_id?: string;
    feedback?: string;
    score?: number;
    passed?: boolean;
    reason?: string;
    reopen?: boolean;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  if (!body.student_id || !body.attempt_id) {
    return Response.json({ error: 'student_id and attempt_id required' }, { status: 400 });
  }
  const reason = (body.reason ?? body.feedback ?? '').trim();
  if (reason.length < 2) {
    return Response.json({ error: 'Reason/feedback required' }, { status: 400 });
  }

  const okLink = await assertTeacherOfStudent(userId, body.student_id);
  if (!okLink) return Response.json({ error: 'Forbidden' }, { status: 403 });

  const ok = await teacherUpdateTestAttempt({
    learnerId: body.student_id,
    attemptId: body.attempt_id,
    feedbackText: body.feedback ?? reason,
    score: typeof body.score === 'number' ? body.score : null,
    passed: typeof body.passed === 'boolean' ? body.passed : null,
    reopen: Boolean(body.reopen),
  });
  if (!ok) return Response.json({ error: 'Update failed' }, { status: 500 });

  await writeTeacherAudit({
    teacherId: userId,
    studentId: body.student_id,
    action: body.reopen ? 'test_reopen' : 'test_grade',
    reason,
    payload: {
      attempt_id: body.attempt_id,
      score: body.score ?? null,
      passed: body.passed ?? null,
      reopen: Boolean(body.reopen),
    },
  });

  await createNotification({
    userId: body.student_id,
    kind: body.reopen ? 'test_reopened' : 'test_checked',
    title: body.reopen ? 'המורה פתח מבחן מחדש' : 'המורה סיים לבדוק מבחן',
    body: reason.slice(0, 240),
    payload: { attempt_id: body.attempt_id, teacher_id: userId },
    href: `/app/tests/${body.attempt_id}`,
  });

  await appendLearnerPersonaLine(
    body.student_id,
    'תצפיות אחרונות',
    body.reopen
      ? `המורה פתח מבחן מחדש: ${reason.slice(0, 180)}`
      : `המורה בדק מבחן: ${reason.slice(0, 180)}`,
  ).catch(() => null);

  return Response.json({ ok: true });
}
