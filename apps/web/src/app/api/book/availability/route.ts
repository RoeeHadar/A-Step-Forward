/**
 * GET /api/book/availability — public free/busy for the booking calendar UI.
 * Query: from, to (ISO) — defaults to now → +8 weeks.
 */
import { LESSON_MAX_AHEAD_MS } from '@/lib/lesson-booking';
import { busyInRange } from '@/lib/lesson-booking-busy';
import { getBusyIntervals } from '@/lib/google-calendar';
import { checkSocialRateLimit } from '@/lib/social-rate-limit';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const fwd = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? 'anon';
  const rl = checkSocialRateLimit(`book-avail:${fwd}`, { limit: 60, windowMs: 60_000 });
  if (!rl.ok) {
    return Response.json(
      { error: 'rate_limited', retryAfterSec: rl.retryAfterSec },
      { status: 429 },
    );
  }

  const url = new URL(req.url);
  const now = Date.now();
  const fromParam = url.searchParams.get('from');
  const toParam = url.searchParams.get('to');
  const force = url.searchParams.get('force') === '1';

  const timeMin = fromParam ? new Date(fromParam) : new Date(now);
  let timeMax = toParam ? new Date(toParam) : new Date(now + LESSON_MAX_AHEAD_MS);

  if (Number.isNaN(timeMin.getTime()) || Number.isNaN(timeMax.getTime())) {
    return Response.json({ error: 'invalid_range' }, { status: 400 });
  }
  if (timeMax.getTime() <= timeMin.getTime()) {
    return Response.json({ error: 'invalid_range' }, { status: 400 });
  }
  // Cap window to 8 weeks to protect FreeBusy quota
  const maxSpan = LESSON_MAX_AHEAD_MS + 24 * 60 * 60 * 1000;
  if (timeMax.getTime() - timeMin.getTime() > maxSpan) {
    timeMax = new Date(timeMin.getTime() + maxSpan);
  }

  const result = await getBusyIntervals({
    timeMin,
    timeMax,
    forceRefresh: force,
  });

  const busy = busyInRange(result.busy, timeMin, timeMax);

  return Response.json({
    busy,
    source: result.source,
    syncedAt: result.syncedAt,
    timeMin: timeMin.toISOString(),
    timeMax: timeMax.toISOString(),
    timeZone: 'Asia/Jerusalem',
  });
}
