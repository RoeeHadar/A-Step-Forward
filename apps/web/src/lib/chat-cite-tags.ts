/**
 * Soft citation machine tags for hybrid tool packs (ADR-0014).
 * Shadow mode: strip from learner-visible text and log; hard eval gates later.
 */
import { logger } from '@/lib/logger';

const CITE_RE = /\[\[ASF_CITE:(\{[\s\S]*?\})\]\]/g;

/**
 * Matches any [[ASF_*:...]] machine tag family.  Used by stream + render
 * defenses to prevent any tag family from leaking into the visible UI.
 * The lazy `[\s\S]*?` stops at the first `]]` — sufficient because tag
 * payloads never contain literal `]]`.
 */
const ALL_ASF_TAGS_RE = /\[\[ASF_[A-Z_]+:[\s\S]*?\]\]/g;

export interface SoftCitationPayload {
  tools?: string[];
  concept_id?: string | null;
  lesson_id?: string | null;
  note?: string | null;
}

export function stripRefPrefix(id: string): string {
  return id.replace(/^(concept|lesson):/, '');
}

/** Normalize a concept id for the turn grounding set. */
export function groundingConceptId(id: string): string {
  return stripRefPrefix(id);
}

/** Normalize a lesson id for the turn grounding set. */
export function groundingLessonId(id: string): string {
  return `lesson:${stripRefPrefix(id)}`;
}

export function buildGroundingLookup(ids: Iterable<string>): Set<string> {
  const set = new Set<string>();
  for (const raw of ids) {
    if (!raw) continue;
    set.add(raw);
    set.add(stripRefPrefix(raw));
  }
  return set;
}

function isConceptGrounded(conceptId: string, ground: Set<string>): boolean {
  const bare = stripRefPrefix(conceptId);
  return ground.has(bare) || ground.has(`concept:${bare}`);
}

function isLessonGrounded(lessonId: string, ground: Set<string>): boolean {
  const bare = stripRefPrefix(lessonId);
  return ground.has(bare) || ground.has(`lesson:${bare}`);
}

/**
 * Classify parsed cite payloads against ids injected into the turn context.
 * Returns normalized refs: `concept:<id>` / `lesson:<id>`.
 */
export function classifyCites(
  cites: SoftCitationPayload[],
  groundingIds: Iterable<string>,
): { valid: string[]; invalid: string[] } {
  const ground = buildGroundingLookup(groundingIds);
  const valid = new Set<string>();
  const invalid = new Set<string>();

  for (const cite of cites) {
    const refs: string[] = [];
    if (cite.concept_id) refs.push(`concept:${stripRefPrefix(cite.concept_id)}`);
    if (cite.lesson_id) refs.push(`lesson:${stripRefPrefix(cite.lesson_id)}`);
    if (refs.length === 0) {
      invalid.add('(no_id)');
      continue;
    }
    for (const ref of refs) {
      const kind = ref.startsWith('lesson:') ? 'lesson' : 'concept';
      const id = stripRefPrefix(ref);
      const grounded =
        kind === 'lesson' ? isLessonGrounded(id, ground) : isConceptGrounded(id, ground);
      if (grounded) valid.add(ref);
      else invalid.add(ref);
    }
  }

  return { valid: [...valid].sort(), invalid: [...invalid].sort() };
}

export function stripCiteMachineTags(content: string): string {
  return content.replace(CITE_RE, '').replace(/\n{3,}/g, '\n\n').trim();
}

/**
 * Strip ALL [[ASF_*:...]] machine-tag families from visible content.
 * Use this in the streaming path and the render layer so no tag family
 * (CITE, MEMORY_NOTE, PLAN_UPDATE, …) ever reaches the learner UI.
 * Safe for client components — no server-only imports.
 */
export function stripAllMachineTags(content: string): string {
  return content.replace(ALL_ASF_TAGS_RE, '').replace(/\n{3,}/g, '\n\n').trim();
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

/** Greppable Vercel audit line for invalid-cite rate measurement. */
export function logCiteAudit(params: {
  agent: string;
  citations: SoftCitationPayload[];
  groundingIds: Iterable<string>;
}): void {
  if (params.citations.length === 0) return;
  const groundingArr = [...params.groundingIds];
  const { valid, invalid } = classifyCites(params.citations, params.groundingIds);
  console.log(
    JSON.stringify({
      tag: 'ASF_CITE_AUDIT',
      agent: params.agent,
      valid,
      invalid,
      groundingCount: groundingArr.length,
    }),
  );
}
