import { auth } from '@clerk/nextjs/server';
import 'server-only';
import { dbConfigured, recordLessonAnswer } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

interface Body {
  lesson_id?: string;
  question_id?: string;
  concept_id?: string;
  correct?: boolean;
  skill_atoms?: string[];
  time_spent_s?: number;
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

  const { lesson_id, question_id, concept_id, correct } = body;
  if (
    typeof lesson_id !== 'string' ||
    typeof question_id !== 'string' ||
    typeof concept_id !== 'string' ||
    typeof correct !== 'boolean'
  ) {
    return Response.json(
      { error: 'lesson_id, question_id, concept_id, correct required' },
      { status: 400 },
    );
  }

  const skillAtoms = Array.isArray(body.skill_atoms)
    ? body.skill_atoms.filter((s): s is string => typeof s === 'string')
    : [];

  try {
    await recordLessonAnswer({
      learnerId: userId,
      lessonId: lesson_id,
      questionId: question_id,
      conceptId: concept_id,
      correct,
      skillAtoms,
      timeSpentS: typeof body.time_spent_s === 'number' ? body.time_spent_s : null,
    });
    return Response.json({ ok: true });
  } catch (err) {
    return Response.json(
      { error: 'failed to record', detail: err instanceof Error ? err.message : String(err) },
      { status: 500 },
    );
  }
}
