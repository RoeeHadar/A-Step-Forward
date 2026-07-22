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
