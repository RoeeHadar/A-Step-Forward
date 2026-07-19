/**
 * Humble readiness model — ADR-0010 Stream E (+ FSRS-style decay from Stream C).
 *
 * Pure and dependency-light: builds on the frontier manifest via plan-pacing only
 * (no DB, no LLM), so it is safe anywhere. The product stance (owner, grilling #2):
 *   - The site is a *tool*, not a predictor of success — readiness must NEVER imply
 *     guaranteed success and must stay humble to the last day.
 *   - Readiness = coverage (proven mastery of critical concepts, decay-applied)
 *     AND proven performance (passing ≥ 1 full-length timed mock at target).
 *   - The readiness number is CONCAVE: gains near the top are deliberately harder to
 *     earn (50→55% is easier than 80→85%) so the number never breeds false confidence.
 *   - Final phase shifts to mocks + gap review; the day before the exam is theory
 *     go-over + a Mentor anxiety-clearing talk only — no new material.
 */
import { criticalConceptsForGoal, getFrontier, MASTERY_THRESHOLD } from './plan-pacing';

/**
 * FSRS-style half-life (days) for unpracticed mastery. A concept last practiced
 * `MASTERY_HALF_LIFE_DAYS` ago is worth half its recorded score for readiness.
 * Conservative (long) so we don't over-penalize; resurfacing/re-checks correct it.
 */
export const MASTERY_HALF_LIFE_DAYS = 45;

/**
 * Hard ceiling on the displayed readiness. The site cannot promise success, so the
 * number never reaches 100% — even at full coverage with a passed mock.
 */
export const READINESS_CEILING = 0.95;

/**
 * Without a passed full-length mock, readiness cannot exceed this — coverage alone
 * (however high) is not proof you can perform under exam conditions.
 */
export const MOCK_GATED_CEILING = 0.7;

/** Exam-ready requires ~90% of critical concepts (decay-applied) AND a passed mock. */
export const EXAM_READY_CRITICAL_COVERAGE = 0.9;

/** Within this many days of the exam, the plan shifts to mocks + targeted gap review. */
export const FINAL_PHASE_DAYS = 14;

export type ReadinessBand = 'foundational' | 'building' | 'approaching' | 'exam_ready';
export type ReadinessPhase = 'building' | 'final_phase' | 'day_before';

/**
 * Exponentially decay a mastery score by time since last practice.
 * `score * 0.5 ^ (daysSince / halfLife)`. No decay for fresh (0-day) or non-positive.
 */
export function decayMastery(
  score: number,
  daysSince: number | null | undefined,
  halfLifeDays: number = MASTERY_HALF_LIFE_DAYS,
): number {
  if (!(score > 0)) return 0;
  if (!(typeof daysSince === 'number') || !(daysSince > 0)) return score;
  const hl = halfLifeDays > 0 ? halfLifeDays : MASTERY_HALF_LIFE_DAYS;
  return score * Math.pow(0.5, daysSince / hl);
}

/**
 * Concave coverage → displayed-readiness map: `ceiling * (1 - (1 - c)^2)`.
 * Increasing with a decreasing slope (2·ceiling·(1-c)), so a fixed display gain
 * costs MORE coverage near the top than near the bottom (80→85 harder than 50→55),
 * and full coverage lands at the sub-1.0 ceiling — never "guaranteed".
 */
export function concaveReadiness(coverage: number, ceiling: number = READINESS_CEILING): number {
  const c = Math.max(0, Math.min(1, coverage));
  return ceiling * (1 - (1 - c) * (1 - c));
}

export interface ReadinessInput {
  goalKey?: string | null;
  /** concept_id → recorded mastery score (0..1). */
  masteryScores: Record<string, number>;
  /** concept_id → days since last activity (for decay). Absent → no decay. */
  activityDays?: Record<string, number> | null;
  /** Whether the learner has passed ≥ 1 full-length mock at target. */
  mockPassed?: boolean;
  /** Whole days until the exam/deadline (null = no dated deadline). */
  daysToExam?: number | null;
  /** Override the decay half-life (tests / calibration). */
  halfLifeDays?: number;
}

export interface ReadinessResult {
  /** Displayed readiness 0..READINESS_CEILING — concave, mock-gated, never 1.0. */
  readiness: number;
  /** Decay-applied fraction of CRITICAL concepts mastered (0..1). */
  critical_coverage: number;
  /** Decay-applied fraction of ALL core concepts mastered (0..1). */
  core_coverage: number;
  /** True only when critical coverage ≥ threshold AND a mock has been passed. */
  exam_ready: boolean;
  mock_passed: boolean;
  band: ReadinessBand;
  phase: ReadinessPhase;
  days_to_exam: number | null;
  /** i18n key under `readiness.msg.*` for the humble guidance line. */
  message_key: string;
}

function coverageOf(
  ids: Iterable<string>,
  scores: Record<string, number>,
  activityDays: Record<string, number> | null | undefined,
  halfLifeDays: number,
): { total: number; mastered: number } {
  let total = 0;
  let mastered = 0;
  for (const id of ids) {
    total += 1;
    const eff = decayMastery(scores[id] ?? 0, activityDays?.[id] ?? 0, halfLifeDays);
    if (eff >= MASTERY_THRESHOLD) mastered += 1;
  }
  return { total, mastered };
}

/**
 * Compute humble readiness for a learner toward their goal. Returns null when the
 * goal has no derived frontier (caller hides the readiness surface gracefully).
 */
export function computeReadiness(input: ReadinessInput): ReadinessResult | null {
  const frontier = getFrontier(input.goalKey);
  if (!frontier) return null;

  const halfLife = input.halfLifeDays ?? MASTERY_HALF_LIFE_DAYS;
  const scores = input.masteryScores ?? {};
  const activity = input.activityDays ?? null;
  const mockPassed = input.mockPassed === true;

  const core = coverageOf(
    frontier.core.map((c) => c.id),
    scores,
    activity,
    halfLife,
  );
  const criticalSet = criticalConceptsForGoal(input.goalKey);
  const crit = coverageOf(criticalSet, scores, activity, halfLife);

  const core_coverage = core.total > 0 ? core.mastered / core.total : 1;
  // Fall back to core coverage when a goal has no critical concepts flagged.
  const critical_coverage = crit.total > 0 ? crit.mastered / crit.total : core_coverage;

  let readiness = concaveReadiness(critical_coverage);
  if (!mockPassed) readiness = Math.min(readiness, MOCK_GATED_CEILING);
  readiness = Math.min(readiness, READINESS_CEILING);

  const exam_ready = critical_coverage >= EXAM_READY_CRITICAL_COVERAGE && mockPassed;

  let band: ReadinessBand;
  if (exam_ready) band = 'exam_ready';
  else if (critical_coverage >= 0.7) band = 'approaching';
  else if (critical_coverage >= 0.35) band = 'building';
  else band = 'foundational';

  const days = typeof input.daysToExam === 'number' ? input.daysToExam : null;
  let phase: ReadinessPhase;
  if (days != null && days <= 1) phase = 'day_before';
  else if (days != null && days <= FINAL_PHASE_DAYS) phase = 'final_phase';
  else phase = 'building';

  const message_key =
    phase === 'day_before' ? 'day_before' : phase === 'final_phase' ? 'final_phase' : band;

  return {
    readiness,
    critical_coverage,
    core_coverage,
    exam_ready,
    mock_passed: mockPassed,
    band,
    phase,
    days_to_exam: days,
    message_key,
  };
}
