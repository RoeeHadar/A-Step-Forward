/**
 * Deterministic goal-paced planning engine (ADR-0009 stream 2).
 *
 * Pure, dependency-light: imports ONLY the derived goal-frontier manifest
 * (goal-frontiers.generated.json). It does NOT import kg-data.json, neon-db, or
 * buildLearningPlan, so it is safe to use on the onboarding critical path
 * (see .cursor/skills/diagnostic-plan-golden-path/SKILL.md hard rules).
 *
 * Given a goal, the learner's mastered concepts, their capacity (hours/week +
 * attention span) and a deadline, it computes:
 *   - remaining scope toward the goal frontier
 *   - required velocity (concepts/week to finish by the deadline)
 *   - sustainable capacity (concepts/week the learner can realistically do)
 *   - a pace status: ahead | on_track | at_risk
 *   - the next concrete concepts to study (foundations-first, unmastered)
 *
 * The heavy, mastery-weighted cross-subject re-sequencing still lives in
 * buildLearningPlan(); this engine is the fast pacing layer on top of the
 * pre-ordered frontier.
 */
import frontiers from './goal-frontiers.generated.json';

/** Concept counts as "mastered" at or above this score. Mirrors learning-plan.ts. */
export const MASTERY_THRESHOLD = 0.8;
/** Max concepts materialized per visible week. Mirrors plan-worklist.ts (kept local to stay light). */
export const CONCEPTS_PER_ROLLING_WEEK = 4;
/** Default planning horizon when the learner gave no deadline. */
export const DEFAULT_HORIZON_WEEKS = 12;

export type PaceStatus = 'ahead' | 'on_track' | 'at_risk';

interface FrontierCoreEntry {
  id: string;
  depth: number;
  downstream: number;
  critical: boolean;
}
interface FrontierGoal {
  goal_key: string;
  subjects: string[];
  points_group: string;
  allowed_levels: string[];
  stretch_levels: string[];
  terminal_concept: string | null;
  core: FrontierCoreEntry[];
  stretch: string[];
  core_count: number;
  critical_count: number;
}
interface FrontierManifest {
  version: number;
  generated_at: string;
  fanout_critical: number;
  goals: Record<string, FrontierGoal>;
}

const manifest = frontiers as FrontierManifest;

export function getFrontier(goalKey: string | null | undefined): FrontierGoal | null {
  if (!goalKey) return null;
  return manifest.goals[goalKey] ?? null;
}

export function hasFrontier(goalKey: string | null | undefined): boolean {
  return getFrontier(goalKey) !== null;
}

export function listGoalKeys(): string[] {
  return Object.keys(manifest.goals);
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

/**
 * Sustainable concepts-per-week from weekly hours + attention span (minutes).
 * base = round(hours / 2.5) clamped [1,6]; scaled by attention (short 0.75,
 * long 1.15, else 1.0); floored at 1.
 */
export function computeCapacity(input: {
  hoursPerWeek: number | null | undefined;
  attentionSpanMin?: number | null;
}): number {
  const hours = Number.isFinite(input.hoursPerWeek) ? Math.max(0, input.hoursPerWeek as number) : 6;
  const base = clamp(Math.round(hours / 2.5), 1, 6);
  let factor = 1.0;
  const a = input.attentionSpanMin;
  if (typeof a === 'number' && Number.isFinite(a)) {
    if (a < 20) factor = 0.75;
    else if (a >= 40) factor = 1.15;
  }
  return Math.max(1, Math.round(base * factor));
}

/** Recommended per-session minutes from attention span; default 30 when unknown. */
export function sessionMinutes(attentionSpanMin?: number | null): number {
  if (typeof attentionSpanMin === 'number' && Number.isFinite(attentionSpanMin)) {
    return clamp(Math.round(attentionSpanMin), 10, 90);
  }
  return 30;
}

/** Whole weeks between now and the deadline; floored at 1. Null deadline → default horizon. */
export function weeksUntil(deadlineISO: string | null | undefined, now: Date = new Date()): number {
  if (!deadlineISO) return DEFAULT_HORIZON_WEEKS;
  const deadline = new Date(deadlineISO);
  if (Number.isNaN(deadline.getTime())) return DEFAULT_HORIZON_WEEKS;
  const days = (deadline.getTime() - now.getTime()) / 86_400_000;
  if (days <= 0) return 1;
  return Math.max(1, Math.ceil(days / 7));
}

/** Build the set of concept ids the learner has already mastered. */
export function masteredSetFromScores(
  scores: Record<string, number> | null | undefined,
  threshold = MASTERY_THRESHOLD,
): Set<string> {
  const out = new Set<string>();
  if (!scores) return out;
  for (const [id, score] of Object.entries(scores)) {
    if (typeof score === 'number' && score >= threshold) out.add(id);
  }
  return out;
}

export interface PacingInputs {
  goalKey: string;
  /** concept_id → mastery score (0..1). Concepts ≥ MASTERY_THRESHOLD are treated as done. */
  masteryScores?: Record<string, number> | null;
  /** Alternatively, pass an explicit mastered set (takes precedence over masteryScores). */
  masteredConceptIds?: Iterable<string> | null;
  hoursPerWeek?: number | null;
  attentionSpanMin?: number | null;
  /** next_test_date ?? final_goal_date; ISO date string. */
  deadlineISO?: string | null;
  /** Measured trailing concepts/week; when provided, enables the 'ahead' status. */
  trailingVelocity?: number | null;
  /**
   * Wellbeing "how, not whether" load ease (ADR-0010 #15). Multiplies the weekly
   * NEW-material load (never below 1); does NOT touch the gate/pass bar. e.g. 0.6 for
   * an anxious / mastery-shocked learner → lighter weeks, same standards.
   */
  loadMultiplier?: number | null;
  now?: Date;
}

export interface PacingResult {
  goal_key: string;
  frontier_size: number;
  mastered_in_frontier: number;
  remaining_scope: number;
  /** mastered_in_frontier / frontier_size, 0..1. */
  goal_readiness: number;
  weeks_left: number;
  /** concepts/week required to clear remaining_scope by the deadline. */
  required_velocity: number;
  /** sustainable concepts/week for this learner. */
  capacity: number;
  /** integer concepts to schedule this week, clamped to [1, CONCEPTS_PER_ROLLING_WEEK]. */
  weekly_load: number;
  status: PaceStatus;
  session_minutes: number;
  /** next concrete concepts to study this week (foundations-first, unmastered). */
  next_concepts: string[];
  /** all unmastered core concepts, in study order (for week chunking). */
  remaining_ordered: string[];
}

/**
 * Compute the pacing state for a learner toward a goal.
 * Returns null when the goal has no frontier (caller should fall back to the
 * legacy planner / bootstrap).
 */
export function computePacing(inputs: PacingInputs): PacingResult | null {
  const frontier = getFrontier(inputs.goalKey);
  if (!frontier) return null;

  const mastered = inputs.masteredConceptIds
    ? new Set(inputs.masteredConceptIds)
    : masteredSetFromScores(inputs.masteryScores);

  const remainingEntries = frontier.core.filter((c) => !mastered.has(c.id));
  const remaining_ordered = remainingEntries.map((c) => c.id);

  const frontier_size = frontier.core.length;
  const mastered_in_frontier = frontier_size - remainingEntries.length;
  const remaining_scope = remainingEntries.length;
  const goal_readiness = frontier_size > 0 ? mastered_in_frontier / frontier_size : 1;

  const weeks_left = weeksUntil(inputs.deadlineISO, inputs.now);
  const capacity = computeCapacity({
    hoursPerWeek: inputs.hoursPerWeek,
    attentionSpanMin: inputs.attentionSpanMin,
  });
  const required_velocity = remaining_scope === 0 ? 0 : remaining_scope / weeks_left;

  let status: PaceStatus;
  if (remaining_scope === 0) {
    status = 'ahead';
  } else if (required_velocity > capacity) {
    status = 'at_risk';
  } else if (
    typeof inputs.trailingVelocity === 'number' &&
    Number.isFinite(inputs.trailingVelocity) &&
    inputs.trailingVelocity > required_velocity
  ) {
    status = 'ahead';
  } else {
    status = 'on_track';
  }

  const baseLoad = Math.min(capacity, Math.max(required_velocity, 1));
  // Wellbeing eases HOW MUCH new material (never below 1); the gate is untouched.
  const easedLoad =
    typeof inputs.loadMultiplier === 'number' && Number.isFinite(inputs.loadMultiplier)
      ? baseLoad * clamp(inputs.loadMultiplier, 0.1, 1)
      : baseLoad;
  const weekly_load = clamp(Math.round(easedLoad), 1, CONCEPTS_PER_ROLLING_WEEK);

  const next_concepts = selectNextConcepts({
    goalKey: frontier.goal_key,
    masteryScores: inputs.masteryScores,
    masteredConceptIds: inputs.masteredConceptIds,
    limit: weekly_load,
  });

  return {
    goal_key: frontier.goal_key,
    frontier_size,
    mastered_in_frontier,
    remaining_scope,
    goal_readiness,
    weeks_left,
    required_velocity,
    capacity,
    weekly_load,
    status,
    session_minutes: sessionMinutes(inputs.attentionSpanMin),
    next_concepts,
    remaining_ordered,
  };
}

export interface SelectNextConceptsInput {
  goalKey: string;
  /** concept_id → mastery score (0..1). */
  masteryScores?: Record<string, number> | null;
  /** Explicit mastered set (takes precedence over masteryScores). */
  masteredConceptIds?: Iterable<string> | null;
  /**
   * Concepts the learner has already engaged (scheduled / self-rated / seen).
   * Their max frontier depth sets the "anchor" so selection progresses forward
   * from the learner's level instead of regressing to far-below foundations.
   */
  engagedConceptIds?: Iterable<string> | null;
  /** Concepts to never (re)schedule (e.g. already in the plan). */
  excludeConceptIds?: Iterable<string> | null;
  /** Weak concepts allowed BELOW the anchor for remediation. */
  weakConceptIds?: Iterable<string> | null;
  /** How many to return. */
  limit: number;
  /** Depth slack allowed below the anchor (default 1). */
  anchorLookback?: number;
  threshold?: number;
}

/**
 * Anchored next-slice selector over the goal frontier (ADR-0009).
 *
 * The frontier core spans every prerequisite down to `arithmetic`, so naive
 * "unmastered, foundations-first" selection would drag an advanced-goal learner
 * back through elementary material. This selector ANCHORS to the deepest concept
 * the learner has already engaged (self-rated / scheduled / mastered) and only
 * pulls concepts at or beyond that depth (minus a small lookback), so the plan
 * progresses forward toward the goal terminal from the learner's actual level.
 * Explicitly weak concepts are still allowed below the anchor for remediation.
 *
 * Beginners (no engagement signal) anchor at depth 0 → start at foundations, which
 * is the safe default. Pure + dependency-light (manifest only).
 */
export function selectNextConcepts(input: SelectNextConceptsInput): string[] {
  const frontier = getFrontier(input.goalKey);
  if (!frontier) return [];
  const threshold = input.threshold ?? MASTERY_THRESHOLD;

  const mastered = input.masteredConceptIds
    ? new Set(input.masteredConceptIds)
    : masteredSetFromScores(input.masteryScores, threshold);
  const excluded = new Set(input.excludeConceptIds ?? []);
  const weak = new Set(input.weakConceptIds ?? []);

  // Engaged = concepts the learner has a signal for (self-rated / scheduled / mastered).
  // Its max frontier depth is the "anchor": the learner's working level.
  const engaged = new Set<string>(input.engagedConceptIds ?? []);
  for (const id of mastered) engaged.add(id);
  let anchorDepth = 0;
  for (const entry of frontier.core) {
    if (engaged.has(entry.id) && entry.depth > anchorDepth) anchorDepth = entry.depth;
  }
  const lookback = input.anchorLookback ?? 0;
  const minDepth = Math.max(0, anchorDepth - lookback);

  // Schedule a concept when it is FORWARD of the anchor (progress toward the
  // terminal), OR is in the learner's own engaged set (their entry concepts), OR
  // is explicitly weak (remediation). Never-engaged concepts far BELOW the anchor
  // are presumed known and skipped — this prevents dragging an advanced-goal
  // learner back through elementary foundations.
  const out: string[] = [];
  for (const entry of frontier.core) {
    if (out.length >= input.limit) break;
    if (mastered.has(entry.id)) continue;
    // Weak concepts are remediation-eligible even if already used — a failed week's
    // concepts must be re-teachable (ADR-0010 remediation carry-forward). Otherwise
    // don't reschedule anything already in the plan.
    if (excluded.has(entry.id) && !weak.has(entry.id)) continue;
    if (entry.depth >= minDepth || engaged.has(entry.id) || weak.has(entry.id)) {
      out.push(entry.id);
    }
  }
  return out;
}

/** Per-critical-concept mastery floor for a weekly gate pass (ADR-0010). */
export const GATE_CRITICAL_FLOOR = 0.6;

/** Default aggregate pass threshold for a weekly gate (mirrors GATE_PASS_THRESHOLD). */
export const GATE_AGGREGATE_THRESHOLD = 0.75;

/** The set of frontier-CRITICAL concept ids for a goal (high downstream degree). */
export function criticalConceptsForGoal(goalKey: string | null | undefined): Set<string> {
  const frontier = getFrontier(goalKey);
  const out = new Set<string>();
  if (!frontier) return out;
  for (const c of frontier.core) if (c.critical) out.add(c.id);
  return out;
}

export interface GatePassResult {
  passed: boolean;
  /** Critical concepts assessed in this gate that fell below the floor. */
  failed_critical: string[];
  aggregate_ok: boolean;
}

/**
 * Decide whether a weekly gate passes (ADR-0010, pure + tested):
 *   aggregate score ≥ threshold AND every frontier-CRITICAL concept assessed in the
 *   gate ≥ the critical floor. A strong average can't mask a zero on a hard
 *   prerequisite; non-critical weak spots don't block (they fold into spaced review).
 *
 * Only critical concepts that actually appear in `perTopic` are checked — the gate
 * can't fail on a critical concept it never assessed.
 */
export function evaluateGatePass(input: {
  aggregateScore: number;
  perTopic: Record<string, number>;
  goalKey?: string | null;
  passThreshold?: number;
  criticalFloor?: number;
}): GatePassResult {
  const threshold = input.passThreshold ?? GATE_AGGREGATE_THRESHOLD;
  const floor = input.criticalFloor ?? GATE_CRITICAL_FLOOR;
  const critical = criticalConceptsForGoal(input.goalKey);

  const failed_critical: string[] = [];
  for (const [topic, score] of Object.entries(input.perTopic)) {
    if (critical.has(topic) && score < floor) failed_critical.push(topic);
  }
  const aggregate_ok = input.aggregateScore >= threshold;
  return {
    passed: aggregate_ok && failed_critical.length === 0,
    failed_critical,
    aggregate_ok,
  };
}
