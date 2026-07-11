import { auth } from '@clerk/nextjs/server';
import {
  getDiagnosticSession,
  recordDiagnosticAnswer,
  bumpDiagnosticIdx,
  completeDiagnostic,
  getDiagnosticItemById,
  updateDiagnosticSessionResults,
  persistDiagnosticSummary,
  itemToQuestion,
  dbConfigured,
} from '@/lib/neon-db';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION } from '@/lib/diagnostic-start';
import {
  advanceDiagnosticSession,
  diagnosticStateToResults,
  loadDiagnosticStateFromSession,
  resolveDiagnosticItemFromSession,
} from '@/lib/diagnostic-service';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const KEY_ORDER = ['A', 'B', 'C', 'D'];

function resolveCorrectLetter(options: { choices: string[]; correct: string }): string {
  const key = (options.correct ?? '').trim().toUpperCase();
  if (/^[A-D]$/.test(key)) return key;
  const idx = options.choices.findIndex((c) => c.trim() === key);
  return idx >= 0 ? (KEY_ORDER[idx] ?? 'A') : 'A';
}

export async function POST(
  req: Request,
  { params }: { params: Promise<{ sessionId: string }> },
) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  const { sessionId } = await params;
  const body = (await req.json()) as { item_id?: string; chosen?: string };
  if (!body.item_id || !body.chosen) {
    return Response.json({ error: 'item_id and chosen required' }, { status: 400 });
  }

  const session = await getDiagnosticSession(sessionId);
  if (!session) {
    return Response.json({ error: 'session not found' }, { status: 404 });
  }
  if (session.learner_id !== userId) {
    return Response.json({ error: 'forbidden' }, { status: 403 });
  }
  if (session.status === 'completed') {
    return Response.json({ error: 'session already completed' }, { status: 409 });
  }

  const priorState = loadDiagnosticStateFromSession(session.results);
  if (!priorState) {
    return Response.json(
      { error: 'Diagnostic session state is invalid. Please start a new diagnostic.' },
      { status: 409 },
    );
  }

  let item = await getDiagnosticItemById(body.item_id);
  if (!item) {
    item = resolveDiagnosticItemFromSession(body.item_id, priorState);
  }
  if (!item) {
    return Response.json({ error: 'item not found' }, { status: 404 });
  }

  const raw = item.options as { choices?: string[]; correct?: string };
  const correctLetter = resolveCorrectLetter({
    choices: raw?.choices ?? [],
    correct: raw?.correct ?? 'A',
  });
  const chosenLetter = body.chosen.trim().toUpperCase();
  const isCorrect = chosenLetter === correctLetter;

  try {
    await recordDiagnosticAnswer(
      sessionId,
      body.item_id,
      chosenLetter,
      isCorrect,
      item.topic,
      userId,
    );
  } catch (err) {
    console.error('[diagnostic/answer] record failed', err);
    return Response.json(
      {
        error:
          err instanceof Error
            ? err.message
            : 'Could not save your answer. Please try again.',
      },
      { status: 500 },
    );
  }

  const advanced = await advanceDiagnosticSession(userId, priorState, {
    item_id: body.item_id,
    topic: item.topic,
    difficulty: item.difficulty,
    correct: isCorrect,
    chosen: chosenLetter,
  });

  await updateDiagnosticSessionResults(
    sessionId,
    diagnosticStateToResults(advanced.state, advanced.summary),
  );
  const newIdx = await bumpDiagnosticIdx(sessionId);

  if (advanced.complete && advanced.summary) {
    await persistDiagnosticSummary(userId, advanced.summary);
    const mastery = await completeDiagnostic(
      sessionId,
      userId,
      diagnosticStateToResults(advanced.state, advanced.summary),
    );
    return Response.json({
      complete: true,
      status: 'calibration_complete',
      results: {
        mastery_by_topic: mastery,
        summary: advanced.summary,
      },
      questions_answered: newIdx,
    });
  }

  if (!advanced.nextItem && !advanced.complete) {
    return Response.json(
      {
        error: 'No further questions available for your profile yet.',
        status: 'exhausted',
        questions_answered: advanced.state.responses.length,
      },
      { status: 409 },
    );
  }

  return Response.json({
    complete: false,
    status: 'question',
    question: itemToQuestion(advanced.nextItem!),
    question_number: newIdx + 1,
    total: DIAGNOSTIC_QUESTIONS_PER_SESSION,
  });
}
