/**
 * Soft citation machine tags for hybrid tool packs (ADR-0014).
 * Shadow mode: strip from learner-visible text and log; hard eval gates later.
 */
import { logger } from '@/lib/logger';

const CITE_RE = /\[\[ASF_CITE:(\{[\s\S]*?\})\]\]/g;

export interface SoftCitationPayload {
  tools?: string[];
  concept_id?: string | null;
  lesson_id?: string | null;
  note?: string | null;
}

export function stripCiteMachineTags(content: string): string {
  return content.replace(CITE_RE, '').replace(/\n{3,}/g, '\n\n').trim();
}

export function parseCiteTags(content: string): SoftCitationPayload[] {
  const out: SoftCitationPayload[] = [];
  for (const match of content.matchAll(CITE_RE)) {
    try {
      const parsed = JSON.parse(match[1]!) as SoftCitationPayload;
      out.push(parsed);
    } catch {
      // ignore malformed
    }
  }
  return out;
}

export function logShadowCitations(params: {
  agent: string;
  learnerId: string;
  citations: SoftCitationPayload[];
  toolsExpected?: string[];
}): void {
  if (params.citations.length === 0 && !(params.toolsExpected?.length)) return;
  logger.info('chat: soft citation shadow', {
    agent: params.agent,
    learnerId: params.learnerId.slice(0, 8),
    cited: params.citations,
    toolsExpected: params.toolsExpected ?? [],
  });
}
