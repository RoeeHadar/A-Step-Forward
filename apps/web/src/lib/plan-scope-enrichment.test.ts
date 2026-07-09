import { describe, expect, it } from 'vitest';
import {
  enrichPlanPayloadFromLearnerContext,
  planPayloadHasExamScope,
} from './plan-scope-enrichment';
import { proposalToUpdatePayload, inferGoalMetaFromText } from './plan-actions';
import { buildPlanChangeRequest } from './plan-change-template';
import { planPayloadNeedsClarification } from './plan-apply';

describe('plan-scope-enrichment', () => {
  const physicsCtx = {
    subjects: ['physics'],
    goal_key: 'bagrut_physics',
    goal: 'בגרות פיזיקה',
    planConceptIds: ['kinematics_1d', 'newton_laws'],
  };

  it('refines vague physics goal text to mechanics scope', () => {
    const enriched = enrichPlanPayloadFromLearnerContext(
      { confirmed: true, reason: 'x', goal: 'מבחן בפיזיקה' },
      physicsCtx,
    );
    expect(enriched.goal).toContain('מכניקה');
    expect(enriched.prepend_concepts?.length).toBeGreaterThan(3);
  });

  it('planPayloadHasExamScope true after enrichment for bagrut physics profile', () => {
    const payload = enrichPlanPayloadFromLearnerContext(
      { confirmed: true, reason: 'x', goal: 'פיזיקה' },
      physicsCtx,
    );
    expect(planPayloadHasExamScope(payload, physicsCtx)).toBe(true);
  });

  it('electricity scope when goal mentions חשמל', () => {
    const enriched = enrichPlanPayloadFromLearnerContext(
      { confirmed: true, reason: 'x', goal: 'מבחן בפיזיקה חשמל' },
      physicsCtx,
    );
    expect(enriched.prepend_concepts).toContain('electric_circuits');
  });

  it('math calc1 from profile goal_key', () => {
    const enriched = enrichPlanPayloadFromLearnerContext(
      { confirmed: true, reason: 'x', goal: 'מבחן במתמטיקה' },
      { subjects: ['math'], goal_key: 'calculus1', goal: 'חדו״א 1' },
    );
    expect(enriched.prepend_concepts?.some((id) => /limits|derivatives|integrals/.test(id))).toBe(
      true,
    );
  });

  it('broad physics template + profile passes clarification (user session case)', () => {
    const template = buildPlanChangeRequest(
      { goal: 'מבחן בפיזיקה', date: 'עוד שבוע' },
      'he',
    );
    const raw = proposalToUpdatePayload({
      reason: 'cram',
      ...inferGoalMetaFromText(template),
    });
    const enriched = enrichPlanPayloadFromLearnerContext(raw, physicsCtx);
    expect(planPayloadNeedsClarification(enriched, physicsCtx)).toBeNull();
  });
});
