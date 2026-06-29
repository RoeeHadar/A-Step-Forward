/**
 * POST /api/lessons/complete
 *
 * Records baseline mastery when a learner marks a lesson as read/complete.
 */
import { auth } from '@clerk/nextjs/server';
import { markLessonComplete } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  let body: { concept_id?: string; lesson_id?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const conceptId = body.concept_id?.trim();
  if (!conceptId) {
    return Response.json({ error: 'concept_id is required' }, { status: 400 });
  }

  try {
    const newMastery = await markLessonComplete(userId, conceptId);
    return Response.json({ success: true, new_mastery: newMastery });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    return Response.json({ error: message }, { status: 500 });
  }
}
