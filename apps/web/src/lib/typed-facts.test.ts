/**
 * AS-42 (Phase 4 C3): typed facts — parse, supersede (kind + key), consolidator.
 * Offline: neon is mocked, no DB, no LLM.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';

vi.mock('server-only', () => ({}));

/** Minimal in-memory learner_agent_notes behind a tagged-template `sql` mock. */
type Row = { id: string; learner_id: string; agent: string; kind: string; content: string; superseded_by: string | null; archived_at: null; created_at: number };
const { rows, queries } = vi.hoisted(() => ({ rows: [] as Row[], queries: [] as string[] }));
const like = (v: string, pat: string) => {
  const re = new RegExp('^' + pat.replace(/\\([\\%_])|([%_])|([.*+?^${}()|[\]\\])/g, (_m, esc, wild, meta) =>
    esc ? esc.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') : wild ? (wild === '%' ? '[\\s\\S]*' : '.') : '\\' + meta) + '$');
  return re.test(v);
};
vi.mock('@neondatabase/serverless', () => {
  process.env['DATABASE_URL'] = 'postgresql://test-typed-facts';
  const sql = async (strings: TemplateStringsArray, ...v: unknown[]) => {
    const q = strings.join('?').replace(/\s+/g, ' ').trim();
    queries.push(q);
    const live = (r: Row) => r.superseded_by === null && r.archived_at === null;
    if (q.startsWith('SELECT content FROM learner_agent_notes')) {
      const [learner, kind, pat] = v as string[];
      return rows.filter((r) => live(r) && r.learner_id === learner && r.kind === kind && like(r.content, pat!)).sort((a, b) => b.created_at - a.created_at).slice(0, 1);
    }
    if (q.startsWith('INSERT INTO learner_agent_notes')) {
      const [id, learner, agent, kind, content] = v as string[];
      rows.push({ id: id!, learner_id: learner!, agent: agent!, kind: kind!, content: content!, superseded_by: null, archived_at: null, created_at: rows.length + 1 });
      return [];
    }
    if (q.startsWith('UPDATE learner_agent_notes SET superseded_by')) {
      const [by, learner, kind, notId, pat] = v as string[];
      for (const r of rows) if (live(r) && r.learner_id === learner && r.kind === kind && r.id !== notId && like(r.content, pat!)) r.superseded_by = by!;
      return [];
    }
    return [];
  };
  return { neon: () => sql, neonConfig: {} };
});

import {
  decodeFactContent, encodeFactContent, keepCurrentFacts, normalizeFactKey, normalizeValidTo, isFactCurrent, supersedeKey,
} from './typed-facts';
import { appendAgentNote } from './neon-db';
import { typedFactFromTag } from './chat-memory-persist';
import { selectConsolidationNotes, buildUserPrompt } from './persona-consolidator';

const live = (learner: string) => rows.filter((r) => r.learner_id === learner && r.superseded_by === null);

describe('AS-42 parse', () => {
  it('typed tag yields kind + normalised key + valid_to', () => {
    expect(typedFactFromTag('goal', { key: 'Exam Date', valid_to: '2026-12-01' }, new Date('2026-01-05T09:00:00Z'))).toEqual({ fact: { key: 'exam_date', valid_to: '2026-12-01T00:00:00.000Z' } });
    expect(typedFactFromTag('state', { key: 'mood', valid_to: 'not a date' }, new Date('2026-01-05T09:00:00Z'))).toEqual({ fact: { key: 'mood', valid_to: '2026-01-19T09:00:00.000Z' } }); // AS-43 default +14 d
  });
  it('old tags without key, or untyped kinds, parse exactly as before (no fact)', () => {
    expect(typedFactFromTag('misconception', {}, new Date('2026-01-05T09:00:00Z'))).toEqual({});
    expect(typedFactFromTag('observation', { key: 'x' }, new Date('2026-01-05T09:00:00Z'))).toEqual({});
    expect(decodeFactContent('plain old note')).toEqual({ text: 'plain old note', meta: null });
    expect(decodeFactContent('broken ⟦fact {nope}⟧')).toEqual({ text: 'broken ⟦fact {nope}⟧', meta: null });
  });
  it('envelope round-trips and display text drops it', () => {
    const c = encodeFactContent('goal is 5 units', { key: 'units', n: 1, valid_to: null });
    expect(c).toBe('goal is 5 units ⟦fact {"key":"units","n":1,"valid_to":null}⟧');
    expect(decodeFactContent(c)).toEqual({ text: 'goal is 5 units', meta: { key: 'units', n: 1, valid_to: null } });
    expect(normalizeFactKey('  ')).toBeNull();
    expect(normalizeValidTo(undefined)).toBeNull();
    expect(supersedeKey('goal', 'units')).toBe('goal:units');
  });
  it('AS-43: C4 hook now enforces TTL (expired valid_to is not current)', () => {
    expect(isFactCurrent({ key: 'mood', n: 1, valid_to: '2000-01-01T00:00:00.000Z' }, new Date('2026-01-05T09:00:00Z'))).toBe(false);
  });
});

describe('AS-42 appendAgentNote supersede by kind + key', () => {
  beforeEach(() => { rows.length = 0; queries.length = 0; });
  it('goal change: only the newest goal with the same key stays live (across agents)', async () => {
    await appendAgentNote('L1', 'mentor', { kind: 'goal', content: 'exam in 2 months', fact: { key: 'exam_date' } });
    await appendAgentNote('L1', 'coach', { kind: 'goal', content: 'aims for 5 units', fact: { key: 'units' } });
    await appendAgentNote('L1', 'mentor', { kind: 'goal', content: 'exam in 2 weeks', fact: { key: 'exam_date' } });
    const goals = live('L1').map((r) => decodeFactContent(r.content).text);
    expect(goals.sort()).toEqual(['aims for 5 units', 'exam in 2 weeks']);
  });
  it('misconception repeat increments the count and keeps one live row', async () => {
    for (let i = 0; i < 3; i++) await appendAgentNote('L2', 'tutor', { kind: 'misconception', content: 'splits sqrt over +', fact: { key: 'sqrt_split' } });
    const l = live('L2');
    expect(l).toHaveLength(1);
    expect(decodeFactContent(l[0]!.content).meta?.n).toBe(3);
  });
  it('does not cross learners, kinds or similar keys (LIKE wildcards escaped)', async () => {
    await appendAgentNote('L3', 'tutor', { kind: 'misconception', content: 'a', fact: { key: 'sqrt_split' } });
    await appendAgentNote('L3', 'tutor', { kind: 'misconception', content: 'b', fact: { key: 'sqrtxsplit' } });
    await appendAgentNote('L3', 'tutor', { kind: 'preference', content: 'c', fact: { key: 'sqrt_split' } });
    await appendAgentNote('L4', 'tutor', { kind: 'misconception', content: 'd', fact: { key: 'sqrt_split' } });
    expect(live('L3')).toHaveLength(3);
    expect(live('L4')).toHaveLength(1);
  });
  it('untyped / keyless notes: one plain INSERT, content unchanged (back-compat)', async () => {
    await appendAgentNote('L5', 'tutor', { kind: 'misconception', content: 'old style note' });
    await appendAgentNote('L5', 'tutor', { kind: 'misconception', content: 'old style note' });
    expect(queries.every((q) => q.startsWith('INSERT'))).toBe(true);
    expect(live('L5').map((r) => r.content)).toEqual(['old style note', 'old style note']);
  });
});

describe('AS-42 persona consolidator keeps non-superseded facts only', () => {
  const n = (id: string, kind: string, content: string, created_at: string) =>
    ({ id, learner_id: 'L', agent: 'mentor', kind, content, importance: 3, related_concept_id: null, source_turn_id: null, created_at: new Date(created_at), last_referenced_at: null });
  it('drops older same-key facts, keeps other keys and plain notes', () => {
    const notes = [
      n('1', 'goal', encodeFactContent('5 units', { key: 'units', n: 1, valid_to: null }), '2026-01-01T00:00:00Z'),
      n('2', 'goal', encodeFactContent('4 units', { key: 'units', n: 1, valid_to: null }), '2026-02-01T00:00:00Z'),
      n('3', 'goal', encodeFactContent('exam in 2 weeks', { key: 'exam_date', n: 1, valid_to: null }), '2026-01-15T00:00:00Z'),
      n('4', 'observation', 'likes diagrams', '2025-12-01T00:00:00Z'),
    ];
    expect(selectConsolidationNotes(notes, new Date('2026-01-05T09:00:00Z')).map((x) => x.id)).toEqual(['2', '3', '4']);
    expect(keepCurrentFacts([notes[1]!, notes[0]!], new Date('2026-01-05T09:00:00Z')).map((x) => x.id)).toEqual(['2']);
    const prompt = buildUserPrompt('', selectConsolidationNotes(notes, new Date('2026-01-05T09:00:00Z')));
    expect(prompt).toContain('kind=goal key=units importance=3 :: 4 units');
    expect(prompt).not.toContain('5 units');
    expect(prompt).not.toContain('⟦fact');
  });
});
