/**
 * Goal-track helpers — profile goal fields are the source of truth for labels
 * and bagrut vs non-bagrut framing (plan-train alignment).
 */

const BAGRUT_GOAL_KEYS = new Set([
  'bagrut_math_5',
  'bagrut_math_4',
  'bagrut_math_3',
  'bagrut_physics',
  'bagrut_math',
]);

export function isBagrutGoalKey(goalKey: string | null | undefined): boolean {
  if (!goalKey) return false;
  return BAGRUT_GOAL_KEYS.has(goalKey) || goalKey.startsWith('bagrut_');
}

/** Heuristic when goal_key is missing — goal text mentions bagrut / יח״ל. */
export function isBagrutGoalText(goal: string | null | undefined): boolean {
  if (!goal) return false;
  return /בגרות|bagrut|יח["״]?ל|5\s*pt|4\s*pt|3\s*pt/i.test(goal);
}

export function isBagrutTrack(opts: {
  goalKey?: string | null;
  goal?: string | null;
}): boolean {
  if (isBagrutGoalKey(opts.goalKey)) return true;
  if (opts.goalKey) return false;
  return isBagrutGoalText(opts.goal);
}

export function resolveGoalDeadlineIso(
  nextTestDate: string | null | undefined,
  finalGoalDate: string | null | undefined,
): string | null {
  const next = nextTestDate?.slice(0, 10) || null;
  const final = finalGoalDate?.slice(0, 10) || null;
  if (final && next) return final >= next ? final : next;
  return final ?? next;
}

export function daysUntilIso(
  isoDate: string | null | undefined,
  now: Date = new Date(),
): number | null {
  if (!isoDate) return null;
  const target = new Date(isoDate.slice(0, 10) + 'T12:00:00');
  if (Number.isNaN(target.getTime())) return null;
  const start = new Date(now);
  start.setHours(12, 0, 0, 0);
  return Math.ceil((target.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}

export function goalCountdownLabel(
  locale: 'he' | 'en',
  daysLeft: number,
  opts: { isBagrut: boolean },
): string {
  const bagrut = opts.isBagrut;
  if (daysLeft <= 0) {
    if (locale === 'he') return bagrut ? 'הבגרות היום!' : 'יום היעד!';
    return bagrut ? 'Exam day!' : 'Goal day!';
  }
  if (locale === 'he') {
    if (bagrut) return `${daysLeft} ימים עד הבגרות`;
    return `${daysLeft} ימים עד היעד`;
  }
  if (bagrut) return `${daysLeft} days until exam`;
  return `${daysLeft} days until your goal`;
}

export function readinessTitle(
  locale: 'he' | 'en',
  opts: { isBagrut: boolean },
): string {
  if (locale === 'he') return opts.isBagrut ? 'מוכנות לבגרות' : 'מוכנות ליעד';
  return opts.isBagrut ? 'Bagrut readiness' : 'Goal readiness';
}
