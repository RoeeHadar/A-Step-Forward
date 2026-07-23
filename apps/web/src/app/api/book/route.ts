/**
 * Book-a-Lesson API — create request + list mine.
 */
import { auth } from '@clerk/nextjs/server';
import { normalizeCreateLessonBooking, type CreateLessonBookingInput } from '@/lib/lesson-booking';
import {
  insertLessonBooking,
  lessonBookingsDbConfigured,
  listLessonBookingsForUser,
  toPublicBookingView,
} from '@/lib/lesson-bookings-db';
import { assertSlotFreeOnGoogle } from '@/lib/google-calendar';
import { checkSocialRateLimit } from '@/lib/social-rate-limit';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function clientKey(req: Request, userId: string | null): string {
  const fwd = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim();
  return `book:${userId ?? fwd ?? 'anon'}`;
}

export async function POST(req: Request) {
  if (!lessonBookingsDbConfigured) {
    return Response.json({ error: 'db_unavailable' }, { status: 503 });
  }

  const { userId } = await auth();
  const rl = checkSocialRateLimit(clientKey(req, userId), { limit: 8, windowMs: 60_000 });
  if (!rl.ok) {
    return Response.json(
      { error: 'rate_limited', retryAfterSec: rl.retryAfterSec },
      { status: 429, headers: { 'Retry-After': String(rl.retryAfterSec) } },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return Response.json({ error: 'invalid_json' }, { status: 400 });
  }

  const input: CreateLessonBookingInput = {
    requesterName: String(body.requesterName ?? body.name ?? ''),
    requesterEmail: String(body.requesterEmail ?? body.email ?? ''),
    requesterPhone: String(body.requesterPhone ?? body.phone ?? ''),
    locale: body.locale === 'en' ? 'en' : 'he',
    modality: body.modality as CreateLessonBookingInput['modality'],
    subjects: Array.isArray(body.subjects)
      ? (body.subjects as CreateLessonBookingInput['subjects'])
      : [],
    level: body.level as CreateLessonBookingInput['level'],
    universityName: body.universityName != null ? String(body.universityName) : undefined,
    universityCourse: body.universityCourse != null ? String(body.universityCourse) : undefined,
    goalText: String(body.goalText ?? ''),
    notes: body.notes != null ? String(body.notes) : undefined,
    durationH: Number(body.durationH) as CreateLessonBookingInput['durationH'],
    preferredDate: String(body.preferredDate ?? ''),
    preferredTime: String(body.preferredTime ?? ''),
    bookingForOther: Boolean(body.bookingForOther),
    learnerName: body.learnerName != null ? String(body.learnerName) : undefined,
    learnerGrade: body.learnerGrade != null ? String(body.learnerGrade) : undefined,
    shareDossier: Boolean(userId) && Boolean(body.shareDossier),
  };

  const normalized = normalizeCreateLessonBooking(input);
  if (!normalized.ok) {
    return Response.json({ error: normalized.error }, { status: 400 });
  }

  const slot = await assertSlotFreeOnGoogle(
    normalized.value.preferredStart,
    normalized.value.preferredEnd,
  );
  if (!slot.free) {
    if (slot.reason === 'busy') {
      return Response.json({ error: 'slot_busy' }, { status: 409 });
    }
    return Response.json({ error: 'calendar_unavailable' }, { status: 503 });
  }

  try {
    const row = await insertLessonBooking({
      data: normalized.value,
      clerkUserId: userId,
    });
    if (!row) {
      return Response.json({ error: 'insert_failed' }, { status: 500 });
    }
    return Response.json({
      ok: true,
      booking: toPublicBookingView(row),
      statusUrl: `/book/r/${row.public_token}`,
    });
  } catch (err) {
    logger.error('[api/book] POST failed', { err: String(err) });
    return Response.json({ error: 'internal' }, { status: 500 });
  }
}

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: 'unauthorized' }, { status: 401 });
  }
  if (!lessonBookingsDbConfigured) {
    return Response.json({ error: 'db_unavailable' }, { status: 503 });
  }
  const rows = await listLessonBookingsForUser(userId);
  return Response.json({
    bookings: rows.map(toPublicBookingView),
  });
}
