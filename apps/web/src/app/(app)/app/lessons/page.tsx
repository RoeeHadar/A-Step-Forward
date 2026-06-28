/**
 * /app/lessons — curriculum category browser.
 *
 * Server component: fetches the learner's profile to determine their
 * curriculum track, then sorts categories so their own track comes first.
 * Rendering is delegated to `LessonsIndexClient` (client component) which
 * handles locale via `useI18n()`.
 */
import { LessonsIndexClient } from './_lessons-index-client';
import { getAuthContext } from '@/lib/auth';
import { getLearnerProfile, dbConfigured } from '@/lib/neon-db';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';
import type { PointsLevel } from '@/lib/curriculum-categories';

export const dynamic = 'force-dynamic';

export default async function LessonsIndexPage() {
  let pointsGroup: string | null = null;
  try {
    const auth = await getAuthContext();
    if (auth && dbConfigured) {
      const profile = await getLearnerProfile(auth.learnerId).catch(() => null);
      pointsGroup = profile?.points_group ?? null;
    }
  } catch {
    // Unauthenticated or DB unavailable — show all categories unsorted
  }

  // IDs of categories that match the learner's track
  const primaryCategoryIds: string[] = pointsGroup
    ? CURRICULUM_CATEGORIES.filter((cat) =>
        cat.points_levels.includes(pointsGroup as PointsLevel),
      ).map((cat) => cat.id)
    : [];

  // Primary track first, then everything else (preserving original order within each group)
  const sorted = [
    ...CURRICULUM_CATEGORIES.filter((cat) => primaryCategoryIds.includes(cat.id)),
    ...CURRICULUM_CATEGORIES.filter((cat) => !primaryCategoryIds.includes(cat.id)),
  ];

  return (
    <LessonsIndexClient categories={sorted} primaryCategoryIds={primaryCategoryIds} />
  );
}
