/**
 * TEMPORARY read-only self-diagnostic for the "Progress / Memory / My Tests not
 * updating" investigation.
 *
 * Returns row counts, latest timestamps, and — critically — how many of the
 * caller's own concept_mastery rows the subject-scope filter HIDES from the
 * Progress + Memory pages. Scoped to the logged-in caller only (their own
 * data), reads nothing else, writes nothing.
 *
 * DELETE THIS ROUTE once the diagnosis is captured.
 */
import { neon } from '@neondatabase/serverless';
import { getAuthContext } from '@/lib/auth';
import { getLearnerProfile } from '@/lib/neon-db';
import { conceptMatchesSubjects, resolveConceptSubject } from '@/lib/concept-scope';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Row = Record<string, unknown>;

export async function GET(req: Request) {
  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
  if (!url) return Response.json({ error: 'DATABASE_URL not set on this deployment' }, { status: 503 });

  const s = neon(url);
  const learnerId = ctx.learnerId;
  const num = (v: unknown): number => Number(v ?? 0);
  const probe = new URL(req.url).searchParams.get('probe') === '1';

  // ---- write-path probes (only with ?probe=1) ----
  // Answers: (1) does CREATE TABLE test_attempts actually work, or is there a
  // real DDL error the lazy ensureTable() is swallowing? (2) do chat_turns
  // writes land at all? Self-cleaning; scoped to the caller.
  let writeProbes: Row | undefined;
  if (probe) {
    const ddl = await (async (): Promise<Row> => {
      try {
        await s`
          CREATE TABLE IF NOT EXISTS test_attempts (
            id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            learner_id     TEXT NOT NULL,
            kind           TEXT NOT NULL DEFAULT 'weekly_gate',
            plan_id        TEXT,
            week_num       INT,
            quiz_id        TEXT,
            locale         TEXT NOT NULL DEFAULT 'he',
            score          DOUBLE PRECISION NOT NULL DEFAULT 0,
            passed         BOOLEAN NOT NULL DEFAULT FALSE,
            pass_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.75,
            per_topic      JSONB NOT NULL DEFAULT '{}'::jsonb,
            weak_concepts  TEXT[] NOT NULL DEFAULT '{}',
            questions      JSONB NOT NULL DEFAULT '[]'::jsonb,
            answers        JSONB NOT NULL DEFAULT '[]'::jsonb,
            feedback       JSONB,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
          )
        `;
        await s`CREATE INDEX IF NOT EXISTS ix_test_attempts_learner ON test_attempts (learner_id, created_at DESC)`;
        const exists = (await s`SELECT to_regclass('public.test_attempts') AS t`) as Row[];
        return { create_table: 'ok', table_now_exists: exists[0]?.t ?? null };
      } catch (err) {
        return { create_table: 'FAILED', error: (err as Error)?.message ?? String(err) };
      }
    })();

    const chatWrite = await (async (): Promise<Row> => {
      try {
        const ins = (await s`
          INSERT INTO chat_turns (id, learner_id, agent, role, content, session_id, created_at)
          VALUES (gen_random_uuid(), ${learnerId}, '__diag__', 'user', 'diagnostic probe', NULL, NOW())
          RETURNING id::text
        `) as Array<{ id: string }>;
        const id = ins[0]?.id ?? null;
        const back = (await s`SELECT COUNT(*)::int AS n FROM chat_turns WHERE learner_id = ${learnerId} AND agent = '__diag__'`) as Row[];
        if (id) await s`DELETE FROM chat_turns WHERE id = ${id}::uuid`;
        return { insert: id ? 'ok' : 'no-id', readback_count: num(back[0]?.n), cleaned_up: Boolean(id) };
      } catch (err) {
        return { insert: 'FAILED', error: (err as Error)?.message ?? String(err) };
      }
    })();

    writeProbes = { test_attempts_ddl: ddl, chat_turns_write: chatWrite };
  }

  const profile = await getLearnerProfile(learnerId).catch(() => null);
  const subjects: string[] = Array.isArray(profile?.subjects) ? profile.subjects : [];
  const hasPersona = Boolean((profile as { learner_persona?: string } | null)?.learner_persona);

  // ---- concept_mastery + the scope-filter effect (hypothesis A) ----
  let mastery: Row = { _error: 'not run' };
  try {
    const rows = (await s`
      SELECT concept_id, score::float AS score, data_points, last_activity
      FROM concept_mastery WHERE learner_id = ${learnerId}
      ORDER BY last_activity DESC NULLS LAST
    `) as Array<{ concept_id: string; score: number; data_points: number; last_activity: string }>;

    let shown = 0;
    const hiddenSamples: Array<{ concept_id: string; resolved_subject: string | null; score: number }> = [];
    for (const r of rows) {
      if (conceptMatchesSubjects(r.concept_id, subjects)) {
        shown += 1;
      } else if (hiddenSamples.length < 15) {
        hiddenSamples.push({
          concept_id: r.concept_id,
          resolved_subject: resolveConceptSubject(r.concept_id),
          score: r.score,
        });
      }
    }
    mastery = {
      total_rows: rows.length,
      mastered_ge_0_7: rows.filter((r) => r.score >= 0.7).length,
      latest_activity: rows[0]?.last_activity ?? null,
      shown_after_scope_filter: shown,
      HIDDEN_by_scope_filter: rows.length - shown,
      hidden_samples: hiddenSamples,
      recent_sample: rows.slice(0, 10).map((r) => ({
        concept_id: r.concept_id,
        score: r.score,
        resolved_subject: resolveConceptSubject(r.concept_id),
        in_scope: conceptMatchesSubjects(r.concept_id, subjects),
        last_activity: r.last_activity,
      })),
    };
  } catch (err) {
    mastery = { _error: (err as Error)?.message ?? String(err) };
  }

  const wrap = async (fn: () => Promise<Row>): Promise<Row> => {
    try {
      return await fn();
    } catch (err) {
      return { _error: (err as Error)?.message ?? String(err) };
    }
  };

  const skillPractice = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(last_practiced) AS latest FROM skill_practice WHERE learner_id = ${learnerId}`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null };
  });

  const chatTurns = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM chat_turns WHERE learner_id = ${learnerId}`) as Row[];
    const byAgent = (await s`SELECT agent AS key, COUNT(*)::int AS n FROM chat_turns WHERE learner_id = ${learnerId} GROUP BY agent ORDER BY agent`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_agent: byAgent };
  });

  const agentNotes = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM learner_agent_notes WHERE learner_id = ${learnerId}`) as Row[];
    const byAgent = (await s`SELECT agent AS key, COUNT(*)::int AS n FROM learner_agent_notes WHERE learner_id = ${learnerId} GROUP BY agent ORDER BY agent`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_agent: byAgent };
  });

  const testAttempts = await wrap(async () => {
    const r = (await s`SELECT COUNT(*)::int AS n, MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId}`) as Row[];
    const byKind = (await s`SELECT kind AS key, COUNT(*)::int AS n, MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId} GROUP BY kind ORDER BY kind`) as Row[];
    return { count: num(r[0]?.n), latest: r[0]?.latest ?? null, by_kind: byKind };
  });

  const otherQuizzes = await wrap(async () => {
    const wk = (await s`SELECT COUNT(*)::int AS gen, COUNT(submitted_at)::int AS submitted FROM weekly_quizzes_ai WHERE user_id = ${learnerId}`) as Row[];
    const mock = (await s`SELECT COUNT(*)::int AS n FROM mock_exam_results WHERE user_id = ${learnerId}`) as Row[];
    return {
      weekly_quizzes_ai_generated: num(wk[0]?.gen),
      weekly_quizzes_ai_submitted: num(wk[0]?.submitted),
      mock_exam_results: num(mock[0]?.n),
    };
  });

  return Response.json({
    learner_id: learnerId,
    profile: { exists: Boolean(profile), subjects, has_persona: hasPersona },
    concept_mastery: mastery,
    skill_practice: skillPractice,
    chat_turns: chatTurns,
    learner_agent_notes: agentNotes,
    test_attempts: testAttempts,
    other_quiz_tables: otherQuizzes,
    write_probes: writeProbes ?? 'add ?probe=1 to run write-path probes (DDL + chat_turns roundtrip)',
    hint: 'If concept_mastery.total_rows > 0 but shown_after_scope_filter is 0 (or much smaller), the SCOPE FILTER is hiding your progress. If total_rows is 0/stale, it is a WRITE-path bug.',
  });
}
