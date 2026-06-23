import { z } from 'zod';
import { citationSchema, idStr } from './common';

export const agentNameSchema = z.enum([
  'tutor',
  'mentor',
  'coach',
  'qa_explainer',
  'reviewer',
  'note_taker',
  'engagement',
  'accessibility',
  'orchestrator',
  'curriculum_designer',
  'assessment_generator',
  'grader',
  'progress_analyzer',
  'content_curator',
  'research',
  'kg_builder',
  'memory_steward',
  'safety_moderation',
  'eval_agent',
  'analytics_insights',
]);
export type AgentName = z.infer<typeof agentNameSchema>;

export const chatRequestSchema = z.object({
  learner_id: idStr,
  message: z.string(),
  requested_agent: agentNameSchema.nullable().optional(),
  session_id: idStr.nullable().optional(),
  locale: z.string().default('en'),
});
export type ChatRequest = z.infer<typeof chatRequestSchema>;

export const chatChunkSchema = z.object({
  kind: z.enum(['token', 'tool_call', 'tool_result', 'citation', 'done', 'error']),
  agent: agentNameSchema.nullable().optional(),
  text: z.string().nullable().optional(),
  citation: citationSchema.nullable().optional(),
  tool: z.string().nullable().optional(),
  payload: z.record(z.unknown()).nullable().optional(),
  ts: z.string().datetime().optional(),
});
export type ChatChunk = z.infer<typeof chatChunkSchema>;

export const learnerFacingAgents: AgentName[] = [
  'tutor',
  'mentor',
  'coach',
  'qa_explainer',
  'reviewer',
  'note_taker',
  'accessibility',
];

export const agentDisplayNames: Record<AgentName, string> = {
  tutor: 'Tutor',
  mentor: 'Mentor',
  coach: 'Coach',
  qa_explainer: 'Q&A Explainer',
  reviewer: 'Reviewer',
  note_taker: 'Note-Taker',
  engagement: 'Engagement',
  accessibility: 'Accessibility',
  orchestrator: 'Orchestrator',
  curriculum_designer: 'Curriculum Designer',
  assessment_generator: 'Assessment Generator',
  grader: 'Grader',
  progress_analyzer: 'Progress Analyzer',
  content_curator: 'Content Curator',
  research: 'Research',
  kg_builder: 'KG Builder',
  memory_steward: 'Memory Steward',
  safety_moderation: 'Safety',
  eval_agent: 'Eval Agent',
  analytics_insights: 'Analytics',
};
