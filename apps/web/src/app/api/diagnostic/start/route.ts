import { auth } from '@clerk/nextjs/server';
import {
  startDiagnosticSession,
  itemToQuestion,
  dbConfigured,
  abandonActiveDiagnosticSessions,
} from '@/lib/neon-db';
import {
  diagnosticStateToResults,
  initializeDiagnosticSession,
  resumePendingDiagnosticQuestion,
} from '@/lib/diagnostic-service';
import { diagnosticAnsweredCount } from '@/lib/diagnostic-plan';
import { normalizeLearnerSubjects } from '@/lib/diagnostic-start';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function startFreshDiagnostic(userId: string) {
  await abandonActiveDiagnosticSessions(userId);
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

  return Response.json({
    session_id: sessionId,
    question: itemToQuestion(firstItem),
    question_number: 1,
    total: state.validation_queue.length,
    goal_concept_id: state.goal_concept_id,
    probe_concepts: state.probe_concepts,
    status: 'question',
    fresh: true,
  });
}

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
    const pending = await resumePendingDiagnosticQuestion(userId);
    if (pending) {
      const answered = diagnosticAnsweredCount(pending.state);
      return Response.json({
        session_id: pending.sessionId,
        question: itemToQuestion(pending.item),
        question_number: answered + 1,
        total: pending.state.validation_queue.length,
        goal_concept_id: pending.state.goal_concept_id,
        probe_concepts: pending.state.probe_concepts,
        status: 'question',
        resumed: true,
      });
    }

    return await startFreshDiagnostic(userId);
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
