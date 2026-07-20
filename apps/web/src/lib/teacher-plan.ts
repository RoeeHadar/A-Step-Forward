/**
 * Teacher-driven plan tweaks for a linked student.
 */
import 'server-only';
import {
  appendLearnerPersonaLine,
  applyPlanProfileUpdates,
  generateLearningPlan,
  getLearnerProfile,
} from '@/lib/neon-db';
import { getAppUser } from '@/lib/social-db';

export async function applyPlanFromTeacher(input: {
  teacherId: string;
  studentId: string;
  reason: string;
  plan: Record<string, unknown>;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  try {
    const teacher = await getAppUser(input.teacherId);
    const profile = await getLearnerProfile(input.studentId);
    if (!profile) return { ok: false, error: 'Student has no learning profile yet.' };

    const goal =
      typeof input.plan.goal === 'string' && input.plan.goal.trim()
        ? input.plan.goal.trim()
        : undefined;
    const hours =
      typeof input.plan.hours_per_week === 'number' && input.plan.hours_per_week > 0
        ? input.plan.hours_per_week
        : undefined;
    const nextTestName =
      typeof input.plan.next_test_name === 'string' ? input.plan.next_test_name : undefined;
    const nextTestDate =
      typeof input.plan.next_test_date === 'string' ? input.plan.next_test_date : undefined;
    const priority =
      Array.isArray(input.plan.priority_concepts)
        ? (input.plan.priority_concepts as unknown[]).filter(
            (x): x is string => typeof x === 'string',
          )
        : undefined;

    await applyPlanProfileUpdates(input.studentId, {
      goal,
      hours_per_week: hours,
      next_test_name: nextTestName,
      next_test_date: nextTestDate,
      goal_key: typeof input.plan.goal_key === 'string' ? input.plan.goal_key : undefined,
    });

    await generateLearningPlan(input.studentId, {
      goalOverride: goal,
      priorityConcepts: priority,
      planChangeReason: `teacher:${input.reason}`,
      fastPath: true,
    });

    const teacherLabel = teacher?.real_name ?? 'Teacher';
    await appendLearnerPersonaLine(
      input.studentId,
      'תצפיות אחרונות',
      `המורה ${teacherLabel} עדכן/ה את התוכנית: ${input.reason.slice(0, 180)}`,
    );

    return { ok: true };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : 'Plan update failed',
    };
  }
}
