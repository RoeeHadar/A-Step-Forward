import { auth } from '@clerk/nextjs/server';
import { getEstimatedBagrutScore, getLearnerProfile } from '@/lib/neon-db';
import { deriveSubjectFromProfile } from '@/lib/learner-enrollment';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

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