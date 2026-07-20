import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import {
  addTeacherNote,
  assertTeacherOfStudent,
  disconnectTeacherStudent,
  writeTeacherAudit,
} from '@/lib/social-db';
import { appendLearnerPersonaLine } from '@/lib/neon-db';
import { createNotification } from '@/lib/social-db';
import { applyPlanFromTeacher } from '@/lib/teacher-plan';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: {
    action?: string;
    student_id?: string;
    content?: string;
    kind?: 'note' | 'concern';
    reason?: string;
    plan?: Record<string, unknown>;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const studentId = body.student_id;
  if (!studentId) return Response.json({ error: 'student_id required' }, { status: 400 });

  const linked = await assertTeacherOfStudent(userId, studentId);
  if (!linked) return Response.json({ error: 'Forbidden' }, { status: 403 });

  if (body.action === 'disconnect') {
    const r = await disconnectTeacherStudent({
      actorId: userId,
      teacherId: userId,
      studentId,
    });
    if (!r.ok) return Response.json({ error: r.error }, { status: 400 });
    return Response.json({ ok: true });
  }

  if (body.action === 'note') {
    const id = await addTeacherNote({
      teacherId: userId,
      studentId,
      content: body.content ?? '',
      kind: body.kind ?? 'note',
    });
    if (!id) return Response.json({ error: 'Failed' }, { status: 500 });
    if (body.kind === 'concern') {
      await appendLearnerPersonaLine(
        studentId,
        'תצפיות אחרונות',
        `המורה סימן חשש: ${(body.content ?? '').slice(0, 200)}`,
      ).catch(() => null);
    }
    return Response.json({ ok: true, id });
  }

  if (body.action === 'plan') {
    const reason = (body.reason ?? '').trim();
    if (reason.length < 3) {
      return Response.json({ error: 'Reason required' }, { status: 400 });
    }
    const result = await applyPlanFromTeacher({
      teacherId: userId,
      studentId,
      reason,
      plan: body.plan ?? {},
    });
    if (!result.ok) return Response.json({ error: result.error }, { status: 400 });
    await writeTeacherAudit({
      teacherId: userId,
      studentId,
      action: 'plan_update',
      reason,
      payload: body.plan ?? {},
    });
    await createNotification({
      userId: studentId,
      kind: 'teacher_plan_changed',
      title: 'המורה עדכן את תוכנית הלימודים',
      body: reason.slice(0, 240),
      payload: { teacher_id: userId },
      href: '/app/plan',
    });
    return Response.json({ ok: true });
  }

  return Response.json({ error: 'Unknown action' }, { status: 400 });
}
