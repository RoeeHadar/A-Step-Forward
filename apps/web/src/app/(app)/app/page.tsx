import { redirect } from 'next/navigation';
import { DashboardContent } from '@/components/dashboard-content';
import type { NextLessonInfo } from '@/components/dashboard-content';
import { getAuthContext } from '@/lib/auth';
import {
  getDashboardSnapshot,
  getLearnerProfile,
  getConceptMastery,
  getGoalCompletionStatus,
  dbConfigured,
  type DashboardSnapshot,
} from '@/lib/neon-db';
import { GoalCompletionBanner } from '@/components/goal-completion-banner';
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

function learnSubjectSlug(
  conceptId: string,
  pointsGroup: string | null,
  subjects?: string[] | null,
): string {
  const physCat = CURRICULUM_CATEGORIES.find((c) => c.id === 'physics-hs');
  if (physCat?.concept_ids.includes(conceptId) || subjects?.includes('physics')) {
    return pointsGroup === 'hs_physics' ? 'hs_physics' : 'physics';
  }
  if (pointsGroup === '3pt') return 'high_school_math_3_points';
  if (pointsGroup === '4pt') return 'high_school_math_4_points';
  if (pointsGroup === '5pt') return 'high_school_math_5_points';
  return 'math';
}

function computeNextLesson(
  mastery: Record<string, number>,
  pointsGroup: string | null,
  subjects?: string[] | null,
): NextLessonInfo | null {
  const index = lessonsIndex as LessonIndexEntry[];
  const indexById = new Map(index.map((l) => [l.id, l]));

  // Determine candidate concept IDs from math units and/or enrolled subjects
  const candidateSet = new Set<string>();
  if (pointsGroup) {
    const cat = CURRICULUM_CATEGORIES.find((c) =>
      c.points_levels.includes(pointsGroup as PointsLevel),
    );
    for (const id of cat?.concept_ids ?? []) candidateSet.add(id);
  }
  if (subjects?.includes('physics')) {
    const physCat = CURRICULUM_CATEGORIES.find((c) =>
      c.points_levels.includes('hs_physics'),
    );
    for (const id of physCat?.concept_ids ?? []) candidateSet.add(id);
  }
  const candidateIds =
    candidateSet.size > 0 ? [...candidateSet] : index.map((l) => l.id);

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
    subject: learnSubjectSlug(chosen.id, pointsGroup, subjects),
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

  const [snapshot, profile, mastery, goalStatus] = await Promise.all([
    dbConfigured
      ? getDashboardSnapshot(auth.learnerId).catch(emptySnapshot)
      : Promise.resolve(emptySnapshot()),
    dbConfigured
      ? getLearnerProfile(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getConceptMastery(auth.learnerId).catch(() => ({}))
      : Promise.resolve({}),
    dbConfigured
      ? getGoalCompletionStatus(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
  ]);

  const nextLesson = computeNextLesson(
    mastery,
    profile?.points_group ?? null,
    profile?.subjects ?? null,
  );

  return (
    <>
      {goalStatus ? <GoalCompletionBanner status={goalStatus} /> : null}
      <DashboardContent
        displayName={auth.displayName}
        snapshot={snapshot}
        nextTestName={profile?.next_test_name ?? null}
        nextTestDate={profile?.next_test_date ?? null}
        nextLesson={nextLesson}
      />
    </>
  );
}
