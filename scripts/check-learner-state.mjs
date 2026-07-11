#!/usr/bin/env node
import { neon } from '@neondatabase/serverless';

const learnerId = process.argv[2];
if (!learnerId) {
  console.error('Usage: node scripts/check-learner-state.mjs <learner_id>');
  process.exit(1);
}

const s = neon(process.env.DATABASE_URL);
const counts = async (label, q) => {
  const r = await q;
  console.log(`${label}:`, Number(r[0]?.n ?? 0));
};

await counts('learner_profiles', s`SELECT COUNT(*) AS n FROM learner_profiles WHERE learner_id = ${learnerId}`);
await counts('learning_plans', s`SELECT COUNT(*) AS n FROM learning_plans WHERE learner_id = ${learnerId}`);
await counts('plan_weeks', s`SELECT COUNT(*) AS n FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${learnerId})`);
await counts('chat_turns', s`SELECT COUNT(*) AS n FROM chat_turns WHERE learner_id = ${learnerId}`);
await counts('concept_mastery', s`SELECT COUNT(*) AS n FROM concept_mastery WHERE learner_id = ${learnerId}`);
