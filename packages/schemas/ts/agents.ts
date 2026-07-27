import { z } from 'zod';

export const learnerFacingAgents = ['tutor', 'coach', 'qa_explainer', 'reviewer', 'mentor'] as const;
export const agentNameSchema = z.enum(learnerFacingAgents);
export type AgentName = z.infer<typeof agentNameSchema>;

export const agentDisplayNames: Record<AgentName, string> = {
  tutor: 'Tutor',
  coach: 'Coach',
  qa_explainer: 'Q&A Explainer',
  reviewer: 'Reviewer',
  mentor: 'Mentor',
};
