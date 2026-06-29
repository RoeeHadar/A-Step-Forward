/**
 * POST /api/quiz/mock-exam
 *
 * Generates (or returns cached) a timed Bagrut-style mock exam for the
 * authenticated learner. Cached per (user, subject, level) for 24 hours.
 */
import { auth } from '@clerk/nextjs/server';
import { getOrCreateMockExam } from '@/lib/mock-exam';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const VALID_SUBJECTS = new Set(['math', 'physics', 'makhina']);
const VALID_LEVELS = new Set([
  '3pt',
  '4pt',
  '5pt',
  'hs_physics',
  'calculus',
  'stats',
  'linear_algebra',
]);

const LEVELS_BY_SUBJECT: Record<string, string[]> = {
  math: ['3pt', '4pt', '5pt'],
  physics: ['hs_physics'],
  makhina: ['calculus', 'stats', 'linear_algebra'],
};

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: { subject?: string; level?: string; duration_minutes?: number; locale?: string };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const subject = body.subject?.trim().toLowerCase() ?? '';
  const level = body.level?.trim().toLowerCase() ?? '';
  const durationMinutes = body.duration_minutes ?? 90;
  const locale = body.locale === 'en' ? 'en' : 'he';

  if (!VALID_SUBJECTS.has(subject)) {
    return Response.json(
      { error: 'subject must be math, physics, or makhina' },
      { status: 400 },
    );
  }
  if (!VALID_LEVELS.has(level)) {
    return Response.json(
      {
        error:
          'level must be 3pt, 4pt, 5pt, hs_physics, calculus, stats, or linear_algebra',
      },
      { status: 400 },
    );
  }
  const allowedLevels = LEVELS_BY_SUBJECT[subject] ?? [];
  if (!allowedLevels.includes(level)) {
    return Response.json({ error: `level ${level} is not valid for subject ${subject}` }, { status: 400 });
  }
  if (![45, 60, 90].includes(durationMinutes)) {
    return Response.json({ error: 'duration_minutes must be 45, 60, or 90' }, { status: 400 });
  }

  try {
    const exam = await getOrCreateMockExam(userId, subject, level, durationMinutes, locale);
    if (!exam) {
      return Response.json(
        {
          error: 'exam_generation_failed',
          message: 'Mock exam is temporarily unavailable. Please try again in a moment.',
        },
        { status: 503 },
      );
    }
    return Response.json(exam);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    return Response.json({ error: message }, { status: 500 });
  }
}
