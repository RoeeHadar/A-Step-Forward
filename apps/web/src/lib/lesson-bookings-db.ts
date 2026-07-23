/**
 * Neon access for private lesson bookings (Book a Lesson).
 * Lazy-ensures `lesson_bookings` (also tracked in Alembic 0022).
 */
import 'server-only';
import { randomBytes } from 'node:crypto';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import type {
  CreateLessonBookingNormalized,
  LessonBookingStatus,
  LessonDurationH,
  LessonLevel,
  LessonModality,
  LessonSubject,
} from '@/lib/lesson-booking';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export const lessonBookingsDbConfigured = Boolean(sql);

let ensured = false;

export async function ensureLessonBookingsTable(): Promise<boolean> {
  if (!sql) return false;
  if (ensured) return true;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS lesson_bookings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        public_token TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'submitted'
          CHECK (status IN (
            'submitted', 'proposal_sent', 'pick_pending',
            'confirmed', 'rejected', 'cancelled', 'expired'
          )),
        requester_name TEXT NOT NULL,
        requester_email TEXT NOT NULL,
        requester_phone TEXT NOT NULL,
        locale TEXT NOT NULL DEFAULT 'he',
        clerk_user_id TEXT,
        booking_for_other BOOLEAN NOT NULL DEFAULT FALSE,
        learner_name TEXT NOT NULL,
        learner_grade TEXT,
        modality TEXT NOT NULL CHECK (modality IN ('online', 'haifa')),
        subjects TEXT[] NOT NULL,
        level_band TEXT NOT NULL
          CHECK (level_band IN ('middle_school', 'bagrut', 'university', 'other')),
        university_name TEXT,
        university_course TEXT,
        goal_text TEXT NOT NULL,
        notes TEXT,
        duration_h NUMERIC(3,1) NOT NULL,
        price_ils INT NOT NULL,
        preferred_start TIMESTAMPTZ NOT NULL,
        preferred_end TIMESTAMPTZ NOT NULL,
        proposed_windows JSONB NOT NULL DEFAULT '[]'::jsonb,
        selected_window JSONB,
        share_dossier BOOLEAN NOT NULL DEFAULT FALSE,
        dossier_snapshot JSONB,
        gcal_event_id TEXT,
        meeting_link TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_lesson_bookings_created ON lesson_bookings (created_at DESC)`;
    await sql`CREATE INDEX IF NOT EXISTS ix_lesson_bookings_clerk ON lesson_bookings (clerk_user_id, created_at DESC)`;
    await sql`CREATE INDEX IF NOT EXISTS ix_lesson_bookings_status ON lesson_bookings (status, created_at DESC)`;
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS ux_lesson_bookings_token ON lesson_bookings (public_token)`;
    ensured = true;
    return true;
  } catch (err) {
    logger.error('[lesson-bookings-db] ensure failed', { err: String(err) });
    return false;
  }
}

function newPublicToken(): string {
  return randomBytes(24).toString('base64url');
}

export type LessonBookingRow = {
  id: string;
  public_token: string;
  status: LessonBookingStatus;
  requester_name: string;
  requester_email: string;
  requester_phone: string;
  locale: 'he' | 'en';
  clerk_user_id: string | null;
  booking_for_other: boolean;
  learner_name: string;
  learner_grade: string | null;
  modality: LessonModality;
  subjects: LessonSubject[];
  level_band: LessonLevel;
  university_name: string | null;
  university_course: string | null;
  goal_text: string;
  notes: string | null;
  duration_h: number;
  price_ils: number;
  preferred_start: string;
  preferred_end: string;
  proposed_windows: unknown;
  selected_window: unknown;
  share_dossier: boolean;
  created_at: string;
  updated_at: string;
};

function mapRow(r: Record<string, unknown>): LessonBookingRow {
  const subjectsRaw = r.subjects;
  const subjects = Array.isArray(subjectsRaw)
    ? (subjectsRaw as string[]).filter(Boolean) as LessonSubject[]
    : [];
  return {
    id: String(r.id),
    public_token: String(r.public_token),
    status: r.status as LessonBookingStatus,
    requester_name: String(r.requester_name),
    requester_email: String(r.requester_email),
    requester_phone: String(r.requester_phone),
    locale: r.locale === 'en' ? 'en' : 'he',
    clerk_user_id: r.clerk_user_id == null ? null : String(r.clerk_user_id),
    booking_for_other: Boolean(r.booking_for_other),
    learner_name: String(r.learner_name),
    learner_grade: r.learner_grade == null ? null : String(r.learner_grade),
    modality: r.modality as LessonModality,
    subjects,
    level_band: r.level_band as LessonLevel,
    university_name: r.university_name == null ? null : String(r.university_name),
    university_course: r.university_course == null ? null : String(r.university_course),
    goal_text: String(r.goal_text),
    notes: r.notes == null ? null : String(r.notes),
    duration_h: Number(r.duration_h),
    price_ils: Number(r.price_ils),
    preferred_start: new Date(String(r.preferred_start)).toISOString(),
    preferred_end: new Date(String(r.preferred_end)).toISOString(),
    proposed_windows: r.proposed_windows ?? [],
    selected_window: r.selected_window ?? null,
    share_dossier: Boolean(r.share_dossier),
    created_at: new Date(String(r.created_at)).toISOString(),
    updated_at: new Date(String(r.updated_at)).toISOString(),
  };
}

/** Public-safe projection (no phone/email for strangers — owner has token). */
export function toPublicBookingView(row: LessonBookingRow) {
  return {
    id: row.id,
    token: row.public_token,
    status: row.status,
    locale: row.locale,
    modality: row.modality,
    subjects: row.subjects,
    level: row.level_band,
    universityName: row.university_name,
    universityCourse: row.university_course,
    durationH: row.duration_h as LessonDurationH,
    priceIls: row.price_ils,
    preferredStart: row.preferred_start,
    preferredEnd: row.preferred_end,
    bookingForOther: row.booking_for_other,
    learnerName: row.learner_name,
    requesterName: row.requester_name,
    proposedWindows: row.proposed_windows,
    selectedWindow: row.selected_window,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

export async function insertLessonBooking(input: {
  data: CreateLessonBookingNormalized;
  clerkUserId: string | null;
}): Promise<LessonBookingRow | null> {
  if (!sql) return null;
  const ok = await ensureLessonBookingsTable();
  if (!ok) return null;

  const token = newPublicToken();
  const subjects = input.data.subjects;
  try {
    const rows = await sql`
      INSERT INTO lesson_bookings (
        public_token, status,
        requester_name, requester_email, requester_phone, locale, clerk_user_id,
        booking_for_other, learner_name, learner_grade,
        modality, subjects, level_band, university_name, university_course,
        goal_text, notes, duration_h, price_ils,
        preferred_start, preferred_end, share_dossier
      ) VALUES (
        ${token}, 'submitted',
        ${input.data.requesterName}, ${input.data.requesterEmail}, ${input.data.requesterPhone},
        ${input.data.locale}, ${input.clerkUserId},
        ${input.data.bookingForOther}, ${input.data.learnerName}, ${input.data.learnerGrade},
        ${input.data.modality}, ${subjects}, ${input.data.level},
        ${input.data.universityName}, ${input.data.universityCourse},
        ${input.data.goalText}, ${input.data.notes}, ${input.data.durationH}, ${input.data.priceIls},
        ${input.data.preferredStart.toISOString()}, ${input.data.preferredEnd.toISOString()},
        ${input.data.shareDossier}
      )
      RETURNING *
    `;
    const row = Array.isArray(rows) ? rows[0] : null;
    if (!row) return null;
    return mapRow(row as Record<string, unknown>);
  } catch (err) {
    logger.error('[lesson-bookings-db] insert failed', { err: String(err) });
    return null;
  }
}

export async function getLessonBookingByToken(token: string): Promise<LessonBookingRow | null> {
  if (!sql || !token) return null;
  const ok = await ensureLessonBookingsTable();
  if (!ok) return null;
  try {
    const rows = await sql`
      SELECT * FROM lesson_bookings WHERE public_token = ${token} LIMIT 1
    `;
    const row = Array.isArray(rows) ? rows[0] : null;
    if (!row) return null;
    return mapRow(row as Record<string, unknown>);
  } catch (err) {
    logger.error('[lesson-bookings-db] getByToken failed', { err: String(err) });
    return null;
  }
}

export async function listLessonBookingsForUser(
  clerkUserId: string,
  limit = 20,
): Promise<LessonBookingRow[]> {
  if (!sql || !clerkUserId) return [];
  const ok = await ensureLessonBookingsTable();
  if (!ok) return [];
  const capped = Math.min(Math.max(limit, 1), 50);
  try {
    const rows = await sql`
      SELECT * FROM lesson_bookings
      WHERE clerk_user_id = ${clerkUserId}
      ORDER BY created_at DESC
      LIMIT ${capped}
    `;
    if (!Array.isArray(rows)) return [];
    return rows.map((r) => mapRow(r as Record<string, unknown>));
  } catch (err) {
    logger.error('[lesson-bookings-db] listForUser failed', { err: String(err) });
    return [];
  }
}
