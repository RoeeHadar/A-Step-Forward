import { describe, expect, it } from 'vitest';
import {
  ANY_REWRITE_MIN_HOURS,
  applyWellbeingOverlay,
  canPersistWellbeingRewrite,
  defaultWellbeingPlanBias,
  detectMasteryShock,
  evaluateWellbeingSignals,
  recordWellbeingPersistedRewrite,
  selectMoraleConcepts,
  selectStrengthAnchors,
  WELLBEING_REWRITE_MAX_PER_WEEK,
  WELLBEING_REWRITE_MIN_HOURS,
} from './wellbeing-plan-bias';
import type { LearnerProfileRow } from './neon-db';

const baseProfile: LearnerProfileRow = {
  learner_id: 'learner-1',
  goal: 'bagrut_math_5',
  grade_level: '12',
  points_group: '5pt',
  subjects: ['math'],
  hours_per_week: 6,
  preferred_style: null,
  attention_span: null,
  self_scores: null,
  background_notes: null,
  next_test_name: null,
  next_test_date: null,
  final_goal_date: null,
  mental_state: { anxiety: 8 },
  personality_profile: { goal_key: 'bagrut_math_5' },
  weak_concepts: null,
  strong_concepts: null,
  wellbeing_plan_bias: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe('canPersistWellbeingRewrite cooldowns', () => {
  const now = new Date('2026-07-11T12:00:00.000Z');

  it('blocks 3rd wellbeing-class rewrite in the same calendar week', () => {
    let bias = defaultWellbeingPlanBias(now);
    bias = {
      ...bias,
      last_persisted_rewrite_at: new Date(now.getTime() - (WELLBEING_REWRITE_MIN_HOURS + 1) * 3600_000).toISOString(),
      wellbeing_rewrites_this_week: WELLBEING_REWRITE_MAX_PER_WEEK,
      week_window_start: '2026-07-06',
    };

    expect(
      canPersistWellbeingRewrite(bias, 'profile_anxiety', baseProfile, now),
    ).toBe(false);
  });

  it('allows mastery shock after wellbeing weekly cap is exhausted', () => {
    const recent = new Date(now.getTime() - (ANY_REWRITE_MIN_HOURS + 1) * 3600_000);
    const bias = {
      ...defaultWellbeingPlanBias(now),
      last_persisted_rewrite_at: recent.toISOString(),
      wellbeing_rewrites_this_week: WELLBEING_REWRITE_MAX_PER_WEEK,
      week_window_start: '2026-07-06',
    };

    expect(canPersistWellbeingRewrite(bias, 'mastery_shock', baseProfile, now)).toBe(true);
  });

  it('enforces 24h minimum between any two persisted rewrites', () => {
    const bias = {
      ...defaultWellbeingPlanBias(now),
      last_persisted_rewrite_at: new Date(now.getTime() - 12 * 3600_000).toISOString(),
      wellbeing_rewrites_this_week: 0,
    };

    expect(canPersistWellbeingRewrite(bias, 'mastery_shock', baseProfile, now)).toBe(false);
    expect(canPersistWellbeingRewrite(bias, 'profile_anxiety', baseProfile, now)).toBe(false);
  });

  it('allows wellbeing rewrite after 72h when under weekly cap', () => {
    const bias = {
      ...defaultWellbeingPlanBias(now),
      last_persisted_rewrite_at: new Date(
        now.getTime() - (WELLBEING_REWRITE_MIN_HOURS + 2) * 3600_000,
      ).toISOString(),
      wellbeing_rewrites_this_week: 1,
      week_window_start: '2026-07-06',
    };

    expect(canPersistWellbeingRewrite(bias, 'profile_anxiety', baseProfile, now)).toBe(true);
  });
});

describe('recordWellbeingPersistedRewrite', () => {
  it('does not increment weekly counter for mastery shock', () => {
    const now = new Date('2026-07-11T12:00:00.000Z');
    const bias = { ...defaultWellbeingPlanBias(now), wellbeing_rewrites_this_week: 2 };
    const next = recordWellbeingPersistedRewrite(bias, 'mastery_shock', now);
    expect(next.wellbeing_rewrites_this_week).toBe(2);
    expect(next.last_persisted_rewrite_at).toBe(now.toISOString());
  });
});

describe('detectMasteryShock', () => {
  it('detects drop >= 0.25', () => {
    expect(
      detectMasteryShock({ limits: 0.4 }, { limits: 0.7 }, ['math']),
    ).toBe(true);
  });

  it('detects cross from >= 0.6 to < 0.4', () => {
    expect(
      detectMasteryShock({ limits: 0.35 }, { limits: 0.62 }, ['math']),
    ).toBe(true);
  });
});

describe('evaluateWellbeingSignals', () => {
  it('activates on profile anxiety >= 7', () => {
    const now = new Date('2026-07-11T12:00:00.000Z');
    const { bias, triggers } = evaluateWellbeingSignals(
      { ...baseProfile, mental_state: { anxiety: 7 } },
      {},
      null,
      now,
    );
    expect(bias.active).toBe(true);
    expect(triggers).toContain('profile_anxiety');
  });

  it('does not activate on anxiety 6', () => {
    const now = new Date('2026-07-11T12:00:00.000Z');
    const { bias, triggers } = evaluateWellbeingSignals(
      { ...baseProfile, mental_state: { anxiety: 6 }, next_test_date: null },
      {},
      null,
      now,
    );
    expect(triggers).not.toContain('profile_anxiety');
    expect(bias.active).toBe(false);
  });
});

describe('selectMoraleConcepts', () => {
  it('picks 1-hop neighbor of a strong concept', async () => {
    const profile: LearnerProfileRow = {
      ...baseProfile,
      points_group: '5pt',
      subjects: ['math'],
    };
    const mastery = { limits: 0.85, continuity: 0.3 };
    const anchors = selectStrengthAnchors(mastery, profile.subjects);
    expect(anchors).toContain('limits');

    const morale = await selectMoraleConcepts({
      learnerId: 'learner-1',
      profile,
      mastery,
      strengthAnchors: anchors,
      maxCount: 4,
    });

    expect(morale.length).toBeGreaterThan(0);
    expect(morale).not.toContain('limits');
    expect(
      morale.some((c) =>
        ['functions_quadratic', 'sequences_geometric', 'trigonometry_identities', 'sequences_arithmetic', 'continuity'].includes(c),
      ),
    ).toBe(true);
  });
});

describe('applyWellbeingOverlay', () => {
  it('blends ~60% goal-critical then ~40% morale', () => {
    const ordered = ['a', 'b', 'c', 'd', 'e', 'g1', 'g2', 'g3', 'g4', 'g5'];
    const morale = ['m1', 'm2', 'm3', 'm4'];
    const blended = applyWellbeingOverlay(ordered, morale, 0.6);

    expect(blended.length).toBe(10);
    expect(blended.slice(0, 6)).toEqual(['a', 'b', 'c', 'd', 'e', 'g1']);
    expect(blended.slice(6)).toEqual(['m1', 'm2', 'm3', 'm4']);
  });

  it('dedupes morale concepts already in goal slice', () => {
    const blended = applyWellbeingOverlay(['x', 'y', 'z'], ['x', 'm1'], 0.6);
    expect(blended.filter((c) => c === 'x').length).toBe(1);
    expect(blended).toContain('m1');
  });
});
