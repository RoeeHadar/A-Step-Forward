/**
 * GET /api/book/gcal/oauth/start — admin starts Google Calendar OAuth.
 */
import { NextResponse } from 'next/server';
import { randomBytes } from 'node:crypto';
import { getAuthContext, requireRole } from '@/lib/auth';
import {
  buildGoogleCalendarAuthUrl,
  googleCalendarOAuthConfigured,
} from '@/lib/google-calendar';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const auth = await getAuthContext();
  if (!auth) return NextResponse.json({ error: 'unauthorized' }, { status: 401 });
  try {
    requireRole(auth, ['admin']);
  } catch {
    return NextResponse.json({ error: 'forbidden' }, { status: 403 });
  }
  if (!googleCalendarOAuthConfigured()) {
    return NextResponse.json(
      { error: 'oauth_not_configured', message: 'Set GOOGLE_CALENDAR_CLIENT_ID/SECRET' },
      { status: 503 },
    );
  }

  const state = randomBytes(16).toString('base64url');
  const res = NextResponse.redirect(buildGoogleCalendarAuthUrl(state));
  res.cookies.set('gcal_oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 600,
  });
  return res;
}
