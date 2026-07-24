import { auth } from '@clerk/nextjs/server';
import {
  getEstimatedBagrutScore,
  getLearnerProfile,
  getConceptMastery,
  getSkillsPracticedCount,
} from '@/lib/neon-db';
import { deriveSubjectFromProfile } from '@/lib/learner-enrollment';
import { isBagrutTrack, daysUntilIso, resolveGoalDeadlineIso } from '@/lib/goal-track';
import { computeReadiness } from '@/lib/readiness';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const subjectParam = url.searchParams.get('subject') ?? undefined;

  const profile = await getLearnerProfile(userId).catch(() => null);
  const goalKey =
    (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ?? null;
  const isBagrut = isBagrutTrack({ goalKey, goal: profile?.goal });

  let subject = subjectParam;
  if (!subject) {
    subject = deriveSubjectFromProfile(profile);
  }

  if (!isBagrut) {
    const [mastery, skillsPracticedCount] = await Promise.all([
      getConceptMastery(userId).catch(() => ({} as Record<string, number>)),
      getSkillsPracticedCount(userId).catch(() => 0),
    ]);
    const scores = Object.values(mastery);
    const masteryAvg =
      scores.length > 0 ? scores.reduce((sum, s) => sum + s, 0) / scores.length : 0;
    const deadline = resolveGoalDeadlineIso(
      profile?.next_test_date,
      profile?.final_goal_date,
    );
    const daysToExam = daysUntilIso(deadline);
    const readiness = computeReadiness({
      goalKey,
      masteryScores: mastery,
      daysToExam,
      skillsPracticedCount,
    });
    const readinessPct =
      readiness != null ? Math.round(readiness.readiness * 100) : null;

    return Response.json({
      isBagrut: false,
      metric: 'goal_readiness',
      estimatedGrade: readinessPct ?? 0,
      readinessPct,
      masteryAvg,
      subject,
    });
  }

  const result = await getEstimatedBagrutScore(userId, subject);
  return Response.json({
    ...result,
    subject,
    isBagrut: true,
    metric: 'estimated_grade',
  });
}
