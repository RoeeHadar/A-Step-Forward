'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@clerk/nextjs';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { Label } from '@asf/ui/label';
import { Textarea } from '@asf/ui/textarea';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';
import {
  LESSON_DURATIONS_H,
  LESSON_HOURLY_RATE_ILS,
  preferredWindowUtc,
  priceIlsForDuration,
  type LessonDurationH,
  type LessonLevel,
  type LessonModality,
  type LessonSubject,
} from '@/lib/lesson-booking';
import { overlapsAnyBusy, type BusyInterval } from '@/lib/lesson-booking-busy';

type FormState = {
  requesterName: string;
  requesterEmail: string;
  requesterPhone: string;
  modality: LessonModality;
  subjects: LessonSubject[];
  level: LessonLevel;
  universityName: string;
  universityCourse: string;
  goalText: string;
  notes: string;
  durationH: LessonDurationH;
  preferredDate: string;
  preferredTime: string;
  bookingForOther: boolean;
  learnerName: string;
  learnerGrade: string;
  shareDossier: boolean;
};

const initial: FormState = {
  requesterName: '',
  requesterEmail: '',
  requesterPhone: '',
  modality: 'online',
  subjects: ['math'],
  level: 'bagrut',
  universityName: '',
  universityCourse: '',
  goalText: '',
  notes: '',
  durationH: 1,
  preferredDate: '',
  preferredTime: '17:00',
  bookingForOther: false,
  learnerName: '',
  learnerGrade: '',
  shareDossier: true,
};

function toggleSubject(list: LessonSubject[], s: LessonSubject): LessonSubject[] {
  if (list.includes(s)) {
    const next = list.filter((x) => x !== s);
    return next.length ? next : list;
  }
  return [...list, s];
}

export function BookLessonClient({ isAdmin = false }: { isAdmin?: boolean }) {
  const { messages, locale } = useI18n();
  const t = messages.book;
  const { isSignedIn } = useAuth();
  const [form, setForm] = useState<FormState>(initial);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusUrl, setStatusUrl] = useState<string | null>(null);
  const [busy, setBusy] = useState<BusyInterval[]>([]);
  const [busySyncedAt, setBusySyncedAt] = useState<string | null>(null);
  const successRef = useRef<HTMLDivElement | null>(null);

  const totalIls = useMemo(() => priceIlsForDuration(form.durationH), [form.durationH]);

  useEffect(() => {
    if (!statusUrl) return;
    successRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [statusUrl]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch('/api/book/availability');
        if (!res.ok) return;
        const data = (await res.json()) as {
          busy?: BusyInterval[];
          syncedAt?: string | null;
        };
        if (!cancelled) {
          setBusy(data.busy ?? []);
          setBusySyncedAt(data.syncedAt ?? null);
        }
      } catch {
        /* availability optional until Google is connected */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const slotConflict = useMemo(() => {
    if (!form.preferredDate || !form.preferredTime) return false;
    const window = preferredWindowUtc(form.preferredDate, form.preferredTime, form.durationH);
    if ('error' in window) return false;
    return overlapsAnyBusy(window.start, window.end, busy);
  }, [form.preferredDate, form.preferredTime, form.durationH, busy]);

  const busyOnSelectedDay = useMemo(() => {
    if (!form.preferredDate) return [];
    return busy.filter((b) => {
      const startLocal = new Date(b.start).toLocaleDateString('en-CA', {
        timeZone: 'Asia/Jerusalem',
      });
      const endLocal = new Date(b.end).toLocaleDateString('en-CA', {
        timeZone: 'Asia/Jerusalem',
      });
      return startLocal === form.preferredDate || endLocal === form.preferredDate;
    });
  }, [busy, form.preferredDate]);

  const errorMessage = (code: string | null) => {
    if (!code) return null;
    const map = t.errors as Record<string, string>;
    return map[code] ?? t.errors.generic;
  };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (slotConflict) {
      setError('slot_busy');
      return;
    }
    setSubmitting(true);
    setError(null);
    setStatusUrl(null);
    try {
      const res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          locale,
          shareDossier: Boolean(isSignedIn) && form.shareDossier,
        }),
      });
      const data = (await res.json().catch(() => ({}))) as {
        error?: string;
        statusUrl?: string;
      };
      if (!res.ok) {
        setError(data.error ?? 'generic');
        return;
      }
      if (data.statusUrl) {
        setStatusUrl(data.statusUrl);
        setForm(initial);
      }
    } catch {
      setError('generic');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-12 px-4 py-10 md:py-14">
      <header className="space-y-4">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          {t.eyebrow}
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
          {t.title}
        </h1>
        <p className="max-w-prose text-base leading-relaxed text-muted-foreground">{t.subtitle}</p>
      </header>

      <section
        className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6 md:p-8"
        aria-labelledby="about-roee-heading"
      >
        <h2 id="about-roee-heading" className="font-display text-xl font-semibold">
          {t.aboutTitle}
        </h2>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
          <div
            className="flex h-24 w-24 shrink-0 items-center justify-center rounded-xl border border-dashed border-border-bright bg-surface-2 text-xs text-muted-foreground"
            aria-hidden
          >
            {t.photoPlaceholder}
          </div>
          <div className="space-y-3 text-sm leading-relaxed text-muted-foreground">
            <p>{t.aboutBio}</p>
            <ul className="list-disc space-y-1 ps-5">
              <li>{t.credential1}</li>
              <li>{t.credential2}</li>
              <li>{t.credential3}</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="space-y-3" aria-labelledby="pricing-heading">
        <h2 id="pricing-heading" className="font-display text-xl font-semibold">
          {t.pricingTitle}
        </h2>
        <p className="text-sm text-muted-foreground">
          {t.pricingBody.replace('{rate}', String(LESSON_HOURLY_RATE_ILS))}
        </p>
        <p className="text-sm text-muted-foreground">{t.paymentMethods}</p>
        <p className="text-sm text-muted-foreground">{t.cancelPolicy}</p>
      </section>

      {isAdmin ? (
        <section
          className="space-y-4 rounded-2xl border border-border bg-surface-1 p-6 md:p-8"
          aria-labelledby="admin-book-notice"
        >
          <h2 id="admin-book-notice" className="font-display text-xl font-semibold">
            {t.adminCannotBookTitle}
          </h2>
          <p className="text-sm leading-relaxed text-muted-foreground">{t.adminCannotBookBody}</p>
          <Link
            href="/admin/bookings"
            className="inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            {t.adminBookingsCta}
          </Link>
        </section>
      ) : null}

      {!isAdmin && statusUrl ? (
        <div
          ref={successRef}
          id="book-request-success"
          className="rounded-2xl border border-primary/40 bg-primary/15 p-6 text-sm shadow-sm"
          role="status"
          aria-live="polite"
        >
          <p className="font-display text-lg font-semibold text-foreground">{t.successTitle}</p>
          <p className="mt-2 text-muted-foreground">{t.successBody}</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href={statusUrl}
              className="inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
              {t.viewStatus}
            </Link>
            <button
              type="button"
              className="text-sm text-primary underline-offset-4 hover:underline"
              onClick={() => {
                setStatusUrl(null);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
            >
              {t.sendAnother}
            </button>
          </div>
        </div>
      ) : null}

      {!isAdmin && !statusUrl ? (
      <form onSubmit={onSubmit} className="space-y-8 rounded-2xl border border-border bg-surface-1 p-6 md:p-8">
        <h2 className="font-display text-xl font-semibold">{t.formTitle}</h2>
        <p className="text-sm text-muted-foreground">{t.calendarNote}</p>
        {busySyncedAt ? (
          <p className="text-xs text-muted-foreground">
            {t.calendarSynced.replace(
              '{time}',
              new Date(busySyncedAt).toLocaleString(locale === 'he' ? 'he-IL' : 'en-GB', {
                timeZone: 'Asia/Jerusalem',
              }),
            )}
          </p>
        ) : null}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={t.name} htmlFor="book-name">
            <Input
              id="book-name"
              required
              value={form.requesterName}
              onChange={(e) => setForm((f) => ({ ...f, requesterName: e.target.value }))}
              autoComplete="name"
            />
          </Field>
          <Field label={t.email} htmlFor="book-email">
            <Input
              id="book-email"
              type="email"
              required
              value={form.requesterEmail}
              onChange={(e) => setForm((f) => ({ ...f, requesterEmail: e.target.value }))}
              autoComplete="email"
            />
          </Field>
          <Field label={t.phone} htmlFor="book-phone">
            <Input
              id="book-phone"
              type="tel"
              required
              value={form.requesterPhone}
              onChange={(e) => setForm((f) => ({ ...f, requesterPhone: e.target.value }))}
              autoComplete="tel"
            />
          </Field>
        </div>

        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            className="mt-1"
            checked={form.bookingForOther}
            onChange={(e) => setForm((f) => ({ ...f, bookingForOther: e.target.checked }))}
          />
          <span>{t.bookingForOther}</span>
        </label>
        {form.bookingForOther ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label={t.learnerName} htmlFor="book-learner-name">
              <Input
                id="book-learner-name"
                required={form.bookingForOther}
                value={form.learnerName}
                onChange={(e) => setForm((f) => ({ ...f, learnerName: e.target.value }))}
              />
            </Field>
            <Field label={t.learnerGrade} htmlFor="book-learner-grade">
              <Input
                id="book-learner-grade"
                value={form.learnerGrade}
                onChange={(e) => setForm((f) => ({ ...f, learnerGrade: e.target.value }))}
              />
            </Field>
          </div>
        ) : null}

        <fieldset>
          <legend className="mb-2 text-sm font-medium">{t.modality}</legend>
          <div className="flex flex-wrap gap-2">
            {(['online', 'haifa'] as const).map((m) => (
              <Chip
                key={m}
                active={form.modality === m}
                onClick={() => setForm((f) => ({ ...f, modality: m }))}
              >
                {m === 'online' ? t.modalityOnline : t.modalityHaifa}
              </Chip>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{t.modalityHint}</p>
        </fieldset>

        <fieldset>
          <legend className="mb-2 text-sm font-medium">{t.subjects}</legend>
          <div className="flex flex-wrap gap-2">
            {(['math', 'physics'] as const).map((s) => (
              <Chip
                key={s}
                active={form.subjects.includes(s)}
                onClick={() => setForm((f) => ({ ...f, subjects: toggleSubject(f.subjects, s) }))}
              >
                {s === 'math' ? t.subjectMath : t.subjectPhysics}
              </Chip>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="mb-2 text-sm font-medium">{t.level}</legend>
          <div className="flex flex-wrap gap-2">
            {(
              [
                ['middle_school', t.levelMiddle],
                ['bagrut', t.levelBagrut],
                ['university', t.levelUniversity],
                ['other', t.levelOther],
              ] as const
            ).map(([value, label]) => (
              <Chip
                key={value}
                active={form.level === value}
                onClick={() => setForm((f) => ({ ...f, level: value }))}
              >
                {label}
              </Chip>
            ))}
          </div>
        </fieldset>

        {form.level === 'university' ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label={t.universityName} htmlFor="book-uni">
              <Input
                id="book-uni"
                required
                value={form.universityName}
                onChange={(e) => setForm((f) => ({ ...f, universityName: e.target.value }))}
              />
            </Field>
            <Field label={t.universityCourse} htmlFor="book-course">
              <Input
                id="book-course"
                required
                value={form.universityCourse}
                onChange={(e) => setForm((f) => ({ ...f, universityCourse: e.target.value }))}
              />
            </Field>
          </div>
        ) : null}

        <Field label={t.goalOptional} htmlFor="book-goal">
          <Textarea
            id="book-goal"
            rows={3}
            value={form.goalText}
            onChange={(e) => setForm((f) => ({ ...f, goalText: e.target.value }))}
          />
        </Field>

        <fieldset>
          <legend className="mb-2 text-sm font-medium">{t.duration}</legend>
          <div className="flex flex-wrap gap-2">
            {LESSON_DURATIONS_H.map((h) => (
              <Chip
                key={h}
                active={form.durationH === h}
                onClick={() => setForm((f) => ({ ...f, durationH: h }))}
              >
                {t.durationHours.replace('{h}', String(h))} · ₪{priceIlsForDuration(h)}
              </Chip>
            ))}
          </div>
          <p className="mt-2 text-sm font-medium text-foreground">
            {t.total.replace('{total}', String(totalIls))}
          </p>
        </fieldset>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={t.preferredDate} htmlFor="book-date">
            <Input
              id="book-date"
              type="date"
              required
              value={form.preferredDate}
              onChange={(e) => setForm((f) => ({ ...f, preferredDate: e.target.value }))}
            />
          </Field>
          <Field label={t.preferredTime} htmlFor="book-time">
            <Input
              id="book-time"
              type="time"
              required
              value={form.preferredTime}
              onChange={(e) => setForm((f) => ({ ...f, preferredTime: e.target.value }))}
            />
          </Field>
        </div>
        <p className="text-xs text-muted-foreground">{t.tzNote}</p>
        {busyOnSelectedDay.length > 0 ? (
          <div className="rounded-xl border border-border bg-surface-2 px-4 py-3 text-sm">
            <p className="font-medium text-foreground">{t.busyTitle}</p>
            <ul className="mt-2 space-y-1 text-muted-foreground">
              {busyOnSelectedDay.map((b) => (
                <li key={`${b.start}-${b.end}`}>
                  {new Date(b.start).toLocaleTimeString(locale === 'he' ? 'he-IL' : 'en-GB', {
                    timeZone: 'Asia/Jerusalem',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  {' – '}
                  {new Date(b.end).toLocaleTimeString(locale === 'he' ? 'he-IL' : 'en-GB', {
                    timeZone: 'Asia/Jerusalem',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {slotConflict ? (
          <p className="text-sm text-destructive" role="alert">
            {t.errors.slot_busy}
          </p>
        ) : null}

        <Field label={t.notes} htmlFor="book-notes">
          <Textarea
            id="book-notes"
            rows={2}
            value={form.notes}
            onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
          />
        </Field>

        {isSignedIn ? (
          <label className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              className="mt-1"
              checked={form.shareDossier}
              onChange={(e) => setForm((f) => ({ ...f, shareDossier: e.target.checked }))}
            />
            <span>{t.shareDossier}</span>
          </label>
        ) : null}

        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {errorMessage(error)}
          </p>
        ) : null}

        <div className="space-y-3 border-t border-border pt-6">
          <Button type="submit" disabled={submitting || slotConflict} className="w-full sm:w-auto">
            {submitting ? t.submitting : t.submit}
          </Button>
          <p className="text-xs text-muted-foreground">{t.submitHint}</p>
        </div>
      </form>
      ) : null}

      {isSignedIn ? <MyBookings /> : null}
    </div>
  );
}

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
    </div>
  );
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-lg border px-3 py-1.5 text-sm transition-colors',
        active
          ? 'border-primary bg-primary/15 font-medium text-foreground'
          : 'border-border text-muted-foreground hover:border-border-bright hover:text-foreground',
      )}
    >
      {children}
    </button>
  );
}

function MyBookings() {
  const { messages } = useI18n();
  const t = messages.book;
  const [items, setItems] = useState<
    { token: string; status: string; preferredStart: string; priceIls: number }[] | null
  >(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch('/api/book');
        if (!res.ok) return;
        const data = (await res.json()) as {
          bookings?: { token: string; status: string; preferredStart: string; priceIls: number }[];
        };
        if (!cancelled) setItems(data.bookings ?? []);
      } catch {
        if (!cancelled) setItems([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!items || items.length === 0) return null;

  return (
    <section className="space-y-3" aria-labelledby="my-bookings-heading">
      <h2 id="my-bookings-heading" className="font-display text-xl font-semibold">
        {t.myRequests}
      </h2>
      <ul className="space-y-2">
        {items.map((b) => (
          <li key={b.token}>
            <Link
              href={`/book/r/${b.token}`}
              className="flex items-center justify-between rounded-xl border border-border bg-surface-1 px-4 py-3 text-sm hover:border-border-bright"
            >
              <span>
                {new Date(b.preferredStart).toLocaleString()} · ₪{b.priceIls}
              </span>
              <span className="text-muted-foreground">{b.status}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
