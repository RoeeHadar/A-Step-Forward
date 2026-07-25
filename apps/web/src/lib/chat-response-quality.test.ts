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
});
