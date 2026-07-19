/**
 * POST /api/quiz/mock-exam/seed-submit
 *
 * Archives a finished seed (catalog) mock exam into test_attempts + Memory.
 * Neon-direct; does not require a prior LLM-generated exam row.
 */
import { auth } from '@clerk/nextjs/server';
import { dbConfigured } from '@/lib/neon-db';
import { submitSeedMockExam } from '@/lib/seed-mock-exam-submit';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  let body: {
    exam_id?: string;
    answers?: Record<string, string>;
    locale?: string;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const examId = typeof body.exam_id === 'string' ? body.exam_id.trim() : '';
  if (!examId) {
    return Response.json({ error: 'exam_id is required' }, { status: 400 });
  }

  const locale = body.locale === 'en' ? 'en' : 'he';
  const answers = body.answers && typeof body.answers === 'object' ? body.answers : {};

  try {
    const result = await submitSeedMockExam(userId, examId, answers, locale);
    if (!result) {
      return Response.json({ error: 'Exam not found' }, { status: 404 });
    }
    return Response.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    return Response.json({ error: message }, { status: 500 });
  }
}
