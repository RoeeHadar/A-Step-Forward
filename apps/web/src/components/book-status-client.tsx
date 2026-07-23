'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';
import { useI18n } from '@/providers/i18n-provider';
import { publicBookingStatusLabel, type LessonBookingStatus } from '@/lib/lesson-booking';

type PublicBooking = {
  token: string;
  status: LessonBookingStatus;
  locale: 'he' | 'en';
  modality: string;
  subjects: string[];
  level: string;
  durationH: number;
  priceIls: number;
  preferredStart: string;
  preferredEnd: string;
  learnerName: string;
  requesterName: string;
  universityName: string | null;
  universityCourse: string | null;
};

export function BookStatusClient({ token }: { token: string }) {
  const { messages, locale } = useI18n();
  const t = messages.book;
  const [booking, setBooking] = useState<PublicBooking | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch(`/api/book/r/${encodeURIComponent(token)}`);
        const data = (await res.json().catch(() => ({}))) as {
          booking?: PublicBooking;
          error?: string;
        };
        if (!res.ok) {
          if (!cancelled) setError(data.error ?? 'not_found');
          return;
        }
        if (!cancelled) setBooking(data.booking ?? null);
      } catch {
        if (!cancelled) setError('generic');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="relative min-h-screen">
      <AmbientBackground />
      <SiteHeader />
      <main className="mx-auto max-w-xl space-y-6 px-4 py-10 md:py-14">
        <Link href="/book" className="text-sm text-primary underline-offset-4 hover:underline">
          {t.backToBook}
        </Link>
        <h1 className="font-display text-2xl font-semibold tracking-tight">{t.statusTitle}</h1>

        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {(t.errors as Record<string, string>)[error] ?? t.errors.generic}
          </p>
        ) : null}

        {!error && !booking ? (
          <p className="text-sm text-muted-foreground">{t.loading}</p>
        ) : null}

        {booking ? (
          <div className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6 text-sm">
            <p>
              <span className="text-muted-foreground">{t.statusLabel}: </span>
              <span className="font-medium">
                {publicBookingStatusLabel(booking.status, locale)}
              </span>
            </p>
            <p>
              <span className="text-muted-foreground">{t.learnerName}: </span>
              {booking.learnerName}
            </p>
            <p>
              <span className="text-muted-foreground">{t.preferredWindow}: </span>
              {new Date(booking.preferredStart).toLocaleString(locale === 'he' ? 'he-IL' : 'en-GB', {
                timeZone: 'Asia/Jerusalem',
              })}{' '}
              →{' '}
              {new Date(booking.preferredEnd).toLocaleTimeString(locale === 'he' ? 'he-IL' : 'en-GB', {
                timeZone: 'Asia/Jerusalem',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
            <p>
              <span className="text-muted-foreground">{t.duration}: </span>
              {t.durationHours.replace('{h}', String(booking.durationH))} · ₪{booking.priceIls}
            </p>
            <p>
              <span className="text-muted-foreground">{t.modality}: </span>
              {booking.modality === 'haifa' ? t.modalityHaifa : t.modalityOnline}
            </p>
            {booking.universityName ? (
              <p>
                <span className="text-muted-foreground">{t.universityName}: </span>
                {booking.universityName} — {booking.universityCourse}
              </p>
            ) : null}
            <p className="text-muted-foreground">{t.statusHint}</p>
          </div>
        ) : null}
      </main>
    </div>
  );
}
