import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { getAuthContext } from '@/lib/auth';
import {
  dbConfigured,
  fetchLessonById,
  getLearnerProfile,
  type LessonPointsLevel,
} from '@/lib/neon-db';
import { getSeedLesson } from '@/lib/seed-lessons';
import { LessonPageClient } from '@/components/lesson-page-client';
import { LegacySeedLessonView } from '@/components/legacy-seed-lesson-view';

export const dynamic = 'force-dynamic';

async function resolveLearnerLevel(learnerId: string): Promise<LessonPointsLevel | null> {
  try {
    const profile = await getLearnerProfile(learnerId);
    const pg = profile?.points_group ?? null;
    if (pg) {
      const num = String(pg).replace(/pt$/i, '').trim();
      if (num === '3') return '3pt';
      if (num === '4') return '4pt';
      if (num === '5') return '5pt';
      if (pg === 'hs_physics') return 'hs_physics';
      if (pg === 'calc1') return 'calc1';
      if (pg === 'la') return 'la';
    } else if (profile?.goal) {
      const g = profile.goal.toLowerCase();
      if (g.includes('3')) return '3pt';
      if (g.includes('4')) return '4pt';
      if (g.includes('5')) return '5pt';
      if (g.includes('phys')) return 'hs_physics';
    }
  } catch {
    // Profile unavailable — render without level filtering.
  }
  return null;
}

export default async function LessonPage({
  params,
}: {
  params: Promise<{ lessonId: string }>;
}) {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const { lessonId } = await params;

  const [lessonData, learnerLevel] = await Promise.all([
    dbConfigured ? fetchLessonById(lessonId) : Promise.resolve(null),
    resolveLearnerLevel(auth.learnerId),
  ]);

  if (lessonData) {
    const { lesson } = lessonData;
    return (
      <div className="max-w-4xl">
        <Link
          href="/app/lessons"
          className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-primary"
        >
          <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
          Back to lessons
        </Link>
        <header className="mb-6">
          <h1 className="font-display text-3xl font-bold">{lesson.title_en}</h1>
          {lesson.title_he ? (
            <p className="mt-1 text-lg text-muted-foreground" dir="rtl">
              {lesson.title_he}
            </p>
          ) : null}
          <p className="mt-2 text-sm text-muted-foreground">
            {lesson.est_minutes} min · {lesson.subject}
          </p>
        </header>
        <LessonPageClient
          data={lessonData}
          conceptId={lesson.concept_id}
          learnerLevel={learnerLevel}
        />
      </div>
    );
  }

  const seed = getSeedLesson(lessonId);
  if (seed) {
    return <LegacySeedLessonView lesson={seed} />;
  }

  notFound();
}
