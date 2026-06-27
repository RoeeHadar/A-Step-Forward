import { auth } from '@clerk/nextjs/server';
import {
  startDiagnosticSession,
  fetchDiagnosticItems,
  itemToQuestion,
  getLearnerProfile,
  dbConfigured,
} from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const QUESTIONS_PER_SESSION = 12;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  let body: { topics?: string[]; subjects?: string[]; points_level?: string } = {};
  try {
    body = await req.json();
  } catch {
    body = {};
  }

  let subjects = body.subjects ?? [];
  let pointsLevel: string | null = null;

  if (subjects.length === 0) {
    const profile = await getLearnerProfile(userId);
    subjects = profile?.subjects ?? ['math'];

    // Derive points_level from goal or explicit points_group
    const pg = profile?.points_group ?? null;
    if (pg) {
      // Stored as e.g. "3", "3pt", "4", "4pt", "5", "5pt"
      const num = String(pg).replace(/pt$/i, '').trim();
      if (['3', '4', '5'].includes(num)) pointsLevel = `${num}pt`;
    } else if (profile?.goal) {
      const g = profile.goal.toLowerCase();
      if (g.includes('3')) pointsLevel = '3pt';
      else if (g.includes('4')) pointsLevel = '4pt';
      else if (g.includes('5')) pointsLevel = '5pt';
    }
  }

  // Allow caller to override points_level explicitly
  if (body.points_level) pointsLevel = body.points_level as string;

  const items = await fetchDiagnosticItems(subjects, QUESTIONS_PER_SESSION, pointsLevel);
  if (items.length === 0) {
    return Response.json(
      { error: 'No diagnostic items available for these subjects.' },
      { status: 404 },
    );
  }
  const sessionId = await startDiagnosticSession(userId, body.topics ?? subjects);

  // Pre-shuffle order is locked here in memory; we identify each question by id
  // and look up correctness later from the DB.
  const question = itemToQuestion(items[0]!);
  return Response.json({
    session_id: sessionId,
    question,
    question_number: 1,
    total: items.length,
    // pre-loaded queue to avoid extra round trips (cached client-side)
    queue: items.map(itemToQuestion),
  });
}
