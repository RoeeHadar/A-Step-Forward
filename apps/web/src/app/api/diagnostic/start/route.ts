import { auth } from '@clerk/nextjs/server';
import {
  startDiagnosticSession,
  itemToQuestion,
  dbConfigured,
} from '@/lib/neon-db';
import {
  diagnosticStateToResults,
  initializeDiagnosticSession,
} from '@/lib/diagnostic-service';
import { DIAGNOSTIC_QUESTIONS_PER_SESSION, normalizeLearnerSubjects } from '@/lib/diagnostic-start';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST() {
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
    const init = await initializeDiagnosticSession(userId);
    if (!init) {
      return Response.json(
        {
          error:
            'No diagnostic questions are available yet for your profile and goal. Please try again in a few minutes or contact support.',
        },
        { status: 404 },
      );
    }

    const { state, firstItem, profile } = init;
    const subjects = normalizeLearnerSubjects(profile.subjects);
    const sessionId = await startDiagnosticSession(
      userId,
      subjects,
      diagnosticStateToResults(state),
    );
    const question = itemToQuestion(firstItem);

    return Response.json({
      session_id: sessionId,
      question,
      question_number: 1,
      total: DIAGNOSTIC_QUESTIONS_PER_SESSION,
      goal_concept_id: state.goal_concept_id,
      probe_concepts: state.probe_concepts,
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
