/**
 * POST /api/quiz/custom/submit
 *
 * Grades from server-stored keys only. Body: quiz_id + answers[] — no questions/keys.
 */
import { auth } from '@clerk/nextjs/server';
import { submitCustomQuizForUser } from '@/lib/custom-quiz';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: 'invalid_json' }, { status: 400 });
  }
  if (!body || typeof body !== 'object') {
    return Response.json({ error: 'invalid_body' }, { status: 400 });
  }
  const b = body as {
    quiz_id?: string;
    locale?: string;
    answers?: Array<{ item_id: string; chosen: string }>;
    questions?: unknown;
  };

  // Reject legacy client-supplied question keys (F1).
  if (Array.isArray(b.questions) && b.questions.length > 0) {
    return Response.json(
      { error: 'questions_not_accepted', message: 'Submit answers only; quiz is server-held.' },
      { status: 400 },
    );
  }

  const quizId = typeof b.quiz_id === 'string' ? b.quiz_id.trim() : '';
  if (!quizId) {
    return Response.json({ error: 'quiz_id_required' }, { status: 400 });
  }

  const answers = Array.isArray(b.answers) ? b.answers : [];
  if (answers.length === 0) {
    return Response.json({ error: 'answers_required' }, { status: 400 });
  }

  const locale = b.locale === 'en' ? 'en' : 'he';
  const result = await submitCustomQuizForUser(userId, quizId, answers, locale);
  if (!result) {
    return Response.json({ error: 'quiz_not_found' }, { status: 404 });
  }
  return Response.json(result);
}
