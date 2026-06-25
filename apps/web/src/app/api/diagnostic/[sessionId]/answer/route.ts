import { auth } from '@clerk/nextjs/server';
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import {
  getDiagnosticSession,
  recordDiagnosticAnswer,
  bumpDiagnosticIdx,
  completeDiagnostic,
  fetchDiagnosticItems,
  itemToQuestion,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;

const TOTAL_QUESTIONS = 12;
const KEY_ORDER = ['A', 'B', 'C', 'D'];

interface ItemRow {
  topic: string;
  subject: string;
  options: { choices: string[]; correct: string };
}

async function getItem(itemId: string): Promise<ItemRow | null> {
  if (!sql) return null;
  const rows = (await sql`
    SELECT topic, subject, options
    FROM diagnostic_items WHERE id = ${itemId}::uuid LIMIT 1
  `) as ItemRow[];
  return rows[0] ?? null;
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

  const item = await getItem(body.item_id);
  if (!item) {
    return Response.json({ error: 'item not found' }, { status: 404 });
  }

  const correctKey = item.options.correct;
  const correctIdx = item.options.choices.findIndex(
    (c) => c.trim() === correctKey?.trim(),
  );
  const correctLetter =
    correctIdx >= 0 ? KEY_ORDER[correctIdx] : (correctKey ?? '').toUpperCase().trim()[0];
  const isCorrect = body.chosen.trim().toUpperCase() === correctLetter;

  await recordDiagnosticAnswer(sessionId, body.item_id, isCorrect, item.topic, userId);
  const newIdx = await bumpDiagnosticIdx(sessionId);

  if (newIdx >= TOTAL_QUESTIONS) {
    const mastery = await completeDiagnostic(sessionId, userId);
    return Response.json({
      complete: true,
      results: { mastery_by_topic: mastery },
    });
  }

  // Fetch next random item (avoid the one we just answered would be nice but acceptable to repeat across sessions)
  const next = await fetchDiagnosticItems(session.topics, 1);
  if (next.length === 0) {
    const mastery = await completeDiagnostic(sessionId, userId);
    return Response.json({
      complete: true,
      results: { mastery_by_topic: mastery },
    });
  }
  return Response.json({
    complete: false,
    question: itemToQuestion(next[0]!),
    question_number: newIdx + 1,
  });
}
