/**
 * Cross-agent handoff digests (ADR-0014).
 * Each agent keeps private notes; peers only see a short ranked digest.
 */
export type LiveAgentId = 'tutor' | 'mentor' | 'coach' | 'reviewer';

export interface DigestNote {
  agent: string;
  kind: string;
  content: string;
  importance: number;
  related_concept_id?: string | null;
  created_at?: string | null;
}

/** Which peers matter most for each reader's role. */
const PEER_PRIORITY: Record<LiveAgentId, LiveAgentId[]> = {
  tutor: ['coach', 'mentor', 'reviewer'],
  coach: ['tutor', 'mentor', 'reviewer'],
  mentor: ['tutor', 'coach', 'reviewer'],
  reviewer: ['tutor', 'coach', 'mentor'],
};

function roleWeight(reader: LiveAgentId, source: string, kind: string): number {
  const peers = PEER_PRIORITY[reader] ?? [];
  const peerIdx = peers.indexOf(source as LiveAgentId);
  const peerBoost = peerIdx >= 0 ? 3 - Math.min(peerIdx, 2) : 0;
  // Role-gated kinds the reader cares about.
  let kindBoost = 0;
  if (reader === 'coach' && (kind === 'strategy' || kind === 'open_question')) kindBoost = 2;
  if (reader === 'tutor' && (kind === 'misconception' || kind === 'strategy')) kindBoost = 2;
  if (reader === 'mentor' && (kind === 'preference' || kind === 'observation')) kindBoost = 1;
  if (source === 'mentor' && kind === 'observation') kindBoost += 1;
  return peerBoost + kindBoost;
}

function scoreNote(reader: LiveAgentId, note: DigestNote, now = Date.now()): number {
  const ageMs = note.created_at ? Math.max(0, now - new Date(note.created_at).getTime()) : 0;
  const recency = Math.exp(-ageMs / (1000 * 60 * 60 * 24 * 14)); // ~2-week half-ish decay
  return note.importance * 2 + roleWeight(reader, note.agent, note.kind) + recency * 2;
}

/**
 * Build a ≤maxBullets / ≤maxChars digest from other agents' notes.
 * Never includes the reader's own notes (those are injected separately).
 */
export function buildHandoffDigest(params: {
  readingAgent: LiveAgentId;
  notes: DigestNote[];
  maxBullets?: number;
  maxChars?: number;
  conceptFilter?: string | null;
}): string {
  const maxBullets = params.maxBullets ?? 5;
  const maxChars = params.maxChars ?? 520;
  const filtered = params.notes.filter((n) => {
    if (n.agent === params.readingAgent) return false;
    if (!n.content?.trim()) return false;
    if (params.conceptFilter && n.related_concept_id && n.related_concept_id !== params.conceptFilter) {
      return false;
    }
    return true;
  });

  const ranked = [...filtered].sort(
    (a, b) => scoreNote(params.readingAgent, b) - scoreNote(params.readingAgent, a),
  );

  const bullets: string[] = [];
  let used = 0;
  for (const n of ranked) {
    if (bullets.length >= maxBullets) break;
    const snippet = n.content.trim().replace(/\s+/g, ' ').slice(0, 140);
    const line = `- [${n.agent}/${n.kind}] ${snippet}`;
    if (used + line.length + 1 > maxChars) break;
    bullets.push(line);
    used += line.length + 1;
  }

  if (bullets.length === 0) return '';

  return [
    `## Cross-agent handoff digest (compressed — not raw notes)`,
    `Use for orientation only. Do not quote as verbatim chat. Expand via memory.expand pack when needed.`,
    ...bullets,
  ].join('\n');
}

export function wantsMemoryExpand(message: string): boolean {
  const t = message.trim();
  if (!t) return false;
  return /(?:מה אתה זוכר|מה אתם זוכרים|what do you remember|why am i stuck|למה אני תקוע|תזכיר לי|remind me|expand memory|מה שמרת|מה כתבת עלי)/i.test(
    t,
  );
}
