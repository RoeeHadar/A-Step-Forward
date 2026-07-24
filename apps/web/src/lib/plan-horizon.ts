import { ROLLING_VISIBLE_WEEKS } from './plan-worklist';

export function clipMaterializedWeeks(opts: {
  daysToGoal: number | null;
  requestedWeeks: number;
  rollingDefault?: number;
}): number {
  const rolling = opts.rollingDefault ?? ROLLING_VISIBLE_WEEKS;
  const n = Math.max(1, opts.requestedWeeks);
  if (opts.daysToGoal == null) return Math.min(n, rolling);
  if (opts.daysToGoal <= 14) return 1;
  if (opts.daysToGoal <= 21) return Math.min(n, 2);
  return Math.min(n, rolling);
}

export function clipHorizonWeeks(opts: {
  daysToGoal: number | null;
  horizonWeeks: number;
}): number {
  if (opts.daysToGoal == null) return opts.horizonWeeks;
  const fromDays = Math.max(1, Math.ceil(opts.daysToGoal / 7));
  return Math.min(opts.horizonWeeks, fromDays);
}

export function weekStartsAfterGoal(
  weekIndex0: number,
  planStartIso: string,
  goalDeadlineIso: string,
): boolean {
  const start = new Date(planStartIso.slice(0, 10) + 'T12:00:00');
  const goal = new Date(goalDeadlineIso.slice(0, 10) + 'T12:00:00');
  const weekStart = new Date(start);
  weekStart.setDate(weekStart.getDate() + 7 * weekIndex0);
  return weekStart.getTime() > goal.getTime();
}

export function filterWeekGroupsBeforeGoal<T>(
  weekGroups: T[][],
  planStartIso: string,
  goalDeadlineIso: string | null,
): T[][] {
  if (!goalDeadlineIso) return weekGroups;
  return weekGroups.filter(
    (_, i) => !weekStartsAfterGoal(i, planStartIso, goalDeadlineIso),
  );
}
