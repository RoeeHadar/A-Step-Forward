/**
 * Pure busy-interval helpers for Book-a-Lesson calendar integration.
 * No network — unit-testable.
 */

export type BusyInterval = { start: string; end: string }; // ISO UTC

/** Pure helper for Google Calendar push webhook auth (unit-tested). */
export function googleWebhookTokenAllowed(
  expected: string | undefined | null,
  channelToken: string,
): boolean {
  const exp = expected?.trim();
  if (!exp) return true;
  return Boolean(channelToken) && channelToken === exp;
}

export function intervalsOverlap(
  aStartMs: number,
  aEndMs: number,
  bStartMs: number,
  bEndMs: number,
): boolean {
  return aStartMs < bEndMs && bStartMs < aEndMs;
}

export function overlapsAnyBusy(
  start: Date,
  end: Date,
  busy: BusyInterval[],
): boolean {
  const a0 = start.getTime();
  const a1 = end.getTime();
  if (!(a0 < a1)) return false;
  for (const b of busy) {
    const b0 = Date.parse(b.start);
    const b1 = Date.parse(b.end);
    if (Number.isNaN(b0) || Number.isNaN(b1)) continue;
    if (intervalsOverlap(a0, a1, b0, b1)) return true;
  }
  return false;
}

/** Filter busy intervals that intersect [rangeStart, rangeEnd). */
export function busyInRange(
  busy: BusyInterval[],
  rangeStart: Date,
  rangeEnd: Date,
): BusyInterval[] {
  const r0 = rangeStart.getTime();
  const r1 = rangeEnd.getTime();
  return busy.filter((b) => {
    const b0 = Date.parse(b.start);
    const b1 = Date.parse(b.end);
    if (Number.isNaN(b0) || Number.isNaN(b1)) return false;
    return intervalsOverlap(r0, r1, b0, b1);
  });
}

export function mergeBusyIntervals(busy: BusyInterval[]): BusyInterval[] {
  const sorted = busy
    .map((b) => ({ start: Date.parse(b.start), end: Date.parse(b.end) }))
    .filter((b) => !Number.isNaN(b.start) && !Number.isNaN(b.end) && b.start < b.end)
    .sort((a, b) => a.start - b.start);
  if (sorted.length === 0) return [];
  const out: { start: number; end: number }[] = [{ ...sorted[0]! }];
  for (let i = 1; i < sorted.length; i++) {
    const cur = sorted[i]!;
    const last = out[out.length - 1]!;
    if (cur.start <= last.end) {
      last.end = Math.max(last.end, cur.end);
    } else {
      out.push({ ...cur });
    }
  }
  return out.map((b) => ({
    start: new Date(b.start).toISOString(),
    end: new Date(b.end).toISOString(),
  }));
}
