import { describe, expect, it } from 'vitest';
import {
  CONCEPTS_PER_ROLLING_WEEK,
  computeCapacity,
  computePacing,
  criticalConceptsForGoal,
  evaluateGatePass,
  GATE_CRITICAL_FLOOR,
  getFrontier,
  hasFrontier,
  listGoalKeys,
  masteredSetFromScores,
  selectNextConcepts,
  sessionMinutes,
  weeksUntil,
} from './plan-pacing';

const GOAL = 'bagrut_math_5';

function depthOf(goalKey: string): Map<string, number> {
  const m = new Map<string, number>();
  for (const c of getFrontier(goalKey)!.core) m.set(c.id, c.depth);
  return m;
}

describe('plan-pacing: frontier access', () => {
  it('exposes every derived goal frontier', () => {
    expect(listGoalKeys().length).toBeGreaterThan(0);
    expect(hasFrontier(GOAL)).toBe(true);
    expect(hasFrontier('not_a_goal')).toBe(false);
    expect(getFrontier(null)).toBeNull();
  });
});

describe('plan-pacing: capacity', () => {
  it('scales base capacity with weekly hours, clamped to [1,6]', () => {
    expect(computeCapacity({ hoursPerWeek: 0 })).toBe(1);
    expect(computeCapacity({ hoursPerWeek: 5 })).toBe(2); // round(5/2.5)=2
    expect(computeCapacity({ hoursPerWeek: 100 })).toBe(6); // clamped
  });

  it('applies attention-span factor', () => {
    // base for 10h = round(4)=4
    expect(computeCapacity({ hoursPerWeek: 10, attentionSpanMin: 10 })).toBe(3); // 4*0.75=3
    expect(computeCapacity({ hoursPerWeek: 10, attentionSpanMin: 30 })).toBe(4); // 4*1.0
    expect(computeCapacity({ hoursPerWeek: 10, attentionSpanMin: 45 })).toBe(5); // 4*1.15=4.6→5
  });

  it('defaults hours to 6 and floors at 1', () => {
    expect(computeCapacity({ hoursPerWeek: null })).toBe(2); // round(6/2.5)=2
    expect(computeCapacity({ hoursPerWeek: 1, attentionSpanMin: 5 })).toBe(1); // round(0.4)=0→floor 1
  });
});

describe('plan-pacing: session minutes', () => {
  it('uses attention span clamped to [10,90], default 30', () => {
    expect(sessionMinutes(null)).toBe(30);
    expect(sessionMinutes(5)).toBe(10);
    expect(sessionMinutes(120)).toBe(90);
    expect(sessionMinutes(25)).toBe(25);
  });
});

describe('plan-pacing: weeksUntil', () => {
  it('defaults to horizon when no deadline', () => {
    expect(weeksUntil(null)).toBe(12);
    expect(weeksUntil('not-a-date')).toBe(12);
  });

  it('floors past/near deadlines at 1 week', () => {
    const now = new Date('2026-07-19T00:00:00Z');
    expect(weeksUntil('2026-07-10', now)).toBe(1); // past
    expect(weeksUntil('2026-07-20', now)).toBe(1); // tomorrow
  });

  it('ceils partial weeks', () => {
    const now = new Date('2026-07-19T00:00:00Z');
    expect(weeksUntil('2026-08-02', now)).toBe(2); // 14 days
    expect(weeksUntil('2026-08-03', now)).toBe(3); // 15 days → ceil
  });
});

describe('plan-pacing: mastered set', () => {
  it('includes only concepts at/above threshold', () => {
    const set = masteredSetFromScores({ a: 0.9, b: 0.8, c: 0.79, d: 0.1 });
    expect([...set].sort()).toEqual(['a', 'b']);
    expect(masteredSetFromScores(null).size).toBe(0);
  });
});

describe('plan-pacing: computePacing', () => {
  it('returns null for an unknown goal', () => {
    expect(computePacing({ goalKey: 'nope' })).toBeNull();
  });

  it('brand-new learner: nothing mastered, full frontier remains', () => {
    const p = computePacing({ goalKey: GOAL, hoursPerWeek: 6, deadlineISO: null })!;
    expect(p).not.toBeNull();
    expect(p.mastered_in_frontier).toBe(0);
    expect(p.remaining_scope).toBe(p.frontier_size);
    expect(p.goal_readiness).toBe(0);
    expect(p.next_concepts.length).toBe(p.weekly_load);
    expect(p.weekly_load).toBeGreaterThanOrEqual(1);
    expect(p.weekly_load).toBeLessThanOrEqual(CONCEPTS_PER_ROLLING_WEEK);
    // First concept should be a foundation (the manifest is foundations-first).
    expect(p.remaining_ordered[0]).toBe(getFrontier(GOAL)!.core[0]!.id);
  });

  it('flags at_risk when required velocity exceeds capacity (tight deadline)', () => {
    const now = new Date('2026-07-19T00:00:00Z');
    const p = computePacing({
      goalKey: GOAL,
      hoursPerWeek: 4,
      deadlineISO: '2026-08-02', // ~2 weeks for a 66-concept frontier
      now,
    })!;
    expect(p.required_velocity).toBeGreaterThan(p.capacity);
    expect(p.status).toBe('at_risk');
  });

  it('is on_track with a comfortable deadline and no velocity signal', () => {
    const now = new Date('2026-07-19T00:00:00Z');
    const p = computePacing({
      goalKey: GOAL,
      hoursPerWeek: 15,
      deadlineISO: '2027-07-19', // ~1 year
      now,
    })!;
    expect(p.required_velocity).toBeLessThanOrEqual(p.capacity);
    expect(p.status).toBe('on_track');
  });

  it('is ahead when trailing velocity beats the required pace', () => {
    const now = new Date('2026-07-19T00:00:00Z');
    const p = computePacing({
      goalKey: GOAL,
      hoursPerWeek: 15,
      deadlineISO: '2027-07-19',
      trailingVelocity: 5,
      now,
    })!;
    expect(p.status).toBe('ahead');
  });

  it('is ahead (done) when the whole frontier is mastered', () => {
    const frontier = getFrontier(GOAL)!;
    const scores: Record<string, number> = {};
    for (const c of frontier.core) scores[c.id] = 1;
    const p = computePacing({ goalKey: GOAL, masteryScores: scores })!;
    expect(p.remaining_scope).toBe(0);
    expect(p.goal_readiness).toBe(1);
    expect(p.status).toBe('ahead');
    expect(p.required_velocity).toBe(0);
    expect(p.next_concepts).toEqual([]);
  });

  it('skips mastered concepts in next_concepts ordering', () => {
    const frontier = getFrontier(GOAL)!;
    const firstId = frontier.core[0]!.id;
    const p = computePacing({
      goalKey: GOAL,
      masteryScores: { [firstId]: 0.95 },
      hoursPerWeek: 6,
    })!;
    expect(p.next_concepts).not.toContain(firstId);
    expect(p.mastered_in_frontier).toBe(1);
  });

  it('explicit masteredConceptIds takes precedence over scores', () => {
    const frontier = getFrontier(GOAL)!;
    const ids = frontier.core.slice(0, 3).map((c) => c.id);
    const p = computePacing({
      goalKey: GOAL,
      masteredConceptIds: ids,
      masteryScores: {},
      hoursPerWeek: 6,
    })!;
    expect(p.mastered_in_frontier).toBe(3);
  });
});

describe('plan-pacing: selectNextConcepts (anchored)', () => {
  it('beginner (no engagement) starts foundations-first from depth 0', () => {
    const picked = selectNextConcepts({ goalKey: GOAL, limit: 4 });
    const core = getFrontier(GOAL)!.core;
    expect(picked).toEqual(core.slice(0, 4).map((c) => c.id));
  });

  it('returns [] for an unknown goal', () => {
    expect(selectNextConcepts({ goalKey: 'nope', limit: 4 })).toEqual([]);
  });

  it('excludes mastered and already-used concepts', () => {
    const core = getFrontier(GOAL)!.core;
    const mastered = core[0]!.id;
    const used = core[1]!.id;
    const picked = selectNextConcepts({
      goalKey: GOAL,
      masteryScores: { [mastered]: 0.95 },
      excludeConceptIds: [used],
      limit: 6,
    });
    expect(picked).not.toContain(mastered);
    expect(picked).not.toContain(used);
  });

  it('anchors to the learner level — does NOT regress to far-below foundations', () => {
    const depth = depthOf(GOAL);
    const core = getFrontier(GOAL)!.core;
    // Anchor at a mid-depth concept; exclude it so we test forward-only selection.
    const anchor = core.find((c) => c.depth >= 2);
    expect(anchor, 'frontier should have a depth>=2 concept').toBeTruthy();
    const shallow = core.filter((c) => c.depth === 0).map((c) => c.id);
    expect(shallow.length).toBeGreaterThan(0);

    const picked = selectNextConcepts({
      goalKey: GOAL,
      engagedConceptIds: [anchor!.id],
      excludeConceptIds: [anchor!.id],
      limit: 8,
    });
    // Nothing below the anchor depth (the presumed-known foundations) is scheduled.
    for (const id of picked) {
      expect(depth.get(id)!).toBeGreaterThanOrEqual(anchor!.depth);
    }
    // Concretely, a depth-0 foundation is NOT dragged in.
    for (const s of shallow) expect(picked).not.toContain(s);
  });

  it('still surfaces an explicitly weak below-anchor concept (remediation)', () => {
    const core = getFrontier(GOAL)!.core;
    const anchor = core.find((c) => c.depth >= 3)!;
    const weakLow = core.find((c) => c.depth === 0)!.id;
    const picked = selectNextConcepts({
      goalKey: GOAL,
      engagedConceptIds: [anchor.id],
      excludeConceptIds: [anchor.id],
      weakConceptIds: [weakLow],
      limit: 8,
    });
    expect(picked).toContain(weakLow);
  });

  it('progresses forward: engaged early concepts yield deeper next concepts', () => {
    const core = getFrontier(GOAL)!.core;
    const depth = depthOf(GOAL);
    const firstTwo = core.slice(0, 2).map((c) => c.id);
    const picked = selectNextConcepts({
      goalKey: GOAL,
      engagedConceptIds: firstTwo,
      excludeConceptIds: firstTwo,
      limit: 3,
    });
    expect(picked.length).toBeGreaterThan(0);
    // None of the returned concepts are the already-used ones.
    for (const id of firstTwo) expect(picked).not.toContain(id);
    // All returned concepts are at/after the anchor depth.
    const anchorDepth = Math.max(...firstTwo.map((id) => depth.get(id)!));
    for (const id of picked) expect(depth.get(id)!).toBeGreaterThanOrEqual(anchorDepth);
  });

  it('remediation: a weak concept is re-scheduled even if already used', () => {
    const core = getFrontier(GOAL)!.core;
    const used = core.slice(0, 3).map((c) => c.id);
    const weakUsed = used[0]!;
    const picked = selectNextConcepts({
      goalKey: GOAL,
      engagedConceptIds: used,
      excludeConceptIds: used,
      weakConceptIds: [weakUsed],
      limit: 5,
    });
    // The weak, already-used concept is pulled back in for remediation…
    expect(picked).toContain(weakUsed);
    // …but a non-weak used concept is not.
    expect(picked).not.toContain(used[1]!);
  });
});

describe('plan-pacing: evaluateGatePass (critical-concept floor)', () => {
  it('exposes the critical concept set for a goal', () => {
    const crit = criticalConceptsForGoal(GOAL);
    expect(crit.size).toBeGreaterThan(0);
    const core = getFrontier(GOAL)!.core;
    for (const id of crit) {
      expect(core.find((c) => c.id === id)?.critical).toBe(true);
    }
  });

  it('empty critical set for an unknown goal', () => {
    expect(criticalConceptsForGoal('nope').size).toBe(0);
  });

  it('passes when aggregate ≥ threshold and no critical concept is below the floor', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    const perTopic: Record<string, number> = {};
    for (const c of crit.slice(0, 2)) perTopic[c] = 0.9;
    const r = evaluateGatePass({ aggregateScore: 0.8, perTopic, goalKey: GOAL });
    expect(r.passed).toBe(true);
    expect(r.failed_critical).toEqual([]);
  });

  it('fails when a critical concept is below the floor even if aggregate passes', () => {
    const crit = [...criticalConceptsForGoal(GOAL)];
    expect(crit.length).toBeGreaterThan(0);
    const weakCritical = crit[0]!;
    const perTopic: Record<string, number> = { [weakCritical]: GATE_CRITICAL_FLOOR - 0.2 };
    const r = evaluateGatePass({ aggregateScore: 0.95, perTopic, goalKey: GOAL });
    expect(r.aggregate_ok).toBe(true);
    expect(r.passed).toBe(false);
    expect(r.failed_critical).toContain(weakCritical);
  });

  it('fails when aggregate is below threshold regardless of critical floors', () => {
    const r = evaluateGatePass({ aggregateScore: 0.5, perTopic: {}, goalKey: GOAL });
    expect(r.passed).toBe(false);
    expect(r.aggregate_ok).toBe(false);
  });

  it('does not fail on a critical concept that was never assessed', () => {
    // No critical concept in perTopic → only the aggregate gates.
    const r = evaluateGatePass({ aggregateScore: 0.8, perTopic: { some_noncritical: 0.1 }, goalKey: GOAL });
    expect(r.failed_critical).toEqual([]);
    expect(r.passed).toBe(true);
  });
});
