import { z } from 'zod';

export const contentSectionRefSchema = z.object({
  id: z.string(),
  title: z.string(),
  chunk_index: z.number().int().nullable().optional(),
  page_start: z.number().int().nullable().optional(),
});

export const bagrutRefSchema = z.object({
  display_name: z.string(),
  file_url: z.string(),
  year: z.number().int().nullable().optional(),
  exam_type: z.string().nullable().optional(),
});

export const planConceptSchema = z.object({
  concept_id: z.string(),
  name: z.string(),
  // Optional Hebrew companion to `name`. UI components prefer this when the
  // learner's language preference is `he`. Optional + nullable so legacy
  // payloads (or the Python backend) that don't include it still validate.
  name_he: z.string().nullable().optional(),
  subject: z.string(),
  mastery: z.number().nullable().optional(),
  suggested_sections: z.array(contentSectionRefSchema).default([]),
  recommended_bagrut: z.array(bagrutRefSchema).default([]),
  // Plan-train alignment (work-item tokens): lesson (default) | train | rest.
  kind: z.enum(['lesson', 'train', 'rest']).optional(),
  target_count: z.number().nullable().optional(),
});

export const planWeekSchema = z.object({
  id: z.string(),
  plan_id: z.string(),
  week_number: z.number().int(),
  concepts: z.array(planConceptSchema).default([]),
  content_ids: z.array(z.string()).nullable().optional(),
  quiz_due_at: z.string().nullable().optional(),
  status: z.string(),
});

// Read-only goal-pacing overlay (ADR-0009). Frames the plan against the goal
// (readiness, time-to-goal, pace) without changing which concepts were selected.
export const planPacingSchema = z.object({
  goal_key: z.string(),
  status: z.enum(['ahead', 'on_track', 'at_risk']),
  goal_readiness: z.number(),
  weeks_left: z.number(),
  remaining_scope: z.number(),
  frontier_size: z.number(),
  required_velocity: z.number(),
  capacity: z.number(),
  // Humble readiness overlay (ADR-0010 Stream E). Optional/back-compat: absent when
  // the goal has no frontier or on older payloads. `readiness` is the concave,
  // mock-gated, sub-1.0 number the UI should show instead of raw goal_readiness.
  readiness: z.number().optional(),
  critical_coverage: z.number().optional(),
  exam_ready: z.boolean().optional(),
  mock_passed: z.boolean().optional(),
  readiness_band: z
    .enum(['foundational', 'building', 'approaching', 'exam_ready'])
    .optional(),
  readiness_phase: z.enum(['building', 'final_phase', 'day_before']).optional(),
  days_to_exam: z.number().nullable().optional(),
  readiness_message_key: z.string().optional(),
});

export const learningPlanSchema = z.object({
  id: z.string(),
  learner_id: z.string(),
  goal: z.string(),
  start_date: z.string(),
  end_date: z.string().nullable().optional(),
  status: z.string(),
  weeks: z.array(planWeekSchema).default([]),
  plan_adjustment_kind: z
    .enum([
      'wellbeing',
      'learner_template',
      'mastery',
      'exam_window',
      'horizon_repair',
      'train_adapt',
    ])
    .nullable()
    .optional(),
  plan_last_adjusted_at: z.string().nullable().optional(),
  pacing: planPacingSchema.nullable().optional(),
});

export const quizOptionSchema = z.object({
  key: z.string(),
  text: z.string(),
});

export const quizQuestionKindSchema = z.enum([
  'mcq',
  'true_false',
  'numeric',
  'short_answer',
  'open',
  'derivation',
]);

export const quizQuestionPartSchema = z.object({
  label: z.string(),
  body: z.string(),
  points: z.number().optional(),
});

export const quizQuestionSchema = z.object({
  id: z.string(),
  topic: z.string(),
  subject: z.string(),
  difficulty: z.number(),
  stem: z.string(),
  /** Empty for open / numeric / short_answer. */
  options: z.array(quizOptionSchema),
  /** ADR-0010 gate kinds; omit/undefined treated as mcq for legacy payloads. */
  kind: quizQuestionKindSchema.optional(),
  /** Bagrut-style sub-parts (א/ב/ג) when present. */
  parts: z.array(quizQuestionPartSchema).optional(),
  total_points: z.number().optional(),
});

export const quizStartResponseSchema = z.object({
  quiz_id: z.string(),
  week_id: z.string(),
  plan_id: z.string(),
  week_number: z.number().int(),
  time_limit_s: z.number().int(),
  questions: z.array(quizQuestionSchema),
  started_at: z.string(),
});

export const processFeedbackSchema = z.object({
  item_id: z.string(),
  status: z.enum(['pending', 'graded', 'failed']),
  retries: z.number(),
  strengths: z.string(),
  steps_present: z.string(),
  steps_skipped: z.string(),
  logic: z.string(),
  material_anchoring: z.string(),
  points_earned: z.number(),
  points_available: z.number(),
  process_score: z.number(),
  next_fix: z.string(),
  graded_at: z.string().optional(),
});

export const quizSubmitResponseSchema = z.object({
  quiz_id: z.string(),
  /** null while grading_status is pending/grading — never invent a score */
  score: z.number().nullable(),
  per_topic: z.record(z.string(), z.number()),
  weak_concepts: z.array(z.string()),
  plan_adapted: z.boolean(),
  next_week_concepts: z.array(z.string()).nullable().optional(),
  passed: z.boolean().nullable().optional(),
  pass_threshold: z.number().optional(),
  attempt_id: z.string().nullable().optional(),
  grading_status: z
    .enum(['pending', 'grading', 'needs_human', 'complete', 'failed', 'reopened'])
    .optional(),
  item_feedback: z.record(z.string(), processFeedbackSchema).optional(),
  item_scores: z.record(z.string(), z.number()).optional(),
  open_pending: z.number().optional(),
  open_total: z.number().optional(),
  graded_open: z.number().optional(),
  busy: z.boolean().optional(),
  message: z.string().optional(),
});

export type PlanConcept = z.infer<typeof planConceptSchema>;
export type PlanWeek = z.infer<typeof planWeekSchema>;
export type PlanPacing = z.infer<typeof planPacingSchema>;
export type LearningPlan = z.infer<typeof learningPlanSchema>;
export type QuizOption = z.infer<typeof quizOptionSchema>;
export type QuizQuestion = z.infer<typeof quizQuestionSchema>;
export type QuizStartResponse = z.infer<typeof quizStartResponseSchema>;
export type QuizSubmitResponse = z.infer<typeof quizSubmitResponseSchema>;
