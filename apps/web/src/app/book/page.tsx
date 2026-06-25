'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { SiteHeader } from '@/components/site-header';

const DURATIONS = [1, 1.5, 2, 2.5, 3] as const;
const SUBJECTS = ['Math', 'Physics', 'Other'] as const;
const HOURLY_RATE = 150;

function timeSlots(): string[] {
  const slots: string[] = [];
  for (let h = 8; h <= 20; h++) {
    for (const m of [0, 30]) {
      if (h === 20 && m === 30) break;
      slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
    }
  }
  return slots;
}

export default function BookPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('10:00');
  const [duration, setDuration] = useState<number>(1);
  const [subject, setSubject] = useState<(typeof SUBJECTS)[number]>('Math');
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [emailSent, setEmailSent] = useState(true);

  const slots = useMemo(() => timeSlots(), []);
  const total = HOURLY_RATE * duration;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg('');
    try {
      const res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name,
          email,
          phone: phone || undefined,
          date,
          time,
          duration_h: duration,
          subject,
          notes: notes || undefined,
        }),
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as { error?: string };
        throw new Error(body.error ?? 'Booking failed');
      }
      const payload = (await res.json()) as { emailed?: boolean };
      setEmailSent(payload.emailed !== false);
      setStatus('success');
    } catch (err) {
      setStatus('error');
      setErrorMsg(err instanceof Error ? err.message : 'Something went wrong');
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
        <section className="about mb-10 flex flex-col gap-6 sm:flex-row">
          <div className="flex h-40 w-40 shrink-0 items-center justify-center rounded-2xl border border-dashed border-border bg-surface-1/50 text-sm text-muted-foreground">
            Photo coming soon
          </div>
          <div>
            <h1 className="font-display text-3xl font-bold">Roee Hadar — Math &amp; Physics Tutor</h1>
            <p className="mt-3 text-foreground" dir="rtl">
              מורה מנוסה למתמטיקה ופיזיקה לכל הרמות — מחטיבת הביניים ועד ה-12, כולל הכנה לבגרות,
              קורסים אקדמיים, ופיזיקה אוניברסיטאית. שיעורים מותאמים אישית, בקצב שלך.
            </p>
            <p className="en-bio mt-3 text-muted-foreground">
              Experienced Math &amp; Physics tutor for all levels — middle school through grade 12,
              Bagrut prep, and university courses. Personalised sessions at your pace.
            </p>
          </div>
        </section>

        {status === 'success' ? (
          <div className="glass-surface rounded-2xl p-8 text-center">
            <h2 className="text-xl font-semibold text-foreground">Request received!</h2>
            <p className="mt-2 text-muted-foreground">
              {emailSent
                ? "We'll confirm your lesson by email shortly."
                : 'Your request was saved. We may follow up by email if notification delivery failed.'}
            </p>
            <Link href="/" className="mt-4 inline-block text-primary hover:underline">
              Back to home
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="glass-surface space-y-5 rounded-2xl p-6">
            <h2 className="font-display text-xl font-semibold">Book a private lesson</h2>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm">
                Full name *
                <input
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                />
              </label>
              <label className="block text-sm">
                Email *
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                />
              </label>
              <label className="block text-sm">
                Phone (optional)
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                />
              </label>
              <label className="block text-sm">
                Subject *
                <select
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value as (typeof SUBJECTS)[number])}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                >
                  {SUBJECTS.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                Preferred date *
                <input
                  required
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                />
              </label>
              <label className="block text-sm">
                Preferred time *
                <select
                  required
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
                >
                  {slots.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <fieldset>
              <legend className="text-sm font-medium">Session duration *</legend>
              <div className="mt-2 flex flex-wrap gap-2">
                {DURATIONS.map((d) => (
                  <label
                    key={d}
                    className={`cursor-pointer rounded-lg border px-4 py-2 text-sm ${
                      duration === d
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border text-muted-foreground'
                    }`}
                  >
                    <input
                      type="radio"
                      name="duration"
                      value={d}
                      checked={duration === d}
                      onChange={() => setDuration(d)}
                      className="sr-only"
                    />
                    {d} hr{d !== 1 ? 's' : ''}
                  </label>
                ))}
              </div>
            </fieldset>

            <label className="block text-sm">
              Notes (optional)
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="mt-1 w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2"
              />
            </label>

            <div className="rounded-xl border border-accent-magenta/30 bg-accent-magenta/10 px-4 py-3 text-center">
              <p className="text-lg font-bold text-foreground">
                {HOURLY_RATE} ₪ × {duration} = {total} ₪
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                Payment is handled at the start of the session.
              </p>
            </div>

            {status === 'error' ? (
              <p className="text-sm text-destructive" role="alert">
                {errorMsg}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={status === 'loading'}
              className="w-full rounded-xl bg-gradient-to-r from-primary to-accent-magenta py-3 font-semibold text-primary-foreground disabled:opacity-60"
            >
              {status === 'loading' ? 'Sending…' : 'Request booking'}
            </button>
          </form>
        )}
      </main>
    </div>
  );
}
