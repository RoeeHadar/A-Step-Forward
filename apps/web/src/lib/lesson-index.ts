import lessonsIndex from './lessons-index.generated.json';

export interface LessonIndexEntry {
  id: string;
  subject?: string;
  concept_id?: string;
  title_en: string;
  title_he?: string;
  est_minutes: number;
  estimated_minutes?: number;
  math_track: string[];
}

const byConceptId = new Map<string, LessonIndexEntry>(
  (lessonsIndex as LessonIndexEntry[]).map((entry) => [entry.id, entry]),
);

/** Returns authored-lesson metadata from the static index (fallback when Neon is unavailable). */
export function getLessonIndexEntry(conceptId: string): LessonIndexEntry | undefined {
  return byConceptId.get(conceptId);
}

export function isConceptInLessonIndex(conceptId: string): boolean {
  return byConceptId.has(conceptId);
}
