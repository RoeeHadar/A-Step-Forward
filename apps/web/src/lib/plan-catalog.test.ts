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
  learnerAffirmedProposal,
  learnerCanceledPlanFlow,
  learnerPlanChangeIntentHeuristic,
  looksLikePlanApplyIntent,
  looksLikePlanProposal,
  proposalToUpdatePayload,
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
  learnerPlanChangeIntent,
  planPayloadToOptions,
  CALC1_EXAM_CONCEPTS,
  DISCRETE_EXAM_CONCEPTS,
  PHYSICS_MECHANICS_EXAM_CONCEPTS,
} from '@/lib/plan-actions';
import { buildPlanChangeRequest } from '@/lib/plan-change-template';

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

  it('affirms a bare yes but treats slot edits as non-confirmation', () => {
    // bare confirmations apply the staged proposal
    expect(learnerAffirmedProposal('yes')).toBe(true);
    expect(learnerAffirmedProposal('yes, update my plan')).toBe(true);
    expect(learnerAffirmedProposal('כן, אני מסכים')).toBe(true);
    // edits carrying new slot content must NOT apply the old proposal
    expect(learnerAffirmedProposal('update the date to September')).toBe(false);
    expect(learnerAffirmedProposal('עדכן ל-20 בספטמבר')).toBe(false);
    expect(learnerAffirmedProposal('yes but change it to Calculus 1')).toBe(false);
    // plain non-confirmations
    expect(learnerAffirmedProposal('maybe later')).toBe(false);
  });

  it('cancels the guided flow only on strong/short cancels, not on edits', () => {
    // strong / short cancels end the flow
    expect(learnerCanceledPlanFlow('no')).toBe(true);
    expect(learnerCanceledPlanFlow('cancel')).toBe(true);
    expect(learnerCanceledPlanFlow('never mind')).toBe(true);
    expect(learnerCanceledPlanFlow('לא')).toBe(true);
    expect(learnerCanceledPlanFlow('ביטול')).toBe(true);
    // an EDIT keeps the session so we re-collect instead of losing slots
    expect(learnerCanceledPlanFlow('no, change the date to September 20')).toBe(false);
    expect(learnerCanceledPlanFlow('actually make it Calculus 1 exam')).toBe(false);
  });

  it('infers discrete-math concepts from Hebrew topic names', () => {
    const ids = inferConceptIdsFromText(
      'תורת הקבוצות, תורת הגרפים, קומבינטוריקה',
      'מתמטיקה בדידה באוניברסיטה הפתוחה',
    );
    expect(ids).toContain('combinatorics');
    expect(ids).toContain('probability_basic');
  });

  it('infers physics concepts only when the exam scope is specific', () => {
    expect(inferConceptIdsFromText('מבחן בפיזיקה עוד שבוע')).toEqual([]);

    const mechanics = inferConceptIdsFromText('מבחן בפיזיקה במכניקה 036-361 עוד שבוע');
    expect(mechanics).toEqual(expect.arrayContaining([...PHYSICS_MECHANICS_EXAM_CONCEPTS]));

    const electricity = inferConceptIdsFromText('physics electricity test in a week');
    expect(electricity).toEqual(
      expect.arrayContaining(['electrostatics', 'electric_field', 'electric_circuits']),
    );
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
    expect(learnerPlanChangeIntentHeuristic(userMsg)).toBe(true);
  });

  it('applies plan when user sends template and tutor commits', () => {
    const userMsg = buildPlanChangeRequest(
      {
        goal: 'מבחן במתמטיקה בדידה',
        date: 'בעוד 8 חודשים',
        details: 'אני לא עושה בגרות יותר',
      },
      'he',
    );
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

  it('applies calc1 exam plan when user sends official template', () => {
    const userMsg = buildPlanChangeRequest(
      { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
      'he',
    );
    const assistant =
      'אני הולך לשנות את התוכנית שלך. התוכנית החדשה תכלול חזרה על נושאים חשובים למבחן.';
    expect(learnerPlanChangeIntent(userMsg)).toBe(true);
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
    const meta = inferGoalMetaFromText(userMsg, assistant);
    expect(meta.goal_key).toBe('calculus1');
    expect(meta.final_goal_date).toBeTruthy();
    expect(meta.next_test_date).toBeTruthy();
  });

  it('infers calculus1 goal_key when template uses Hebrew gershayim (חדו״א)', () => {
    const userMsg = buildPlanChangeRequest(
      { goal: 'מבחן בחדו״א 1', date: 'עוד שבוע' },
      'he',
    );
    const meta = inferGoalMetaFromText(userMsg);
    expect(meta.goal).toContain('חדו');
    expect(meta.goal_key).toBe('calculus1');
    expect(meta.final_goal_date).toBeTruthy();
  });

  it('builds one-week exam cram options for calc1 test in seven days', () => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    const iso = d.toISOString().slice(0, 10);
    const opts = planPayloadToOptions({
      confirmed: true,
      reason: 'calc1 cram',
      goal: 'מבחן בחדוא 1',
      goal_key: 'calculus1',
      final_goal_date: iso,
      next_test_date: iso,
      prepend_concepts: [...CALC1_EXAM_CONCEPTS],
      priority_concepts: [],
    });
    // numWeeksOverride intentionally removed (Bug 4 fix): materialising up to 24 weeks
    // caused FUNCTION_INVOCATION_TIMEOUT. Rolling window (2 weeks) is enforced by
    // generateLearningPlan; the exam horizon is stored on the profile as end_date only.
    expect(opts.numWeeksOverride).toBeUndefined();
    expect(opts.focusConceptsOnly).toBe(true);
    expect(opts.prependConcepts).toEqual(expect.arrayContaining(['limits', 'integrals_intro']));
  });

  it('does not apply casual phrasing without the template', () => {
    const userMsg = 'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם';
    const assistant = 'מעולה, נתחיל מגבולות ונגזרות.';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(false);
  });

  it('applies immediately on first template message', () => {
    const userMsg = buildPlanChangeRequest(
      { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
      'he',
    );
    expect(shouldApplyPlanImmediately(userMsg)).toBe(true);
    const assistant =
      'לפני שאני אציג לך את התוכנית, האם תוכל לספר לי על הנושאים שקשים לך?';
    expect(shouldApplyPlanChange(userMsg, assistant)).toBe(true);
  });

  it('parses compact template with עוד שבועיים for discrete math', () => {
    const userMsg = `[[ASF-PLAN-UPDATE | עדכון תוכנית לימוד]]
אני מבקש/ת לעדכן את תוכנית הלימוד והמטרה שלי.
מטרה או מבחן:מבחן במתמטיקה בדידה מועד:עוד שבועיים
[[/ASF-PLAN-UPDATE]]`;
    const meta = inferGoalMetaFromText(userMsg);
    expect(meta.goal).toContain('מתמטיקה בדידה');
    expect(meta.final_goal_date).toBeTruthy();
    expect(meta.next_test_date).toBeTruthy();
    const opts = planPayloadToOptions({
      confirmed: true,
      reason: 'discrete cram',
      goal: meta.goal,
      goal_key: 'university_prep',
      final_goal_date: meta.final_goal_date,
      next_test_date: meta.next_test_date,
      prepend_concepts: [...DISCRETE_EXAM_CONCEPTS],
    });
    // numWeeksOverride intentionally undefined (Bug 4 fix) — rolling window enforced by planner.
    expect(opts.numWeeksOverride).toBeUndefined();
    expect(opts.prependConcepts).toEqual(expect.arrayContaining(['combinatorics']));
  });

  it('does not treat casual plan phrasing as official template', () => {
    const userMsg = 'אני רוצה שתשנה לי את תוכנית הלימוד';
    expect(learnerPlanChangeIntent(userMsg)).toBe(false);
    expect(learnerPlanChangeIntentHeuristic(userMsg)).toBe(true);
  });

  it('applies immediately only for official template messages', () => {
    const template = buildPlanChangeRequest({ goal: 'מבחן בבגרות' }, 'he');
    expect(learnerPlanChangeIntent(template)).toBe(true);
    expect(shouldApplyPlanImmediately(template)).toBe(true);

    const phrases = [
      'שנה את התוכנית',
      'תעדכן לי את תוכנית הלימוד',
      'please adjust my study plan for the exam',
    ];
    for (const msg of phrases) {
      expect(learnerPlanChangeIntent(msg)).toBe(false);
      expect(shouldApplyPlanImmediately(msg)).toBe(false);
    }
  });

  it('does not treat general tutoring as plan change', () => {
    const phrases = [
      'מה זה נגזרת?',
      'explain the chain rule',
      'תוכל לעזור לי עם תרגיל 3',
      'how do I solve this integral',
    ];
    for (const msg of phrases) {
      expect(learnerPlanChangeIntent(msg)).toBe(false);
      expect(shouldApplyPlanImmediately(msg)).toBe(false);
    }
  });

  it('does not apply on follow-up turn without resending the template', () => {
    const priorUser = buildPlanChangeRequest(
      { goal: 'מבחן בחדוא 1', date: 'עוד שבוע' },
      'he',
    );
    const userMsg = 'כן';
    const assistant = 'אני הולך לשנות את התוכנית שלך.';
    expect(shouldApplyPlanChange(userMsg, assistant, priorUser)).toBe(false);
  });
});
