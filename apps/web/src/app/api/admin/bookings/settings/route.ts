/**
 * Admin Book-a-Lesson settings: contact secrets + calendar status + watch renew.
 */
import { getAuthContext, requireRole } from '@/lib/auth';
import {
  ensureGoogleCalendarWatch,
  getBusyIntervals,
  googleCalendarOAuthConfigured,
} from '@/lib/google-calendar';
import { LESSON_MAX_AHEAD_MS } from '@/lib/lesson-booking';
import {
  getLessonBookingSettings,
  updateBookingContactSecrets,
} from '@/lib/lesson-booking-settings-db';
import { listLessonBookingsAdmin, toPublicBookingView } from '@/lib/lesson-bookings-db';
import { bookingSecretsConfigured } from '@/lib/booking-secrets-crypto';
import { bookingNotifyEmail, bookingFromAddress, resendConfigured, sendBookingTestEmail, usesResendTestFrom } from '@/lib/booking-email';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function requireAdmin() {
  const auth = await getAuthContext();
  if (!auth) return { error: Response.json({ error: 'unauthorized' }, { status: 401 }) };
  try {
    requireRole(auth, ['admin']);
  } catch {
    return { error: Response.json({ error: 'forbidden' }, { status: 403 }) };
  }
  return { auth };
}

export async function GET() {
  const gate = await requireAdmin();
  if ('error' in gate && gate.error) return gate.error;

  const settings = await getLessonBookingSettings();
  const now = Date.now();
  let busyPreview: { count: number; syncedAt: string | null; source: string } | null = null;
  if (settings?.hasRefreshToken) {
    const r = await getBusyIntervals({
      timeMin: new Date(now),
      timeMax: new Date(now + LESSON_MAX_AHEAD_MS),
    });
    busyPreview = { count: r.busy.length, syncedAt: r.syncedAt, source: r.source };
  }

  const bookings = await listLessonBookingsAdmin(40);

  return Response.json({
    oauthConfigured: googleCalendarOAuthConfigured(),
    secretsKeyConfigured: bookingSecretsConfigured(),
    resendConfigured: resendConfigured(),
    notifyEmail: bookingNotifyEmail(),
    fromAddress: bookingFromAddress(),
    usesTestFrom: usesResendTestFrom(),
    settings: settings
      ? {
          calendarId: settings.calendarId,
          hasRefreshToken: settings.hasRefreshToken,
          googleChannelId: settings.googleChannelId,
          googleChannelExpiration: settings.googleChannelExpiration,
          meetingLink: settings.meetingLink,
          hasPhone: settings.hasPhone,
          hasAddress: settings.hasAddress,
          busyCacheUpdatedAt: settings.busyCacheUpdatedAt,
        }
      : null,
    busyPreview,
    bookings: bookings.map((b) => ({
      ...toPublicBookingView(b),
      requesterEmail: b.requester_email,
      requesterPhone: b.requester_phone,
      goalText: b.goal_text,
      notes: b.notes,
    })),
    connectUrl: '/api/book/gcal/oauth/start',
  });
}

export async function PUT(req: Request) {
  const gate = await requireAdmin();
  if ('error' in gate && gate.error) return gate.error;

  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return Response.json({ error: 'invalid_json' }, { status: 400 });
  }

  if (body.action === 'test_email') {
    const result = await sendBookingTestEmail();
    if (!result.ok) {
      return Response.json(
        {
          ok: false,
          error: result.error,
          detail: result.detail ?? null,
          status: result.status ?? null,
          notifyEmail: bookingNotifyEmail(),
          fromAddress: bookingFromAddress(),
          usesTestFrom: usesResendTestFrom(),
        },
        { status: 502 },
      );
    }
    return Response.json({
      ok: true,
      id: result.id ?? null,
      notifyEmail: bookingNotifyEmail(),
      fromAddress: bookingFromAddress(),
    });
  }

  if (body.action === 'renew_watch') {
    const watch = await ensureGoogleCalendarWatch();
    if (!watch.ok) return Response.json({ error: watch.error }, { status: 502 });
    return Response.json({ ok: true, watch });
  }

  if (body.action === 'refresh_busy') {
    const now = Date.now();
    const r = await getBusyIntervals({
      timeMin: new Date(now),
      timeMax: new Date(now + LESSON_MAX_AHEAD_MS),
      forceRefresh: true,
    });
    return Response.json({
      ok: true,
      busyCount: r.busy.length,
      source: r.source,
      syncedAt: r.syncedAt,
    });
  }

  const result = await updateBookingContactSecrets({
    phone: body.phone != null ? String(body.phone) : undefined,
    address: body.address != null ? String(body.address) : undefined,
    meetingLink: body.meetingLink !== undefined ? String(body.meetingLink ?? '') : undefined,
    calendarId: body.calendarId != null ? String(body.calendarId) : undefined,
  });
  if (!result.ok) {
    return Response.json({ error: result.error }, { status: 400 });
  }
  return Response.json({ ok: true });
}
