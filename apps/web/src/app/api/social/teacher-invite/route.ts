import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { getAppUser, searchLearnersForInvite, sendTeacherInvite } from '@/lib/social-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  const me = await getAppUser(userId);
  if (!me || me.role !== 'educator') {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }
  const q = new URL(req.url).searchParams.get('q') ?? '';
  const results = dbConfigured ? await searchLearnersForInvite(q) : [];
  return Response.json({ results });
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { student_id?: string; message?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  if (!body.student_id) {
    return Response.json({ error: 'student_id required' }, { status: 400 });
  }
  const result = await sendTeacherInvite({
    teacherId: userId,
    studentId: body.student_id,
    message: body.message,
  });
  if (!result.ok) return Response.json({ error: result.error }, { status: 400 });
  return Response.json(result);
}
