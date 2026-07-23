/**
 * Singleton settings for Book-a-Lesson (Google tokens, contact secrets, busy cache).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import { openBookingSecret, sealBookingSecret } from '@/lib/booking-secrets-crypto';
import type { BusyInterval } from '@/lib/lesson-booking-busy';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

let ensured = false;

export async function ensureLessonBookingSettingsTable(): Promise<boolean> {
  if (!sql) return false;
  if (ensured) return true;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS lesson_booking_settings (
        id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
        calendar_id TEXT NOT NULL DEFAULT 'primary',
        google_refresh_token_enc TEXT,
        google_channel_id TEXT,
        google_resource_id TEXT,
        google_channel_expiration TIMESTAMPTZ,
        busy_cache JSONB NOT NULL DEFAULT '[]'::jsonb,
        busy_cache_from TIMESTAMPTZ,
        busy_cache_to TIMESTAMPTZ,
        busy_cache_updated_at TIMESTAMPTZ,
        phone_enc TEXT,
        address_enc TEXT,
        meeting_link TEXT,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`
      INSERT INTO lesson_booking_settings (id) VALUES (1)
      ON CONFLICT (id) DO NOTHING
    `;
    ensured = true;
    return true;
  } catch (err) {
    logger.error('[lesson-booking-settings] ensure failed', { err: String(err) });
    return false;
  }
}

export type LessonBookingSettings = {
  calendarId: string;
  hasRefreshToken: boolean;
  googleChannelId: string | null;
  googleResourceId: string | null;
  googleChannelExpiration: string | null;
  busyCache: BusyInterval[];
  busyCacheFrom: string | null;
  busyCacheTo: string | null;
  busyCacheUpdatedAt: string | null;
  meetingLink: string | null;
  hasPhone: boolean;
  hasAddress: boolean;
};

function envRefreshToken(): string | null {
  const t = process.env.GOOGLE_CALENDAR_REFRESH_TOKEN?.trim();
  return t || null;
}

export async function getLessonBookingSettings(): Promise<LessonBookingSettings | null> {
  if (!sql) return null;
  const ok = await ensureLessonBookingSettingsTable();
  if (!ok) return null;
  try {
    const rows = await sql`SELECT * FROM lesson_booking_settings WHERE id = 1 LIMIT 1`;
    const r = Array.isArray(rows) ? rows[0] : null;
    if (!r) return null;
    const enc = r.google_refresh_token_enc != null ? String(r.google_refresh_token_enc) : '';
    const hasDbToken = Boolean(enc && openBookingSecret(enc));
    return {
      calendarId: String(r.calendar_id || 'primary'),
      hasRefreshToken: hasDbToken || Boolean(envRefreshToken()),
      googleChannelId: r.google_channel_id == null ? null : String(r.google_channel_id),
      googleResourceId: r.google_resource_id == null ? null : String(r.google_resource_id),
      googleChannelExpiration:
        r.google_channel_expiration == null
          ? null
          : new Date(String(r.google_channel_expiration)).toISOString(),
      busyCache: Array.isArray(r.busy_cache) ? (r.busy_cache as BusyInterval[]) : [],
      busyCacheFrom:
        r.busy_cache_from == null ? null : new Date(String(r.busy_cache_from)).toISOString(),
      busyCacheTo: r.busy_cache_to == null ? null : new Date(String(r.busy_cache_to)).toISOString(),
      busyCacheUpdatedAt:
        r.busy_cache_updated_at == null
          ? null
          : new Date(String(r.busy_cache_updated_at)).toISOString(),
      meetingLink:
        (r.meeting_link != null && String(r.meeting_link)) ||
        process.env.BOOKING_MEETING_LINK?.trim() ||
        null,
      hasPhone: Boolean(
        (r.phone_enc && openBookingSecret(String(r.phone_enc))) ||
          process.env.BOOKING_ADMIN_PHONE?.trim(),
      ),
      hasAddress: Boolean(
        (r.address_enc && openBookingSecret(String(r.address_enc))) ||
          process.env.BOOKING_ADMIN_ADDRESS?.trim(),
      ),
    };
  } catch (err) {
    logger.error('[lesson-booking-settings] get failed', { err: String(err) });
    return null;
  }
}

export async function getGoogleRefreshToken(): Promise<string | null> {
  if (!sql) return envRefreshToken();
  await ensureLessonBookingSettingsTable();
  try {
    const rows = await sql`SELECT google_refresh_token_enc FROM lesson_booking_settings WHERE id = 1`;
    const enc = Array.isArray(rows) ? rows[0]?.google_refresh_token_enc : null;
    if (enc) {
      const opened = openBookingSecret(String(enc));
      if (opened) return opened;
    }
  } catch (err) {
    logger.error('[lesson-booking-settings] get token failed', { err: String(err) });
  }
  return envRefreshToken();
}

export async function getCalendarId(): Promise<string> {
  const s = await getLessonBookingSettings();
  return s?.calendarId || process.env.GOOGLE_CALENDAR_ID?.trim() || 'primary';
}

export async function saveGoogleRefreshToken(refreshToken: string): Promise<boolean> {
  if (!sql) return false;
  const sealed = sealBookingSecret(refreshToken);
  if (!sealed) {
    logger.error('[lesson-booking-settings] cannot seal token — set BOOKING_SECRETS_KEY');
    return false;
  }
  const ok = await ensureLessonBookingSettingsTable();
  if (!ok) return false;
  try {
    await sql`
      UPDATE lesson_booking_settings
      SET google_refresh_token_enc = ${sealed}, updated_at = NOW()
      WHERE id = 1
    `;
    return true;
  } catch (err) {
    logger.error('[lesson-booking-settings] save token failed', { err: String(err) });
    return false;
  }
}

export async function saveBusyCache(input: {
  busy: BusyInterval[];
  from: Date;
  to: Date;
}): Promise<void> {
  if (!sql) return;
  await ensureLessonBookingSettingsTable();
  try {
    await sql`
      UPDATE lesson_booking_settings
      SET
        busy_cache = ${JSON.stringify(input.busy)}::jsonb,
        busy_cache_from = ${input.from.toISOString()},
        busy_cache_to = ${input.to.toISOString()},
        busy_cache_updated_at = NOW(),
        updated_at = NOW()
      WHERE id = 1
    `;
  } catch (err) {
    logger.error('[lesson-booking-settings] save busy cache failed', { err: String(err) });
  }
}

export async function invalidateBusyCache(): Promise<void> {
  if (!sql) return;
  await ensureLessonBookingSettingsTable();
  try {
    await sql`
      UPDATE lesson_booking_settings
      SET busy_cache_updated_at = NULL, updated_at = NOW()
      WHERE id = 1
    `;
  } catch (err) {
    logger.error('[lesson-booking-settings] invalidate busy failed', { err: String(err) });
  }
}

export async function saveWatchChannel(input: {
  channelId: string;
  resourceId: string;
  expiration: Date;
}): Promise<void> {
  if (!sql) return;
  await ensureLessonBookingSettingsTable();
  try {
    await sql`
      UPDATE lesson_booking_settings
      SET
        google_channel_id = ${input.channelId},
        google_resource_id = ${input.resourceId},
        google_channel_expiration = ${input.expiration.toISOString()},
        updated_at = NOW()
      WHERE id = 1
    `;
  } catch (err) {
    logger.error('[lesson-booking-settings] save watch failed', { err: String(err) });
  }
}

export async function updateBookingContactSecrets(input: {
  phone?: string;
  address?: string;
  meetingLink?: string | null;
  calendarId?: string;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  if (!sql) return { ok: false, error: 'db_unavailable' };
  const ok = await ensureLessonBookingSettingsTable();
  if (!ok) return { ok: false, error: 'db_unavailable' };

  try {
    if (input.phone != null && input.phone.trim()) {
      const sealed = sealBookingSecret(input.phone.trim());
      if (!sealed) return { ok: false, error: 'secrets_key_missing' };
      await sql`
        UPDATE lesson_booking_settings SET phone_enc = ${sealed}, updated_at = NOW() WHERE id = 1
      `;
    }
    if (input.address != null && input.address.trim()) {
      const sealed = sealBookingSecret(input.address.trim());
      if (!sealed) return { ok: false, error: 'secrets_key_missing' };
      await sql`
        UPDATE lesson_booking_settings SET address_enc = ${sealed}, updated_at = NOW() WHERE id = 1
      `;
    }
    if (input.meetingLink !== undefined) {
      const link = input.meetingLink?.trim() || null;
      await sql`
        UPDATE lesson_booking_settings SET meeting_link = ${link}, updated_at = NOW() WHERE id = 1
      `;
    }
    if (input.calendarId != null && input.calendarId.trim()) {
      await sql`
        UPDATE lesson_booking_settings
        SET calendar_id = ${input.calendarId.trim()}, updated_at = NOW()
        WHERE id = 1
      `;
    }
    return { ok: true };
  } catch (err) {
    logger.error('[lesson-booking-settings] update contacts failed', { err: String(err) });
    return { ok: false, error: 'update_failed' };
  }
}

/** Resolve phone/address for sending after accept (PR3). Never expose publicly. */
export async function getBookingContactSecrets(): Promise<{
  phone: string | null;
  address: string | null;
  meetingLink: string | null;
}> {
  const envPhone = process.env.BOOKING_ADMIN_PHONE?.trim() || null;
  const envAddress = process.env.BOOKING_ADMIN_ADDRESS?.trim() || null;
  const envMeet = process.env.BOOKING_MEETING_LINK?.trim() || null;
  if (!sql) {
    return { phone: envPhone, address: envAddress, meetingLink: envMeet };
  }
  await ensureLessonBookingSettingsTable();
  try {
    const rows = await sql`
      SELECT phone_enc, address_enc, meeting_link FROM lesson_booking_settings WHERE id = 1
    `;
    const r = Array.isArray(rows) ? rows[0] : null;
    const phone =
      (r?.phone_enc ? openBookingSecret(String(r.phone_enc)) : null) || envPhone;
    const address =
      (r?.address_enc ? openBookingSecret(String(r.address_enc)) : null) || envAddress;
    const meetingLink =
      (r?.meeting_link != null ? String(r.meeting_link) : null) || envMeet;
    return { phone, address, meetingLink };
  } catch {
    return { phone: envPhone, address: envAddress, meetingLink: envMeet };
  }
}
