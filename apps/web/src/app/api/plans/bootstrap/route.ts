import { auth } from '@clerk/nextjs/server';
import {
  bootstrapOnboardingPlan,
  learnerHasPlan,
} from '@/lib/onboarding-plan-bootstrap';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 30;

/**
 * Lightweight plan create for /plan-setup — uses profile already in DB.
 * Avoids neon-db monolith (FUNCTION_INVOCATION_TIMEOUT root cause).
 */
export async function POST() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!(process.env.DATABASE_URL ?? process.env.POSTGRES_URL)) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  try {
    if (await learnerHasPlan(userId)) {
      return Response.json({ ok: true, has_plan: true, already: true });
    }

    // Minimal payload from existing profile row
    const { neon, neonConfig } = await import('@neondatabase/serverless');
    neonConfig.fetchConnectionCache = true;
    const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
    const s = neon(url);
    const rows = (await s`
      SELECT goal, grade_level, points_group, subjects, hours_per_week,
             preferred_style, attention_span, self_scores, background_notes,
             next_test_name, next_test_date, final_goal_date,
             mental_state, personality_profile
      FROM learner_profiles WHERE learner_id = ${userId} LIMIT 1
    `) as Array<Record<string, unknown>>;

    const profile = rows[0];
    if (!profile) {
      return Response.json(
        { error: 'Complete onboarding before creating a plan' },
        { status: 400 },
      );
    }

    const result = await bootstrapOnboardingPlan(userId, {
      goal: String(profile.goal ?? 'Learning plan'),
      grade_level: (profile.grade_level as string | null) ?? null,
      points_group: (profile.points_group as string | null) ?? null,
      subjects: (profile.subjects as string[]) ?? ['math'],
      hours_per_week: Number(profile.hours_per_week ?? 6),
      preferred_style: (profile.preferred_style as string | null) ?? null,
      attention_span: (profile.attention_span as number | null) ?? null,
      self_scores: (profile.self_scores as Record<string, number> | null) ?? {},
      background_notes: (profile.background_notes as string | null) ?? null,
      next_test_name: (profile.next_test_name as string | null) ?? null,
      next_test_date: (profile.next_test_date as string | null) ?? null,
      final_goal_date: (profile.final_goal_date as string | null) ?? null,
      mental_state: (profile.mental_state as Record<string, unknown> | null) ?? null,
      personality_profile:
        (profile.personality_profile as Record<string, unknown> | null) ?? null,
    });

    return Response.json({
      ok: true,
      has_plan: true,
      plan_id: result.plan_id,
      week_count: result.week_count,
    });
  } catch (err) {
    console.error('[plans/bootstrap]', err);
    return Response.json(
      { error: err instanceof Error ? err.message : 'Plan bootstrap failed' },
      { status: 500 },
    );
  }
}
