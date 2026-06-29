import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { WeekQuizClient } from '@/components/week-quiz-client';
import { QuizUnavailable } from '@/components/quiz-unavailable';
import { SiteHeader } from '@/components/site-header';
import { generateWeeklyQuizForUser } from '@/lib/weekly-quiz';
import type { QuizStartResponse } from '@asf/schemas/learning_path';

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

  // Primary path: generate/cache entirely within Neon + Vercel (no Render dependency).
  let quiz: QuizStartResponse | null = null;
  try {
    quiz = await generateWeeklyQuizForUser(userId, plan_id, weekNum);
  } catch {
    quiz = null;
  }

  // Obtain a token for the submit route (still proxied to Render for scoring,
  // but the start/generate step no longer depends on Render).
  const token = (await getToken()) ?? '';

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
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
      </main>
    </div>
  );
}
