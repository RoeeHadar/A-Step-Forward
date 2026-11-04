/** AS-43 (C4): affect TTL — kind=state valid_to default, read filter, state-only evidence. */
import { describe, expect, it, vi } from 'vitest';

vi.mock('server-only', () => ({}));
const byIds = vi.fn(async (_l: string, _ids: string[]) => [] as Array<{ id: string; kind: string; content: string }>);
const setSession = vi.fn(async () => undefined);
vi.mock('@/lib/neon-db', () => ({
  fetchAgentNotesByIds: (l: string, ids: string[]) => byIds(l, ids),
  fetchLessonByConceptId: async () => null,
  getCurrentPlan: async () => null,
  getLearnerProfile: async () => null,
  getPlanChangeSession: async () => null,
  setPlanChangeSession: () => setSession(),
}));

import { STATE_TTL_DAYS, defaultValidTo, dropExpiredFacts, encodeFactContent, isFactCurrent, isStateOnlyEvidence, keepCurrentFacts } from './typed-facts';
import { selectConsolidationNotes } from './persona-consolidator';
import { getPlanChangeTools } from './agent-tools';

const DAY = 86_400_000;
const T0 = new Date('2026-01-05T09:00:00Z');
const at = (d: number) => new Date(T0.getTime() + d * DAY);
const stateNote = (id = 's1') => ({
  id, learner_id: 'L', agent: 'coach', kind: 'state', importance: 3, related_concept_id: null, source_turn_id: null,
  last_referenced_at: null, created_at: T0,
  content: encodeFactContent('feels unmotivated', { key: 'mood', n: 1, valid_to: defaultValidTo('state', null, T0) }),
});

describe('AS-43 TTL (injected clock)', () => {
  it('kind=state defaults to now + 14 d; other kinds stay null; explicit wins', () => {
    expect(STATE_TTL_DAYS).toBe(14);
    expect(defaultValidTo('state', null, T0)).toBe(at(14).toISOString());
    expect(defaultValidTo('goal', null, T0)).toBeNull();
    expect(defaultValidTo('state', '2026-02-01T00:00:00.000Z', T0)).toBe('2026-02-01T00:00:00.000Z');
  });
  it('state fact current at day 13, absent at day 15 on every read helper', () => {
    const notes = [stateNote(), { ...stateNote('o1'), kind: 'observation', content: 'likes diagrams' }];
    expect(isFactCurrent({ key: 'mood', n: 1, valid_to: at(14).toISOString() }, at(13))).toBe(true);
    expect(dropExpiredFacts(notes, at(13)).map((n) => n.id)).toEqual(['s1', 'o1']);
    expect(dropExpiredFacts(notes, at(15)).map((n) => n.id)).toEqual(['o1']);
    expect(keepCurrentFacts(notes, at(15)).map((n) => n.id)).toEqual(['o1']);
    expect(selectConsolidationNotes(notes, at(15)).map((n) => n.id)).toEqual(['o1']);
    expect(isFactCurrent(null, at(999))).toBe(true);
  });
});

describe('AS-43 propose_plan_change rejects state-only evidence', () => {
  const tool = getPlanChangeTools().find((t) => t.spec.function.name === 'propose_plan_change')!;
  const ctx = { userId: 'L', agent: 'coach', locale: 'en' as const };
  it('isStateOnlyEvidence', () => {
    expect(isStateOnlyEvidence([{ kind: 'state' }])).toBe(true);
    expect(isStateOnlyEvidence([{ kind: 'state' }, { kind: 'goal' }])).toBe(false);
    expect(isStateOnlyEvidence([])).toBe(false);
  });
  it('mood-only evidence: rejected, nothing staged', async () => {
    byIds.mockResolvedValueOnce([{ id: 's1', kind: 'state', content: 'x' }]);
    setSession.mockClear();
    const r = await tool.handler({ goal: 'Bagrut 4 units', target_date: 'in 2 weeks', evidence_note_ids: ['s1'] }, ctx);
    expect(r.observation).toMatch(/^rejected_state_only_evidence/);
    expect(setSession).not.toHaveBeenCalled();
  });
  it('mixed evidence is not rejected by the state rule', async () => {
    byIds.mockResolvedValueOnce([{ id: 's1', kind: 'state', content: 'x' }, { id: 'g1', kind: 'goal', content: 'y' }]);
    const r = await tool.handler({ goal: 'Bagrut 4 units', target_date: 'in 2 weeks', evidence_note_ids: ['s1', 'g1'] }, ctx);
    expect(r.observation).not.toMatch(/^rejected_state_only_evidence/);
  });
});
