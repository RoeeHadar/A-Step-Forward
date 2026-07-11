import { auth } from '@clerk/nextjs/server';
import {
  getDiagnosticSession,
  recordDiagnosticAnswer,
  bumpDiagnosticIdx,
  completeDiagnostic,
  getDiagnosticItemById,
  fetchDiagnosticItemsWithFallback,
  itemToQuestion,
  dbConfigured,
} from '@/lib/neon-db';
import {
  DIAGNOSTIC_QUESTIONS_PER_SESSION,
  normalizeLearnerSubjects,
} from '@/lib/diagnostic-start';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const KEY_ORDER = ['A', 'B', 'C', 'D'];

interface ItemRow {
  topic: string;
  subject: string;
  options: { choices: string[]; correct: string };
}

async function getItem(itemId: string): Promise<ItemRow | null> {
  const item = await getDiagnosticItemById(itemId);
  if (!item) return null;
  const raw = item.options as { choices?: string[]; correct?: string };
  return {
    topic: item.topic,
    subject: item.subject,
    options: {
      choices: raw?.choices ?? [],
      correct: raw?.correct ?? 'A',
    },
  };
}

function resolveCorrectLetter(options: { choices: string[]; correct: string }): string {
  const key = (options.correct ?? '').trim().toUpperCase();
  if (/^[A-D]$/.test(key)) return key;
  const idx = options.choices.findIndex((c) => c.trim() === key);
  return idx >= 0 ? (KEY_ORDER[idx] ?? 'A') : 'A';
}

function sessionItemIds(session: { results: Record<string, unknown> | null }): string[] {
  const raw = session.results?.item_ids;
  if (!Array.isArray(raw)) return [];
  return raw.filter((id): id is string => typeof id === 'string');
}

function sessionSubjects(session: {
  topics: string[];
  results: Record<string, unknown> | null;
}): string[] {
  const fromResults = session.results?.subjects;
  if (Array.isArray(fromResults)) {
    const subjects = fromResults.filter((s): s is string => typeof s === 'string');
    if (subjects.length > 0) return normalizeLearnerSubjects(subjects);
  }
  return normalizeLearnerSubjects(session.topics);
}

async function resolveNextQuestion(
  session: {
    topics: string[];
    results: Record<string, unknown> | null;
  },
  nextIdx: number,
) {
  const itemIds = sessionItemIds(session);
  const queuedId = itemIds[nextIdx];
  if (queuedId) {
    const queued = await getDiagnosticItemById(queuedId);
    if (queued) return queued;
  }

  // Legacy sessions (pre-queue deploy) or stale IDs after a bank reseed.
  const subjects = sessionSubjects(session);
  const fallback = await fetchDiagnosticItemsWithFallback(subjects, 1);
  return fallback[0] ?? null;
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

  const item = await getItem(body.item_id);
  if (!item) {
    return Response.json({ error: 'item not found' }, { status: 404 });
  }

  const correctLetter = resolveCorrectLetter(item.options);
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

  const newIdx = await bumpDiagnosticIdx(sessionId);

  if (newIdx >= DIAGNOSTIC_QUESTIONS_PER_SESSION) {
    const mastery = await completeDiagnostic(sessionId, userId);
    return Response.json({
      complete: true,
      results: { mastery_by_topic: mastery },
      questions_answered: newIdx,
    });
  }

  const nextItem = await resolveNextQuestion(session, newIdx);
  if (!nextItem) {
    const mastery = await completeDiagnostic(sessionId, userId);
    return Response.json({
      complete: true,
      results: { mastery_by_topic: mastery },
      questions_answered: newIdx,
    });
  }

  const itemIds = sessionItemIds(session);
  return Response.json({
    complete: false,
    question: itemToQuestion(nextItem),
    question_number: newIdx + 1,
    total: itemIds.length || DIAGNOSTIC_QUESTIONS_PER_SESSION,
  });
}
