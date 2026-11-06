import { describe, expect, it } from 'vitest';
import { formatJerusalem } from './booking-email';

// AS-61: neon 0.10.4 returns timestamptz as Date; formatting must accept it.
describe('booking-email formatJerusalem', () => {
  it('formats a Date input in Asia/Jerusalem, same as its ISO string', () => {
    const d = new Date('2026-11-04T08:30:00.000Z');
    const out = formatJerusalem(d);
    expect(out).toBe(formatJerusalem(d.toISOString()));
    expect(out).toContain('10:30');
    expect(out).not.toContain('T08:30');
  });
  it('returns the raw value for an unparseable input', () => {
    expect(formatJerusalem('not-a-date')).toBe('not-a-date');
  });
});
