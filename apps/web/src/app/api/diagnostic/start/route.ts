import { auth } from '@clerk/nextjs/server';
import {
  startDiagnosticSession,
  itemToQuestion,
  dbConfigured,
  completeDiagnostic,
  persistDiagnosticSummary,
  abandonActiveDiagnosticSessions,
} from '@/lib/neon-db';
import {
  diagnosticStateToResults,
  initializeDiagnosticSession,
  resumeOrFinalizeDiagnosticSession,
} from '@/lib/diagnostic-service';
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
    const resumed = await resumeOrFinalizeDiagnosticSession(userId);
    if (resumed?.mode === 'question') {
      return Response.json({
        session_id: resumed.sessionId,
        question: itemToQuestion(resumed.item),
        question_number: resumed.questionNumber,
        total: resumed.state.validation_queue.length,
        goal_concept_id: resumed.state.goal_concept_id,
        probe_concepts: resumed.state.probe_concepts,
        status: 'question',
        resumed: true,
      });
    }

    if (resumed?.mode === 'complete' && resumed.questionsAnswered >= 1) {
      await persistDiagnosticSummary(userId, resumed.summary);
      const mastery = await completeDiagnostic(
        resumed.sessionId,
        userId,
        diagnosticStateToResults(resumed.state, resumed.summary),
      );
      return Response.json({
        session_id: resumed.sessionId,
        complete: true,
        status: 'calibration_complete',
        resumed: true,
        results: {
          mastery_by_topic: mastery,
          summary: resumed.summary,
        },
        questions_answered: resumed.questionsAnswered,
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
