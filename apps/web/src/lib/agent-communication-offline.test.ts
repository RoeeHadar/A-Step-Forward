/**
 * Offline ADR-0011 "tester" — scores known bad transcript replies vs good targets.
 * No network. Complements the live suite in agent-communication.llm.integration.test.ts.
 */
import { describe, expect, it } from 'vitest';
import { scoreCommunicationReply } from './agent-communication-score';

/** Excerpt from the user-reported failure transcript. */
const BAD_STATUS = `שער שבוע 1: 100% (עבר/ה) שער שבוע 1: 94% (עבר/ה)
XP של הלומד:
סה"כ XP: 985
רמה 10 (עוד 15 לרמה הבאה)
תאריך הבגרות: Tue Sep 15 2026 00:00:00 GMT+0000 (Coordinated Universal Time)
תאריך היעד הסופי: Wed Jun 30 2027 00:00:00 GMT+0000 (Coordinated Universal Time)`;

const BAD_BAGRUT = `בערך 100%. אתה כבר עברת 100% בשער שבוע 1... אני חושב שתהיה בקצב טוב לבגרות.
אני חושב שזה יעזור.`;

const BAD_EXTRA = `אני לא ממליץ לך ללמוד עוד חומר... אבל יש חומרים שאולי יכולים לעזור.
אני ממליץ לך ללמוד על סדרות גאומטריות. זה חומר שאולי יכול לעזור לך להבנה טוב יותר של אינטגרלים.
אני חושב שזה יהיה עזר.`;

const BAD_SIMPLE = `אנו מחשבים את שטח הטרפז באופן פשוט.
שטח הטרפז הוא 1.
אז, אנו מסיק ש אינטגרל של f(x)=x^2 בין 0 ל-1 הוא 1.
אני חושב שזה יעזור.`;

const GOOD_STATUS = `אתה ברמה 10, עברת את שער שבוע 1 (~94%), ועובד על שבוע 2 (מבוא לאינטגרציה ונגזרות).
מוכנות הבגרות עדיין בבנייה — לא מבטיחים תוצאה, אבל הקצב נראה סביר.
הצעד הבא: תרגול קצר על מבוא לאינטגרציה מהשבוע הפעיל.`;

const GOOD_BAGRUT = `אי אפשר להבטיח ציון בבגרות. לפי המוכנות (~42%, שלב בנייה) והקצב הנוכחי אתה בכיוון סביר, ועדיין יש פערים לחזק.
המלצה אחת: תרגול ממוקד על מבוא לאינטגרציה השבוע.`;

const GOOD_SIMPLE = `נזנח את הסבר הסדרות — הוא לא נחוץ כאן.
הדרך הפשוטה והנכונה: כלל החזקה.
$$\\int_0^1 x^2\\,dx = \\Big[\\frac{x^3}{3}\\Big]_0^1 = \\frac{1}{3}$$
רוצה לנסות תרגיל דומה בעצמך?`;

/** ADR-0012 pressure-family bad / good targets from post-0011 transcript. */
const BAD_PRESSURE = `אני לא יודע את התוכנית שלך כרגע.
היעד: bagrut_math_5
פערים: עדיין לא סומנו
אתה כבר למדת את החומר של 5pt.
אל תדאג, אתה יכול לעשות הכל.
בחר נושא:
1. נגזרות
2. אינטגרלים
3. סדרות
זה חשוך באחריות להביא לדמיון חששותי.`;

const GOOD_PRESSURE = `אני מבין שאתה לחוץ מהלו״ז — זה הגיוני.
יש לי את התוכנית שלך: מסלול 5 יח׳, שבוע פעיל על מבוא לאינטגרציה, והקצב בסיכון לפיגור — בלי הבטחות על הבגרות.
הצעד הבא האחד: תרגול קצר על מבוא לאינטגרציה.
רוצה שנתחיל בזה עכשיו?`;

describe('ADR-0011 offline communication tester', () => {
  it('rejects the original transcript failure modes', () => {
    expect(scoreCommunicationReply(BAD_STATUS, ['no_dump', 'no_filler']).ok).toBe(false);
    expect(scoreCommunicationReply(BAD_BAGRUT, ['no_guarantee', 'no_filler']).ok).toBe(false);
    expect(scoreCommunicationReply(BAD_EXTRA, ['no_fake_bridge', 'no_filler']).ok).toBe(false);
    expect(
      scoreCommunicationReply(BAD_SIMPLE, ['no_wrong_area', 'no_filler', 'has_correct_third'])
        .ok,
    ).toBe(false);
  });

  it('accepts improved target replies', () => {
    expect(scoreCommunicationReply(GOOD_STATUS, ['no_dump', 'no_filler', 'no_guarantee']).ok).toBe(
      true,
    );
    expect(
      scoreCommunicationReply(GOOD_BAGRUT, ['no_guarantee', 'no_filler', 'no_dump']).ok,
    ).toBe(true);
    expect(
      scoreCommunicationReply(GOOD_SIMPLE, [
        'no_wrong_area',
        'no_filler',
        'no_fake_bridge',
        'has_correct_third',
      ]).ok,
    ).toBe(true);
  });
});

describe('ADR-0012 offline pressure-family tester', () => {
  const pressureChecks = [
    'no_deny_knowledge',
    'no_dump',
    'no_points_misread',
    'no_topic_menu',
    'no_empty_reassurance',
    'no_garbage_hebrew',
    'no_filler',
  ] as const;

  it('rejects contract non-compliance under pressure', () => {
    const scored = scoreCommunicationReply(BAD_PRESSURE, [...pressureChecks]);
    expect(scored.ok).toBe(false);
    expect(scored.failures).toEqual(
      expect.arrayContaining([
        'deny_knowledge',
        'raw_dump',
        'points_misread',
        'topic_menu',
        'empty_reassurance',
        'garbage_hebrew',
      ]),
    );
  });

  it('accepts 4-beat grounded pressure reply', () => {
    expect(scoreCommunicationReply(GOOD_PRESSURE, [...pressureChecks]).ok).toBe(true);
  });
});
