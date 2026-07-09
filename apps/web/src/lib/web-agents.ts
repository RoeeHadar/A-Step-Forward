/**
 * The four learner-facing agents live on the public website (homepage + chat).
 * Q&A explainer capability is folded into Tutor; Note-Taker is a future
 * standalone feature in the learning section (not a chat agent).
 */
import type { AgentName } from '@asf/schemas/agents';

export const WEB_LIVE_AGENTS = ['tutor', 'mentor', 'coach', 'reviewer'] as const;
export type WebLiveAgent = (typeof WEB_LIVE_AGENTS)[number];

/** Legacy chat slugs that redirect to Tutor. */
export const DEPRECATED_CHAT_AGENTS = ['qa_explainer', 'note_taker'] as const;

export function isWebLiveAgent(agent: string): agent is WebLiveAgent {
  return (WEB_LIVE_AGENTS as readonly string[]).includes(agent);
}

/**
 * Resolve the agent slug used for persona, skills, and per-turn context.
 * Deprecated slugs map to `tutor`; unknown slugs fall back to `tutor`.
 */
export function resolveWebChatAgent(agent: string): WebLiveAgent {
  if (isWebLiveAgent(agent)) return agent;
  return 'tutor';
}

/** Agents shown in chat switcher, dashboard cards, memory tabs, etc. */
export const WEB_LIVE_AGENT_NAMES: Record<WebLiveAgent, { he: string; en: string }> = {
  tutor: { he: 'מורה', en: 'Tutor' },
  mentor: { he: 'מנטור', en: 'Mentor' },
  coach: { he: 'מאמן', en: 'Coach' },
  reviewer: { he: 'מבקר', en: 'Reviewer' },
};

export function webLiveAgentLabel(agent: WebLiveAgent, locale: 'he' | 'en'): string {
  return WEB_LIVE_AGENT_NAMES[agent][locale];
}

/** Type guard for schema-valid agent names used in chat routing. */
export function isDeprecatedChatAgent(agent: AgentName): boolean {
  return (DEPRECATED_CHAT_AGENTS as readonly string[]).includes(agent);
}
