import { describe, expect, it } from 'vitest';
import {
  LESSON_HOURLY_RATE_ILS,
  normalizeCreateLessonBooking,
  preferredWindowUtc,
  priceIlsForDuration,
  wallTimeInZoneToUtc,
} from './lesson-booking';

describe('priceIlsForDuration', () => {
  it('charges 200 ILS per hour', () => {
    expect(priceIlsForDuration(1)).toBe(200);
    expect(priceIlsForDuration(1.5)).toBe(300);
    expect(priceIlsForDuration(2.5)).toBe(500);
    expect(priceIlsForDuration(3)).toBe(600);
    expect(LESSON_HOURLY_RATE_ILS).toBe(200);
  });
});

describe('wallTimeInZoneToUtc', () => {
  it('maps Jerusalem winter time (UTC+2) correctly', () => {
    // 2026-01-15 17:00 Asia/Jerusalem ≈ 15:00 UTC (IST)
    const d = wallTimeInZoneToUtc('2026-01-15', '17:00', 'Asia/Jerusalem');
    expect(d.toISOString()).toBe('2026-01-15T15:00:00.000Z');
  });

  it('maps Jerusalem summer time (UTC+3) correctly', () => {
    // 2026-07-15 17:00 Asia/Jerusalem ≈ 14:00 UTC (IDT)
    const d = wallTimeInZoneToUtc('2026-07-15', '17:00', 'Asia/Jerusalem');
    expect(d.toISOString()).toBe('2026-07-15T14:00:00.000Z');
  });
});

describe('preferredWindowUtc', () => {
  const now = Date.parse('2026-07-20T10:00:00.000Z');

  it('rejects times sooner than 24h', () => {
    const r = preferredWindowUtc('2026-07-20', '18:00', 1, now);
    expect(r).toEqual({ error: 'too_soon' });
  });

  it('rejects times further than 8 weeks', () => {
    const r = preferredWindowUtc('2026-10-01', '17:00', 1, now);
    expect(r).toEqual({ error: 'too_far' });
  });

  it('accepts a valid window and sets end from duration', () => {
    const r = preferredWindowUtc('2026-07-23', '17:00', 2, now);
    expect('error' in r).toBe(false);
    if ('error' in r) return;
    expect(r.end.getTime() - r.start.getTime()).toBe(2 * 60 * 60 * 1000);
  });
});

describe('normalizeCreateLessonBooking', () => {
  const now = Date.parse('2026-07-20T10:00:00.000Z');
  const base = {
    requesterName: 'Roee Test',
    requesterEmail: 'student@example.com',
    requesterPhone: '0501234567',
    locale: 'he' as const,
    modality: 'online' as const,
    subjects: ['math' as const],
    level: 'bagrut' as const,
    goalText: 'Bagrut prep',
    durationH: 1.5 as const,
    preferredDate: '2026-07-25',
    preferredTime: '17:00',
  };

  it('requires university fields when level is university', () => {
    const r = normalizeCreateLessonBooking({ ...base, level: 'university' }, now);
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.error).toBe('university_name_required');
  });

  it('normalizes a valid guest request', () => {
    const r = normalizeCreateLessonBooking(
      {
        ...base,
        level: 'university',
        universityName: 'Technion',
        universityCourse: 'Calculus 1',
      },
      now,
    );
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.value.priceIls).toBe(300);
    expect(r.value.universityName).toBe('Technion');
    expect(r.value.learnerName).toBe('Roee Test');
  });

  it('requires learner name when booking for other', () => {
    const r = normalizeCreateLessonBooking(
      { ...base, bookingForOther: true, learnerName: '' },
      now,
    );
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.error).toBe('learner_name_required');
  });
});
