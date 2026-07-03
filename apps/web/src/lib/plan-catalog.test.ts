import { describe, expect, it } from 'vitest';
import {
  canonicalConceptId,
  goalKeyToPointsGroup,
  isKnownConceptId,
  isValidGoalKey,
  sanitizeConceptIds,
  sanitizePlanUpdatePayload,
} from './plan-catalog';
import {
  extractPlanUpdate,
  inferConceptIdsFromText,
  inferGoalMetaFromText,
  learnerConfirmedChange,
  learnerExplicitChangeRequest,
  looksLikePlanApplyIntent,
  looksLikePlanProposal,
  proposalToUpdatePayload,
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
} from './plan-actions';

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
    expect(learnerConfirmedChange('כן, אני מסכים')).toBe(true);
    expect(learnerConfirmedChange('maybe later')).toBe(false);
  });

  it('infers discrete-math concepts from Hebrew topic names', () => {
    const ids = inferConceptIdsFromText(
      'תורת הקבוצות, תורת הגרפים, קומבינטוריקה',
      'מתמטיקה בדידה באוניברסיטה הפתוחה',
    );
    expect(ids).toContain('combinatorics');
    expect(ids).toContain('probability_basic');
  });

  it('detects plan proposal language', () => {
    const text =
      'אני מציע להוסיף קומבינטוריקה. האם אתה מסכים?';
    expect(looksLikePlanProposal(text)).toBe(true);
  });

  it('converts stored proposal to confirmed update payload', () => {
    const payload = proposalToUpdatePayload({
      reason: 'discrete math prep',
      prepend_concepts: ['combinatorics'],
    });
    expect(payload.confirmed).toBe(true);
    expect(payload.prepend_concepts).toEqual(['combinatorics']);
  });

  it('infers goal and 8-month horizon from Hebrew goal-change request', () => {
    const userMsg =
      'שנה את המטרה שלי במערכת - אני לא עושה בגרות עוד תשעה ימים, המטרה החדשה שלי היא מבחן במתמטיקה בדידה בעוד 8 חודשים';
    const meta = inferGoalMetaFromText(userMsg);
    expect(meta.goal).toContain('מתמטיקה בדידה');
    expect(meta.goal_key).toBe('university_prep');
    expect(meta.clear_next_test).toBe(true);
    expect(meta.final_goal_date).toBeTruthy();
    expect(learnerExplicitChangeRequest(userMsg)).toBe(true);
  });

  it('applies plan when user gives explicit goal change and tutor commits', () => {
    const userMsg =
      'שנה את המטרה שלי - המטרה החדשה שלי היא מבחן במתמטיקה בדידה בעוד 8 חודשים';
    const assistant =
      'המטרה החדשה שלך היא מבחן במתמטיקה בדידה. אני אעדכן את התוכנית השבועית שלך בהתאם.';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
    expect(looksLikePlanApplyIntent(assistant)).toBe(true);
    const payload = proposalToUpdatePayload({
      reason: 'goal change',
      ...inferGoalMetaFromText(userMsg, assistant),
      prepend_concepts: inferConceptIdsFromText(userMsg),
    });
    expect(payload.goal).toBeTruthy();
    expect(payload.clear_next_test).toBe(true);
    expect(payload.prepend_concepts).toContain('combinatorics');
  });

  it('applies calc1 exam plan when user asks to change plan for exam in one week', () => {
    const userMsg = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    const assistant =
      'אני הולך לשנות את התוכנית שלך. התוכנית החדשה תכלול חזרה על נושאים חשובים למבחן.';
    expect(learnerExplicitChangeRequest(userMsg)).toBe(true);
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
    const meta = inferGoalMetaFromText(userMsg, assistant);
    expect(meta.goal_key).toBe('calculus1');
    expect(meta.final_goal_date).toBeTruthy();
    expect(meta.next_test_date).toBeTruthy();
  });

  it('applies when user message includes both request and plan-change intent', () => {
    const userMsg =
      'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם\nאני הולך לשנות את התוכנית שלך.';
    const assistant = 'מעולה, נתחיל מגבולות ונגזרות.';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
  });

  it('applies with minimal tutor ack when goal is inferable from user message', () => {
    const userMsg = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    const assistant = 'אני הולך לשנות את התוכנית שלך.';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
  });

  it('applies immediately on first message without waiting for tutor Q&A', () => {
    const userMsg = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    expect(shouldApplyPlanImmediately(userMsg)).toBe(true);
    const assistant =
      'לפני שאני אציג לך את התוכנית, האם תוכל לספר לי על הנושאים שקשים לך?';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
  });

  it('detects "אני רוצה שתשנה לי את תוכנית הלימוד"', () => {
    const userMsg = 'אני רוצה שתשנה לי את תוכנית הלימוד';
    expect(learnerExplicitChangeRequest(userMsg)).toBe(true);
  });

  it('does not apply immediately when goal is not inferable', () => {
    expect(shouldApplyPlanImmediately('שנה את התוכנית')).toBe(false);
  });

  it('applies on follow-up turn when prior user message was explicit', () => {
    const priorUser = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    const userMsg = 'כן';
    const assistant = 'אני הולך לשנות את התוכנית שלך.';
    expect(shouldApplyPlanChange(userMsg, assistant, priorUser)).toBe(true);
  });
});
