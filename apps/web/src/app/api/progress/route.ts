import { auth } from '@clerk/nextjs/server';
import { getAuthContext } from '@/lib/auth';
import { dbConfigured, getProgressFromNeon } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** Live progress from Neon — same source as `/app/progress`. */
export async function GET() {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  if (!dbConfigured) {
    return Response.json({
      learner_id: ctx.learnerId,
      streak_days: 0,
      total_minutes: 0,
      lessons_completed: 0,
      concepts: [],
    });
  }

  const snap = await getProgressFromNeon(ctx.learnerId);
  return Response.json({
    learner_id: ctx.learnerId,
    streak_days: snap.streak.current_days,
    total_minutes: snap.total_minutes,
    lessons_completed: snap.lessons_completed,
    concepts: snap.concepts.map((c) => ({
      concept_id: c.concept_id,
      concept_name: c.concept_name,
      current_score: c.current_score,
      history: c.history,
    })),
  });
}
