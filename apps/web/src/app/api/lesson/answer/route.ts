import { auth } from '@clerk/nextjs/server';
import 'server-only';
import {
  dbConfigured,
  fetchLessonQuestionForGrading,
  gradeLessonAnswer,
  recordLessonAnswer,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

interface Body {
  lesson_id?: string;
  question_id?: string;
  concept_id?: string;
  /** Self-assessment for open/derivation kinds; ignored for objective kinds. */
  correct?: boolean;
  skill_atoms?: string[];
  time_spent_s?: number;
  /** Structured payload of what the learner submitted (per-kind shape). */
  user_answer?: unknown;
}

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  let body: Body;
  try {
    body = (await req.json()) as Body;
  } catch {
    return Response.json({ error: 'invalid json' }, { status: 400 });
  }

  const { lesson_id, question_id, concept_id } = body;
  if (
    typeof lesson_id !== 'string' ||
    typeof question_id !== 'string' ||
    typeof concept_id !== 'string'
  ) {
    return Response.json(
      { error: 'lesson_id, question_id, concept_id required' },
      { status: 400 },
    );
  }

  const skillAtoms = Array.isArray(body.skill_atoms)
    ? body.skill_atoms.filter((s): s is string => typeof s === 'string')
    : [];

  // Server-side grading. Load the question, recompute correctness from the
  // user's structured answer; never trust the client's `correct` flag for
  // objective kinds. Open/derivation fall back to self-assessment.
  const question = await fetchLessonQuestionForGrading(question_id);
  if (!question) {
    return Response.json({ error: 'question not found' }, { status: 404 });
  }
  const graded = gradeLessonAnswer(question, body.user_answer, body.correct);

  try {
    await recordLessonAnswer({
      learnerId: userId,
      lessonId: lesson_id,
      questionId: question_id,
      conceptId: concept_id,
      correct: graded.correct,
      skillAtoms,
      timeSpentS: typeof body.time_spent_s === 'number' ? body.time_spent_s : null,
    });
    return Response.json({
      ok: true,
      correct: graded.correct,
      graded_by: graded.graded_by,
    });
  } catch (err) {
    return Response.json(
      { error: 'failed to record', detail: err instanceof Error ? err.message : String(err) },
      { status: 500 },
    );
  }
}
