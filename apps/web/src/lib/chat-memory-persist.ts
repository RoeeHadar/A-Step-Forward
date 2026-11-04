/**
 * Persist agent memory from chat turns: ASF_MEMORY_NOTE tags only.
 *
 * Notes must be model-authored summaries. Raw learner messages are NOT
 * persisted here — they go into `chat_turns` via `recordChatTurn`.
 */
import 'server-only';
import { appendAgentNote } from '@/lib/neon-db';
import { ruleClassify } from '@/lib/chat-safety';
import { isTypedFactKind, normalizeFactKey, normalizeValidTo } from '@/lib/typed-facts';

const MEMORY_NOTE_RE = /\[\[ASF_MEMORY_NOTE:(\{[\s\S]*?\})\]\]/g;

/** Strip any embedded machine tags from note content before persistence. */
const MACHINE_TAG_RE = /\[\[ASF_[^\]]*\]\]/g;

const MAX_NOTE_CONTENT_CHARS = 600;

const VALID_KINDS = new Set([
  'observation',
  'preference',
  'strategy',
  'open_question',
  'misconception',
  'win',
  'plan',
  // AS-42 (C3) typed-fact kinds (misconception/preference already above).
  'goal',
  'state',
]);

export function stripMemoryMachineTags(content: string): string {
  return content.replace(MEMORY_NOTE_RE, '').trim();
}

interface MemoryNotePayload {
  kind?: string;
  content?: string;
  importance?: number;
  related_concept_id?: string | null;
  /** AS-42 (C3): supersede key for typed facts (kind + key). Optional: old tags omit it. */
  key?: string;
  /** AS-42 (C3): ISO end of validity, stored for C4 (state TTL); not enforced here. */
  valid_to?: string | null;
}

/**
 * AS-42 (C3): typed-fact fields of a parsed tag. Returns {} for untyped kinds or tags
 * without a usable key (old tags), so those notes are stored exactly as before.
 */
export function typedFactFromTag(
  kind: string,
  parsed: Pick<MemoryNotePayload, 'key' | 'valid_to'>,
): { fact?: { key: string; valid_to: string | null } } {
  if (!isTypedFactKind(kind)) return {};
  const key = normalizeFactKey(parsed.key);
  if (!key) return {};
  return { fact: { key, valid_to: normalizeValidTo(parsed.valid_to) } };
}

export async function applyMemoryTagsFromAssistant(
  learnerId: string,
  agent: string,
  assistantContent: string,
  opts?: { childMode?: boolean },
): Promise<number> {
  const childMode = opts?.childMode ?? false;
  let applied = 0;
  for (const match of assistantContent.matchAll(MEMORY_NOTE_RE)) {
    try {
      const parsed = JSON.parse(match[1]!) as MemoryNotePayload;

      const rawContent = parsed.content?.trim();
      if (!rawContent) {
        console.warn('[ASF_MEMORY_TAG_SKIP] empty content', { agent });
        continue;
      }

      // Strip any machine tags that leaked into the note text, then cap length.
      const content = rawContent.replace(MACHINE_TAG_RE, '').trim().slice(0, MAX_NOTE_CONTENT_CHARS);
      if (!content) {
        console.warn('[ASF_MEMORY_TAG_SKIP] content empty after tag strip', { agent });
        continue;
      }

      // Kinds are an open vocabulary by design (see agent-skill-notes skill) —
      // coerce unknown kinds to 'observation' instead of dropping the note.
      const rawKind = parsed.kind ?? 'observation';
      const kind = VALID_KINDS.has(rawKind) ? rawKind : 'observation';
      if (kind !== rawKind) {
        console.warn('[ASF_MEMORY_TAG_COERCE] unknown kind → observation', { agent, kind: rawKind });
      }

      // Clamp importance to 1–5.
      const rawImportance = parsed.importance;
      const importance =
        typeof rawImportance === 'number' && isFinite(rawImportance)
          ? Math.max(1, Math.min(5, Math.round(rawImportance)))
          : 3;

      // Safety classification on note content.
      if (ruleClassify(content, { childMode })) continue;

      await appendAgentNote(learnerId, agent, {
        kind,
        content,
        importance,
        related_concept_id: parsed.related_concept_id ?? null,
        ...typedFactFromTag(kind, parsed),
      });
      applied += 1;
    } catch (err) {
      console.warn('[ASF_MEMORY_TAG_SKIP] parse or write error', { agent, err: String(err) });
    }
  }
  return applied;
}
