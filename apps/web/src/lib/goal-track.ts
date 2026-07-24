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

/**
 * Optional quotes between חדו and א — ASCII, curly, and Hebrew geresh/gershayim
 * (U+05F3 ׳ / U+05F4 ״). Templates often write "חדו״א 1"; detectors that only
 * accept ASCII quotes leave personality_profile.goal_key stuck on bagrut_*.
 */
export const CALC1_GOAL_RE =
  /חדו["'\u05F3\u05F4\u2018\u2019\u201C\u201D׳״]?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i;

export function looksLikeCalculus1Goal(text: string | null | undefined): boolean {
  return Boolean(text && CALC1_GOAL_RE.test(text));
}

/** Non-bagrut tracks that must override a stale bagrut_* goal_key in UI framing. */
export function isClearlyNonBagrutGoalText(text: string | null | undefined): boolean {
  if (!text?.trim()) return false;
  if (/בגרות|bagrut|יח["׳״'"]?\s*[345]/i.test(text)) return false;
  if (looksLikeCalculus1Goal(text)) return true;
  if (/מתמטיקה בדיד|discrete math|\bבדיד\b/i.test(text)) return true;
  if (/אלגברה לינאר|linear algebra/i.test(text)) return true;
  if (/מכינה|makhina|university prep|הכנה לאוניברסיט/i.test(text)) return true;
  return false;
}

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
  // Live goal text wins over a stale bagrut_* key (e.g. calc1 template that
  // updated `goal` but failed to rewrite personality_profile.goal_key).
  if (isClearlyNonBagrutGoalText(opts.goal)) return false;
  if (isBagrutGoalKey(opts.goalKey)) return true;
  if (opts.goalKey) return false;
  return isBagrutGoalText(opts.goal);
}

export function resolveGoalDeadlineIso(
  nextTestDate: string | Date | null | undefined,
  finalGoalDate: string | Date | null | undefined,
): string | null {
  const next = toIsoDateOnly(nextTestDate);
  const final = toIsoDateOnly(finalGoalDate);
  if (final && next) return final >= next ? final : next;
  return final ?? next;
}

/** Normalize Neon date / ISO string / Date into YYYY-MM-DD. */
export function toIsoDateOnly(
  value: string | Date | null | undefined,
): string | null {
  if (value == null) return null;
  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) return null;
    return value.toISOString().slice(0, 10);
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;
    return trimmed.slice(0, 10);
  }
  const asString = String(value);
  return /^\d{4}-\d{2}-\d{2}/.test(asString) ? asString.slice(0, 10) : null;
}

export function daysUntilIso(
  isoDate: string | Date | null | undefined,
  now: Date = new Date(),
): number | null {
  const day = toIsoDateOnly(isoDate);
  if (!day) return null;
  const target = new Date(day + 'T12:00:00');
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
