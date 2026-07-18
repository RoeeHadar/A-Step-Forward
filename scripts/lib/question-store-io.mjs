/**
 * Node IO for the internal question-item store (`question_items`).
 *
 * The offline pipeline (ingestion -> mapping/generation -> verification ->
 * baking) uses this; the web app has its own read-only lib
 * (apps/web/src/lib/question-store.ts). All functions take the Neon `sql`
 * client by dependency injection so they are unit-testable with a fake.
 *
 * Idempotency: each item gets a deterministic id derived from its content, so
 * re-ingesting the same source item UPDATEs rather than duplicates.
 */
import { createHash } from 'node:crypto';

const QUESTION_KINDS = new Set([
  'mcq',
  'mcq_multi',
  'true_false',
  'open',
  'short_answer',
  'fill_blank',
  'numeric',
  'match',
  'ordering',
  'derivation',
]);
const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);
const LICENSES = new Set([
  'public-official',
  'generated-original',
  'CC-BY-SA-4.0',
  'proprietary',
  'unknown',
]);
const VERIFIED_STATUSES = ['auto_verified', 'human_verified'];

/** Deterministic v5-shaped UUID from a content string (idempotent upserts). */
export function deterministicItemId(input) {
  const h = createHash('sha256').update(input).digest('hex');
  const variant = ((parseInt(h.slice(16, 17), 16) & 0x3) | 0x8).toString(16);
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-5${h.slice(13, 16)}-${variant}${h.slice(17, 20)}-${h.slice(20, 32)}`;
}

function stableItemKey(item) {
  const partStems = (item.parts ?? []).map((p) => `${p.stem_en ?? ''}::${p.stem_he ?? ''}`).join('|');
  return [item.concept_id, item.source, item.source_ref ?? '', item.stem_en ?? '', partStems].join('␟');
}

/**
 * Enforce the source-tier policy at write time: proprietary / unknown-licensed
 * material may only inform generation, never be stored verbatim. Throws.
 */
export function assertStorable(item) {
  if (!QUESTION_KINDS.has(item.kind)) throw new Error(`invalid kind: ${item.kind}`);
  if (!DIFFICULTIES.has(item.difficulty)) throw new Error(`invalid difficulty: ${item.difficulty}`);
  if (!LICENSES.has(item.license)) throw new Error(`invalid license: ${item.license}`);
  if (!Array.isArray(item.parts) || item.parts.length === 0) {
    throw new Error('item.parts must contain >=1 part (single-part is the degenerate case)');
  }
  if (item.license === 'proprietary' || item.license === 'unknown') {
    throw new Error(
      `license '${item.license}' is style-reference-only; generate an original item instead of storing verbatim`,
    );
  }
  if (item.display_publicly && item.license !== 'public-official') {
    throw new Error('display_publicly is only allowed for public-official items');
  }
}

function normalizeForStore(item) {
  assertStorable(item);
  const id = item.id ?? deterministicItemId(stableItemKey(item));
  const skillAtoms = Array.isArray(item.skill_atoms)
    ? item.skill_atoms
    : [...new Set((item.parts ?? []).flatMap((p) => p.skill_atoms ?? []))];
  return {
    id,
    concept_id: item.concept_id,
    extra_concept_ids: item.extra_concept_ids ?? [],
    subject: item.subject,
    level: item.level,
    math_track: item.math_track ?? [],
    points_level: item.points_level ?? null,
    points_level_min: item.points_level_min ?? null,
    kind: item.kind,
    difficulty: item.difficulty,
    stem_en: item.stem_en ?? '',
    stem_he: item.stem_he ?? '',
    parts: item.parts,
    skill_atoms: skillAtoms,
    answer_payload: item.answer_payload ?? null,
    est_seconds: item.est_seconds ?? null,
    source: item.source,
    source_ref: item.source_ref ?? null,
    license: item.license,
    provenance: item.provenance ?? null,
    display_publicly: Boolean(item.display_publicly),
    verification_status: item.verification_status ?? 'unverified',
    verification: item.verification ?? null,
    parameter_spec: item.parameter_spec ?? null,
  };
}

/**
 * Upsert composite items. Returns the list of ids written. `sql` is the Neon
 * tagged-template client.
 */
export async function upsertQuestionItems(sql, items) {
  const ids = [];
  for (const raw of items) {
    const it = normalizeForStore(raw);
    await sql`
      INSERT INTO question_items (
        id, concept_id, extra_concept_ids, subject, level, math_track,
        points_level, kind, difficulty, stem_en, stem_he, parts, skill_atoms,
        answer_payload, est_seconds, source, source_ref, license, provenance,
        display_publicly, verification_status, verification, parameter_spec
      ) VALUES (
        ${it.id}, ${it.concept_id}, ${it.extra_concept_ids}, ${it.subject},
        ${it.level}, ${it.math_track}, ${it.points_level}, ${it.kind},
        ${it.difficulty}, ${it.stem_en}, ${it.stem_he},
        ${JSON.stringify(it.parts)}::jsonb, ${JSON.stringify(it.skill_atoms)}::jsonb,
        ${it.answer_payload === null ? null : JSON.stringify(it.answer_payload)}::jsonb,
        ${it.est_seconds}, ${it.source}, ${it.source_ref}, ${it.license},
        ${it.provenance === null ? null : JSON.stringify(it.provenance)}::jsonb,
        ${it.display_publicly}, ${it.verification_status},
        ${it.verification === null ? null : JSON.stringify(it.verification)}::jsonb,
        ${it.parameter_spec === null ? null : JSON.stringify(it.parameter_spec)}::jsonb
      )
      ON CONFLICT (id) DO UPDATE SET
        extra_concept_ids = EXCLUDED.extra_concept_ids,
        math_track = EXCLUDED.math_track,
        points_level = EXCLUDED.points_level,
        difficulty = EXCLUDED.difficulty,
        parts = EXCLUDED.parts,
        skill_atoms = EXCLUDED.skill_atoms,
        answer_payload = EXCLUDED.answer_payload,
        est_seconds = EXCLUDED.est_seconds,
        provenance = EXCLUDED.provenance,
        parameter_spec = EXCLUDED.parameter_spec,
        updated_at = NOW()
    `;
    ids.push(it.id);
  }
  return ids;
}

/** Verified items for a concept, for offline baking into lessons. */
export async function queryItemsForBaking(sql, { conceptId, gradedOnly = true, limit = 100 }) {
  if (gradedOnly) {
    return sql`
      SELECT * FROM question_items
      WHERE concept_id = ${conceptId}
        AND verification_status = ANY(${VERIFIED_STATUSES}::text[])
      ORDER BY difficulty, kind
      LIMIT ${limit}
    `;
  }
  return sql`
    SELECT * FROM question_items
    WHERE concept_id = ${conceptId}
    ORDER BY difficulty, kind
    LIMIT ${limit}
  `;
}

/** Update an item's verification verdict (set by the verifier or human queue). */
export async function setVerificationStatus(sql, id, status, verification = null) {
  await sql`
    UPDATE question_items
    SET verification_status = ${status},
        verification = ${verification === null ? null : JSON.stringify(verification)}::jsonb,
        updated_at = NOW()
    WHERE id = ${id}
  `;
}

/** Counts per verification_status for a concept (pipeline dashboard). */
export async function countByStatus(sql, conceptId) {
  const rows = await sql`
    SELECT verification_status, COUNT(*)::int AS n
    FROM question_items
    WHERE concept_id = ${conceptId}
    GROUP BY verification_status
  `;
  return Object.fromEntries(rows.map((r) => [r.verification_status, r.n]));
}

export const _internal = { stableItemKey, normalizeForStore, VERIFIED_STATUSES };
