/**
 * POST /api/social/teacher-link/disconnect — student or teacher ends accepted link.
 */
import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import {
  disconnectTeacherStudent,
  getAcceptedTeacherForStudent,
} from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { student_id?: string; teacher_id?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    body = {};
  }

  // Student disconnecting self from their teacher
  if (!body.student_id || body.student_id === userId) {
    const teacher = await getAcceptedTeacherForStudent(userId);
    if (!teacher) return Response.json({ error: 'No teacher linked' }, { status: 404 });
    const r = await disconnectTeacherStudent({
      actorId: userId,
      teacherId: teacher.clerk_user_id,
      studentId: userId,
    });
    if (!r.ok) return Response.json({ error: r.error }, { status: 400 });
    return Response.json({ ok: true });
  }

  // Teacher disconnecting a student (same as educator student-action)
  if (body.student_id && (!body.teacher_id || body.teacher_id === userId)) {
    const r = await disconnectTeacherStudent({
      actorId: userId,
      teacherId: userId,
      studentId: body.student_id,
    });
    if (!r.ok) return Response.json({ error: r.error }, { status: 400 });
    return Response.json({ ok: true });
  }

  return Response.json({ error: 'Invalid request' }, { status: 400 });
}
