import { describe, expect, it } from 'vitest';
import {
  busyInRange,
  googleWebhookTokenAllowed,
  intervalsOverlap,
  mergeBusyIntervals,
  overlapsAnyBusy,
} from './lesson-booking-busy';

describe('intervalsOverlap', () => {
  it('detects overlap and adjacency', () => {
    expect(intervalsOverlap(0, 10, 5, 15)).toBe(true);
    expect(intervalsOverlap(0, 10, 10, 20)).toBe(false);
    expect(intervalsOverlap(0, 10, 11, 20)).toBe(false);
  });
});

describe('overlapsAnyBusy', () => {
  const busy = [
    { start: '2026-07-25T14:00:00.000Z', end: '2026-07-25T16:00:00.000Z' },
  ];

  it('flags a conflicting preferred window', () => {
    expect(
      overlapsAnyBusy(
        new Date('2026-07-25T15:00:00.000Z'),
        new Date('2026-07-25T17:00:00.000Z'),
        busy,
      ),
    ).toBe(true);
  });

  it('allows a free window', () => {
    expect(
      overlapsAnyBusy(
        new Date('2026-07-25T16:00:00.000Z'),
        new Date('2026-07-25T17:00:00.000Z'),
        busy,
      ),
    ).toBe(false);
  });
});

describe('mergeBusyIntervals', () => {
  it('merges overlapping blocks', () => {
    const merged = mergeBusyIntervals([
      { start: '2026-07-25T14:00:00.000Z', end: '2026-07-25T15:00:00.000Z' },
      { start: '2026-07-25T14:30:00.000Z', end: '2026-07-25T16:00:00.000Z' },
    ]);
    expect(merged).toEqual([
      { start: '2026-07-25T14:00:00.000Z', end: '2026-07-25T16:00:00.000Z' },
    ]);
  });
});

describe('busyInRange', () => {
  it('keeps only intersecting intervals', () => {
    const out = busyInRange(
      [
        { start: '2026-07-25T10:00:00.000Z', end: '2026-07-25T11:00:00.000Z' },
        { start: '2026-07-26T10:00:00.000Z', end: '2026-07-26T11:00:00.000Z' },
      ],
      new Date('2026-07-25T00:00:00.000Z'),
      new Date('2026-07-25T23:59:59.000Z'),
    );
    expect(out).toHaveLength(1);
  });
});

describe('googleWebhookTokenAllowed', () => {
  it('allows all requests when no expected token is configured', () => {
    expect(googleWebhookTokenAllowed(undefined, '')).toBe(true);
    expect(googleWebhookTokenAllowed('', 'anything')).toBe(true);
  });

  it('requires a matching token when configured', () => {
    expect(googleWebhookTokenAllowed('secret', '')).toBe(false);
    expect(googleWebhookTokenAllowed('secret', 'wrong')).toBe(false);
    expect(googleWebhookTokenAllowed('secret', 'secret')).toBe(true);
  });
});
