import { cookies } from 'next/headers';
import { LegacySeedLessonClient } from '@/components/legacy-seed-lesson-client';
import { getLessonIndexEntry } from '@/lib/lesson-index';
import type { Lesson } from '@asf/schemas/curriculum';

/** Renders legacy OpenStax seed lessons that are not yet in Neon. */
export async function LegacySeedLessonView({ lesson }: { lesson: Lesson }) {
  const cookieStore = await cookies();
  const locale = cookieStore.get('asf-locale')?.value === 'en' ? 'en' : 'he';
  const indexEntry = getLessonIndexEntry(lesson.id);

  return (
    <LegacySeedLessonClient
      lesson={lesson}
      locale={locale}
      sectionCount={1}
      levelMin={indexEntry && 'level_min' in indexEntry ? String((indexEntry as { level_min?: string }).level_min ?? '') : null}
      mathTrack={indexEntry?.math_track}
    />
  );
}
