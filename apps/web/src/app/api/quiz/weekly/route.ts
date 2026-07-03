/**
 * GET /api/quiz/weekly?plan_id=...&week_num=...
 *
 * Generates (or returns a cached) weekly quiz for the authenticated learner
 * entirely within the Next.js / Neon path — no Render cold-start involved.
 * Target latency: <3 s (Groq p50 ≈ 1.5 s for quiz generation).
 */
import { auth } from '@clerk/nextjs/server';
import { cookies } from 'next/headers';
import { generateWeeklyQuizForUser } from '@/lib/weekly-quiz';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const planId = url.searchParams.get('plan_id') ?? '';
  const weekNumRaw = url.searchParams.get('week_num');
  const weekNum = weekNumRaw ? Number.parseInt(weekNumRaw, 10) : NaN;

  if (!planId || !Number.isFinite(weekNum) || weekNum < 1) {
    return Response.json(
      { error: 'plan_id and a valid week_num are required' },
      { status: 400 },
    );
  }

  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);
  const quiz = await generateWeeklyQuizForUser(userId, planId, weekNum, locale);

  if (!quiz) {
    return Response.json(
      {
        error: 'quiz_generation_failed',
        message:
          'Weekly quiz is temporarily unavailable. Please try again in a moment.',
      },
      { status: 503 },
    );
  }

  return Response.json(quiz);
}
