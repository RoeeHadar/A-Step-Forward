#!/usr/bin/env node
/**
 * seed-pilot-demo.mjs — seed a learner into a deterministic ADR-0010 demo state so
 * readiness, the mock-gate, phases and gating are immediately visible for manual QA.
 *
 * Variants:
 *   building   (default) — ~82% of critical concepts mastered, deadline ~8 weeks out,
 *                          NO passed mock → readiness ~70% (mock-gated), "sit a mock" note.
 *   near-exam            — ~95% of critical mastered, deadline ~5 days out, a PASSED mock
 *                          inserted → readiness ~95% (ungated), exam-ready, final-phase note.
 *
 * Usage (Windows / corporate proxy):
 *   $env:NODE_TLS_REJECT_UNAUTHORIZED='0'
 *   $env:DATABASE_URL='<prod Neon URL — never commit>'
 *   node scripts/seed-pilot-demo.mjs --variant near-exam [--user-id user_xxx] [--goal bagrut_math_5]
 *
 * Idempotent: replaces the learner's plan + re-seeds mastery each run. Safe to re-run
 * and to flip between variants. Never commits secrets.
 */
import { neon } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const frontiers = require('../apps/web/src/lib/goal-frontiers.generated.json');

const args = process.argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};
const LEARNER = getArg('--user-id', 'user_3FakzyAcsPAfzap2ule6sVHNahk');
const GOAL = getArg('--goal', 'bagrut_math_5');
const VARIANT = getArg('--variant', 'building');
if (!['building', 'near-exam'].includes(VARIANT)) {
  console.error(`Unknown --variant ${VARIANT} (use "building" or "near-exam")`);
  process.exit(1);
}

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) { console.error('DATABASE_URL not set'); process.exit(1); }
const sql = neon(url);

const goal = frontiers.goals[GOAL];
if (!goal) { console.error(`No frontier for goal ${GOAL}`); process.exit(1); }

const core = goal.core;
const criticalIds = core.filter((c) => c.critical).map((c) => c.id);
const nonCritical = core.filter((c) => !c.critical).map((c) => c.id);
const MASTER_SCORE = 0.88;

const cfg =
  VARIANT === 'near-exam'
    ? { criticalFrac: 0.96, extra: 30, deadlineDays: 5, passedMock: true }
    : { criticalFrac: 0.82, extra: 8, deadlineDays: 56, passedMock: false };

const nMasterCritical = Math.floor(criticalIds.length * cfg.criticalFrac);
const masteredCritical = criticalIds.slice(0, nMasterCritical);
const masteredExtra = nonCritical.slice(0, cfg.extra);
const masteredSet = new Set([...masteredCritical, ...masteredExtra]);

const unmastered = core.map((c) => c.id).filter((id) => !masteredSet.has(id));
const weekGroups = [unmastered.slice(0, 4), unmastered.slice(4, 8), unmastered.slice(8, 12)].filter(
  (g) => g.length > 0,
);

const now = new Date();
const deadline = new Date(now); deadline.setDate(deadline.getDate() + cfg.deadlineDays);
const startStr = now.toISOString().slice(0, 10);
const endDate = new Date(now); endDate.setDate(endDate.getDate() + 21);
const endStr = endDate.toISOString().slice(0, 10);

console.log(`Seeding ${LEARNER} — variant "${VARIANT}" — goal ${GOAL}`);
console.log(`  critical: ${criticalIds.length} total, mastering ${masteredCritical.length} (+${masteredExtra.length} non-critical)`);
console.log(`  deadline: +${cfg.deadlineDays}d   passed mock: ${cfg.passedMock}   plan weeks: ${weekGroups.map((g) => g.length).join(' / ') || '(goal near-complete)'}`);

try {
  // 1) Profile
  const existing = await sql`SELECT personality_profile FROM learner_profiles WHERE learner_id = ${LEARNER} LIMIT 1`;
  const prevPP = existing[0]?.personality_profile && typeof existing[0].personality_profile === 'object'
    ? existing[0].personality_profile : {};
  const pp = { ...prevPP, goal_key: GOAL, attention_span_min: 40 };
  if (existing.length > 0) {
    await sql`
      UPDATE learner_profiles SET goal=${GOAL}, points_group=${goal.points_group}, subjects=${goal.subjects},
        hours_per_week=10, attention_span=40, next_test_date=${deadline.toISOString().slice(0, 10)},
        personality_profile=${JSON.stringify(pp)}::jsonb, updated_at=NOW()
      WHERE learner_id=${LEARNER}`;
    console.log('  \u2713 profile updated');
  } else {
    await sql`
      INSERT INTO learner_profiles (learner_id, goal, points_group, subjects, hours_per_week, attention_span,
        next_test_date, personality_profile, created_at, updated_at)
      VALUES (${LEARNER}, ${GOAL}, ${goal.points_group}, ${goal.subjects}, 10, 40,
        ${deadline.toISOString().slice(0, 10)}, ${JSON.stringify(pp)}::jsonb, NOW(), NOW())`;
    console.log('  \u2713 profile inserted');
  }

  // 2) Mastery (fresh → no decay)
  for (const id of masteredSet) {
    await sql`
      INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
      VALUES (${LEARNER}, ${id}, ${MASTER_SCORE}, 3, NOW(), NOW())
      ON CONFLICT (learner_id, concept_id) DO UPDATE SET score=${MASTER_SCORE},
        data_points=GREATEST(concept_mastery.data_points, 3), last_activity=NOW()`;
  }
  console.log(`  \u2713 mastery seeded (${masteredSet.size} concepts)`);

  // 3) Replace plan
  await sql`DELETE FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${LEARNER})`;
  await sql`DELETE FROM learning_plans WHERE learner_id = ${LEARNER}`;
  const planId = randomUUID();
  await sql`
    INSERT INTO learning_plans (id, learner_id, goal, start_date, end_date, status,
      plan_schema_version, plan_adjustment_kind, plan_last_adjusted_at, created_at, updated_at)
    VALUES (${planId}, ${LEARNER}, ${GOAL}, ${startStr}, ${endStr}, 'active', 2, NULL, NULL, NOW(), NOW())`;
  const groups = weekGroups.length > 0 ? weekGroups : [unmastered.slice(0, 4)];
  for (let i = 0; i < groups.length; i += 1) {
    if (groups[i].length === 0) continue;
    const quizDue = new Date(now); quizDue.setDate(quizDue.getDate() + 7 * (i + 1));
    await sql`
      INSERT INTO plan_weeks (id, plan_id, week_number, concepts, quiz_due_at, status)
      VALUES (${randomUUID()}, ${planId}, ${i + 1}, ${groups[i]}, ${quizDue.toISOString()}, ${i === 0 ? 'active' : 'upcoming'})`;
  }
  console.log(`  \u2713 active plan (${planId})`);

  // 4) Mock signal
  if (cfg.passedMock) {
    const mockQs = [
      { id: 'demo-m1', topic: masteredCritical[0] ?? 'algebra', subject: 'math', stem: 'פתרו: $2x+3=11$', options: [{ key: 'A', text: '$x=4$' }, { key: 'B', text: '$x=7$' }, { key: 'C', text: '$x=2$' }, { key: 'D', text: '$x=5$' }], correct: 'A' },
      { id: 'demo-m2', topic: masteredCritical[1] ?? 'algebra', subject: 'math', stem: 'נגזרת של $x^2$ היא:', options: [{ key: 'A', text: '$2x$' }, { key: 'B', text: '$x$' }, { key: 'C', text: '$x^2$' }, { key: 'D', text: '$2$' }], correct: 'A' },
    ];
    const mockAns = [{ item_id: 'demo-m1', chosen: 'A' }, { item_id: 'demo-m2', chosen: 'A' }];
    await sql`
      INSERT INTO test_attempts (id, learner_id, kind, plan_id, week_num, quiz_id, locale, score, passed,
        pass_threshold, per_topic, weak_concepts, questions, answers, feedback, created_at)
      VALUES (gen_random_uuid(), ${LEARNER}, 'mock_exam', NULL, NULL, ${'demo-mock-' + Date.now()}, 'he',
        0.85, TRUE, 0.6, ${JSON.stringify({})}::jsonb, ${[]},
        ${JSON.stringify(mockQs)}::jsonb, ${JSON.stringify(mockAns)}::jsonb, NULL, NOW())`;
    console.log('  \u2713 passed mock inserted (readiness ungated + shows in My Tests)');
  } else {
    await sql`DELETE FROM test_attempts WHERE learner_id = ${LEARNER} AND kind = 'mock_exam' AND passed = TRUE`;
    await sql`DELETE FROM mock_exam_results WHERE user_id = ${LEARNER} AND max_mcq > 0 AND (score_mcq::float / max_mcq::float) >= 0.6`;
    console.log('  \u2713 passing mocks cleared (mock-gate visible)');
  }

  // 5) Report
  const coverage = masteredCritical.length / criticalIds.length;
  const concave = 0.95 * (1 - (1 - coverage) ** 2);
  const displayed = cfg.passedMock ? Math.min(concave, 0.95) : Math.min(concave, 0.70);
  const phase = cfg.deadlineDays <= 1 ? 'day_before' : cfg.deadlineDays <= 14 ? 'final_phase' : 'building';
  const examReady = coverage >= 0.9 && cfg.passedMock;
  console.log('\nExpected readiness:');
  console.log(`  critical_coverage ≈ ${(coverage * 100).toFixed(0)}%   phase=${phase}   exam_ready=${examReady}`);
  console.log(`  displayed ≈ ${(displayed * 100).toFixed(0)}%  (never 100% — humble by design)`);
  console.log('\nSeed complete. Hard-refresh /app.');
} catch (err) {
  console.error('Seed failed:', err instanceof Error ? err.message : err);
  process.exit(1);
}
