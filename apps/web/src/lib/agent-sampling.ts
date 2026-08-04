/**
 * Per-agent decoding parameters for learner chat.
 *
 * Each live agent has a distinct job, so temperature / top_p differ:
 *  - Reviewer & Coach want precision/consistency (low temp).
 *  - Tutor is grounded teaching (slightly higher for fluency).
 *  - Mentor benefits from warmth/variation.
 *
 * Reasoning-model families are clamped separately in `llm-provider.ts`
 * (isReasoningModel) because low temperature breaks them; that override wins
 * over these per-agent values when such a model is used.
 */

export interface SamplingProfile {
  temperature: number;
  topP: number;
}

/** Fallback when an agent has no explicit profile. */
export const DEFAULT_SAMPLING: SamplingProfile = { temperature: 0.4, topP: 0.9 };

const AGENT_SAMPLING: Record<string, SamplingProfile> = {
  tutor: { temperature: 0.3, topP: 0.9 },
  coach: { temperature: 0.2, topP: 0.9 },
  reviewer: { temperature: 0.2, topP: 0.85 },
  mentor: { temperature: 0.5, topP: 0.95 },
};

/** Deterministic decoding for routing / classification steps. */
export const ROUTER_SAMPLING: SamplingProfile = { temperature: 0, topP: 1 };

export function resolveAgentSampling(agent: string): SamplingProfile {
  return AGENT_SAMPLING[agent] ?? DEFAULT_SAMPLING;
}
