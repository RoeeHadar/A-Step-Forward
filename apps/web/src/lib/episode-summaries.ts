/**
 * AS-57 (Phase 4 C6): episode summaries instead of raw turns past K.
 *
 * Flag EPISODE_SUMMARIES (default off). When on:
 *  - write: after an assistant turn is stored, the session's turns are summarised with the
 *    cheap model chain (llm-provider.ts) and stored as a learner_agent_notes row of kind
 *    'episode' (no migration). The content carries the AS-42 typed-fact envelope with
 *    key `session.<sessionId>` (n = turns covered) so a rewrite supersedes the older one.
 *  - read: the last K raw turns of the current session stay as chat messages; everything
 *    older (earlier sessions, and the current session once it is longer than K) is injected
 *    as a short "## Earlier sessions" block built from the stored summaries.
 * Pure helpers here take their I/O as deps so they are unit-testable offline.
 */
import { decodeFactContent, encodeFactContent, normalizeFactKey } from '@/lib/typed-facts';

export const EPISODE_KIND = 'episode';
/** Raw turns kept verbatim (= CHAT_CONTEXT.maxMemoryTurns). */
export const EPISODE_K = 4;
/** Stored summary cap (chars); appendAgentNote hard-caps notes at 600. */
export const EPISODE_MAX_CHARS = 400;
/** Summaries injected per prompt. */
export const EPISODE_MAX_INJECT = 3;
/** Turns read back when (re)summarising one session. */
export const EPISODE_MAX_SOURCE_TURNS = 40;
/** Marker the summariser system prompt starts with (also lets tests route a mock). */
export const EPISODE_SUMMARIZER_MARKER = '[ASF_EPISODE_SUMMARY]';
export const EPISODE_BLOCK_HEADER = '## Earlier sessions (episode summaries)';

export function episodeSummariesEnabled(env: Record<string, string | undefined> = process.env): boolean {
  const v = (env.EPISODE_SUMMARIES ?? '').trim().toLowerCase();
  return v === '1' || v === 'true' || v === 'on';
}

export function episodeKey(sessionId: string): string | null {
  return normalizeFactKey(`session.${sessionId}`);
}

/**
 * Write trigger: after the first exchange (2 turns) and then every K turns. A session
 * therefore always has a summary once it has one reply, and it is refreshed as it grows;
 * at most K-1 trailing turns are not yet in the summary (they are still raw within K).
 */
export function shouldWriteEpisode(turnCount: number, k = EPISODE_K): boolean {
  return turnCount === 2 || (turnCount > 0 && turnCount % k === 0);
}

/**
 * Token estimate used for the memory-context budget (no tokenizer dependency):
 * Hebrew letters ≈ 2 chars/token, everything else ≈ 4 chars/token.
 */
export function estimateTokens(text: string): number {
  let he = 0;
  for (const ch of text) if (ch >= '\u0590' && ch <= '\u05FF') he += 1;
  const other = [...text].length - he;
  return Math.ceil(he / 2 + other / 4);
}

export interface EpisodeTurn { role: 'user' | 'assistant'; content: string }

function clip(s: string, n: number): string {
  const t = s.replace(/\s+/g, ' ').trim();
  return t.length <= n ? t : `${t.slice(0, Math.max(0, n - 1)).trimEnd()}…`;
}

/** Deterministic, LLM-free fallback summary (learner turns are the signal). */
export function extractiveEpisodeSummary(agent: string, turns: EpisodeTurn[]): string {
  const users = turns.filter((t) => t.role === 'user').map((t) => clip(t.content, 90));
  const body = users.length > 0 ? `learner: ${users.slice(0, 2).concat(users.length > 3 ? ['…'] : [], users.length > 2 ? users.slice(-1) : []).join(' | ')}` : 'no learner turns';
  return clip(`${agent} session (${turns.length} turns) — ${body}`, EPISODE_MAX_CHARS);
}

export function buildSummarizerPrompt(agent: string, locale: 'he' | 'en', turns: EpisodeTurn[]): { system: string; user: string } {
  const system = `${EPISODE_SUMMARIZER_MARKER} Summarise one learner chat session with the ${agent} for future sessions. ` +
    `At most 3 short lines, ${EPISODE_MAX_CHARS} characters total, in ${locale === 'he' ? 'Hebrew' : 'English'}. ` +
    'Keep: topics, what the learner got right/wrong, open questions, agreed next step. No greetings, no quotes, no personal data beyond the learning context.';
  const user = turns.map((t) => `${t.role === 'user' ? 'Learner' : 'Agent'}: ${clip(t.content, 600)}`).join('\n');
  return { system, user };
}

export interface EpisodeNoteLike { id: string; agent: string; kind: string; content: string; created_at: string }

export interface WriteEpisodeDeps {
  fetchSessionTurns: () => Promise<EpisodeTurn[]>;
  /** Cheap-chain completion; null/throw → extractive fallback. */
  complete: (system: string, user: string) => Promise<string | null>;
  fetchEpisodes: () => Promise<EpisodeNoteLike[]>;
  append: (note: { kind: string; content: string; importance: number }) => Promise<string | null>;
  supersede: (oldId: string, newId: string) => Promise<void>;
  warn?: (msg: string, meta: Record<string, unknown>) => void;
}

/**
 * Fire-and-forget write. Never throws: every failure is logged and swallowed so a
 * summariser or DB error can never break chat. Returns what happened (for tests).
 */
export async function writeEpisodeSummary(
  args: { agent: string; sessionId: string | undefined; locale: 'he' | 'en' },
  deps: WriteEpisodeDeps,
): Promise<'skipped' | 'written' | 'fallback' | 'failed'> {
  try {
    if (!args.sessionId) return 'skipped';
    const key = episodeKey(args.sessionId);
    if (!key) return 'skipped';
    const turns = (await deps.fetchSessionTurns()).slice(-EPISODE_MAX_SOURCE_TURNS);
    if (!shouldWriteEpisode(turns.length)) return 'skipped';
    let text: string | null = null;
    try {
      const p = buildSummarizerPrompt(args.agent, args.locale, turns);
      text = (await deps.complete(p.system, p.user))?.replace(/\s+/g, ' ').trim() || null;
    } catch (err) {
      deps.warn?.('[ASF_EPISODE_SUMMARY_FAIL] summariser failed', { agent: args.agent, err: String(err) });
      text = null;
    }
    const usedFallback = !text;
    const summary = clip(text ?? extractiveEpisodeSummary(args.agent, turns), EPISODE_MAX_CHARS);
    const prev = (await deps.fetchEpisodes()).filter((n) => decodeFactContent(n.content).meta?.key === key);
    const id = await deps.append({
      kind: EPISODE_KIND,
      content: encodeFactContent(summary, { key, n: turns.length, valid_to: null }),
      importance: 2,
    });
    if (id) for (const p of prev) await deps.supersede(p.id, id);
    return usedFallback ? 'fallback' : 'written';
  } catch (err) {
    deps.warn?.('[ASF_EPISODE_SUMMARY_FAIL] episode write failed', { agent: args.agent, err: String(err) });
    return 'failed';
  }
}

/**
 * Episodes to inject for this turn: other sessions (newest first), plus the current
 * session's own summary only when it covers more than K turns (older raw turns dropped).
 */
export function selectEpisodes(notes: EpisodeNoteLike[], currentSessionId: string | undefined, max = EPISODE_MAX_INJECT): EpisodeNoteLike[] {
  const curKey = currentSessionId ? episodeKey(currentSessionId) : null;
  const seen = new Set<string>();
  const out: EpisodeNoteLike[] = [];
  for (const n of [...notes].sort((a, b) => (a.created_at < b.created_at ? 1 : -1))) {
    if (n.kind !== EPISODE_KIND) continue;
    const meta = decodeFactContent(n.content).meta;
    if (!meta || seen.has(meta.key)) continue;
    seen.add(meta.key);
    if (curKey && meta.key === curKey && meta.n <= EPISODE_K) continue;
    out.push(n);
    if (out.length >= max) break;
  }
  return out;
}

/** "## Earlier sessions" block (oldest first), or '' when nothing to inject (fallback = raw-only). */
export function buildEpisodeBlock(notes: EpisodeNoteLike[]): string {
  if (notes.length === 0) return '';
  const lines = [...notes].reverse().map((n) => `- ${n.created_at.slice(0, 10)} ${n.agent}: ${decodeFactContent(n.content).text.trim()}`);
  return `${EPISODE_BLOCK_HEADER}\n(Summaries of older turns — hints, the current question comes first.)\n${lines.join('\n')}`;
}
