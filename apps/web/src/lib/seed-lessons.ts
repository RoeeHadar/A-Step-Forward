/**
 * Offline snapshot of the `foundations-of-math` seed course.
 *
 * Used as a guaranteed-available fallback on the public `/lessons/<id>` route
 * so the live demo keeps rendering content even when `NEXT_PUBLIC_API_BASE_URL`
 * is unreachable. Regenerate via `scripts/export_seed_lessons.py`.
 */
import snapshot from './seed-lessons.generated.json';
import type { Lesson } from '@asf/schemas/curriculum';

type SeedLesson = Lesson & {
  course_id: string;
  course_title: string;
  unit_id: string;
  unit_title: string;
};

interface SeedSnapshot {
  course: {
    id: string;
    title: string;
    level: string;
    summary: string;
    units: {
      id: string;
      title: string;
      summary: string;
      lesson_ids: string[];
    }[];
  };
  lessons: SeedLesson[];
}

const data = snapshot as unknown as SeedSnapshot;

export const seedCourse = data.course;
export const seedLessons: SeedLesson[] = data.lessons;

const lessonById = new Map<string, SeedLesson>(
  data.lessons.map((lesson) => [lesson.id, lesson]),
);

export function getSeedLesson(lessonId: string): SeedLesson | null {
  return lessonById.get(lessonId) ?? null;
}

export function listSeedLessonIds(): string[] {
  return data.lessons.map((lesson) => lesson.id);
}
