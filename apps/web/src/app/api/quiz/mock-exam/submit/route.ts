/**
 * POST /api/quiz/mock-exam/submit
 *
 * Auto-grades MCQs and stores the attempt in mock_exam_results.
 */
import { auth } from '@clerk/nextjs/server';
import { submitMockExam } from '@/lib/mock-exam';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  let body: {
    exam_id?: number;
    answers?: Record<string, string>;
    time_taken_seconds?: number;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const examId = body.exam_id;
  const answers = body.answers ?? {};
  const timeTaken = body.time_taken_seconds ?? 0;

  if (!examId || !Number.isFinite(examId)) {
    return Response.json({ error: 'exam_id is required' }, { status: 400 });
  }

  try {
    const result = await submitMockExam(userId, examId, answers, timeTaken);
    if (!result) {
      return Response.json({ error: 'Exam not found' }, { status: 404 });
    }
    return Response.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    return Response.json({ error: message }, { status: 500 });
  }
}
