import { auth } from '@clerk/nextjs/server';
import { submitWeeklyQuizForUser } from '@/lib/weekly-quiz';

export const runtime = 'nodejs';

export async function POST(
  req: Request,
  { params }: { params: Promise<{ week_id: string }> },
) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  const { week_id: quizId } = await params;
  const body = (await req.json()) as {
    plan_id: string;
    week_num: number;
    answers: { item_id: string; chosen: string; time_spent_s: number | null }[];
    token?: string;
  };

  if (!body.plan_id || typeof body.week_num !== 'number') {
    return Response.json({ error: 'invalid_request' }, { status: 400 });
  }

  const result = await submitWeeklyQuizForUser(userId, quizId, {
    planId: body.plan_id,
    weekNum: body.week_num,
    answers: body.answers ?? [],
  });

  if (!result) {
    return Response.json({ error: 'quiz_not_found' }, { status: 404 });
  }

  return Response.json(result);
}
