import { describe, expect, it } from 'vitest';
import {
  CONCEPTS_PER_ROLLING_WEEK,
  computeCapacity,
  computePacing,
  getFrontier,
  hasFrontier,
  listGoalKeys,
  masteredSetFromScores,
  sessionMinutes,
  weeksUntil,
} from './plan-pacing';

const GOAL = 'bagrut_math_5';

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
