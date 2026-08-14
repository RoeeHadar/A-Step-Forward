import { describe, expect, it } from 'vitest';
import { buildPlanChangeRequest } from './plan-change-template';
import {
  learnerPlanChangeIntent,
  learnerPlanChangeIntentHeuristic,
  shouldApplyPlanImmediately,
  shouldApplyPlanChange,
} from './plan-actions';

const CALC1_TEMPLATE = buildPlanChangeRequest(
  {
    goal: 'מבחן בחדוא 1',
    date: 'עוד שבוע',
    topics: 'גבולות, נגזרות, אינטגרלים',
  },
  'he',
);

const CASUAL_REQUESTS = [
  'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם',
  'אני רוצה שתשנה לי את תוכנית הלימוד',
  'אני רוצה לשנות את התוכנית שלי',
  'please update my weekly plan for calculus 1',
  "I'd like to change my plan",
];

const NON_PLAN_CHAT = [
  'מה זה אינטגרל?',
  'can you explain Newton\'s second law?',
  'thanks for the explanation',
];

describe('template-only plan change detection', () => {
  it('detects only the official template', () => {
    expect(learnerPlanChangeIntent(CALC1_TEMPLATE)).toBe(true);
    for (const msg of CASUAL_REQUESTS) {
      expect(learnerPlanChangeIntent(msg)).toBe(false);
    }
  });

  it('still recognizes casual phrasing via heuristic helper (not for apply)', () => {
    for (const msg of CASUAL_REQUESTS) {
      expect(learnerPlanChangeIntentHeuristic(msg)).toBe(true);
    }
  });

  it('applies immediately only for template messages', () => {
    expect(shouldApplyPlanImmediately(CALC1_TEMPLATE)).toBe(true);
    for (const msg of CASUAL_REQUESTS) {
      expect(shouldApplyPlanImmediately(msg)).toBe(false);
    }
  });

  it('ignores general tutoring', () => {
    for (const msg of NON_PLAN_CHAT) {
      expect(learnerPlanChangeIntent(msg)).toBe(false);
      expect(shouldApplyPlanImmediately(msg)).toBe(false);
    }
  });

  it('applies only when the current message is the template', () => {
    const assistant = 'בטח, אעדכן את התוכנית בהתאם למבחן.';
    expect(shouldApplyPlanChange(CALC1_TEMPLATE)).toBe(true);
    expect(shouldApplyPlanChange(CALC1_TEMPLATE, assistant)).toBe(true);
  });

  it('does not apply casual request even after tutor reply', () => {
    const user = CASUAL_REQUESTS[0]!;
    const assistant = 'בטח, ספר לי עוד על המטרה.';
    expect(shouldApplyPlanChange(user, assistant)).toBe(false);
  });

  it('does not apply when casual text is prepended to the template', () => {
    const template = buildPlanChangeRequest(
      { goal: 'מבחן במתמטיקה', date: 'עוד חודש' },
      'he',
    );
    const combined = `יש לי מבחן מתמטיקה עוד חודש שנה לי את תוכנית הלימוד\n${template}`;
    expect(shouldApplyPlanImmediately(combined)).toBe(false);
    expect(shouldApplyPlanChange(combined)).toBe(false);
  });

  it('does not treat Bagrut readiness questions as plan-change intent', () => {
    expect(
      learnerPlanChangeIntentHeuristic(
        'הבגרות שלי עוד שבוע, האם התוכנית אכן תכין אותי בזמן למבחן?',
      ),
    ).toBe(false);
    expect(learnerPlanChangeIntentHeuristic('מה הסטטוס שלי כרגע')).toBe(false);
    expect(
      learnerPlanChangeIntentHeuristic('מה הסטטוס שלי בהקשר של התוכנית לימוד'),
    ).toBe(false);
    expect(
      learnerPlanChangeIntentHeuristic(
        'Will the plan prepare me in time for my Bagrut exam next week?',
      ),
    ).toBe(false);
    expect(
      learnerPlanChangeIntentHeuristic(
        'יש לי יעד באתר. אני רוצה לדעת איך ההתקדמות שלי לקראת היעד הזה יחסית לקצב ההתקדמות הנוכחי שלי',
      ),
    ).toBe(false);
  });
});
