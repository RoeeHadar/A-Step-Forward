import { notFound, redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { dbConfigured, fetchLessonById } from '@/lib/neon-db';
import { getSeedLesson } from '@/lib/seed-lessons';
import { LegacySeedLessonView } from '@/components/legacy-seed-lesson-view';

export const dynamic = 'force-dynamic';

export default async function LessonPage({
  params,
}: {
  params: Promise<{ lessonId: string }>;
}) {
  const { userId } = await auth();
  if (!userId) redirect('/learn');

  const { lessonId } = await params;

  const lessonData = dbConfigured ? await fetchLessonById(lessonId) : null;

  if (lessonData) {
    const { lesson } = lessonData;
    redirect(`/learn/${lesson.subject}/concept/${lesson.concept_id}`);
  }
  const seed = getSeedLesson(lessonId);
  if (seed) {
    return <LegacySeedLessonView lesson={seed} />;
  }

  notFound();
}
