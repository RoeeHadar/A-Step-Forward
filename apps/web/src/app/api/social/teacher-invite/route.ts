/**
 * GET  — search learners (username / real name); includes plan summary for disambiguation
 * POST — send teacher invite
 */
import { auth } from '@clerk/nextjs/server';
import { dbConfigured, getCurrentPlan, getLearnerProfile } from '@/lib/neon-db';
import { getAppUser, searchLearnersForInvite, sendTeacherInvite } from '@/lib/social-db';
import { checkSocialRateLimit } from '@/lib/social-rate-limit';
import { currentActiveWeek } from '@/lib/learning-path-types';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  const me = await getAppUser(userId);
  if (!me || me.role !== 'educator') {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }
  const limited = checkSocialRateLimit(`teacher-search:${userId}`, {
    limit: 20,
    windowMs: 60_000,
  });
  if (!limited.ok) {
    return Response.json(
      { error: 'Too many searches. Try again shortly.', retry_after: limited.retryAfterSec },
      { status: 429, headers: { 'Retry-After': String(limited.retryAfterSec) } },
    );
  }
  const q = new URL(req.url).searchParams.get('q') ?? '';
  if (!dbConfigured) return Response.json({ results: [] });

  const users = await searchLearnersForInvite(q);
  const results = await Promise.all(
    users.map(async (u) => {
      const [profile, plan] = await Promise.all([
        getLearnerProfile(u.clerk_user_id).catch(() => null),
        getCurrentPlan(u.clerk_user_id).catch(() => null),
      ]);
      const week = plan ? currentActiveWeek(plan) : undefined;
      const concepts =
        week?.concepts.slice(0, 4).map((c) => c.name_he || c.name || c.concept_id) ?? [];
      const plan_summary =
        week && concepts.length > 0
          ? `Week ${week.week_number}: ${concepts.join(', ')}`
          : profile?.goal?.trim() || null;
      return {
        clerk_user_id: u.clerk_user_id,
        username: u.username,
        real_name: u.real_name,
        goal: profile?.goal ?? null,
        plan_summary,
      };
    }),
  );

  return Response.json({ results });
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) return Response.json({ error: 'DB unavailable' }, { status: 503 });

  let body: { student_id?: string; message?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  if (!body.student_id) {
    return Response.json({ error: 'student_id required' }, { status: 400 });
  }
  const result = await sendTeacherInvite({
    teacherId: userId,
    studentId: body.student_id,
    message: body.message,
  });
  if (!result.ok) return Response.json({ error: result.error }, { status: 400 });
  return Response.json(result);
}
