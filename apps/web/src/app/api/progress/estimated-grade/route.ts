import { auth } from '@clerk/nextjs/server';
import { getEstimatedBagrutScore, getLearnerProfile, type LearnerProfileRow } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function deriveSubjectFromProfile(profile: LearnerProfileRow | null): string {
  if (!profile) return 'math_5';

  const pg = profile.points_group;
  const subjects = profile.subjects ?? [];

  const hasPhysics =
    pg === 'hs_physics' ||
    subjects.includes('physics') ||
    subjects.includes('bagrut_physics');

  if (hasPhysics && (pg === 'hs_physics' || !pg || !/^(\d|3pt|4pt|5pt)$/.test(pg))) {
    return 'hs_physics';
  }

  const units = pg?.replace(/pt$/, '') ?? '';
  if (units === '3') return 'math_3';
  if (units === '4') return 'math_4';
  if (units === '5') return 'math_5';

  return 'math_5';
}

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = new URL(req.url);
  const subjectParam = url.searchParams.get('subject') ?? undefined;

  let subject = subjectParam;
  if (!subject) {
    const profile = await getLearnerProfile(userId).catch(() => null);
    subject = deriveSubjectFromProfile(profile);
  }

  const result = await getEstimatedBagrutScore(userId, subject);
  return Response.json({ ...result, subject });
}