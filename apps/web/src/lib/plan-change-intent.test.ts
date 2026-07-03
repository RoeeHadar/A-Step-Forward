import { describe, expect, it } from 'vitest';
import {
  learnerPlanChangeIntent,
  shouldApplyPlanImmediately,
  shouldApplyPlanChange,
} from './plan-actions';

const SHOULD_DETECT = [
  'יש לי מבחן בחדוא 1 עוד שבוע שנה לי את התוכנית בהתאם',
  'אני רוצה שתשנה לי את תוכנית הלימוד',
  'שנה את המטרה שלי — מבחן במתמטיקה בדידה בעוד 8 חודשים',
  'תעדכן את תוכנית השבוע שלי',
  'תתאם את המסלול למבחן בפיזיקה',
  'please update my weekly plan for calculus 1',
  'change my goal — I am not doing bagrut anymore',
  'reorganize my study schedule',
  'adjust my learning path to focus on limits',
  'הוסף קומבינטוריקה לתוכנית',
  'דחף את ההסתברות לשבוע הקרוב',
];

const SHOULD_NOT_DETECT = [
  'מה זה אינטגרל?',
  'can you explain Newton\'s second law?',
  'עזור לי עם שאלה 5',
  'thanks for the explanation',
  'what topics are in the curriculum',
];

describe('learnerPlanChangeIntent (broad detection)', () => {
  it.each(SHOULD_DETECT)('detects plan change: %s', (msg) => {
    expect(learnerPlanChangeIntent(msg)).toBe(true);
  });

  it.each(SHOULD_NOT_DETECT)('ignores non-plan chat: %s', (msg) => {
    expect(learnerPlanChangeIntent(msg)).toBe(false);
  });

  it('triggers immediate apply for detected plan-change requests', () => {
    for (const msg of SHOULD_DETECT) {
      expect(shouldApplyPlanImmediately(msg)).toBe(true);
    }
  });

  it('applies after tutor reply for any detected request', () => {
    const user = 'תעדכן את תוכנית הלימוד שלי לקראת הבחינה';
    const assistant = 'בטח, ספר לי עוד על המטרה.';
    expect(shouldApplyPlanChange(user, assistant)).toBe(true);
  });
});
