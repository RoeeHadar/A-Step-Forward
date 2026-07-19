#!/usr/bin/env node
/**
 * READ-ONLY diagnostic for the "Progress / Memory / My Tests not updating" bug.
 *
 * Dumps counts, latest timestamps, and small samples for every table that the
 * Progress, Memory, and My Tests pages read from — so we can tell whether the
 * writes are landing in Neon (write-path bug) or the rows exist but the UI
 * hides them (scope-filter / read bug).
 *
 * Usage (PowerShell):
 *   $env:DATABASE_URL="postgres://..."; node scripts/diagnose-learner-updates.mjs <clerk_user_id>
 *
 * Does NOT write anything.
 */
import { neon } from '@neondatabase/serverless';

const learnerId = process.argv[2];
if (!learnerId) {
  console.error('Usage: node scripts/diagnose-learner-updates.mjs <clerk_user_id>');
  process.exit(1);
}
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL is not set. In PowerShell:');
  console.error('  $env:DATABASE_URL="postgres://..."; node scripts/diagnose-learner-updates.mjs <clerk_user_id>');
  process.exit(1);
}

const s = neon(process.env.DATABASE_URL);

const hr = (label) => console.log(`\n===== ${label} =====`);
const safe = async (label, fn) => {
  try {
    return await fn();
  } catch (err) {
    console.log(`  [${label}] query failed:`, err?.message ?? err);
    return null;
  }
};

console.log(`Diagnosing learner_id = ${learnerId}`);

// ---- learner_profiles: subjects + persona (drives the scope filter) ----
hr('learner_profiles (subjects + persona)');
await safe('learner_profiles', async () => {
  const rows = await s`
    SELECT subjects, level, goal,
           (learner_persona IS NOT NULL AND length(learner_persona) > 0) AS has_persona,
           length(coalesce(learner_persona, '')) AS persona_len,
           updated_at
    FROM learner_profiles WHERE learner_id = ${learnerId}`;
  if (!rows.length) return console.log('  NO PROFILE ROW — this alone breaks scope-filtered lists.');
  const r = rows[0];
  console.log('  subjects   :', JSON.stringify(r.subjects));
  console.log('  level/goal :', r.level, '/', r.goal);
  console.log('  persona    :', r.has_persona ? `yes (${r.persona_len} chars)` : 'NONE');
  console.log('  updated_at :', r.updated_at);
});

// ---- concept_mastery: the Progress list source ----
hr('concept_mastery (Progress source)');
await safe('concept_mastery', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM concept_mastery WHERE learner_id = ${learnerId}`;
  const [{ latest }] = await s`SELECT MAX(last_activity) AS latest FROM concept_mastery WHERE learner_id = ${learnerId}`;
  const [{ mastered }] = await s`SELECT COUNT(*) AS mastered FROM concept_mastery WHERE learner_id = ${learnerId} AND score >= 0.7`;
  console.log(`  rows: ${Number(n)}   mastered(>=0.7): ${Number(mastered)}   latest last_activity: ${latest}`);
  const rows = await s`
    SELECT concept_id, score, data_points, last_activity
    FROM concept_mastery WHERE learner_id = ${learnerId}
    ORDER BY last_activity DESC NULLS LAST LIMIT 20`;
  for (const r of rows) {
    console.log(`    ${r.concept_id.padEnd(40)} score=${Number(r.score).toFixed(2)} dp=${r.data_points} @ ${r.last_activity}`);
  }
  if (rows.length) {
    console.log('  ^ Compare these concept_id prefixes against the profile.subjects above.');
    console.log('    If subjects do not cover these concepts, the scope filter hides them from Progress + Memory.');
  }
});

// ---- skill_practice ----
hr('skill_practice (atom mastery)');
await safe('skill_practice', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM skill_practice WHERE learner_id = ${learnerId}`;
  const [{ latest }] = await s`SELECT MAX(last_practiced) AS latest FROM skill_practice WHERE learner_id = ${learnerId}`;
  console.log(`  rows: ${Number(n)}   latest last_practiced: ${latest}`);
});

// ---- chat_turns: Memory timeline + persistence ----
hr('chat_turns (Memory + chat persistence)');
await safe('chat_turns', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM chat_turns WHERE learner_id = ${learnerId}`;
  const [{ latest }] = await s`SELECT MAX(created_at) AS latest FROM chat_turns WHERE learner_id = ${learnerId}`;
  console.log(`  rows: ${Number(n)}   latest created_at: ${latest}`);
  const byAgent = await s`
    SELECT agent, role, COUNT(*) AS n FROM chat_turns WHERE learner_id = ${learnerId}
    GROUP BY agent, role ORDER BY agent, role`;
  for (const r of byAgent) console.log(`    ${String(r.agent).padEnd(14)} ${String(r.role).padEnd(10)} ${Number(r.n)}`);
});

// ---- learner_agent_notes: Memory notes source ----
hr('learner_agent_notes (Memory notes source)');
await safe('learner_agent_notes', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM learner_agent_notes WHERE learner_id = ${learnerId}`;
  const [{ latest }] = await s`SELECT MAX(created_at) AS latest FROM learner_agent_notes WHERE learner_id = ${learnerId}`;
  console.log(`  rows: ${Number(n)}   latest created_at: ${latest}`);
  const byAgent = await s`
    SELECT agent, COUNT(*) AS n FROM learner_agent_notes WHERE learner_id = ${learnerId}
    GROUP BY agent ORDER BY agent`;
  for (const r of byAgent) console.log(`    ${String(r.agent).padEnd(14)} ${Number(r.n)}`);
});

// ---- test_attempts: My Tests source ----
hr('test_attempts (My Tests source)');
await safe('test_attempts', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM test_attempts WHERE learner_id = ${learnerId}`;
  const [{ latest }] = await s`SELECT MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId}`;
  console.log(`  rows: ${Number(n)}   latest created_at: ${latest}`);
  const byKind = await s`
    SELECT kind, COUNT(*) AS n, MAX(created_at) AS latest FROM test_attempts WHERE learner_id = ${learnerId}
    GROUP BY kind ORDER BY kind`;
  for (const r of byKind) console.log(`    ${String(r.kind).padEnd(16)} ${Number(r.n)}  latest ${r.latest}`);
});

// ---- other quiz tables (context for My Tests unification) ----
hr('other quiz tables (context)');
await safe('weekly_quizzes_ai', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM weekly_quizzes_ai WHERE user_id = ${learnerId}`;
  const [{ submitted }] = await s`SELECT COUNT(*) AS submitted FROM weekly_quizzes_ai WHERE user_id = ${learnerId} AND submitted_at IS NOT NULL`;
  console.log(`  weekly_quizzes_ai: ${Number(n)} generated, ${Number(submitted)} submitted`);
});
await safe('mock_exam_results', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM mock_exam_results WHERE user_id = ${learnerId}`;
  console.log(`  mock_exam_results: ${Number(n)}`);
});
await safe('quiz_responses', async () => {
  const [{ n }] = await s`SELECT COUNT(*) AS n FROM quiz_responses WHERE learner_id = ${learnerId}`;
  console.log(`  quiz_responses: ${Number(n)}`);
});

console.log('\nDone (read-only).');
