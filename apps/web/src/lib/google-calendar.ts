/**
 * Google Calendar client for Book-a-Lesson (OAuth + freeBusy + events + watch).
 * Uses fetch only (no googleapis package).
 */
import 'server-only';
import { randomUUID } from 'node:crypto';
import { logger } from '@/lib/logger';
import { LESSON_MAX_AHEAD_MS } from '@/lib/lesson-booking';
import {
  busyInRange,
  mergeBusyIntervals,
  overlapsAnyBusy,
  type BusyInterval,
} from '@/lib/lesson-booking-busy';
import {
  getCalendarId,
  getGoogleRefreshToken,
  getLessonBookingSettings,
  invalidateBusyCache,
  saveBusyCache,
  saveWatchChannel,
} from '@/lib/lesson-booking-settings-db';

const TOKEN_URL = 'https://oauth2.googleapis.com/token';
const CAL_BASE = 'https://www.googleapis.com/calendar/v3';
const SCOPES = ['https://www.googleapis.com/auth/calendar'].join(' ');

/** Max age of busy cache before forced refresh (near–real-time poll fallback). */
export const BUSY_CACHE_MAX_AGE_MS = 45_000;

export function googleCalendarOAuthConfigured(): boolean {
  return Boolean(
    process.env.GOOGLE_CALENDAR_CLIENT_ID?.trim() &&
      process.env.GOOGLE_CALENDAR_CLIENT_SECRET?.trim(),
  );
}

export function googleCalendarRedirectUri(): string {
  if (process.env.GOOGLE_CALENDAR_REDIRECT_URI?.trim()) {
    return process.env.GOOGLE_CALENDAR_REDIRECT_URI.trim();
  }
  const base =
    process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, '') ||
    process.env.VERCEL_URL?.replace(/\/$/, '') ||
    'http://localhost:3000';
  const origin = base.startsWith('http') ? base : `https://${base}`;
  return `${origin}/api/book/gcal/oauth/callback`;
}

export function buildGoogleCalendarAuthUrl(state: string): string {
  const clientId = process.env.GOOGLE_CALENDAR_CLIENT_ID!.trim();
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: googleCalendarRedirectUri(),
    response_type: 'code',
    scope: SCOPES,
    access_type: 'offline',
    prompt: 'consent',
    state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}

export async function exchangeGoogleCalendarCode(code: string): Promise<{
  refreshToken: string;
  accessToken: string;
} | null> {
  const clientId = process.env.GOOGLE_CALENDAR_CLIENT_ID?.trim();
  const clientSecret = process.env.GOOGLE_CALENDAR_CLIENT_SECRET?.trim();
  if (!clientId || !clientSecret) return null;

  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: googleCalendarRedirectUri(),
      grant_type: 'authorization_code',
    }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logger.error('[gcal] code exchange failed', { status: res.status, text: text.slice(0, 300) });
    return null;
  }
  const data = (await res.json()) as {
    access_token?: string;
    refresh_token?: string;
  };
  if (!data.access_token) return null;
  if (!data.refresh_token) {
    logger.error('[gcal] no refresh_token — revoke prior grant and reconnect with prompt=consent');
    return null;
  }
  return { accessToken: data.access_token, refreshToken: data.refresh_token };
}

async function refreshAccessToken(): Promise<string | null> {
  const clientId = process.env.GOOGLE_CALENDAR_CLIENT_ID?.trim();
  const clientSecret = process.env.GOOGLE_CALENDAR_CLIENT_SECRET?.trim();
  const refreshToken = await getGoogleRefreshToken();
  if (!clientId || !clientSecret || !refreshToken) return null;

  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logger.error('[gcal] refresh failed', { status: res.status, text: text.slice(0, 300) });
    return null;
  }
  const data = (await res.json()) as { access_token?: string };
  return data.access_token ?? null;
}

async function gcalFetch(path: string, init?: RequestInit): Promise<Response | null> {
  const access = await refreshAccessToken();
  if (!access) return null;
  const url = path.startsWith('http') ? path : `${CAL_BASE}${path}`;
  return fetch(url, {
    ...init,
    headers: {
      Authorization: `Bearer ${access}`,
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
}

export async function fetchGoogleFreeBusy(input: {
  timeMin: Date;
  timeMax: Date;
}): Promise<BusyInterval[] | null> {
  const calendarId = await getCalendarId();
  const res = await gcalFetch('/freeBusy', {
    method: 'POST',
    body: JSON.stringify({
      timeMin: input.timeMin.toISOString(),
      timeMax: input.timeMax.toISOString(),
      timeZone: 'Asia/Jerusalem',
      items: [{ id: calendarId }],
    }),
  });
  if (!res) return null;
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logger.error('[gcal] freeBusy failed', { status: res.status, text: text.slice(0, 300) });
    return null;
  }
  const data = (await res.json()) as {
    calendars?: Record<string, { busy?: { start: string; end: string }[] }>;
  };
  const busy = data.calendars?.[calendarId]?.busy ?? [];
  return mergeBusyIntervals(
    busy.map((b) => ({
      start: new Date(b.start).toISOString(),
      end: new Date(b.end).toISOString(),
    })),
  );
}

/**
 * Near–real-time busy windows: use DB cache if fresh, else FreeBusy + cache.
 * Webhook invalidation clears freshness so the next read hits Google.
 *
 * Only persists cache when the requested window is the full booking horizon
 * (or `persistCache: true` with a wide span) so narrow slot checks cannot
 * shrink the public 8-week busy cache.
 */
export async function getBusyIntervals(input: {
  timeMin: Date;
  timeMax: Date;
  forceRefresh?: boolean;
  /** When false, never write the FreeBusy result to the DB cache. */
  persistCache?: boolean;
}): Promise<{ busy: BusyInterval[]; source: 'cache' | 'google' | 'empty'; syncedAt: string | null }> {
  const settings = await getLessonBookingSettings();
  const now = Date.now();
  const cacheAge = settings?.busyCacheUpdatedAt
    ? now - Date.parse(settings.busyCacheUpdatedAt)
    : Number.POSITIVE_INFINITY;
  const cacheCovers = Boolean(
    settings?.busyCacheFrom &&
      settings?.busyCacheTo &&
      Date.parse(settings.busyCacheFrom) <= input.timeMin.getTime() &&
      Date.parse(settings.busyCacheTo) >= input.timeMax.getTime(),
  );

  if (
    !input.forceRefresh &&
    cacheCovers &&
    cacheAge < BUSY_CACHE_MAX_AGE_MS &&
    settings?.busyCache
  ) {
    return {
      busy: busyInRange(settings.busyCache, input.timeMin, input.timeMax),
      source: 'cache',
      syncedAt: settings.busyCacheUpdatedAt,
    };
  }

  const fromGoogle = await fetchGoogleFreeBusy({
    timeMin: input.timeMin,
    timeMax: input.timeMax,
  });
  if (fromGoogle == null) {
    // Degraded: only reuse stale cache when it covers the requested window.
    if (cacheCovers && settings?.busyCache) {
      return {
        busy: busyInRange(settings.busyCache, input.timeMin, input.timeMax),
        source: 'cache',
        syncedAt: settings.busyCacheUpdatedAt,
      };
    }
    return { busy: [], source: 'empty', syncedAt: null };
  }

  const spanMs = input.timeMax.getTime() - input.timeMin.getTime();
  const wideEnoughToPersist = spanMs >= LESSON_MAX_AHEAD_MS * 0.9;
  const shouldPersist = input.persistCache !== false && wideEnoughToPersist;
  if (shouldPersist) {
    await saveBusyCache({
      busy: fromGoogle,
      from: input.timeMin,
      to: input.timeMax,
    });
  }

  return {
    busy: fromGoogle,
    source: 'google',
    syncedAt: new Date().toISOString(),
  };
}

/**
 * Hard conflict check against Google busy.
 * Always refreshes the full 8-week horizon (and persists it) so we never
 * replace the public cache with a few-hour slice.
 */
export async function assertSlotFreeOnGoogle(
  start: Date,
  end: Date,
): Promise<{ free: true } | { free: false; reason: 'busy' | 'calendar_unavailable' }> {
  const hasToken = Boolean(await getGoogleRefreshToken());
  if (!hasToken) {
    // No calendar connected — allow requests; hard-block on accept (PR3) when writing events.
    return { free: true };
  }

  const now = Date.now();
  const { busy, source } = await getBusyIntervals({
    timeMin: new Date(now),
    timeMax: new Date(now + LESSON_MAX_AHEAD_MS),
    forceRefresh: true,
    persistCache: true,
  });

  if (source === 'empty') {
    return { free: false, reason: 'calendar_unavailable' };
  }
  if (overlapsAnyBusy(start, end, busy)) {
    return { free: false, reason: 'busy' };
  }
  return { free: true };
}

export type CreateLessonGcalEventInput = {
  summary: string;
  description: string;
  start: Date;
  end: Date;
  attendeeEmail?: string;
  location?: string;
};

/** Write a confirmed lesson to Google Calendar. Returns event id. */
export async function createConfirmedLessonEvent(
  input: CreateLessonGcalEventInput,
): Promise<{ eventId: string; htmlLink?: string } | { error: string }> {
  const conflict = await assertSlotFreeOnGoogle(input.start, input.end);
  if (!conflict.free) {
    return { error: conflict.reason === 'busy' ? 'slot_busy' : 'calendar_unavailable' };
  }

  const calendarId = encodeURIComponent(await getCalendarId());
  const body: Record<string, unknown> = {
    summary: input.summary,
    description: input.description,
    start: { dateTime: input.start.toISOString(), timeZone: 'Asia/Jerusalem' },
    end: { dateTime: input.end.toISOString(), timeZone: 'Asia/Jerusalem' },
    status: 'confirmed',
  };
  if (input.location) body.location = input.location;
  if (input.attendeeEmail) {
    body.attendees = [{ email: input.attendeeEmail }];
  }

  const res = await gcalFetch(`/calendars/${calendarId}/events?sendUpdates=none`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  if (!res) return { error: 'calendar_unavailable' };
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logger.error('[gcal] create event failed', { status: res.status, text: text.slice(0, 300) });
    return { error: 'create_failed' };
  }
  const data = (await res.json()) as { id?: string; htmlLink?: string };
  if (!data.id) return { error: 'create_failed' };
  await invalidateBusyCache();
  return { eventId: data.id, htmlLink: data.htmlLink };
}

export async function deleteLessonCalendarEvent(
  eventId: string,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const calendarId = encodeURIComponent(await getCalendarId());
  const res = await gcalFetch(`/calendars/${calendarId}/events/${encodeURIComponent(eventId)}`, {
    method: 'DELETE',
  });
  if (!res) return { ok: false, error: 'calendar_unavailable' };
  if (res.status === 404 || res.status === 410) {
    await invalidateBusyCache();
    return { ok: true };
  }
  if (!res.ok) {
    return { ok: false, error: 'delete_failed' };
  }
  await invalidateBusyCache();
  return { ok: true };
}

export function googleWebhookAddress(): string {
  if (process.env.GOOGLE_CALENDAR_WEBHOOK_URL?.trim()) {
    return process.env.GOOGLE_CALENDAR_WEBHOOK_URL.trim();
  }
  const base =
    process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, '') ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL.replace(/\/$/, '')}` : '');
  if (!base) return '';
  return `${base}/api/book/gcal/webhook`;
}

/** Register a push watch channel (expires ~7 days — renew via cron). */
export async function ensureGoogleCalendarWatch(): Promise<
  { ok: true; channelId: string; expiration: string } | { ok: false; error: string }
> {
  const address = googleWebhookAddress();
  if (!address.startsWith('https://')) {
    return { ok: false, error: 'webhook_https_required' };
  }
  const calendarId = encodeURIComponent(await getCalendarId());
  const channelId = randomUUID();
  const token = process.env.GOOGLE_CALENDAR_WEBHOOK_TOKEN?.trim() || channelId;

  const res = await gcalFetch(`/calendars/${calendarId}/events/watch`, {
    method: 'POST',
    body: JSON.stringify({
      id: channelId,
      type: 'web_hook',
      address,
      token,
    }),
  });
  if (!res) return { ok: false, error: 'calendar_unavailable' };
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    logger.error('[gcal] watch failed', { status: res.status, text: text.slice(0, 400) });
    return { ok: false, error: 'watch_failed' };
  }
  const data = (await res.json()) as {
    id?: string;
    resourceId?: string;
    expiration?: string;
  };
  if (!data.resourceId || !data.expiration) {
    return { ok: false, error: 'watch_failed' };
  }
  const expiration = new Date(Number(data.expiration));
  await saveWatchChannel({
    channelId: data.id || channelId,
    resourceId: data.resourceId,
    expiration,
  });
  return { ok: true, channelId: data.id || channelId, expiration: expiration.toISOString() };
}
