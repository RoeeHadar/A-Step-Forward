/**
 * GET /api/book/r/[token] — public status for a booking request (secret link).
 */
import {
  getLessonBookingByToken,
  lessonBookingsDbConfigured,
  toPublicBookingView,
} from '@/lib/lesson-bookings-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Ctx = { params: Promise<{ token: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  if (!lessonBookingsDbConfigured) {
    return Response.json({ error: 'db_unavailable' }, { status: 503 });
  }
  const { token } = await ctx.params;
  if (!token || token.length < 16) {
    return Response.json({ error: 'not_found' }, { status: 404 });
  }
  const row = await getLessonBookingByToken(token);
  if (!row) {
    return Response.json({ error: 'not_found' }, { status: 404 });
  }
  return Response.json({ booking: toPublicBookingView(row) });
}
