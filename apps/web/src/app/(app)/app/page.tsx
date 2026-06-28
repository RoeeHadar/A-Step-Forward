import { redirect } from 'next/navigation';
import { DashboardContent } from '@/components/dashboard-content';
import type { NextLessonInfo } from '@/components/dashboard-content';
import { getAuthContext } from '@/lib/auth';
import {
  getDashboardSnapshot,
  getLearnerProfile,
  getConceptMastery,
  dbConfigured,
  type DashboardSnapshot,
} from '@/lib/neon-db';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';
import type { PointsLevel } from '@/lib/curriculum-categories';
import lessonsIndex from '@/lib/lessons-index.generated.json';

export const dynamic = 'force-dynamic';

interface LessonIndexEntry {
  id: string;
  title_en: string;
  title_he?: string;
  est_minutes: number;
  math_track: string[];
}

function emptySnapshot(): DashboardSnapshot {
  return {
    stats: { streak_days: 0, lessons_completed: 0, level: 1 },
    recent_lessons: [],
    mastery_summary: [],
  };
}

function computeNextLesson(
  mastery: Record<string, number>,
  pointsGroup: string | null,
): NextLessonInfo | null {
  const index = lessonsIndex as LessonIndexEntry[];
  const indexById = new Map(index.map((l) => [l.id, l]));

  // Determine candidate concept IDs from learner's track
  let candidateIds: string[];
  if (pointsGroup) {
    const cat = CURRICULUM_CATEGORIES.find((c) =>
      c.points_levels.includes(pointsGroup as PointsLevel),
    );
    candidateIds = cat?.concept_ids ?? index.map((l) => l.id);
  } else {
    candidateIds = index.map((l) => l.id);
  }

  // Keep only concept IDs that have an authored lesson
  const available = candidateIds.filter((id) => indexById.has(id));
  if (available.length === 0) return null;

  const withMastery = available
    .map((id) => ({ id, score: mastery[id] }))
    .filter((l): l is { id: string; score: number } => typeof l.score === 'number');

  const unstarted = available.filter((id) => mastery[id] === undefined);

  let chosen: { id: string; reason: string } | null = null;

  if (withMastery.length > 0) {
    // Weakest concept = lowest mastery score
    const weakest = withMastery.reduce((a, b) => (a.score <= b.score ? a : b));
    chosen = {
      id: weakest.id,
      reason: weakest.score >= 0.7 ? 'Continue learning plan' : 'Weakest topic',
    };
  } else if (unstarted.length > 0) {
    chosen = { id: unstarted[0]!, reason: 'Recommended next' };
  }

  if (!chosen) return null;

  const entry = indexById.get(chosen.id)!;
  return {
    concept_id: chosen.id,
    lesson_id: chosen.id,
    title: entry.title_en,
    title_he: entry.title_he ?? entry.title_en,
    est_minutes: entry.est_minutes,
    reason: chosen.reason,
  };
}

export default async function DashboardPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const [snapshot, profile, mastery] = await Promise.all([
    dbConfigured
      ? getDashboardSnapshot(auth.learnerId).catch(emptySnapshot)
      : Promise.resolve(emptySnapshot()),
    dbConfigured
      ? getLearnerProfile(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getConceptMastery(auth.learnerId).catch(() => ({}))
      : Promise.resolve({}),
  ]);

  const nextLesson = computeNextLesson(mastery, profile?.points_group ?? null);

  return (
    <DashboardContent
      displayName={auth.displayName}
      snapshot={snapshot}
      nextTestName={profile?.next_test_name ?? null}
      nextTestDate={profile?.next_test_date ?? null}
      nextLesson={nextLesson}
    />
  );
}
