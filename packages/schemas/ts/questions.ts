import { z } from 'zod';
import { idStr } from './common';

/**
 * Canonical schema for the internal question-item store (`question_items`).
 *
 * Items are composite: a shared bilingual stem plus an ordered `parts` array
 * (>= 1 part). A single-part question is the degenerate one-part case. The store
 * feeds two consumers: (a) offline baking into lessons' `questions[]`, and
 * (b) the educator-only on-the-fly quiz/test builder. See the plan + skills
 * `build-custom-quiz`, `cross-subject-kg`, `neon-direct-route`.
 */

export const questionKindSchema = z.enum([
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
export type QuestionKind = z.infer<typeof questionKindSchema>;

export const questionDifficultySchema = z.enum(['easy', 'medium', 'hard']);
export type QuestionDifficulty = z.infer<typeof questionDifficultySchema>;

/**
 * Legal tier — enforces the source-policy decided in the plan. Only
 * `public-official` and `generated-original` are safe to display verbatim to
 * learners without extra review; `CC-BY-SA-4.0` carries copyleft; `proprietary`
 * / `unknown` are style-reference-only and must never be stored verbatim.
 */
export const questionLicenseSchema = z.enum([
  'public-official', // MoE Meyda official exams
  'generated-original', // clean-room LLM generation
  'CC-BY-SA-4.0', // Wikibooks (segregated only; pilot uses clean-room instead)
  'proprietary', // commercial books — style reference only
  'unknown', // no license found — treat as all-rights-reserved
]);
export type QuestionLicense = z.infer<typeof questionLicenseSchema>;

export const questionSourceSchema = z.enum([
  'moe_meyda',
  'generated',
  'wikibooks',
  'motib',
  'openclass',
  'textbook',
  'other',
]);
export type QuestionSource = z.infer<typeof questionSourceSchema>;

export const verificationStatusSchema = z.enum([
  'unverified',
  'auto_verified', // deterministic solver / official answer key match
  'human_verified',
  'rejected',
]);
export type VerificationStatus = z.infer<typeof verificationStatusSchema>;

/** Answer payload shape varies by kind; validated per-kind at ingest time. */
export const answerPayloadSchema = z.record(z.unknown());

export const questionPartSchema = z.object({
  ord: z.number().int().min(1),
  kind: questionKindSchema,
  difficulty: questionDifficultySchema.optional(),
  stem_en: z.string().min(1),
  stem_he: z.string().min(1),
  answer_payload: answerPayloadSchema.nullable().optional(),
  rubric_en: z.string().nullable().optional(),
  rubric_he: z.string().nullable().optional(),
  explanation_en: z.string().default(''),
  explanation_he: z.string().default(''),
  points: z.number().min(0).nullable().optional(),
  skill_atoms: z.array(idStr).default([]),
});
export type QuestionPart = z.infer<typeof questionPartSchema>;

/** Deterministic parameterized re-generation (safe answer recomputation). */
export const parameterSpecSchema = z.object({
  params: z.array(
    z.object({
      name: z.string().min(1),
      type: z.enum(['int', 'float', 'choice']),
      min: z.number().optional(),
      max: z.number().optional(),
      step: z.number().optional(),
      choices: z.array(z.union([z.string(), z.number()])).optional(),
    }),
  ),
  // How to recompute the answer from params (e.g. a sympy expression string).
  answer_formula: z.string().min(1),
  constraints: z.array(z.string()).default([]),
});
export type ParameterSpec = z.infer<typeof parameterSpecSchema>;

export const questionItemSchema = z
  .object({
    id: z.string().uuid().optional(),
    concept_id: idStr,
    extra_concept_ids: z.array(idStr).default([]),
    subject: z.string().min(1),
    level: z.string().min(1),
    math_track: z.array(z.string()).default([]),
    points_level: z.string().nullable().optional(),
    kind: questionKindSchema,
    difficulty: questionDifficultySchema,
    stem_en: z.string().default(''),
    stem_he: z.string().default(''),
    parts: z.array(questionPartSchema).min(1),
    skill_atoms: z.array(idStr).default([]),
    answer_payload: answerPayloadSchema.nullable().optional(),
    est_seconds: z.number().int().min(1).nullable().optional(),
    source: questionSourceSchema,
    source_ref: z.string().nullable().optional(),
    license: questionLicenseSchema,
    provenance: z.record(z.unknown()).nullable().optional(),
    display_publicly: z.boolean().default(false),
    verification_status: verificationStatusSchema.default('unverified'),
    verification: z.record(z.unknown()).nullable().optional(),
    parameter_spec: parameterSpecSchema.nullable().optional(),
  })
  .superRefine((item, ctx) => {
    // Policy: proprietary / unknown-licensed items must never be stored verbatim.
    if (item.license === 'proprietary' || item.license === 'unknown') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `license '${item.license}' is style-reference-only; do not store verbatim items`,
        path: ['license'],
      });
    }
    // Only public-official items may be flagged for public display verbatim.
    if (item.display_publicly && item.license === 'CC-BY-SA-4.0') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'CC-BY-SA items require a segregated, attributed partition — not display_publicly here',
        path: ['display_publicly'],
      });
    }
  });
export type QuestionItem = z.infer<typeof questionItemSchema>;

/** Only verified items are eligible for graded retrieval / baking into lessons. */
export function isGradedEligible(item: Pick<QuestionItem, 'verification_status'>): boolean {
  return (
    item.verification_status === 'auto_verified' ||
    item.verification_status === 'human_verified'
  );
}
