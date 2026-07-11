/**
 * Persist agent memory from chat turns: ASF_MEMORY_NOTE tags + throttled observations.
 */
import 'server-only';
import { appendAgentNote, fetchAgentNotes } from '@/lib/neon-db';

const MEMORY_NOTE_RE = /\[\[ASF_MEMORY_NOTE:(\{[\s\S]*?\})\]\]/g;

const IMPLICIT_NOTE_MIN_CHARS = 28;
const IMPLICIT_NOTE_COOLDOWN_MS = 12 * 60 * 1000;

export function stripMemoryMachineTags(content: string): string {
  return content.replace(MEMORY_NOTE_RE, '').trim();
}

interface MemoryNotePayload {
  kind?: string;
  content?: string;
  importance?: number;
  related_concept_id?: string | null;
}

export async function applyMemoryTagsFromAssistant(
  learnerId: string,
  agent: string,
  assistantContent: string,
): Promise<number> {
  let applied = 0;
  for (const match of assistantContent.matchAll(MEMORY_NOTE_RE)) {
    try {
      const parsed = JSON.parse(match[1]!) as MemoryNotePayload;
      const content = parsed.content?.trim();
      if (!content) continue;
      await appendAgentNote(learnerId, agent, {
        kind: parsed.kind ?? 'observation',
        content,
        importance: parsed.importance ?? 3,
        related_concept_id: parsed.related_concept_id ?? null,
      });
      applied += 1;
    } catch {
      // ignore malformed tags
    }
  }
  return applied;
}

export async function persistThrottledChatObservation(
  learnerId: string,
  agent: string,
  userMessage: string,
  topic?: string | null,
): Promise<void> {
  const trimmed = userMessage.trim();
  if (trimmed.length < IMPLICIT_NOTE_MIN_CHARS) return;
  if (/ASF_PLAN_UPDATE|ASF_PLAN/i.test(trimmed)) return;

  const recent = await fetchAgentNotes(learnerId, agent, 1);
  const latest = recent[0];
  if (latest?.created_at) {
    const age = Date.now() - new Date(latest.created_at).getTime();
    if (age < IMPLICIT_NOTE_COOLDOWN_MS && latest.kind === 'observation') return;
  }

  const content =
    trimmed.length > 420
      ? `${trimmed.slice(0, 417)}…`
      : trimmed;

  await appendAgentNote(learnerId, agent, {
    kind: 'observation',
    content,
    importance: 3,
    related_concept_id: topic ?? null,
  });
}
