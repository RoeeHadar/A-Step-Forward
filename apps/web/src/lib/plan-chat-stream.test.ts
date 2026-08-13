/**
 * Simulates chat stream tail: plan apply decision + learner-visible notices.
 */
import { describe, expect, it } from 'vitest';
import {
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
  stripPlanMachineTags,
  inferConceptIdsFromText,
  inferGoalMetaFromText,
  proposalToUpdatePayload,
  planModificationProtocol,
  PLAN_AGENT_INSTRUCTIONS,
  PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE,
} from './plan-actions';
import { buildPlanChangeRequest } from './plan-change-template';
import {
  buildPlanAppliedNotice,
  buildPlanClarificationNotice,
  buildPlanApplyingNotice,
  buildPlanApplyFailureNotice,
  planPayloadNeedsClarification,
} from './plan-apply';

const USER = buildPlanChangeRequest(
  { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
  'he',
);
const ASSISTANT =
  'אני הולך לשנות את התוכנית שלך. התוכנית החדשה תכלול חזרה על נושאים חשובים למבחן.';

describe('chat stream finalize (calc1 plan change template)', () => {
  it('triggers immediate apply on first template message', () => {
    expect(shouldApplyPlanImmediately(USER)).toBe(true);
  });

  it('decides to apply only when the user message is the template', () => {
    expect(shouldApplyPlanChange(USER, ASSISTANT)).toBe(true);
    expect(shouldApplyPlanChange('כן', ASSISTANT)).toBe(false);
  });

  it('does not apply casual phrasing without template', () => {
    const casual = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    expect(shouldApplyPlanImmediately(casual)).toBe(false);
  });

  it('builds applying + success notices for Hebrew locale', () => {
    expect(buildPlanApplyingNotice('he')).toContain('מעדכן את המטרה');
    const payload = proposalToUpdatePayload({
      reason: 'הכנה למבחן בחדו״א 1',
      ...inferGoalMetaFromText(USER, ASSISTANT),
      prepend_concepts: inferConceptIdsFromText(USER, ASSISTANT),
    });
    const notice = buildPlanAppliedNotice(
      {
        applied: true,
        reason: payload.reason,
        goal: payload.goal ?? undefined,
        finalGoalDate: payload.final_goal_date ?? undefined,
        weekSummaries: [
          { week: 1, conceptIds: ['limits', 'derivatives_intro'] },
          { week: 2, conceptIds: ['integrals_intro'] },
        ],
      },
      'he',
    );
    expect(notice).toContain('המטרה והתוכנית השבועית עודכנו');
    expect(notice).toContain('שבוע 1');
    expect(stripPlanMachineTags(`${ASSISTANT}\n\n${notice}`)).not.toContain('ASF_PLAN');
  });

  it('encodes data-stream events the client listens for', () => {
    const encodeData = (data: unknown) =>
      `2:${JSON.stringify([data])}\n`;
    const applying = encodeData({ type: 'plan_applying' });
    const updated = encodeData({
      type: 'plan_updated',
      planId: 'plan-test',
      reason: 'calc1 exam',
    });
    expect(JSON.parse(applying.slice(2).trim())[0].type).toBe('plan_applying');
    expect(JSON.parse(updated.slice(2).trim())[0].type).toBe('plan_updated');
  });

  it('surfaces failure notice when payload is missing', () => {
    const failure = buildPlanApplyFailureNotice('he', 'missing_payload');
    expect(failure).toContain('לא הצלחתי לעדכן את התוכנית');
    expect(failure).toContain('בשיחה');
  });

  it('requires clarification before applying a broad physics exam template', () => {
    const broadPhysics = buildPlanChangeRequest(
      { goal: 'מבחן בפיזיקה', date: 'עוד שבוע' },
      'he',
    );
    const payload = proposalToUpdatePayload({
      reason: 'הכנה למבחן בפיזיקה',
      ...inferGoalMetaFromText(broadPhysics),
      prepend_concepts: inferConceptIdsFromText(broadPhysics),
    });

    expect(payload.prepend_concepts).toEqual([]);
    expect(planPayloadNeedsClarification(payload)).toBe('physics');
    expect(buildPlanClarificationNotice('he', 'physics')).toContain('מכניקה');
  });

  it('requires clarification before applying a broad math exam template', () => {
    const broadMath = buildPlanChangeRequest(
      { goal: 'מבחן במתמטיקה', date: 'עוד חודש' },
      'he',
    );
    const payload = proposalToUpdatePayload({
      reason: 'הכנה למבחן במתמטיקה',
      ...inferGoalMetaFromText(broadMath),
      prepend_concepts: inferConceptIdsFromText(broadMath),
    });

    expect(planPayloadNeedsClarification(payload)).toBe('math');
    expect(buildPlanClarificationNotice('he', 'math')).toContain('בגרות');
  });

  it('accepts physics mechanics scope without extra clarification', () => {
    const mechanics = buildPlanChangeRequest(
      {
        goal: 'פיזיקה בגרות מכניקה',
        date: 'עוד שבוע',
        notes: 'מוכן ללמוד כמה שצריך',
      },
      'he',
    );
    const meta = inferGoalMetaFromText(mechanics);
    const payload = proposalToUpdatePayload({
      reason: 'הכנה למבחן בפיזיקה מכניקה',
      ...meta,
      prepend_concepts: inferConceptIdsFromText(mechanics),
    });

    expect(payload.prepend_concepts?.length).toBeGreaterThan(0);
    expect(planPayloadNeedsClarification(payload)).toBeNull();
    expect(meta.hours_per_week).toBe(35);
  });
});

describe('planModificationProtocol (ReAct kill-switch)', () => {
  it('promises guided confirmable flow when ReAct is on', () => {
    const text = planModificationProtocol(true);
    expect(text).toBe(PLAN_AGENT_INSTRUCTIONS);
    expect(text).toMatch(/explicitly confirms/i);
  });

  it('does not promise a confirmable diff when ReAct is off', () => {
    const text = planModificationProtocol(false);
    expect(text).toBe(PLAN_AGENT_INSTRUCTIONS_UNAVAILABLE);
    expect(text).toMatch(/temporarily unavailable|paused/i);
    expect(text).not.toMatch(/call `propose_plan_change`/);
    expect(text).not.toMatch(/ask yes\/no/i);
  });
});
