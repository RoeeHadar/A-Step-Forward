import { describe, expect, it } from 'vitest';
import { qualityRepairInstruction, scoreResponseQuality } from './chat-response-quality';

describe('chat-response-quality (ADR-0015)', () => {
  it('rejects empty / too short', () => {
    expect(scoreResponseQuality('', 'he').ok).toBe(false);
    expect(scoreResponseQuality('קצר', 'he').failures).toContain('too_short');
  });

  it('rejects garbage Hebrew and filler', () => {
    const garbage = scoreResponseQuality('זה חשוך באחריות להביא לדמיון עכשיו', 'he');
    expect(garbage.ok).toBe(false);
    expect(garbage.failures).toContain('garbage_hebrew');

    const filler = scoreResponseQuality('אני חושב שזה יעזור לך מאוד מאוד ללמוד את זה עכשיו', 'he');
    expect(filler.failures).toContain('filler');
  });

  it('rejects prompt label leaks', () => {
    const leak = scoreResponseQuality('הצעה להמשך: ללמוד אינטגרלים עכשיו בבקשה', 'he');
    expect(leak.failures).toContain('raw_dump');
  });

  it('flags script mismatch for Hebrew locale', () => {
    const enOnly = scoreResponseQuality(
      'The derivative of x squared is two x. Here is a longer English explanation.',
      'he',
    );
    expect(enOnly.failures).toContain('script_mismatch');
  });

  it('accepts a coherent Hebrew answer', () => {
    const ok = scoreResponseQuality(
      'הממוצע הוא סכום הערכים חלקי מספרם. אם חסר ערך אחד, נבודד אותו מהמשוואה.',
      'he',
    );
    expect(ok.ok).toBe(true);
  });

  it('builds a repair instruction listing failures', () => {
    const he = qualityRepairInstruction('he', ['filler', 'raw_dump']);
    expect(he).toContain('quality repair');
    expect(he).toContain('filler');
    const en = qualityRepairInstruction('en', ['script_mismatch']);
    expect(en).toContain('English');
  });

  it('flags status denial and new-plan offers only on status turns', () => {
    const denial =
      'אני רואה שאין מידע על הסטטוס הנוכחי שלך. האם תרצה לדבר על מה שאתה לומד כרגע או לשאול שאלה ספציפית? אני כאן כדי לעזור.';
    expect(scoreResponseQuality(denial, 'he').failures).not.toContain('status_denial');
    expect(scoreResponseQuality(denial, 'he', { statusTurn: true }).failures).toContain(
      'status_denial',
    );

    const fishing =
      'לצורך קבלת סטטוס התקדמות שלך, אני זקוק למידע נוסף. מהו הקצב הנוכחי שלך בלימודים? כמה חומר תיאורטי אתה מספיק ללמוד בשבוע?';
    expect(scoreResponseQuality(fishing, 'he', { statusTurn: true }).failures).toContain(
      'status_denial',
    );

    const newPlan =
      'נראה שהתוכנית הנוכחית שלך לא נבנית עקב חוסר מידע על הנושאים שאתה צריך ללמוד. אם אתה רוצה, אני יכול לעזור לך לבנות תוכנית לימודים חדשה שתתאים לצרכים שלך.';
    const scored = scoreResponseQuality(newPlan, 'he', { statusTurn: true });
    expect(scored.failures).toContain('status_denial');
    expect(scored.failures).toContain('invented_plan_offer');

    const ok = scoreResponseQuality(
      'היעד שלך הוא בגרות מתמטיקה 5 יחידות ל־8 בינואר 2027. לפי הקצב בתוכנית אתה על המסלול, והצעד הבא הוא נושא אחד מהשבוע הפעיל.',
      'he',
      { statusTurn: true },
    );
    expect(ok.failures).not.toContain('status_denial');
    expect(ok.failures).not.toContain('invented_plan_offer');

    const repair = qualityRepairInstruction('he', ['status_denial']);
    expect(repair).toContain('אסור להגיד שאין מידע');
  });
});
