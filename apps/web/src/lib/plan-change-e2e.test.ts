/**
 * End-to-end plan-change path (no LLM): Hebrew calc1 exam template → payload → optional Neon write.
 */
import { describe, expect, it } from 'vitest';
import {
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
  inferGoalMetaFromText,
  inferConceptIdsFromText,
  proposalToUpdatePayload,
} from './plan-actions';
import { buildPlanChangeRequest } from './plan-change-template';
import { resolvePayloadForApply, executePlanUpdate } from './plan-apply';

const CALC1_USER = buildPlanChangeRequest(
  {
    goal: 'מבחן בחדוא 1',
    date: 'עוד שבוע',
    topics: 'גבולות, נגזרות, אינטגרלים',
  },
  'he',
);
const CALC1_ASSISTANT =
  'אני הולך לשנות את התוכנית שלך. התוכנית החדשה תכלול חזרה על נושאים חשובים למבחן.';

const hasDb = (() => {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  return /^postgres(ql)?:\/\/.+@/.test(url);
})();

describe('plan change e2e (calc1 exam, Hebrew template)', () => {
  it('detects official template and tutor acknowledgment', () => {
    expect(shouldApplyPlanChange(CALC1_USER, CALC1_ASSISTANT)).toBe(true);
  });

  it('builds a calc1 payload with dates and priority concepts', () => {
    const meta = inferGoalMetaFromText(CALC1_USER, CALC1_ASSISTANT);
    const payload = proposalToUpdatePayload({
      reason: 'הכנה למבחן בחדו״א 1',
      ...meta,
      prepend_concepts: inferConceptIdsFromText(CALC1_USER, CALC1_ASSISTANT),
    });
    expect(payload.confirmed).toBe(true);
    expect(payload.goal_key).toBe('calculus1');
    expect(payload.final_goal_date).toBeTruthy();
    expect(payload.next_test_date).toBeTruthy();
    expect(payload.prepend_concepts).toEqual(
      expect.arrayContaining(['limits', 'derivatives_intro', 'integrals_intro']),
    );
    expect(inferConceptIdsFromText(CALC1_USER)).toContain('limits');
  });

  it('does not apply casual phrasing without template', () => {
    const casual = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    expect(shouldApplyPlanChange(casual, 'מעולה, נתחיל מגבולות.')).toBe(false);
    expect(shouldApplyPlanImmediately(casual)).toBe(false);
  });

  it('applies immediately when template is sent', () => {
    expect(
      shouldApplyPlanChange(
        CALC1_USER,
        'האם אתה רוצה להתמקד בגבולות או בנגזרות?',
      ),
    ).toBe(true);
    expect(shouldApplyPlanImmediately(CALC1_USER)).toBe(true);
  });
});

describe.skipIf(!hasDb)('plan change e2e (live Neon write)', () => {
  it('executes calc1 plan update and returns week preview', async () => {
    const { neon } = await import('@neondatabase/serverless');
    const sql = neon(process.env.DATABASE_URL ?? process.env.POSTGRES_URL!);

    let rows: Array<{ learner_id: string }>;
    try {
      rows = (await sql`
        SELECT lp.learner_id
        FROM learning_plans lp
        JOIN learner_profiles p ON p.learner_id = lp.learner_id
        WHERE lp.status = 'active'
        ORDER BY lp.updated_at DESC NULLS LAST
        LIMIT 1
      `) as Array<{ learner_id: string }>;
    } catch (err) {
      console.warn('[plan-change-e2e] Neon unreachable — skipping live write:', String(err));
      return;
    }

    const learnerId = rows[0]?.learner_id;
    if (!learnerId) return;

    const payload = await resolvePayloadForApply(learnerId, CALC1_USER);
    expect(payload).not.toBeNull();

    const result = await executePlanUpdate(learnerId, payload!, {
      agent: 'tutor',
      source: 'chat',
    });

    expect(result.applied).toBe(true);
    expect(result.weekSummaries?.length).toBeGreaterThan(0);
    expect(result.noticeHe).toContain('המטרה והתוכנית השבועית עודכנו');

    const weekIds = result.weekSummaries!.flatMap((w) => w.conceptIds);
    expect(weekIds.some((id) => /limits|derivatives|integrals/.test(id))).toBe(true);
  }, 90_000);
});
