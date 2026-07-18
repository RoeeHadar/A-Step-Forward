/**
 * Tiered verifier for question-store items. Gates `verification_status`, which
 * in turn gates graded retrieval and baking into lessons.
 *
 * Tiers (strongest first):
 *   1. official_key  — matches an authoritative MoE answer key -> auto_verified
 *   2. cas           — a deterministic solver recomputes the answer -> auto_verified
 *   3. self_consistency (LLM) — informs a human queue but NEVER auto-verifies
 *   4. human         — solo file-based review queue (append-only JSONL)
 *
 * Per the plan: deterministic OR official-key -> auto_verified; everything open /
 * multi-part / closed-form-without-ground-truth requires human sign-off. Any
 * contradiction (key or CAS mismatch) -> rejected.
 *
 * CAS and LLM are injected (casRunner / llmRunner) so this file has no runtime
 * dependency on a solver or model provider and is fully unit-testable.
 */
import fs from 'node:fs';
import path from 'node:path';

/** Best-effort canonical answer for closed-form kinds (used for comparisons). */
export function extractCanonicalAnswer(part) {
  const ap = part.answer_payload ?? {};
  switch (part.kind) {
    case 'numeric':
      return ap.value ?? ap.answer ?? null;
    case 'mcq':
      return ap.correct_index ?? ap.correct ?? null;
    case 'mcq_multi':
      return Array.isArray(ap.correct_indices) ? [...ap.correct_indices].sort() : null;
    case 'true_false':
      return typeof ap.value === 'boolean' ? ap.value : (ap.answer ?? null);
    case 'short_answer':
    case 'fill_blank':
      return Array.isArray(ap.acceptable_answers) ? ap.acceptable_answers[0] ?? null : null;
    default:
      return null; // open / derivation / match / ordering -> not closed-form
  }
}

const CLOSED_FORM = new Set(['numeric', 'mcq', 'mcq_multi', 'true_false', 'short_answer', 'fill_blank']);

function normScalar(v) {
  if (typeof v === 'number') return Math.round(v * 1e6) / 1e6;
  if (typeof v === 'string') return v.trim().toLowerCase();
  if (Array.isArray(v)) return JSON.stringify(v);
  return v;
}

/**
 * Verify a single part. Returns { status, method, confidence, details }.
 * status ∈ auto_verified | unverified | rejected.
 */
export async function verifyPart(part, { casRunner, llmRunner, officialAnswer } = {}) {
  const canonical = extractCanonicalAnswer(part);

  // Tier 1 — official answer key.
  if (officialAnswer !== undefined && officialAnswer !== null) {
    if (canonical === null) {
      return { status: 'unverified', method: 'official_key', confidence: 0, details: 'no canonical answer to compare' };
    }
    const matches = normScalar(canonical) === normScalar(officialAnswer);
    return matches
      ? { status: 'auto_verified', method: 'official_key', confidence: 1, details: 'matches MoE key' }
      : { status: 'rejected', method: 'official_key', confidence: 1, details: `key mismatch: ${canonical} != ${officialAnswer}` };
  }

  // Tier 2 — deterministic CAS.
  if (typeof casRunner === 'function') {
    const cas = await casRunner(part);
    if (cas && cas.supported) {
      return cas.matches
        ? { status: 'auto_verified', method: 'cas', confidence: 1, details: cas.details ?? 'CAS confirmed' }
        : { status: 'rejected', method: 'cas', confidence: 1, details: cas.details ?? `CAS mismatch (computed ${cas.computed})` };
    }
  }

  // Tier 3 — LLM self-consistency: informs the human queue, never auto-verifies.
  let confidence = 0;
  let details = 'no ground truth; needs human sign-off';
  if (typeof llmRunner === 'function') {
    const sc = await llmRunner(part);
    confidence = sc?.agreement ?? 0;
    details = `self-consistency agreement=${confidence.toFixed(2)}; needs human sign-off`;
  }
  return {
    status: 'unverified',
    method: CLOSED_FORM.has(part.kind) ? 'self_consistency' : 'human',
    confidence,
    details,
  };
}

/**
 * Verify a composite item: auto_verified iff EVERY part auto_verified; rejected
 * if any part rejected; otherwise unverified (queued for human review).
 */
export async function verifyItem(item, hooks = {}) {
  const keys = hooks.officialAnswers ?? {}; // { [ord]: answer }
  const partResults = [];
  for (const part of item.parts ?? []) {
    const res = await verifyPart(part, { ...hooks, officialAnswer: keys[part.ord] });
    partResults.push({ ord: part.ord, ...res });
  }

  let status = 'auto_verified';
  if (partResults.some((r) => r.status === 'rejected')) status = 'rejected';
  else if (partResults.some((r) => r.status !== 'auto_verified')) status = 'unverified';

  const minConfidence = partResults.length
    ? Math.min(...partResults.map((r) => r.confidence))
    : 0;

  return {
    status,
    needsHumanReview: status === 'unverified',
    confidence: minConfidence,
    verification: {
      verified_at: new Date().toISOString(),
      parts: partResults,
      overall_method: partResults.map((r) => r.method).join('+'),
    },
  };
}

/* ------------------------------- human queue ------------------------------ */

/** Append an item + verdict to the append-only JSONL review queue. */
export function enqueueForReview(queuePath, item, verdict) {
  fs.mkdirSync(path.dirname(queuePath), { recursive: true });
  const entry = {
    enqueued_at: new Date().toISOString(),
    item_id: item.id ?? null,
    concept_id: item.concept_id,
    kind: item.kind,
    difficulty: item.difficulty,
    source: item.source,
    confidence: verdict.confidence,
    verification: verdict.verification,
    stem_en: item.stem_en,
    parts: item.parts,
  };
  fs.appendFileSync(queuePath, JSON.stringify(entry) + '\n', 'utf8');
  return entry;
}

/** Load all pending entries from the JSONL review queue. */
export function loadReviewQueue(queuePath) {
  if (!fs.existsSync(queuePath)) return [];
  return fs
    .readFileSync(queuePath, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}
