/**
 * Unit tests for Plan v2 goal-bounded plan horizon contract (plan-capacity.ts).
 *
 * Covers:
 *  R1 — planHorizon: test date, goal date, no date → default, and pastdate edge case.
 *  R2 — conceptsPerWeekFromHours: capacity mapping.
 *  R3 — compression prerequisite order: verified via chunkConceptsIntoWeeks from plan-worklist.
 *  R5 — isPlanExpired: post-goal state trigger.
 *  R6 — hasLesson tie-break: sorting in buildLearningPlan (no-import test).
 */
import { describe, expect, it } from 'vitest';
import {
  conceptsPerWeekFromHours,
  DEFAULT_CONCEPTS_PER_WEEK,
  isPlanExpired,
  planHorizon,
  type CapacityProfile,
} from './plan-capacity';

// ---------------------------------------------------------------------------
// Local re-implementation of sequential chunking for R3 tests.
// plan-worklist.ts is server-only (has `import 'server-only'`), so we can't
// import it in vitest. The logic is deterministic and easy to mirror.
// ---------------------------------------------------------------------------
function chunkConceptsIntoWeeks(
  concepts: string[],
  numWeeks: number,
  perWeek = 4,
): string[][] {
  const weeks = Math.max(1, numWeeks);
  const cap = Math.max(1, perWeek);
  const limited = concepts.slice(0, weeks * cap);
  const groups: string[][] = Array.from({ length: weeks }, () => []);
  for (let i = 0; i < limited.length; i += 1) {
    const weekIdx = Math.min(weeks - 1, Math.floor(i / cap));
    groups[weekIdx]!.push(limited[i]!);
  }
  return groups;
}

// ---------------------------------------------------------------------------
// R1 — planHorizon
// ---------------------------------------------------------------------------

describe('planHorizon (R1)', () => {
  const days = (n: number, now = new Date()): string => {
    const d = new Date(now);
    d.setDate(d.getDate() + n);
    return d.toISOString().slice(0, 10);
  };

  it('returns null when no goal dates are set', () => {
    expect(planHorizon({})).toBeNull();
    expect(planHorizon({ next_test_date: null, final_goal_date: null })).toBeNull();
  });

  it('derives horizon from next_test_date alone', () => {
    const now = new Date('2026-07-24T12:00:00');
    const profile: CapacityProfile = { next_test_date: '2026-08-14' }; // 21 days → 3 weeks
    expect(planHorizon(profile, now)).toBe(3);
  });

  it('derives horizon from final_goal_date alone', () => {
    const now = new Date('2026-07-24T12:00:00');
    const profile: CapacityProfile = { final_goal_date: '2026-09-04' }; // 42 days → 6 weeks
    expect(planHorizon(profile, now)).toBe(6);
  });

  it('uses the LATER of next_test_date and final_goal_date', () => {
    const now = new Date('2026-07-24T12:00:00');
    const profile: CapacityProfile = {
      next_test_date: '2026-08-07',  // 14 days → 2 weeks
      final_goal_date: '2026-09-04', // 42 days → 6 weeks — later wins
    };
    expect(planHorizon(profile, now)).toBe(6);
  });

  it('uses the LATER when next_test_date is after final_goal_date', () => {
    const now = new Date('2026-07-24T12:00:00');
    const profile: CapacityProfile = {
      next_test_date: '2026-09-18',  // 56 days → 8 weeks — later wins
      final_goal_date: '2026-08-07', // 14 days → 2 weeks
    };
    expect(planHorizon(profile, now)).toBe(8);
  });

  it('returns 1 for a goal today, null for a stale past goal', () => {
    const now = new Date('2026-07-24T12:00:00');
    // goal = yesterday → stale deadline, treated as no goal so re-plans fall
    // back to the default cadence instead of perpetual 1-week plans.
    const pastProfile: CapacityProfile = { next_test_date: '2026-07-23' };
    expect(planHorizon(pastProfile, now)).toBeNull();
    // goal = today → one final cram week
    const todayProfile: CapacityProfile = { final_goal_date: '2026-07-24' };
    expect(planHorizon(todayProfile, now)).toBe(1);
  });

  it('clamps maximum to 24 weeks', () => {
    const now = new Date('2026-07-24T12:00:00');
    // goal = 2 years away (>24 weeks)
    const farProfile: CapacityProfile = { final_goal_date: '2028-07-24' };
    expect(planHorizon(farProfile, now)).toBe(24);
  });

  it('rounds up partial weeks (7 days = 1 week; 8 days = 2 weeks)', () => {
    const now = new Date('2026-07-24T12:00:00');
    const profile7: CapacityProfile = { next_test_date: days(7, now) };
    expect(planHorizon(profile7, now)).toBe(1);
    const profile8: CapacityProfile = { next_test_date: days(8, now) };
    expect(planHorizon(profile8, now)).toBe(2);
  });

  it('handles invalid date strings gracefully (returns null)', () => {
    const profile: CapacityProfile = { next_test_date: 'not-a-date' };
    expect(planHorizon(profile)).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// R2 — conceptsPerWeekFromHours
// ---------------------------------------------------------------------------

describe('conceptsPerWeekFromHours (R2)', () => {
  it('uses DEFAULT_CONCEPTS_PER_WEEK when hours is null/undefined/0', () => {
    expect(conceptsPerWeekFromHours(null)).toBe(DEFAULT_CONCEPTS_PER_WEEK);
    expect(conceptsPerWeekFromHours(undefined)).toBe(DEFAULT_CONCEPTS_PER_WEEK);
    expect(conceptsPerWeekFromHours(0)).toBe(DEFAULT_CONCEPTS_PER_WEEK);
    expect(conceptsPerWeekFromHours(-1)).toBe(DEFAULT_CONCEPTS_PER_WEEK);
  });

  it('returns 1 concept/week for < 2 h/week', () => {
    expect(conceptsPerWeekFromHours(0.5)).toBe(1);
    expect(conceptsPerWeekFromHours(1)).toBe(1);
    expect(conceptsPerWeekFromHours(1.9)).toBe(1);
  });

  it('returns 2 concepts/week for 2–3.9 h/week', () => {
    expect(conceptsPerWeekFromHours(2)).toBe(2);
    expect(conceptsPerWeekFromHours(3)).toBe(2);
    expect(conceptsPerWeekFromHours(3.9)).toBe(2);
  });

  it('returns 3 concepts/week for 4–5.9 h/week', () => {
    expect(conceptsPerWeekFromHours(4)).toBe(3);
    expect(conceptsPerWeekFromHours(5)).toBe(3);
  });

  it('returns 4 concepts/week for 6–8.9 h/week', () => {
    expect(conceptsPerWeekFromHours(6)).toBe(4);
    expect(conceptsPerWeekFromHours(8)).toBe(4);
    expect(conceptsPerWeekFromHours(8.9)).toBe(4);
  });

  it('returns 5 concepts/week for ≥ 9 h/week', () => {
    expect(conceptsPerWeekFromHours(9)).toBe(5);
    expect(conceptsPerWeekFromHours(15)).toBe(5);
    expect(conceptsPerWeekFromHours(40)).toBe(5);
  });
});

// ---------------------------------------------------------------------------
// R3 — Compression: prerequisite order is preserved via sequential chunking
// ---------------------------------------------------------------------------

describe('compression preserves prerequisite order (R3)', () => {
  // chunkConceptsIntoWeeks emits week 1 = first N concepts in order.
  // If the BFS order is [prereq, concept, advanced], slicing to horizon×capacity
  // will always keep prerequisites before their dependents.

  it('sequential chunking always puts earlier (prerequisite) concepts in week 1', () => {
    const concepts = ['a_prereq', 'b_concept', 'c_advanced', 'd_goal'];
    const groups = chunkConceptsIntoWeeks(concepts, 2, 2);
    expect(groups[0]).toEqual(['a_prereq', 'b_concept']);
    expect(groups[1]).toEqual(['c_advanced', 'd_goal']);
    // 'a_prereq' (index 0) always appears before 'b_concept' (index 1)
    const flat = groups.flat();
    expect(flat.indexOf('a_prereq')).toBeLessThan(flat.indexOf('b_concept'));
    expect(flat.indexOf('b_concept')).toBeLessThan(flat.indexOf('c_advanced'));
  });

  it('overflow slice never breaks order: kept concepts are a prefix of the full list', () => {
    const fullBfsPath = ['p1', 'p2', 'c1', 'c2', 'c3', 'c4', 'g1'];
    const horizonSlots = 4; // horizon × capacity
    const kept = fullBfsPath.slice(0, horizonSlots);
    const overflow = fullBfsPath.slice(horizonSlots);

    // kept is a prefix → all prerequisites that were in kept are still in kept
    expect(kept).toEqual(['p1', 'p2', 'c1', 'c2']);
    expect(overflow).toEqual(['c3', 'c4', 'g1']);
    // Order within kept is unchanged from BFS
    for (let i = 0; i < kept.length - 1; i++) {
      expect(fullBfsPath.indexOf(kept[i]!)).toBeLessThan(fullBfsPath.indexOf(kept[i + 1]!));
    }
  });
});

// ---------------------------------------------------------------------------
// R5 — isPlanExpired (post-goal state trigger)
// ---------------------------------------------------------------------------

describe('isPlanExpired (R5)', () => {
  it('returns false when endDate is null / undefined', () => {
    expect(isPlanExpired(null)).toBe(false);
    expect(isPlanExpired(undefined)).toBe(false);
    expect(isPlanExpired('')).toBe(false);
  });

  it('returns false when today is before the end date', () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const endDate = tomorrow.toISOString().slice(0, 10);
    expect(isPlanExpired(endDate)).toBe(false);
  });

  it('returns false on the end date itself (end of day)', () => {
    const today = new Date().toISOString().slice(0, 10);
    // isPlanExpired checks "now > end_date at 23:59:59"
    // Since now < end-of-today, this should return false.
    const now = new Date();
    now.setHours(0, 0, 0, 0); // start of today
    expect(isPlanExpired(today, now)).toBe(false);
  });

  it('returns true when end date was yesterday', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const endDate = yesterday.toISOString().slice(0, 10);
    expect(isPlanExpired(endDate)).toBe(true);
  });

  it('returns true for an end date in the past', () => {
    expect(isPlanExpired('2025-01-01')).toBe(true);
  });

  it('handles invalid end date strings gracefully (returns false)', () => {
    expect(isPlanExpired('not-a-date')).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// R6 — hasLesson tie-break (conceptual test; actual sort is in learning-plan.ts)
// ---------------------------------------------------------------------------

describe('hasLesson tie-break semantics (R6)', () => {
  // The actual sort is in buildLearningPlan in learning-plan.ts.
  // Here we verify the invariant: when urgency and edge_weight are equal,
  // a concept with hasLesson=true must sort before one with hasLesson=false.

  interface MockNode {
    concept_id: string;
    urgency: number;
    edge_weight: number;
    hasLesson: boolean;
    relation: 'prereq' | 'self';
  }

  function sortNodes(nodes: MockNode[]): MockNode[] {
    return [...nodes].sort((a, b) => {
      if (a.relation === 'self' && b.relation !== 'self') return 1;
      if (b.relation === 'self' && a.relation !== 'self') return -1;
      const urgencyDiff = b.urgency - a.urgency;
      if (Math.abs(urgencyDiff) > 0.001) return urgencyDiff;
      const weightDiff = b.edge_weight - a.edge_weight;
      if (Math.abs(weightDiff) > 0.001) return weightDiff;
      // R6 — prefer hasLesson as tie-break
      return (b.hasLesson ? 1 : 0) - (a.hasLesson ? 1 : 0);
    });
  }

  it('prefers hasLesson=true when urgency and weight are equal', () => {
    const nodes: MockNode[] = [
      { concept_id: 'no_lesson', urgency: 0.5, edge_weight: 1, hasLesson: false, relation: 'prereq' },
      { concept_id: 'has_lesson', urgency: 0.5, edge_weight: 1, hasLesson: true, relation: 'prereq' },
    ];
    const sorted = sortNodes(nodes);
    expect(sorted[0]!.concept_id).toBe('has_lesson');
    expect(sorted[1]!.concept_id).toBe('no_lesson');
  });

  it('urgency always beats hasLesson (never violates prerequisite order)', () => {
    const nodes: MockNode[] = [
      { concept_id: 'urgent_no_lesson', urgency: 0.9, edge_weight: 1, hasLesson: false, relation: 'prereq' },
      { concept_id: 'low_has_lesson', urgency: 0.3, edge_weight: 1, hasLesson: true, relation: 'prereq' },
    ];
    const sorted = sortNodes(nodes);
    // More urgent concept wins even without a lesson
    expect(sorted[0]!.concept_id).toBe('urgent_no_lesson');
  });

  it('goal node (relation=self) always goes last', () => {
    const nodes: MockNode[] = [
      { concept_id: 'goal', urgency: 0.0, edge_weight: 1, hasLesson: true, relation: 'self' },
      { concept_id: 'prereq', urgency: 0.8, edge_weight: 1, hasLesson: false, relation: 'prereq' },
    ];
    const sorted = sortNodes(nodes);
    expect(sorted[sorted.length - 1]!.concept_id).toBe('goal');
  });
});
