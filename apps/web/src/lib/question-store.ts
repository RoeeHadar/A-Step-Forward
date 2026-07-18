/**
 * Read access to the internal question-item store (`question_items`).
 *
 * Structured-filter-first retrieval (concept / skill-atom / difficulty / level)
 * over Neon-direct HTTP, matching the neon-direct-route pattern. Graded/educator
 * retrieval is restricted to verified items; a pgvector semantic fallback for
 * natural-language queries is added once the offline embedder is wired.
 *
 * Consumers:
 *  - Offline baking of lessons' `questions[]` (via the Node pipeline, separate).
 *  - Educator-only on-the-fly quiz/test builder (`/api/educator/questions`).
 * Learners never call this directly.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

/** Parameterized ($1..$n) query form; present at runtime but absent from the 0.10.1 types. */
type ParamQuery = (queryText: string, params?: unknown[]) => Promise<Record<string, unknown>[]>;

function rawQuery(): ParamQuery {
  if (!sql) {
    throw new Error('DATABASE_URL is not set; question-store retrieval unavailable.');
  }
  const client = sql as unknown as { query: ParamQuery };
  return client.query.bind(client);
}

export type QuestionDifficulty = 'easy' | 'medium' | 'hard';

export interface QuestionPart {
  ord: number;
  kind: string;
  difficulty?: QuestionDifficulty;
  stem_en: string;
  stem_he: string;
  answer_payload?: Record<string, unknown> | null;
  rubric_en?: string | null;
  rubric_he?: string | null;
  explanation_en?: string;
  explanation_he?: string;
  points?: number | null;
  skill_atoms?: string[];
}

export interface RetrievedQuestion {
  id: string;
  concept_id: string;
  extra_concept_ids: string[];
  subject: string;
  level: string;
  math_track: string[];
  points_level: string | null;
  kind: string;
  difficulty: QuestionDifficulty;
  stem_en: string;
  stem_he: string;
  parts: QuestionPart[];
  skill_atoms: string[];
  answer_payload: Record<string, unknown> | null;
  est_seconds: number | null;
  source: string;
  source_ref: string | null;
  license: string;
  display_publicly: boolean;
  verification_status: string;
  /** True when the item carries a deterministic parameter spec (safe to re-parameterize). */
  adaptable: boolean;
}

export interface RetrieveQuestionsParams {
  conceptId: string;
  difficulty?: QuestionDifficulty;
  /** Return items exercising ANY of these skill atoms. */
  skillAtoms?: string[];
  level?: string;
  pointsLevel?: string;
  limit?: number;
  /** Restrict to verified items (default true) — required for graded use. */
  gradedOnly?: boolean;
  /** Restrict to items cleared for public display (learner-facing). */
  publicOnly?: boolean;
}

interface QuestionItemRow {
  id: string;
  concept_id: string;
  extra_concept_ids: string[] | null;
  subject: string;
  level: string;
  math_track: string[] | null;
  points_level: string | null;
  kind: string;
  difficulty: string;
  stem_en: string;
  stem_he: string;
  parts: unknown;
  skill_atoms: unknown;
  answer_payload: unknown;
  est_seconds: number | null;
  source: string;
  source_ref: string | null;
  license: string;
  display_publicly: boolean;
  verification_status: string;
  parameter_spec: unknown;
}

function asDifficulty(value: string): QuestionDifficulty {
  return value === 'easy' || value === 'hard' ? value : 'medium';
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === 'string') : [];
}

function asParts(value: unknown): QuestionPart[] {
  if (!Array.isArray(value)) return [];
  return value.map((raw, i) => {
    const p = (raw ?? {}) as Record<string, unknown>;
    return {
      ord: typeof p.ord === 'number' ? p.ord : i + 1,
      kind: typeof p.kind === 'string' ? p.kind : 'open',
      stem_en: typeof p.stem_en === 'string' ? p.stem_en : '',
      stem_he: typeof p.stem_he === 'string' ? p.stem_he : '',
      answer_payload: (p.answer_payload as Record<string, unknown> | null) ?? null,
      rubric_en: (p.rubric_en as string | null) ?? null,
      rubric_he: (p.rubric_he as string | null) ?? null,
      explanation_en: typeof p.explanation_en === 'string' ? p.explanation_en : '',
      explanation_he: typeof p.explanation_he === 'string' ? p.explanation_he : '',
      points: (p.points as number | null) ?? null,
      skill_atoms: asStringArray(p.skill_atoms),
    };
  });
}

function mapRow(row: QuestionItemRow): RetrievedQuestion {
  return {
    id: row.id,
    concept_id: row.concept_id,
    extra_concept_ids: row.extra_concept_ids ?? [],
    subject: row.subject,
    level: row.level,
    math_track: row.math_track ?? [],
    points_level: row.points_level,
    kind: row.kind,
    difficulty: asDifficulty(row.difficulty),
    stem_en: row.stem_en,
    stem_he: row.stem_he,
    parts: asParts(row.parts),
    skill_atoms: asStringArray(row.skill_atoms),
    answer_payload: (row.answer_payload as Record<string, unknown> | null) ?? null,
    est_seconds: row.est_seconds,
    source: row.source,
    source_ref: row.source_ref,
    license: row.license,
    display_publicly: row.display_publicly,
    verification_status: row.verification_status,
    adaptable: row.parameter_spec != null,
  };
}

const VERIFIED_STATUSES = ['auto_verified', 'human_verified'];

/**
 * Structured-filter-first retrieval. Verified-only by default. Ordered randomly
 * so repeated educator quiz builds vary; cap the limit to keep it cheap.
 */
export async function retrieveQuestions(
  params: RetrieveQuestionsParams,
): Promise<RetrievedQuestion[]> {
  const {
    conceptId,
    difficulty,
    skillAtoms,
    level,
    pointsLevel,
    limit = 10,
    gradedOnly = true,
    publicOnly = false,
  } = params;

  const conditions: string[] = ['concept_id = $1'];
  const values: unknown[] = [conceptId];

  if (difficulty) {
    values.push(difficulty);
    conditions.push(`difficulty = $${values.length}`);
  }
  if (level) {
    values.push(level);
    conditions.push(`level = $${values.length}`);
  }
  if (pointsLevel) {
    values.push(pointsLevel);
    conditions.push(`points_level = $${values.length}`);
  }
  if (skillAtoms && skillAtoms.length > 0) {
    values.push(JSON.stringify(skillAtoms));
    // jsonb ?| checks whether any array element string is present.
    conditions.push(`skill_atoms ?| (SELECT array_agg(value) FROM jsonb_array_elements_text($${values.length}::jsonb))`);
  }
  if (gradedOnly) {
    values.push(VERIFIED_STATUSES);
    conditions.push(`verification_status = ANY($${values.length}::text[])`);
  }
  if (publicOnly) {
    conditions.push('display_publicly = TRUE');
  }

  const cappedLimit = Math.min(Math.max(1, limit), 50);
  values.push(cappedLimit);
  const limitPlaceholder = `$${values.length}`;

  const text = `
    SELECT id, concept_id, extra_concept_ids, subject, level, math_track,
           points_level, kind, difficulty, stem_en, stem_he, parts, skill_atoms,
           answer_payload, est_seconds, source, source_ref, license,
           display_publicly, verification_status, parameter_spec
    FROM question_items
    WHERE ${conditions.join(' AND ')}
    ORDER BY random()
    LIMIT ${limitPlaceholder}
  `;

  const rows = (await rawQuery()(text, values)) as unknown as QuestionItemRow[];
  return rows.map(mapRow);
}

/** Fetch a single item by id (verified filter optional). */
export async function getQuestionItem(
  id: string,
  gradedOnly = true,
): Promise<RetrievedQuestion | null> {
  const text = `
    SELECT id, concept_id, extra_concept_ids, subject, level, math_track,
           points_level, kind, difficulty, stem_en, stem_he, parts, skill_atoms,
           answer_payload, est_seconds, source, source_ref, license,
           display_publicly, verification_status, parameter_spec
    FROM question_items
    WHERE id = $1
    ${gradedOnly ? `AND verification_status = ANY($2::text[])` : ''}
    LIMIT 1
  `;
  const values: unknown[] = gradedOnly ? [id, VERIFIED_STATUSES] : [id];
  const rows = (await rawQuery()(text, values)) as unknown as QuestionItemRow[];
  return rows.length > 0 ? mapRow(rows[0]!) : null;
}
