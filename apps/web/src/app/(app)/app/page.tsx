import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import { DashboardContent } from '@/components/dashboard-content';
import type { NextLessonInfo } from '@/components/dashboard-content';
import { AgentsIntroBanner } from '@/components/agents-intro-banner';
import { LearningPlanDashboard } from '@/components/learning-plan-dashboard';
import { LearnerStreakCard } from '@/components/learner-streak-card';
import { ActivityHeatmap } from '@/components/activity-heatmap';
import { NoPlanEmptyState } from '@/components/no-plan-empty-state';
import { DueReviewsWidget } from '@/components/due-reviews-widget';
import { MicroWinToast } from '@/components/micro-win-toast';
import { getAuthContext } from '@/lib/auth';
import {
  getDashboardSnapshot,
  getLearnerProfile,
  getConceptMastery,
  getGoalCompletionStatus,
  getCurrentPlan,
  getLearnerStreak,
  getRecentActivity,
  getDailyActivity,
  getWeeklyRecap,
  dbConfigured,
  type DashboardSnapshot,
} from '@/lib/neon-db';
import { GoalCompletionBanner } from '@/components/goal-completion-banner';
import { CURRICULUM_CATEGORIES, conceptIdsForLevel } from '@/lib/curriculum-categories';
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

const EMPTY_STREAK = {
  current_days: 0,
  longest_days: 0,
  last_active: null,
  active_today: false,
  active_days_last_30: 0,
} as const;

const EMPTY_WEEKLY = {
  week_start: '',
  week_end: '',
  chat_turns: 0,
  concepts_touched: 0,
  atoms_practiced: 0,
  mastery_gain: 0,
  best_day: null,
} as const;

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
  const bioCat = CURRICULUM_CATEGORIES.find((c) => c.id === 'biology-4pt');
  if (bioCat?.concept_ids.includes(conceptId) || subjects?.includes('biology')) {
    return 'biology';
  }
  const physCat = CURRICULUM_CATEGORIES.find((c) => c.id === 'physics-hs');
  if (physCat?.concept_ids.includes(conceptId) || subjects?.includes('physics')) {
    return pointsGroup === 'hs_physics' ? 'hs_physics' : 'physics';
  }
  if (pointsGroup === '3pt') return 'high_school_math_3_points';
  if (pointsGroup === '4pt') return 'high_school_math_4_points';
  if (pointsGroup === '5pt') return 'high_school_math_5_points';
  return 'math';
}

const BIOLOGY_CONCEPT_PREFIXES = ['cell_', 'heredity_', 'natural_'] as const;

function hasStudiedBiology(mastery: Record<string, number>): boolean {
  const biologyIds = new Set(conceptIdsForLevel('biology_4pt'));
  return Object.keys(mastery).some(
    (id) =>
      biologyIds.has(id) ||
      BIOLOGY_CONCEPT_PREFIXES.some((prefix) => id.startsWith(prefix)),
  );
}

function computeNextLesson(
  mastery: Record<string, number>,
  pointsGroup: string | null,
  subjects?: string[] | null,
  personalityProfile?: Record<string, unknown> | null,
): NextLessonInfo | null {
  const index = lessonsIndex as LessonIndexEntry[];
  const indexById = new Map(index.map((l) => [l.id, l]));

  const hsBiology = personalityProfile?.hs_biology === true;

  if (hsBiology && !hasStudiedBiology(mastery)) {
    const cellEntry = indexById.get('cell_structure');
    if (cellEntry) {
      return {
        concept_id: 'cell_structure',
        lesson_id: 'cell_structure',
        subject: 'biology',
        title: cellEntry.title_en,
        title_he: cellEntry.title_he ?? cellEntry.title_en,
        est_minutes: cellEntry.est_minutes,
        reason: 'Recommended next',
      };
    }
  }

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
  if (hsBiology || subjects?.includes('biology')) {
    for (const id of conceptIdsForLevel('biology_4pt')) candidateSet.add(id);
  }
  const candidateIds =
    candidateSet.size > 0 ? [...candidateSet] : index.map((l) => l.id);

  const available = candidateIds.filter((id) => indexById.has(id));
  if (available.length === 0) return null;

  const withMastery = available
    .map((id) => ({ id, score: mastery[id] }))
    .filter((l): l is { id: string; score: number } => typeof l.score === 'number');

  const unstarted = available.filter((id) => mastery[id] === undefined);

  let chosen: { id: string; reason: string } | null = null;

  if (withMastery.length > 0) {
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

  const [
    snapshot,
    profile,
    mastery,
    goalStatus,
    plan,
    streak,
    activity,
    daily,
    weekly,
  ] = await Promise.all([
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
    dbConfigured
      ? getCurrentPlan(auth.learnerId).catch(() => null)
      : Promise.resolve(null),
    dbConfigured
      ? getLearnerStreak(auth.learnerId).catch(() => ({ ...EMPTY_STREAK }))
      : Promise.resolve({ ...EMPTY_STREAK }),
    dbConfigured
      ? getRecentActivity(auth.learnerId, 8).catch(() => [])
      : Promise.resolve([]),
    dbConfigured
      ? getDailyActivity(auth.learnerId, 30).catch(() => [])
      : Promise.resolve([]),
    dbConfigured
      ? getWeeklyRecap(auth.learnerId).catch(() => ({ ...EMPTY_WEEKLY }))
      : Promise.resolve({ ...EMPTY_WEEKLY }),
  ]);

  const nextLesson = computeNextLesson(
    mastery,
    profile?.points_group ?? null,
    profile?.subjects ?? null,
    profile?.personality_profile ?? null,
  );

  return (
    <>
      {goalStatus ? <GoalCompletionBanner status={goalStatus} /> : null}
      <AgentsIntroBanner />
      <Suspense fallback={null}>
        <MicroWinToast />
      </Suspense>
      <div className="mb-8 space-y-6">
        <LearnerStreakCard streak={streak} activity={activity} />
        <DueReviewsWidget />
        <ActivityHeatmap daily={daily} weekly={weekly} />
        {!plan ? <NoPlanEmptyState /> : <LearningPlanDashboard plan={plan} />}
      </div>
      <DashboardContent
        displayName={auth.displayName}
        snapshot={snapshot}
        nextTestName={profile?.next_test_name ?? null}
        nextTestDate={profile?.next_test_date ?? null}
        nextLesson={nextLesson}
        streak={streak}
      />
    </>
  );
}
