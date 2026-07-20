/**
 * Cron: notify teachers + students when an active weekly gate is overdue.
 *
 * GET/POST /api/cron/weekly-gate-due?limit=100
 * Auth: x-cron-secret or Authorization Bearer matching CRON_SECRET.
 */
import { dbConfigured, getCurrentPlan } from '@/lib/neon-db';
import {
  listAcceptedTeacherStudentPairs,
  maybeNotifyWeeklyGateDue,
} from '@/lib/social-db';
import { currentActiveWeek } from '@/lib/learning-path-types';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const DEFAULT_LIMIT = 100;
const MAX_LIMIT = 300;

function authorized(req: Request): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const header =
    req.headers.get('x-cron-secret') ??
    (req.headers.get('authorization') ?? '').replace(/^Bearer\s+/i, '');
  return header === secret;
}

async function handle(req: Request) {
  if (!authorized(req)) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'db_unavailable' }, { status: 503 });
  }

  const url = new URL(req.url);
  const limit = Math.max(
    1,
    Math.min(MAX_LIMIT, Number(url.searchParams.get('limit') ?? DEFAULT_LIMIT)),
  );

  const pairs = await listAcceptedTeacherStudentPairs(limit);
  let checked = 0;
  let notified = 0;
  const errors: string[] = [];

  for (const pair of pairs) {
    checked += 1;
    try {
      const plan = await getCurrentPlan(pair.student_id);
      const week = plan ? currentActiveWeek(plan) : undefined;
      if (!week?.quiz_due_at || week.status !== 'active') continue;
      const dueMs = new Date(week.quiz_due_at).getTime();
      if (Number.isNaN(dueMs) || Date.now() < dueMs) continue;

      await maybeNotifyWeeklyGateDue({
        learnerId: pair.student_id,
        weekId: week.id,
        weekNumber: week.week_number,
        quizDueAt: week.quiz_due_at,
      });
      notified += 1;
    } catch (err) {
      errors.push(`${pair.student_id}:${err instanceof Error ? err.message : 'error'}`);
    }
  }

  return Response.json({
    pairs: pairs.length,
    checked,
    notified,
    errors: errors.slice(0, 20),
  });
}

export async function GET(req: Request) {
  return handle(req);
}

export async function POST(req: Request) {
  return handle(req);
}
