/**
 * Cron: renew Google Calendar watch channel before expiry.
 * Auth: Authorization: Bearer CRON_SECRET (same as other crons).
 */
import { ensureGoogleCalendarWatch, googleCalendarOAuthConfigured } from '@/lib/google-calendar';
import { getGoogleRefreshToken, getLessonBookingSettings } from '@/lib/lesson-booking-settings-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function authorize(req: Request): boolean {
  const secret = process.env.CRON_SECRET?.trim();
  if (!secret) return false;
  const header = req.headers.get('authorization') ?? '';
  return header === `Bearer ${secret}`;
}

export async function GET(req: Request) {
  if (!authorize(req)) {
    return Response.json({ error: 'unauthorized' }, { status: 401 });
  }
  if (!googleCalendarOAuthConfigured()) {
    return Response.json({ ok: true, skipped: 'oauth_not_configured' });
  }
  const token = await getGoogleRefreshToken();
  if (!token) {
    return Response.json({ ok: true, skipped: 'no_refresh_token' });
  }

  const settings = await getLessonBookingSettings();
  const exp = settings?.googleChannelExpiration
    ? Date.parse(settings.googleChannelExpiration)
    : 0;
  const renewIfWithinMs = 48 * 60 * 60 * 1000;
  if (exp && exp - Date.now() > renewIfWithinMs) {
    return Response.json({
      ok: true,
      skipped: 'not_due',
      expiresAt: settings?.googleChannelExpiration,
    });
  }

  const watch = await ensureGoogleCalendarWatch();
  if (!watch.ok) {
    return Response.json({ ok: false, error: watch.error }, { status: 502 });
  }
  return Response.json({ ok: true, watch });
}
