import { z } from 'zod';
import { API_BASE_URL } from '@/lib/api';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';

const bookingSchema = z.object({
  name: z.string().min(1).max(200),
  email: z.string().email(),
  phone: z.string().max(40).optional(),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  time: z.string().regex(/^\d{2}:\d{2}$/),
  duration_h: z.number().min(1).max(3),
  subject: z.string().min(1).max(100),
  notes: z.string().max(2000).optional(),
});

async function sendBookingEmail(
  data: z.infer<typeof bookingSchema>,
  priceIls: number,
): Promise<boolean> {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) return false;

  const tutorEmail = process.env.TUTOR_EMAIL ?? 'roeehadar@gmail.com';
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: process.env.RESEND_FROM ?? 'A Step Forward <onboarding@resend.dev>',
      to: [tutorEmail],
      subject: `New lesson booking — ${data.name}`,
      html: `
        <h2>New booking request</h2>
        <p><strong>Name:</strong> ${data.name}</p>
        <p><strong>Email:</strong> ${data.email}</p>
        <p><strong>Phone:</strong> ${data.phone ?? '—'}</p>
        <p><strong>Date:</strong> ${data.date} at ${data.time}</p>
        <p><strong>Duration:</strong> ${data.duration_h} hours</p>
        <p><strong>Subject:</strong> ${data.subject}</p>
        <p><strong>Price:</strong> ${priceIls} ₪</p>
        <p><strong>Notes:</strong> ${data.notes ?? '—'}</p>
      `,
    }),
  });
  return res.ok;
}

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const parsed = bookingSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: 'Invalid booking data' }, { status: 400 });
  }

  const data = parsed.data;
  let bookingId: string | null = null;
  let priceIls = Math.round(150 * data.duration_h);

  try {
    const res = await fetch(`${API_BASE_URL}/v1/bookings`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (res.ok) {
      const payload = (await res.json()) as { id?: string; price_ils?: number };
      bookingId = payload.id ?? null;
      priceIls = payload.price_ils ?? priceIls;
    }
  } catch (err) {
    logger.warn('booking backend persist failed', { err: String(err) });
  }

  const emailed = await sendBookingEmail(data, priceIls);

  if (!bookingId && !emailed) {
    logger.warn('booking saved nowhere — configure DATABASE_URL or RESEND_API_KEY');
    return Response.json(
      { error: 'Booking service unavailable. Please email directly.' },
      { status: 503 },
    );
  }

  logger.info('booking received', { bookingId, emailed, date: data.date });
  return Response.json({ ok: true, id: bookingId, emailed });
}
