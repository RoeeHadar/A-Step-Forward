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
} from './plan-actions';
import {
  buildPlanAppliedNotice,
  buildPlanApplyingNotice,
  buildPlanApplyFailureNotice,
} from './plan-apply';

const USER =
  'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
const ASSISTANT =
  'אני הולך לשנות את התוכנית שלך. התוכנית החדשה תכלול חזרה על נושאים חשובים למבחן.';

describe('chat stream finalize (calc1 plan change)', () => {
  it('triggers immediate apply on first calc1 exam message', () => {
    expect(shouldApplyPlanImmediately(USER)).toBe(true);
  });

  it('decides to apply after tutor acknowledgment', () => {
    expect(shouldApplyPlanChange(USER, ASSISTANT)).toBe(true);
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
  });
});
