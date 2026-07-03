import type { LearningPlan } from '@asf/schemas/learning_path';

/** Days before goal/test when we surface exam-prep quiz prompts. */
export const EXAM_PREP_WINDOW_DAYS = 14;

function currentActiveWeek(plan: LearningPlan) {
  const active = plan.weeks.find((w) => w.status === 'active');
  if (active) return active;
  return plan.weeks.find((w) => w.status === 'upcoming') ?? plan.weeks[0];
}

export function resolveGoalTargetDate(
  nextTestDate?: string | null,
  finalGoalDate?: string | null,
): string | null {
  if (nextTestDate && finalGoalDate) {
    const testMs = new Date(nextTestDate).getTime();
    const goalMs = new Date(finalGoalDate).getTime();
    if (!Number.isNaN(testMs) && !Number.isNaN(goalMs)) {
      return testMs <= goalMs ? nextTestDate : finalGoalDate;
    }
  }
  return nextTestDate ?? finalGoalDate ?? null;
}

export function daysUntilIsoDate(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const target = new Date(iso);
  if (Number.isNaN(target.getTime())) return null;
  return Math.ceil((target.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
}

export function isWithinExamPrepWindow(daysLeft: number | null): boolean {
  return daysLeft != null && daysLeft > 0 && daysLeft <= EXAM_PREP_WINDOW_DAYS;
}

export function examPrepContext(
  plan: LearningPlan | null | undefined,
  nextTestDate?: string | null,
  finalGoalDate?: string | null,
): {
  show: boolean;
  daysLeft: number;
  targetDate: string;
  weekId?: string;
  weekNumber?: number;
  planId?: string;
} | null {
  const targetDate = resolveGoalTargetDate(nextTestDate, finalGoalDate);
  const daysLeft = daysUntilIsoDate(targetDate);
  if (!isWithinExamPrepWindow(daysLeft) || !targetDate || daysLeft == null) {
    return null;
  }

  const week = plan ? currentActiveWeek(plan) : undefined;
  return {
    show: true,
    daysLeft,
    targetDate,
    weekId: week?.id,
    weekNumber: week?.week_number,
    planId: plan?.id,
  };
}
