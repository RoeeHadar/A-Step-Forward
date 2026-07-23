/**
 * Outbound email via Resend for Book-a-Lesson notifications.
 */
import 'server-only';
import { logger } from '@/lib/logger';
import type { LessonBookingRow } from '@/lib/lesson-bookings-db';

export function bookingNotifyEmail(): string {
  return (
    process.env.BOOKING_NOTIFY_EMAIL?.trim() ||
    process.env.TUTOR_EMAIL?.trim() ||
    'roeehadar@gmail.com'
  );
}

export function bookingFromAddress(): string {
  return process.env.RESEND_FROM?.trim() || 'A Step Forward <onboarding@resend.dev>';
}

export function resendConfigured(): boolean {
  return Boolean(process.env.RESEND_API_KEY?.trim());
}

export function usesResendTestFrom(): boolean {
  return /@resend\.dev>?$/i.test(bookingFromAddress()) || /onboarding@resend\.dev/i.test(bookingFromAddress());
}

function appOrigin(): string {
  const base =
    process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, '') ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL.replace(/\/$/, '')}` : '');
  return base.startsWith('http') ? base : base ? `https://${base}` : 'https://a-step-forward-waij.vercel.app';
}

function formatJerusalem(iso: string): string {
  try {
    return new Date(iso).toLocaleString('he-IL', {
      timeZone: 'Asia/Jerusalem',
      dateStyle: 'full',
      timeStyle: 'short',
    });
  } catch {
    return iso;
  }
}

export type BookingEmailResult =
  | { ok: true; id?: string }
  | { ok: false; error: string; detail?: string; status?: number };

async function sendResendEmail(input: {
  to: string;
  subject: string;
  html: string;
}): Promise<BookingEmailResult> {
  const apiKey = process.env.RESEND_API_KEY?.trim();
  if (!apiKey) {
    logger.warn('[booking-email] RESEND_API_KEY missing — skipping notify');
    return { ok: false, error: 'resend_not_configured' };
  }

  const from = bookingFromAddress();
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: [input.to],
        subject: input.subject,
        html: input.html,
      }),
    });
    const text = await res.text().catch(() => '');
    let parsed: { id?: string; message?: string; name?: string } = {};
    try {
      parsed = text ? (JSON.parse(text) as typeof parsed) : {};
    } catch {
      parsed = {};
    }

    if (!res.ok) {
      const detail =
        parsed.message ||
        parsed.name ||
        text.slice(0, 500) ||
        `HTTP ${res.status}`;
      logger.error('[booking-email] Resend failed', {
        status: res.status,
        detail,
        from,
        to: input.to,
        testFrom: usesResendTestFrom(),
      });
      return {
        ok: false,
        error: 'send_failed',
        detail,
        status: res.status,
      };
    }

    return { ok: true, id: parsed.id };
  } catch (err) {
    logger.error('[booking-email] send threw', { err: String(err) });
    return { ok: false, error: 'send_failed', detail: String(err) };
  }
}

export async function sendBookingRequestNotifyEmail(
  row: LessonBookingRow,
): Promise<BookingEmailResult> {
  const to = bookingNotifyEmail();
  const origin = appOrigin();
  const adminUrl = `${origin}/admin/bookings`;
  const statusUrl = `${origin}/book/r/${row.public_token}`;

  const subject = `בקשת שיעור חדשה · ${row.learner_name} · ₪${row.price_ils}`;
  const html = `
    <div style="font-family:system-ui,sans-serif;line-height:1.5;color:#1a1a1a">
      <h2 style="margin:0 0 12px">בקשת שיעור חדשה</h2>
      <p><strong>תלמיד/ה:</strong> ${escapeHtml(row.learner_name)}</p>
      <p><strong>פונה:</strong> ${escapeHtml(row.requester_name)}
        &lt;${escapeHtml(row.requester_email)}&gt;
        · ${escapeHtml(row.requester_phone)}</p>
      <p><strong>פורמט:</strong> ${row.modality === 'haifa' ? 'חיפה (פרונטלי)' : 'אונליין'}</p>
      <p><strong>מקצועות:</strong> ${escapeHtml(row.subjects.join(', '))}</p>
      <p><strong>רמה:</strong> ${escapeHtml(row.level_band)}</p>
      ${
        row.university_name
          ? `<p><strong>אוניברסיטה:</strong> ${escapeHtml(row.university_name)} — ${escapeHtml(row.university_course ?? '')}</p>`
          : ''
      }
      <p><strong>זמן מועדף:</strong> ${escapeHtml(formatJerusalem(row.preferred_start))}
        → ${escapeHtml(formatJerusalem(row.preferred_end))}
        (${row.duration_h} ש׳ · ₪${row.price_ils})</p>
      ${row.goal_text ? `<p><strong>מטרה:</strong> ${escapeHtml(row.goal_text)}</p>` : ''}
      ${row.notes ? `<p><strong>הערות:</strong> ${escapeHtml(row.notes)}</p>` : ''}
      <p style="margin-top:20px">
        <a href="${adminUrl}">פתח ניהול בקשות</a>
        · <a href="${statusUrl}">קישור סטטוס לתלמיד</a>
      </p>
      <p style="color:#666;font-size:12px">נוצר: ${escapeHtml(row.created_at)}</p>
    </div>
  `.trim();

  return sendResendEmail({ to, subject, html });
}

/** Admin sanity-check: send a short test message to BOOKING_NOTIFY_EMAIL. */
export async function sendBookingTestEmail(): Promise<BookingEmailResult> {
  const to = bookingNotifyEmail();
  const from = bookingFromAddress();
  const html = `
    <div style="font-family:system-ui,sans-serif;line-height:1.5">
      <p>Book-a-Lesson email test from A Step Forward.</p>
      <p><strong>From:</strong> ${escapeHtml(from)}</p>
      <p><strong>To:</strong> ${escapeHtml(to)}</p>
      <p><strong>Time:</strong> ${escapeHtml(new Date().toISOString())}</p>
      ${
        usesResendTestFrom()
          ? `<p style="color:#a30">Note: you are still using Resend's test sender (<code>onboarding@resend.dev</code>).
             It can only deliver to the email address on your Resend account.
             To notify ${escapeHtml(to)} reliably, verify your own domain in Resend and set
             <code>RESEND_FROM</code> to an address on that domain.</p>`
          : ''
      }
    </div>
  `.trim();

  return sendResendEmail({
    to,
    subject: 'A Step Forward — booking email test',
    html,
  });
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
