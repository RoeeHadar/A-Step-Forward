/**
 * AS-42 (Phase 4 C3): typed semantic facts on top of learner_agent_notes.
 *
 * No schema change (AS-32 §7 Q2). Everything rides in columns that already exist
 * in infra/alembic/versions/0015_persona_agent_notes.py:56-69:
 *   - `kind` TEXT (0015:60) carries the fact type: misconception | goal | preference | state.
 *   - `content` TEXT (0015:61) carries the note text plus a trailing fact envelope
 *     ` ⟦fact {"key":…,"n":…,"valid_to":…}⟧` that holds key, count and valid_to.
 *   - `superseded_by` UUID (0015:65) marks the replaced fact; every reader already
 *     filters `superseded_by IS NULL` (neon-db.ts fetchAgentNotes, countAgentNotes,
 *     persona-consolidator fetchAllLiveNotes).
 *
 * Supersede key = `${kind}:${key}`, per learner, across agents. A new live fact with the
 * same supersede key supersedes every older live fact with that key (any agent), so a
 * learner has at most one current goal:exam_date, one misconception:sqrt_split, etc.
 * Misconceptions carry a running count `n` (prior n + 1) so a repeated error increments.
 *
 * Back-compat: notes without the envelope (all notes written before AS-42, and tags
 * without `key`) decode to `meta: null` and behave exactly as before (never superseded
 * by key).
 *
 * C4 (AS-43): `valid_to` is enforced by `isFactCurrent(meta, now)` — the single TTL rule,
 * applied on every read path (chat agent notes, handoff digest, persona consolidator).
 * kind=state defaults to valid_to = now + STATE_TTL_DAYS (14 d). `now` is always injected
 * (no clock read inside this module).
 */

export const TYPED_FACT_KINDS = ['misconception', 'goal', 'preference', 'state'] as const;
export type TypedFactKind = (typeof TYPED_FACT_KINDS)[number];

export interface FactMeta {
  key: string;
  /** Occurrence count; incremented for misconceptions on each repeat. */
  n: number;
  /** ISO timestamp or null. Stored only (C4 enforces it). */
  valid_to: string | null;
}

const ENVELOPE_RE = /\s*⟦fact (\{[^⟧]*\})⟧\s*$/;

export function isTypedFactKind(kind: string | null | undefined): kind is TypedFactKind {
  return (TYPED_FACT_KINDS as readonly string[]).includes(kind ?? '');
}

/** Lowercase, [a-z0-9_.-] only, ≤64 chars; returns null when nothing usable is left. */
export function normalizeFactKey(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  const k = raw.trim().toLowerCase().replace(/[^a-z0-9_.-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 64);
  return k || null;
}

/** Validated ISO string or null (unparseable dates are dropped, never thrown). */
export function normalizeValidTo(raw: unknown): string | null {
  if (typeof raw !== 'string' || !raw.trim()) return null;
  const t = Date.parse(raw);
  return Number.isFinite(t) ? new Date(t).toISOString() : null;
}

export function supersedeKey(kind: string, key: string): string {
  return `${kind}:${key}`;
}

/** Key is serialised first so SQL can match the prefix `⟦fact {"key":"<key>"`. */
export function encodeFactContent(text: string, meta: FactMeta): string {
  return `${text.replace(ENVELOPE_RE, '')} ⟦fact ${JSON.stringify({ key: meta.key, n: meta.n, valid_to: meta.valid_to })}⟧`;
}

export function factEnvelopePrefix(key: string): string {
  return `⟦fact {"key":${JSON.stringify(key)}`;
}

export function decodeFactContent(content: string): { text: string; meta: FactMeta | null } {
  const m = ENVELOPE_RE.exec(content ?? '');
  if (!m) return { text: content ?? '', meta: null };
  try {
    const j = JSON.parse(m[1]!) as Partial<FactMeta>;
    const key = normalizeFactKey(j.key);
    if (!key) return { text: content, meta: null };
    const n = typeof j.n === 'number' && Number.isFinite(j.n) && j.n >= 1 ? Math.floor(j.n) : 1;
    return { text: content.slice(0, m.index), meta: { key, n, valid_to: normalizeValidTo(j.valid_to) } };
  } catch {
    return { text: content, meta: null };
  }
}

/** Display text for prompts / digests (envelope removed). */
export function factDisplayText(content: string): string {
  return decodeFactContent(content).text;
}

/** Next occurrence count when a fact with the same supersede key already exists. */
export function nextFactCount(kind: string, prev: FactMeta | null): number {
  return kind === 'misconception' && prev ? prev.n + 1 : 1;
}

/** AS-43 (C4): default affect TTL for kind=state. */
export const STATE_TTL_DAYS = 14;
const DAY_MS = 86_400_000;

/** valid_to to store: explicit valid_to wins; kind=state defaults to now + 14 d; else null. */
export function defaultValidTo(kind: string, explicit: string | null, now: Date): string | null {
  if (explicit) return explicit;
  return kind === 'state' ? new Date(now.getTime() + STATE_TTL_DAYS * DAY_MS).toISOString() : null;
}

/** AS-43 (C4): a fact is current until `valid_to` (exclusive). No valid_to = no expiry. */
export function isFactCurrent(meta: FactMeta | null, now: Date): boolean {
  if (!meta?.valid_to) return true;
  const t = Date.parse(meta.valid_to);
  return !Number.isFinite(t) || t > now.getTime();
}

/** AS-43 (C4): read-path filter — drops expired facts; plain notes pass through. */
export function dropExpiredFacts<T extends { kind: string; content: string }>(notes: T[], now: Date): T[] {
  return notes.filter((n) => !isTypedFactKind(n.kind) || isFactCurrent(decodeFactContent(n.content).meta, now));
}

/** AS-43 (C4): true when every cited note is a kind=state fact (mood-only evidence). */
export function isStateOnlyEvidence(notes: Array<{ kind: string }>): boolean {
  return notes.length > 0 && notes.every((n) => n.kind === 'state');
}

/**
 * Keep only non-superseded facts from a note list: for each supersede key the newest
 * note wins (created_at, then list order). Notes without a fact envelope pass through.
 */
export function keepCurrentFacts<T extends { kind: string; content: string; created_at?: string | Date | null }>(notes: T[], now: Date): T[] {
  const winner = new Map<string, { i: number; t: number }>();
  notes.forEach((n, i) => {
    const meta = isTypedFactKind(n.kind) ? decodeFactContent(n.content).meta : null;
    if (!meta) return;
    const k = supersedeKey(n.kind, meta.key);
    const t = (n.created_at == null ? 0 : new Date(n.created_at).getTime()) || 0; // AS-61: Date.parse(Date) drops ms
    const w = winner.get(k);
    if (!w || t > w.t || (t === w.t && i > w.i)) winner.set(k, { i, t });
  });
  return notes.filter((n, i) => {
    const meta = isTypedFactKind(n.kind) ? decodeFactContent(n.content).meta : null;
    if (!meta) return true;
    return winner.get(supersedeKey(n.kind, meta.key))!.i === i && isFactCurrent(meta, now);
  });
}
