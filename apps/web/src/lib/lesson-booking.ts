/**
 * Pure helpers for Book-a-Lesson (pricing, windows, validation).
 * No DB / server-only — safe for unit tests and shared with API + UI.
 */

export const LESSON_HOURLY_RATE_ILS = 200;
export const LESSON_DURATIONS_H = [1, 1.5, 2, 2.5, 3] as const;
export type LessonDurationH = (typeof LESSON_DURATIONS_H)[number];

export const LESSON_TZ = 'Asia/Jerusalem';
export const LESSON_MIN_LEAD_MS = 24 * 60 * 60 * 1000;
export const LESSON_MAX_AHEAD_MS = 8 * 7 * 24 * 60 * 60 * 1000;

export const LESSON_MODALITIES = ['online', 'haifa'] as const;
export type LessonModality = (typeof LESSON_MODALITIES)[number];

export const LESSON_SUBJECTS = ['math', 'physics'] as const;
export type LessonSubject = (typeof LESSON_SUBJECTS)[number];

export const LESSON_LEVELS = ['middle_school', 'bagrut', 'university', 'other'] as const;
export type LessonLevel = (typeof LESSON_LEVELS)[number];

export const LESSON_STATUSES = [
  'submitted',
  'proposal_sent',
  'pick_pending',
  'confirmed',
  'rejected',
  'cancelled',
  'expired',
] as const;
export type LessonBookingStatus = (typeof LESSON_STATUSES)[number];

export function isLessonDuration(value: unknown): value is LessonDurationH {
  return typeof value === 'number' && (LESSON_DURATIONS_H as readonly number[]).includes(value);
}

export function priceIlsForDuration(durationH: LessonDurationH): number {
  return Math.round(LESSON_HOURLY_RATE_ILS * durationH);
}

/** Convert a wall-clock date+time in `timeZone` to a UTC Date. */
export function wallTimeInZoneToUtc(date: string, time: string, timeZone: string): Date {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(time)) {
    throw new Error('invalid_date_or_time');
  }
  const y = Number(date.slice(0, 4));
  const m = Number(date.slice(5, 7));
  const d = Number(date.slice(8, 10));
  const hh = Number(time.slice(0, 2));
  const mm = Number(time.slice(3, 5));
  let utcMs = Date.UTC(y, m - 1, d, hh, mm, 0);
  for (let i = 0; i < 3; i++) {
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).formatToParts(new Date(utcMs));
    const get = (type: Intl.DateTimeFormatPartTypes) =>
      Number(parts.find((p) => p.type === type)?.value ?? NaN);
    let hour = get('hour');
    if (hour === 24) hour = 0;
    const asLocalMs = Date.UTC(
      get('year'),
      get('month') - 1,
      get('day'),
      hour,
      get('minute'),
      get('second'),
    );
    const desiredMs = Date.UTC(y, m - 1, d, hh, mm, 0);
    utcMs += desiredMs - asLocalMs;
  }
  return new Date(utcMs);
}

export function preferredWindowUtc(
  date: string,
  time: string,
  durationH: LessonDurationH,
  nowMs: number = Date.now(),
): { start: Date; end: Date } | { error: string } {
  let start: Date;
  try {
    start = wallTimeInZoneToUtc(date, time, LESSON_TZ);
  } catch {
    return { error: 'invalid_date_or_time' };
  }
  if (Number.isNaN(start.getTime())) return { error: 'invalid_date_or_time' };
  const lead = start.getTime() - nowMs;
  if (lead < LESSON_MIN_LEAD_MS) return { error: 'too_soon' };
  if (lead > LESSON_MAX_AHEAD_MS) return { error: 'too_far' };
  const end = new Date(start.getTime() + durationH * 60 * 60 * 1000);
  return { start, end };
}

export type CreateLessonBookingInput = {
  requesterName: string;
  requesterEmail: string;
  requesterPhone: string;
  locale: 'he' | 'en';
  modality: LessonModality;
  subjects: LessonSubject[];
  level: LessonLevel;
  universityName?: string;
  universityCourse?: string;
  goalText: string;
  notes?: string;
  durationH: LessonDurationH;
  preferredDate: string;
  preferredTime: string;
  bookingForOther?: boolean;
  learnerName?: string;
  learnerGrade?: string;
  shareDossier?: boolean;
};

export type CreateLessonBookingNormalized = {
  requesterName: string;
  requesterEmail: string;
  requesterPhone: string;
  locale: 'he' | 'en';
  modality: LessonModality;
  subjects: LessonSubject[];
  level: LessonLevel;
  universityName: string | null;
  universityCourse: string | null;
  goalText: string;
  notes: string | null;
  durationH: LessonDurationH;
  priceIls: number;
  preferredStart: Date;
  preferredEnd: Date;
  bookingForOther: boolean;
  learnerName: string;
  learnerGrade: string | null;
  shareDossier: boolean;
};

function trim(s: unknown, max: number): string {
  return String(s ?? '')
    .trim()
    .slice(0, max);
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function normalizeCreateLessonBooking(
  raw: CreateLessonBookingInput,
  nowMs: number = Date.now(),
): { ok: true; value: CreateLessonBookingNormalized } | { ok: false; error: string } {
  const requesterName = trim(raw.requesterName, 200);
  const requesterEmail = trim(raw.requesterEmail, 320).toLowerCase();
  const requesterPhone = trim(raw.requesterPhone, 40);
  const goalText = trim(raw.goalText, 2000);
  const notes = trim(raw.notes, 2000) || null;
  const locale = raw.locale === 'en' ? 'en' : 'he';

  if (requesterName.length < 2) return { ok: false, error: 'name_required' };
  if (!EMAIL_RE.test(requesterEmail)) return { ok: false, error: 'email_invalid' };
  if (requesterPhone.length < 7) return { ok: false, error: 'phone_required' };
  // goalText is optional

  if (!LESSON_MODALITIES.includes(raw.modality)) return { ok: false, error: 'modality_invalid' };
  if (!isLessonDuration(raw.durationH)) return { ok: false, error: 'duration_invalid' };
  if (!LESSON_LEVELS.includes(raw.level)) return { ok: false, error: 'level_invalid' };

  const subjects = Array.isArray(raw.subjects)
    ? [...new Set(raw.subjects.filter((s): s is LessonSubject => (LESSON_SUBJECTS as readonly string[]).includes(s)))]
    : [];
  if (subjects.length === 0) return { ok: false, error: 'subjects_required' };

  let universityName: string | null = trim(raw.universityName, 200) || null;
  let universityCourse: string | null = trim(raw.universityCourse, 200) || null;
  if (raw.level === 'university') {
    if (!universityName) return { ok: false, error: 'university_name_required' };
    if (!universityCourse) return { ok: false, error: 'university_course_required' };
  } else {
    universityName = null;
    universityCourse = null;
  }

  const bookingForOther = Boolean(raw.bookingForOther);
  const learnerName = bookingForOther
    ? trim(raw.learnerName, 200)
    : requesterName;
  if (bookingForOther && learnerName.length < 2) {
    return { ok: false, error: 'learner_name_required' };
  }
  const learnerGrade = trim(raw.learnerGrade, 80) || null;

  const window = preferredWindowUtc(raw.preferredDate, raw.preferredTime, raw.durationH, nowMs);
  if ('error' in window) return { ok: false, error: window.error };

  return {
    ok: true,
    value: {
      requesterName,
      requesterEmail,
      requesterPhone,
      locale,
      modality: raw.modality,
      subjects,
      level: raw.level,
      universityName,
      universityCourse,
      goalText,
      notes,
      durationH: raw.durationH,
      priceIls: priceIlsForDuration(raw.durationH),
      preferredStart: window.start,
      preferredEnd: window.end,
      bookingForOther,
      learnerName,
      learnerGrade,
      shareDossier: Boolean(raw.shareDossier),
    },
  };
}

export function publicBookingStatusLabel(
  status: LessonBookingStatus,
  locale: 'he' | 'en',
): string {
  const en: Record<LessonBookingStatus, string> = {
    submitted: 'Awaiting confirmation',
    proposal_sent: 'New times proposed — pick one',
    pick_pending: 'Your pick is awaiting confirmation',
    confirmed: 'Confirmed',
    rejected: 'Declined',
    cancelled: 'Cancelled',
    expired: 'Expired',
  };
  const he: Record<LessonBookingStatus, string> = {
    submitted: 'ממתין לאישור',
    proposal_sent: 'הוצעו זמנים חדשים — בחרו אחד',
    pick_pending: 'הבחירה שלכם ממתינה לאישור',
    confirmed: 'אושר',
    rejected: 'נדחה',
    cancelled: 'בוטל',
    expired: 'פג תוקף',
  };
  return (locale === 'he' ? he : en)[status];
}
