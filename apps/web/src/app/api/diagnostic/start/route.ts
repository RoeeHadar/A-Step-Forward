import { auth } from '@clerk/nextjs/server';
import {
  startDiagnosticSession,
  fetchDiagnosticItemsWithFallback,
  itemToQuestion,
  getLearnerProfile,
  dbConfigured,
} from '@/lib/neon-db';
import {
  normalizeLearnerSubjects,
  resolveDiagnosticPointsLevel,
} from '@/lib/diagnostic-start';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const QUESTIONS_PER_SESSION = 12;

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return Response.json(
      { error: 'unauthorized', message: 'Authentication required' },
      { status: 401 },
    );
  }
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  try {
    let body: { topics?: string[]; subjects?: string[]; points_level?: string } = {};
    try {
      body = await req.json();
    } catch {
      body = {};
    }

    let subjects = normalizeLearnerSubjects(body.subjects);
    let pointsLevel: string | null = body.points_level ?? null;

    if ((body.subjects ?? []).length === 0) {
      const profile = await getLearnerProfile(userId);
      subjects = normalizeLearnerSubjects(profile?.subjects);
      const personality = (profile?.personality_profile ?? {}) as Record<string, unknown>;
      pointsLevel =
        pointsLevel ??
        resolveDiagnosticPointsLevel({
          pointsGroup: profile?.points_group,
          goalKey:
            typeof personality.goal_key === 'string' ? personality.goal_key : null,
          adultGoal:
            typeof personality.adult_goal === 'string' ? personality.adult_goal : null,
        });
    }

    const items = await fetchDiagnosticItemsWithFallback(
      subjects,
      QUESTIONS_PER_SESSION,
      pointsLevel,
    );
    if (items.length === 0) {
      return Response.json(
        {
          error:
            'No diagnostic questions are available yet for your subjects. Please try again in a few minutes or contact support.',
        },
        { status: 404 },
      );
    }

    const sessionId = await startDiagnosticSession(userId, body.topics ?? subjects);
    const question = itemToQuestion(items[0]!);
    if (!question.options.length || !question.stem.trim()) {
      return Response.json(
        { error: 'Diagnostic question bank returned an invalid item.' },
        { status: 500 },
      );
    }

    return Response.json({
      session_id: sessionId,
      question,
      question_number: 1,
      total: items.length,
      queue: items.map(itemToQuestion),
    });
  } catch (err) {
    console.error('[diagnostic/start]', err);
    return Response.json(
      {
        error:
          err instanceof Error
            ? err.message
            : 'Failed to start diagnostic session',
      },
      { status: 500 },
    );
  }
}
