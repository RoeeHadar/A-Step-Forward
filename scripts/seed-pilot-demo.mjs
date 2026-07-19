#!/usr/bin/env node
/**
 * seed-pilot-demo.mjs — seed a learner into a deterministic ADR-0010 demo state so
 * readiness, the mock-gate, phases, pacing and gating are immediately visible in QA.
 *
 * Variants (--variant):
 *   fresh         — nothing mastered, deadline far out → readiness ~0%, "foundational",
 *                   plan starts at foundations (anchored selection, no regression).
 *   building      — ~82% critical mastered, ~8wk deadline, NO passed mock → readiness
 *                   ~70% (mock-gated) + "sit a mock" note. Plan has unmastered weeks →
 *                   best for testing retake rotation + gate→advance. (default)
 *   at-risk       — ~30% critical, tight deadline + low hours → required_velocity >
 *                   capacity → amber "Behind pace" badge (triage).
 *   near-exam     — ~96% critical, ~5d deadline, a PASSED mock → readiness ~95%,
 *                   exam-ready, final-phase note, mock shows in My Tests.
 *   day-before    — like near-exam but deadline tomorrow → "theory + Mentor only" note.
 *   goal-complete — whole frontier mastered + passed mock → remaining_scope 0, "Ahead",
 *                   maintenance/review week.
 *
 * Usage (Windows / corporate proxy):
 *   $env:NODE_TLS_REJECT_UNAUTHORIZED='0'
 *   $env:DATABASE_URL='<prod Neon URL — never commit>'
 *   node scripts/seed-pilot-demo.mjs --variant building [--user-id user_xxx] [--goal bagrut_math_5]
 *
 * Idempotent: replaces the learner's plan + re-seeds mastery each run. Safe to re-run
 * and to flip between variants. Never commits secrets. One account = one state at a time.
 */
import { neon } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const frontiers = require('../apps/web/src/lib/goal-frontiers.generated.json');

const VARIANTS = {
  fresh: { criticalFrac: 0, extra: 0, deadlineDays: 90, passedMock: false, hours: 10 },
  building: { criticalFrac: 0.82, extra: 8, deadlineDays: 56, passedMock: false, hours: 10 },
  'at-risk': { criticalFrac: 0.3, extra: 4, deadlineDays: 25, passedMock: false, hours: 3 },
  'near-exam': { criticalFrac: 0.96, extra: 30, deadlineDays: 5, passedMock: true, hours: 10 },
  'day-before': { criticalFrac: 0.96, extra: 30, deadlineDays: 1, passedMock: true, hours: 10 },
  'goal-complete': { criticalFrac: 1, extra: 'all', deadlineDays: 30, passedMock: true, hours: 10 },
};

const args = process.argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};
const LEARNER = getArg('--user-id', 'user_3FakzyAcsPAfzap2ule6sVHNahk');
const GOAL = getArg('--goal', 'bagrut_math_5');
const VARIANT = getArg('--variant', 'building');
if (!VARIANTS[VARIANT]) {
  console.error(`Unknown --variant "${VARIANT}". Use one of: ${Object.keys(VARIANTS).join(', ')}`);
  process.exit(1);
}
const cfg = VARIANTS[VARIANT];

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL;
if (!url) { console.error('DATABASE_URL not set'); process.exit(1); }
const sql = neon(url);

const goal = frontiers.goals[GOAL];
if (!goal) { console.error(`No frontier for goal ${GOAL}`); process.exit(1); }

const core = goal.core;
const criticalIds = core.filter((c) => c.critical).map((c) => c.id);
const nonCritical = core.filter((c) => !c.critical).map((c) => c.id);
const MASTER_SCORE = 0.88;

const nMasterCritical = Math.floor(criticalIds.length * cfg.criticalFrac);
const masteredCritical = criticalIds.slice(0, nMasterCritical);
const masteredExtra = cfg.extra === 'all' ? nonCritical : nonCritical.slice(0, cfg.extra);
const masteredSet = new Set([...masteredCritical, ...masteredExtra]);

const unmastered = core.map((c) => c.id).filter((id) => !masteredSet.has(id));
let weekGroups = [unmastered.slice(0, 4), unmastered.slice(4, 8), unmastered.slice(8, 12)].filter(
  (g) => g.length > 0,
);
// Goal-complete / no unmastered → a maintenance-review week on top critical concepts.
if (weekGroups.length === 0) weekGroups = [criticalIds.slice(0, 4)];

const now = new Date();
const deadline = new Date(now); deadline.setDate(deadline.getDate() + cfg.deadlineDays);
const startStr = now.toISOString().slice(0, 10);
const endDate = new Date(now); endDate.setDate(endDate.getDate() + 21);
const endStr = endDate.toISOString().slice(0, 10);

console.log(`Seeding ${LEARNER} — variant "${VARIANT}" — goal ${GOAL}`);
console.log(`  critical: ${criticalIds.length} total, mastering ${masteredCritical.length} (+${masteredExtra.length} non-critical)`);
console.log(`  deadline: +${cfg.deadlineDays}d   hours/wk: ${cfg.hours}   passed mock: ${cfg.passedMock}   plan weeks: ${weekGroups.map((g) => g.length).join(' / ')}`);

try {
  // 1) Profile
  const existing = await sql`SELECT personality_profile FROM learner_profiles WHERE learner_id = ${LEARNER} LIMIT 1`;
  const prevPP = existing[0]?.personality_profile && typeof existing[0].personality_profile === 'object'
    ? existing[0].personality_profile : {};
  const pp = { ...prevPP, goal_key: GOAL, attention_span_min: 40 };
  if (existing.length > 0) {
    await sql`
      UPDATE learner_profiles SET goal=${GOAL}, points_group=${goal.points_group}, subjects=${goal.subjects},
        hours_per_week=${cfg.hours}, attention_span=40, next_test_date=${deadline.toISOString().slice(0, 10)},
        personality_profile=${JSON.stringify(pp)}::jsonb, updated_at=NOW()
      WHERE learner_id=${LEARNER}`;
    console.log('  \u2713 profile updated');
  } else {
    await sql`
      INSERT INTO learner_profiles (learner_id, goal, points_group, subjects, hours_per_week, attention_span,
        next_test_date, personality_profile, created_at, updated_at)
      VALUES (${LEARNER}, ${GOAL}, ${goal.points_group}, ${goal.subjects}, ${cfg.hours}, 40,
        ${deadline.toISOString().slice(0, 10)}, ${JSON.stringify(pp)}::jsonb, NOW(), NOW())`;
    console.log('  \u2713 profile inserted');
  }

  // 2) Mastery — reset this learner's mastery first so variants are clean, then seed.
  await sql`DELETE FROM concept_mastery WHERE learner_id = ${LEARNER}`;
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
  for (let i = 0; i < weekGroups.length; i += 1) {
    if (weekGroups[i].length === 0) continue;
    const quizDue = new Date(now); quizDue.setDate(quizDue.getDate() + 7 * (i + 1));
    await sql`
      INSERT INTO plan_weeks (id, plan_id, week_number, concepts, quiz_due_at, status)
      VALUES (${randomUUID()}, ${planId}, ${i + 1}, ${weekGroups[i]}, ${quizDue.toISOString()}, ${i === 0 ? 'active' : 'upcoming'})`;
  }
  console.log(`  \u2713 active plan (${planId})`);

  // 4) Mock signal
  if (cfg.passedMock) {
    // Remove prior demo mocks so we don't stack duplicates.
    await sql`DELETE FROM test_attempts WHERE learner_id = ${LEARNER} AND kind = 'mock_exam' AND quiz_id LIKE 'demo-mock-%'`;
    const mockQs = [
      { id: 'demo-m1', topic: masteredCritical[0] ?? criticalIds[0] ?? 'algebra', subject: 'math', stem: 'פתרו: $2x+3=11$', options: [{ key: 'A', text: '$x=4$' }, { key: 'B', text: '$x=7$' }, { key: 'C', text: '$x=2$' }, { key: 'D', text: '$x=5$' }], correct: 'A' },
      { id: 'demo-m2', topic: masteredCritical[1] ?? criticalIds[0] ?? 'algebra', subject: 'math', stem: 'הנגזרת של $x^2$ היא:', options: [{ key: 'A', text: '$2x$' }, { key: 'B', text: '$x$' }, { key: 'C', text: '$x^2$' }, { key: 'D', text: '$2$' }], correct: 'A' },
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
  const coverage = criticalIds.length > 0 ? masteredCritical.length / criticalIds.length : 1;
  const concave = 0.95 * (1 - (1 - coverage) ** 2);
  const displayed = cfg.passedMock ? Math.min(concave, 0.95) : Math.min(concave, 0.7);
  const phase = cfg.deadlineDays <= 1 ? 'day_before' : cfg.deadlineDays <= 14 ? 'final_phase' : 'building';
  const examReady = coverage >= 0.9 && cfg.passedMock;
  console.log('\nExpected on /app:');
  console.log(`  critical_coverage ≈ ${(coverage * 100).toFixed(0)}%   phase=${phase}   exam_ready=${examReady}   remaining=${unmastered.length}`);
  console.log(`  readiness displayed ≈ ${(displayed * 100).toFixed(0)}%  (never 100% — humble by design)`);
  console.log('\nSeed complete. Hard-refresh /app.');
} catch (err) {
  console.error('Seed failed:', err instanceof Error ? err.message : err);
  process.exit(1);
}
