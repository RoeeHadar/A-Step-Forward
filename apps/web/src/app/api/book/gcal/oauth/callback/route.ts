/**
 * GET /api/book/gcal/oauth/callback — Google OAuth redirect.
 */
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { getAuthContext, requireRole } from '@/lib/auth';
import {
  exchangeGoogleCalendarCode,
  ensureGoogleCalendarWatch,
  googleCalendarOAuthConfigured,
} from '@/lib/google-calendar';
import { saveGoogleRefreshToken } from '@/lib/lesson-booking-settings-db';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function adminBookingsUrl(query: string): URL {
  const base =
    process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, '') ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000');
  return new URL(`/admin/bookings?${query}`, base.startsWith('http') ? base : `https://${base}`);
}

export async function GET(req: Request) {
  const auth = await getAuthContext();
  if (!auth) return NextResponse.redirect(adminBookingsUrl('gcal=unauthorized'));
  try {
    requireRole(auth, ['admin']);
  } catch {
    return NextResponse.redirect(adminBookingsUrl('gcal=forbidden'));
  }
  if (!googleCalendarOAuthConfigured()) {
    return NextResponse.redirect(adminBookingsUrl('gcal=not_configured'));
  }

  const url = new URL(req.url);
  const err = url.searchParams.get('error');
  if (err) {
    return NextResponse.redirect(adminBookingsUrl(`gcal=denied`));
  }
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const jar = await cookies();
  const expected = jar.get('gcal_oauth_state')?.value;
  jar.delete('gcal_oauth_state');

  if (!code || !state || !expected || state !== expected) {
    return NextResponse.redirect(adminBookingsUrl('gcal=state_mismatch'));
  }

  const tokens = await exchangeGoogleCalendarCode(code);
  if (!tokens) {
    return NextResponse.redirect(adminBookingsUrl('gcal=exchange_failed'));
  }

  const saved = await saveGoogleRefreshToken(tokens.refreshToken);
  if (!saved) {
    return NextResponse.redirect(adminBookingsUrl('gcal=save_failed'));
  }

  const watch = await ensureGoogleCalendarWatch();
  if (!watch.ok) {
    logger.error('[gcal oauth] watch setup failed', { error: watch.error });
    return NextResponse.redirect(adminBookingsUrl(`gcal=connected&watch=${watch.error}`));
  }

  return NextResponse.redirect(adminBookingsUrl('gcal=connected'));
}
