/**
 * GET /api/quiz/weekly?plan_id=...&week_num=...
 */
import { auth } from '@clerk/nextjs/server';
import { getOrCreateWeeklyQuiz } from '@/lib/weekly-quiz';
import { getCurrentPlan } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const planId = url.searchParams.get('plan_id');
  const weekNumRaw = url.searchParams.get('week_num');
  const weekNum = weekNumRaw ? Number.parseInt(weekNumRaw, 10) : NaN;

  if (!planId || !Number.isFinite(weekNum) || weekNum < 1) {
    return Response.json({ error: 'plan_id and week_num are required' }, { status: 400 });
  }

  const plan = await getCurrentPlan(userId).catch(() => null);
  if (!plan || plan.id !== planId) {
    return Response.json({ error: 'plan_not_found' }, { status: 404 });
  }

  const week = plan.weeks.find((w) => w.week_number === weekNum);
  if (!week) {
    return Response.json({ error: 'week_not_found' }, { status: 404 });
  }

  const quiz = await getOrCreateWeeklyQuiz({
    learnerId: userId,
    planId,
    weekNum,
    weekId: week.id,
  });

  if (!quiz) {
    return Response.json(
      {
        error: 'quiz_generation_failed',
        message: 'Weekly quiz is temporarily unavailable. Please try again in a moment.',
      },
      { status: 503 },
    );
  }

  return Response.json(quiz);
}
