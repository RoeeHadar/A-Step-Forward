/**
 * Teacher override → learning-plan gate sync (ADR-0010 + sealed release).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { advanceRollingPlanWindow } from '@/lib/neon-db';
import { logger } from '@/lib/logger';

neonConfig.fetchConnectionCache = true;
const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

/**
 * After a teacher changes pass/fail/reopen on a weekly_gate attempt, sync plan week.
 * - pass: complete active week + advance window
 * - fail / reopen: reopen completed week matching this plan/week if present
 */
export async function syncGateAfterTeacherOverride(input: {
  learnerId: string;
  attemptId: string;
  kind: string;
  planId: string | null;
  weekNum: number | null;
  passed: boolean | null;
  reopen: boolean;
}): Promise<{ advanced: boolean; revoked: boolean }> {
  if (!sql) return { advanced: false, revoked: false };
  if (input.kind !== 'weekly_gate' || !input.planId || input.weekNum == null) {
    return { advanced: false, revoked: false };
  }

  try {
    if (input.reopen || input.passed === false) {
      const updated = (await sql`
        UPDATE plan_weeks pw
        SET status = 'active'
        FROM learning_plans lp
        WHERE pw.plan_id = lp.id
          AND lp.id = ${input.planId}::uuid
          AND lp.learner_id = ${input.learnerId}
          AND pw.week_number = ${input.weekNum}
          AND pw.status = 'completed'
        RETURNING pw.id
      `) as Array<{ id: string }>;
      return { advanced: false, revoked: updated.length > 0 };
    }

    if (input.passed === true) {
      const updated = (await sql`
        UPDATE plan_weeks pw
        SET status = 'completed'
        FROM learning_plans lp
        WHERE pw.plan_id = lp.id
          AND lp.id = ${input.planId}::uuid
          AND lp.learner_id = ${input.learnerId}
          AND pw.week_number = ${input.weekNum}
          AND pw.status = 'active'
        RETURNING pw.id
      `) as Array<{ id: string }>;
      if (updated.length > 0) {
        const rolled = await advanceRollingPlanWindow(input.learnerId).catch(() => ({
          advanced: false,
        }));
        return { advanced: Boolean(rolled.advanced), revoked: false };
      }
    }
  } catch (err) {
    logger.error('[teacher-gate-sync] failed', {
      attempt_id: input.attemptId,
      err: String(err),
    });
  }
  return { advanced: false, revoked: false };
}
