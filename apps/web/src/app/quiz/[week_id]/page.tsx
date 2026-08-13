import { auth } from '@clerk/nextjs/server';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { WeekQuizClient } from '@/components/week-quiz-client';
import { QuizUnavailable } from '@/components/quiz-unavailable';
import { generateWeeklyQuizForUser } from '@/lib/weekly-quiz';
import type { QuizStartResponse } from '@asf/schemas/learning_path';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ week_id: string }>;
  searchParams: Promise<{ plan_id?: string; week_num?: string }>;
}

export default async function QuizPage({ params, searchParams }: Props) {
  const { userId, getToken } = await auth();
  if (!userId) redirect('/sign-in');

  await params; // week_id is in the URL for routing only
  const { plan_id, week_num } = await searchParams;

  if (!plan_id || !week_num) {
    redirect('/dashboard');
  }

  const weekNum = Number(week_num);
  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);

  // Primary path: generate/cache entirely within Neon + Vercel (no Render dependency).
  let quiz: QuizStartResponse | null = null;
  try {
    quiz = await generateWeeklyQuizForUser(userId, plan_id, weekNum, locale);
  } catch {
    quiz = null;
  }

  // Obtain a token for the submit route (still proxied to Render for scoring,
  // but the start/generate step no longer depends on Render).
  const token = (await getToken()) ?? '';

  return (
    <div className="bg-background">
      <div className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
        {quiz ? (
          <WeekQuizClient
            quiz={quiz}
            planId={plan_id}
            weekNum={weekNum}
            token={token}
          />
        ) : (
          <QuizUnavailable />
        )}
      </div>
    </div>
  );
}
