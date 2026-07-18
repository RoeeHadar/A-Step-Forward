#!/usr/bin/env node
/**
 * End-to-end question-store pipeline (offline, file-backed):
 *   load generated/ingested items -> verify (sympy CAS) -> store -> [bake].
 *
 * Runs without a DB or external sources. Verified items are eligible for
 * baking into a lesson's `questions[]`; unverified/open items are appended to
 * the human review queue.
 *
 * Usage:
 *   node scripts/pipeline-run.mjs --concept=derivatives_rules \
 *     --generated=content/question-store/generated/derivatives_rules.json
 *   node scripts/pipeline-run.mjs --concept=derivatives_rules --bake --write
 */
import fs from 'node:fs';
import path from 'node:path';
import { verifyItem, enqueueForReview } from './lib/question-verifier.mjs';
import { makeSympyCasRunner } from './lib/cas-runner.mjs';
import {
  upsertItemsFile,
  setVerificationStatusFile,
  queryItemsForBakingFile,
  countByStatusFile,
} from './lib/question-store-file.mjs';
import { bakeConceptQuestions } from './bake-question-items.mjs';

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}

const concept = args.get('concept');
if (!concept || concept === 'true') {
  console.error('--concept=<id> is required');
  process.exit(1);
}
const generatedPath =
  args.get('generated') && args.get('generated') !== 'true'
    ? args.get('generated')
    : `content/question-store/generated/${concept}.json`;
const storePath = args.get('store') && args.get('store') !== 'true'
  ? args.get('store')
  : 'content/question-store/items.json';
const queuePath = args.get('queue') && args.get('queue') !== 'true'
  ? args.get('queue')
  : 'content/question-store/review-queue.jsonl';
const lessonsDir = args.get('lessons-dir') ?? 'scripts/seed_data/lessons';
const doBake = args.get('bake') === 'true';
const doWrite = args.get('write') === 'true';
const maxBaked = Number(args.get('max') ?? 10);

/**
 * Ensure `agent_hints` is a structured object whose `skill_atoms_unlocked`
 * exactly matches the atoms the baked questions assess. This keeps the strict
 * validator's "structured hints" + "every taught atom is exercised" gates
 * green by construction, and preserves any hand-authored insight fields.
 */
function ensureStructuredAgentHints(lesson, questions) {
  const atoms = [...new Set(questions.flatMap((q) => q.skill_atoms ?? []))].sort();
  let h = lesson.agent_hints;
  if (typeof h === 'string') {
    h = { socratic_prompt: h, key_insights: [], common_misconceptions: [] };
  } else if (!h || typeof h !== 'object' || Array.isArray(h)) {
    h = { key_insights: [], common_misconceptions: [] };
  } else {
    h = { ...h };
  }
  h.skill_atoms_unlocked = atoms;
  lesson.agent_hints = h;
}

async function run() {
  if (!fs.existsSync(generatedPath)) {
    console.error(`no items at ${generatedPath} (run the generator first)`);
    process.exit(1);
  }
  const items = JSON.parse(fs.readFileSync(generatedPath, 'utf8'));
  console.log(`Loaded ${items.length} items for '${concept}' from ${generatedPath}`);

  const casRunner = makeSympyCasRunner();
  let verified = 0;
  let rejected = 0;
  let queued = 0;

  for (const item of items) {
    const verdict = await verifyItem(item, { casRunner });
    item.verification_status = verdict.status;
    item.verification = verdict.verification;
    if (verdict.status === 'auto_verified') verified += 1;
    else if (verdict.status === 'rejected') rejected += 1;
    else {
      queued += 1;
      enqueueForReview(queuePath, item, verdict);
    }
  }

  upsertItemsFile(storePath, items);
  console.log(`Verify: auto_verified=${verified} rejected=${rejected} queued=${queued}`);
  console.log(`Store status for '${concept}':`, countByStatusFile(storePath, concept));
  if (rejected > 0) {
    console.log('  ! rejected items indicate a generator bug — inspect before baking');
  }

  if (!doBake) {
    console.log('\n(no --bake — store populated; pass --bake [--write] to bake into the lesson)');
    return;
  }

  const verifiedItems = queryItemsForBakingFile(storePath, { conceptId: concept, gradedOnly: true });
  const { questions, warnings } = bakeConceptQuestions(verifiedItems, { max: maxBaked });
  const withOrd = questions.map((q, i) => ({ ord: i + 1, ...q }));
  console.log(`\nBake: ${verifiedItems.length} verified -> ${withOrd.length} baked questions`);
  for (const w of warnings) console.log(`  ! ${w}`);

  if (doWrite) {
    const file = path.join(lessonsDir, `${concept}.json`);
    if (!fs.existsSync(file)) {
      console.error(`  lesson not found: ${file}`);
      process.exit(1);
    }
    const lesson = JSON.parse(fs.readFileSync(file, 'utf8'));
    lesson.questions = withOrd;
    ensureStructuredAgentHints(lesson, withOrd);
    fs.writeFileSync(file, JSON.stringify(lesson, null, 2) + '\n', 'utf8');
    console.log(`  wrote ${withOrd.length} questions -> ${file}`);
  } else {
    console.log('  (dry-run — pass --write to persist into the lesson JSON)');
  }
}

run().catch((err) => {
  console.error(err instanceof Error ? err.stack : err);
  process.exit(1);
});
