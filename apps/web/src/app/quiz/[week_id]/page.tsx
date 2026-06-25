import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { WeekQuizClient } from '@/components/week-quiz-client';
import { SiteHeader } from '@/components/site-header';
import { API_BASE_URL } from '@/lib/api';
import type { QuizStartResponse } from '@asf/schemas/learning_path';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ week_id: string }>;
  searchParams: Promise<{ plan_id?: string; week_num?: string }>;
}

async function fetchQuiz(
  token: string,
  planId: string,
  weekNum: number,
): Promise<QuizStartResponse | null> {
  try {
    const res = await fetch(
      `${API_BASE_URL}/v1/learners/me/plans/${planId}/weeks/${weekNum}/quiz`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      },
    );
    if (!res.ok) return null;
    return res.json() as Promise<QuizStartResponse>;
  } catch {
    return null;
  }
}

export default async function QuizPage({ params, searchParams }: Props) {
  const { userId, getToken } = await auth();
  if (!userId) redirect('/sign-in');

  const { week_id } = await params;
  const { plan_id, week_num } = await searchParams;

  if (!plan_id || !week_num) {
    redirect('/dashboard');
  }

  const token = await getToken();
  if (!token) redirect('/sign-in');

  const quiz = await fetchQuiz(token, plan_id, Number(week_num));

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
        {quiz ? (
          <WeekQuizClient
            quiz={quiz}
            planId={plan_id}
            weekNum={Number(week_num)}
            token={token}
          />
        ) : (
          <div className="glass-surface rounded-2xl p-8 text-center">
            <h1 className="font-display text-2xl font-bold">Quiz unavailable</h1>
            <p className="mt-2 text-muted-foreground">
              Unable to load the quiz. Please try again from your dashboard.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
