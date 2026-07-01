import { describe, expect, it } from 'vitest';
import {
  canonicalConceptId,
  goalKeyToPointsGroup,
  isKnownConceptId,
  isValidGoalKey,
  sanitizeConceptIds,
  sanitizePlanUpdatePayload,
} from './plan-catalog';
import { extractPlanUpdate, learnerConfirmedChange } from './plan-actions';

describe('plan-catalog grounding', () => {
  it('recognizes KG concept ids', () => {
    expect(isKnownConceptId('limits')).toBe(true);
    expect(isKnownConceptId('khan_academy_calculus')).toBe(false);
  });

  it('sanitizes concept lists to known KG ids only', () => {
    const out = sanitizeConceptIds(['limits', 'youtube_playlist', 'limits']);
    expect(out).toEqual(['limits']);
  });

  it('maps onboarding goal_key to points_group', () => {
    expect(isValidGoalKey('bagrut_math_5')).toBe(true);
    expect(isValidGoalKey('bagrut_math')).toBe(false);
    expect(goalKeyToPointsGroup('bagrut_math_5')).toBe('5pt');
    expect(goalKeyToPointsGroup('bagrut_physics')).toBe('hs_physics');
  });

  it('strips invalid goal_key and external concepts from plan payloads', () => {
    const payload = sanitizePlanUpdatePayload({
      confirmed: true,
      reason: 'focus on limits',
      goal_key: 'not_a_real_goal',
      priority_concepts: ['limits', 'external_course'],
      prepend_concepts: [],
      exclude_concepts: ['fake_topic'],
    });
    expect(payload).not.toBeNull();
    expect(payload!.goal_key).toBeUndefined();
    expect(payload!.priority_concepts).toEqual(['limits']);
    expect(payload!.exclude_concepts).toEqual([]);
  });

  it('canonicalConceptId resolves aliases when present in KG', () => {
    const id = canonicalConceptId('limits');
    expect(id).toBe('limits');
    expect(isKnownConceptId(id!)).toBe(true);
  });
});

describe('plan-actions', () => {
  it('extracts and sanitizes ASF_PLAN_UPDATE tag', () => {
    const raw =
      'Great — updating your plan now.\n[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"learner asked","priority_concepts":["limits","khan"],"goal_key":"bagrut_math_5"}]]';
    const { visible, payload } = extractPlanUpdate(raw);
    expect(visible).not.toContain('ASF_PLAN_UPDATE');
    expect(payload?.priority_concepts).toEqual(['limits']);
    expect(payload?.goal_key).toBe('bagrut_math_5');
  });

  it('requires explicit learner confirmation phrases', () => {
    expect(learnerConfirmedChange('yes, update my plan')).toBe(true);
    expect(learnerConfirmedChange('עדכן')).toBe(true);
    expect(learnerConfirmedChange('maybe later')).toBe(false);
  });
});
