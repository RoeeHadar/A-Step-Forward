/**
 * Plan capacity helpers — pure, no heavy imports, safe on the onboarding
 * critical path (onboarding-plan-bootstrap.ts) AND in neon-db.ts (full path).
 *
 * R1: planHorizon()            — single source of truth for goal horizon weeks.
 * R2: conceptsPerWeekFromHours() — capacity mapping from hours_per_week.
 * R5: isPlanExpired()           — detects post-goal state for re-plan CTA.
 *
 * Cross-reference: onboarding-plan-bootstrap.ts (thin path, must stay import-light)
 * and neon-db.ts (generateLearningPlan, advanceRollingPlanWindow) for R7.
 */

// ---------------------------------------------------------------------------
// Shared profile shape (subset of LearnerProfileRow / OnboardingBootstrapPayload)
// ---------------------------------------------------------------------------

export interface CapacityProfile {
  next_test_date?: string | null;
  final_goal_date?: string | null;
  hours_per_week?: number | null;
}

// ---------------------------------------------------------------------------
// R2 — Capacity mapping: hours_per_week → concepts_per_week
//
// Rule of thumb: ~1 concept per 1.5–2 h of focused study. Clamped to [1, 5]
// to guard against unrealistic self-reports (e.g. 0 h or 30 h/week).
//
// | Hours / week | Concepts / week |
// |     0 – <2   |       1         |  (minimum: at least one step forward)
// |     2 – <4   |       2         |
// |     4 – <6   |       3         |
// |     6 – <9   |       4         |  (current hard-coded default)
// |     ≥ 9      |       5         |  (maximum: avoid sprint fatigue)
// ---------------------------------------------------------------------------

interface CapacityRow {
  minHours: number;
  maxHoursExcl: number;
  perWeek: number;
}

const CAPACITY_TABLE: CapacityRow[] = [
  { minHours: 0, maxHoursExcl: 2, perWeek: 1 },
  { minHours: 2, maxHoursExcl: 4, perWeek: 2 },
  { minHours: 4, maxHoursExcl: 6, perWeek: 3 },
  { minHours: 6, maxHoursExcl: 9, perWeek: 4 },
  { minHours: 9, maxHoursExcl: Infinity, perWeek: 5 },
];

/** Fallback capacity when hours_per_week is absent/zero (≈ 3 h/week learner). */
export const DEFAULT_CONCEPTS_PER_WEEK = 3;

/**
 * R2: Map a learner's declared study hours per week → concepts per week.
 * Uses CAPACITY_TABLE; result clamped to [1, 5].
 */
export function conceptsPerWeekFromHours(hours: number | null | undefined): number {
  if (!hours || hours <= 0) return DEFAULT_CONCEPTS_PER_WEEK;
  for (const { minHours, maxHoursExcl, perWeek } of CAPACITY_TABLE) {
    if (hours >= minHours && hours < maxHoursExcl) return perWeek;
  }
  return 5; // ≥ 9 h/week
}

// ---------------------------------------------------------------------------
// R1 — Horizon derivation: single source of truth
//
// Uses the LATER of next_test_date and final_goal_date as the deadline
// (mirrors resolveGoalDeadlineIso in goal-track.ts — kept separate to avoid
// importing goal-track.ts so this module remains import-free).
//
// Returns null when no goal date is set (callers should fall back to their own
// rolling-window default, e.g. ROLLING_VISIBLE_WEEKS = 2).
// Range: [1, 24] weeks. A past goal still returns 1 (plan must show something).
// ---------------------------------------------------------------------------

/**
 * R1: Derive the plan horizon (study weeks from today to the goal deadline).
 */
export function planHorizon(
  profile: CapacityProfile,
  now: Date = new Date(),
): number | null {
  const next = profile.next_test_date?.slice(0, 10) ?? null;
  const final = profile.final_goal_date?.slice(0, 10) ?? null;

  // The later date wins (same logic as resolveGoalDeadlineIso in goal-track.ts).
  let deadline: string | null = null;
  if (final && next) {
    deadline = final >= next ? final : next;
  } else {
    deadline = final ?? next;
  }
  if (!deadline) return null;

  const target = new Date(`${deadline}T12:00:00`);
  if (Number.isNaN(target.getTime())) return null;

  const nowNoon = new Date(now);
  nowNoon.setHours(12, 0, 0, 0);

  const days = Math.ceil((target.getTime() - nowNoon.getTime()) / (1000 * 60 * 60 * 24));
  // Goal today → one final cram week. Goal in the PAST → stale deadline: treat as
  // no goal (null) so re-plans fall back to the default cadence instead of
  // producing perpetual 1-week plans against an expired date.
  if (days === 0) return 1;
  if (days < 0) return null;
  return Math.max(1, Math.min(24, Math.ceil(days / 7)));
}

// ---------------------------------------------------------------------------
// R5 — Post-goal detection
// ---------------------------------------------------------------------------

/**
 * R5: Returns true when today is past the plan's end_date, signalling that
 * advanceRollingPlanWindow must NOT silently march on and the dashboard
 * should show a bilingual re-plan CTA.
 */
export function isPlanExpired(
  endDate: string | null | undefined,
  now: Date = new Date(),
): boolean {
  if (!endDate) return false;
  const end = new Date(`${endDate.slice(0, 10)}T23:59:59`);
  if (Number.isNaN(end.getTime())) return false;
  return now.getTime() > end.getTime();
}
