/**
 * Unit tests for consolidateLearnerMemory DB claim logic and cron worklist ordering.
 * All DB / LLM calls are mocked — no network required.
 *
 * Claim scenarios tested:
 *  - Claim succeeds (column null / expired)  → calls LLM and releases
 *  - Claim blocked (0 rows returned)         → returns ran:false immediately
 *  - Claim released on completion (success)  → release UPDATE fired in finally
 *  - Claim released on error                 → release UPDATE fired in finally
 *  - DB claim skipped on SQL error           → falls through to advisory lock only
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('server-only', () => ({}));

const { mockNeonSql, mockEnsureMemoryClaimColumns, mockGetLearnerPersona, mockPersistResult } =
  vi.hoisted(() => ({
    mockNeonSql: vi.fn(),
    mockEnsureMemoryClaimColumns: vi.fn().mockResolvedValue(undefined),
    mockGetLearnerPersona: vi.fn().mockResolvedValue({ text: 'current persona' }),
    mockPersistResult: vi.fn().mockResolvedValue({ ok: true }),
  }));

vi.mock('@neondatabase/serverless', () => {
  process.env['DATABASE_URL'] = 'postgresql://test-consolidate';
  return {
    neon: () => mockNeonSql,
    neonConfig: {},
  };
});

vi.mock('@/lib/neon-db', () => ({
  ensureMemoryClaimColumns: mockEnsureMemoryClaimColumns,
  getLearnerPersona: mockGetLearnerPersona,
  persistConsolidationResult: mockPersistResult,
}));

vi.mock('@/lib/llm-provider', () => ({
  llmCompleteJson: vi.fn().mockResolvedValue({
    json: {
      persona: 'new persona text',
      promoted_ids: [],
      notes: 'ok',
    },
    model: 'test-model',
  }),
}));

import { consolidateLearnerMemory, listLearnersWithLiveNotes } from './persona-consolidator';

let _counter = 0;
function freshLearner(): string {
  return `learner_consolidate_test_${++_counter}`;
}

/** Minimal live-notes rows to pass the MIN_NOTES_TO_CONSOLIDATE threshold (6). */
function liveNoteRows(count = 7) {
  return Array.from({ length: count }, (_, i) => ({
    id: `note-${i}`,
    learner_id: 'x',
    agent: 'tutor',
    kind: 'observation',
    content: `Note ${i}`,
    importance: 3,
    related_concept_id: null,
    source_turn_id: null,
    created_at: new Date().toISOString(),
    last_referenced_at: null,
  }));
}

// ---------------------------------------------------------------------------
// consolidateLearnerMemory — claim lifecycle
// ---------------------------------------------------------------------------
describe('consolidateLearnerMemory — DB claim lifecycle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockEnsureMemoryClaimColumns.mockResolvedValue(undefined);
    mockGetLearnerPersona.mockResolvedValue({ text: 'current persona' });
    mockPersistResult.mockResolvedValue({ ok: true });
  });

  it('calls ensureMemoryClaimColumns before the DB claim', async () => {
    const callOrder: string[] = [];
    mockEnsureMemoryClaimColumns.mockImplementation(async () => { callOrder.push('ensure'); });
    mockNeonSql
      .mockImplementationOnce(async () => { callOrder.push('claim'); return [{ learner_id: 'x' }]; }) // claim
      .mockResolvedValueOnce(liveNoteRows())   // fetchAllLiveNotes
      .mockResolvedValueOnce(undefined);       // release

    await consolidateLearnerMemory(freshLearner(), { force: true });

    expect(callOrder[0]).toBe('ensure');
    expect(callOrder[1]).toBe('claim');
  });

  it('returns ran:false with reason consolidation_in_progress when claim returns 0 rows', async () => {
    // 0 rows = another Vercel instance is consolidating this learner.
    mockNeonSql.mockResolvedValueOnce([]);

    const result = await consolidateLearnerMemory(freshLearner());

    expect(result.ran).toBe(false);
    expect(result.reason).toBe('consolidation_in_progress');
    // Only 1 SQL call — the claim attempt (no fetchAllLiveNotes, no release).
    expect(mockNeonSql).toHaveBeenCalledTimes(1);
  });

  it('releases the claim (consolidation_started_at = NULL) after successful run', async () => {
    mockNeonSql
      .mockResolvedValueOnce([{ learner_id: 'x' }]) // claim succeeds
      .mockResolvedValueOnce(liveNoteRows())          // fetchAllLiveNotes
      .mockResolvedValueOnce(undefined);              // release

    const result = await consolidateLearnerMemory(freshLearner(), { force: true });

    expect(result.ran).toBe(true);
    // Verify 3 SQL calls and the last is the NULL release.
    expect(mockNeonSql).toHaveBeenCalledTimes(3);
    const releaseStrings: string[] = mockNeonSql.mock.calls[2]![0] as string[];
    expect(releaseStrings.join('')).toMatch(/consolidation_started_at\s*=\s*NULL/i);
  });

  it('releases the claim even when the inner LLM call fails', async () => {
    const { llmCompleteJson } = await import('@/lib/llm-provider');
    vi.mocked(llmCompleteJson).mockRejectedValueOnce(new Error('LLM error'));

    mockNeonSql
      .mockResolvedValueOnce([{ learner_id: 'x' }]) // claim succeeds
      .mockResolvedValueOnce(liveNoteRows())          // fetchAllLiveNotes
      .mockResolvedValueOnce(undefined);              // release

    await expect(consolidateLearnerMemory(freshLearner(), { force: true })).rejects.toThrow(
      'LLM error',
    );

    expect(mockNeonSql).toHaveBeenCalledTimes(3);
    const releaseStrings: string[] = mockNeonSql.mock.calls[2]![0] as string[];
    expect(releaseStrings.join('')).toMatch(/consolidation_started_at\s*=\s*NULL/i);
  });

  it('falls back to in-memory guard when claim query throws (column race on first cold start)', async () => {
    mockNeonSql
      .mockRejectedValueOnce(new Error('column "consolidation_started_at" does not exist')) // claim fails
      .mockResolvedValueOnce(liveNoteRows()) // fetchAllLiveNotes
      .mockResolvedValueOnce(undefined);     // no release since dbClaimed=false

    const result = await consolidateLearnerMemory(freshLearner(), { force: true });

    // Should still run consolidation
    expect(result.ran).toBe(true);
    // 2 SQL calls: failed claim + live notes fetch (no release).
    expect(mockNeonSql).toHaveBeenCalledTimes(2);
  });

  it('the same-instance guard fires before DB claim for concurrent calls', async () => {
    const learnerId = freshLearner();

    // Start a "slow" first consolidation
    let resolveFirstClaim!: (v: unknown) => void;
    const firstClaimPromise = new Promise((res) => { resolveFirstClaim = res; });

    mockNeonSql
      .mockImplementationOnce(() => firstClaimPromise) // first claim hangs
      .mockResolvedValue(liveNoteRows());

    const firstCall = consolidateLearnerMemory(learnerId, { force: true });

    // While first is running, a second call for the same learner
    const secondResult = await consolidateLearnerMemory(learnerId, { force: true });

    // Second call blocked by in-memory Set before reaching DB
    expect(secondResult.ran).toBe(false);
    expect(secondResult.reason).toBe('consolidation_in_progress');

    // Resolve and clean up the hanging first call
    resolveFirstClaim([]);
    await firstCall.catch(() => {});
  });
});

// ---------------------------------------------------------------------------
// listLearnersWithLiveNotes — fair FIFO ordering
// ---------------------------------------------------------------------------
describe('listLearnersWithLiveNotes — ordering', () => {
  // Use resetAllMocks to also flush any leftover once-queues from prior tests.
  beforeEach(() => vi.resetAllMocks());

  it('returns learner IDs from the query result', async () => {
    mockNeonSql.mockResolvedValueOnce([{ learner_id: 'c' }, { learner_id: 'd' }]);

    const result = await listLearnersWithLiveNotes(3, 50);
    expect(result).toEqual(['c', 'd']);
  });

  it('issues GROUP BY + HAVING + ORDER BY MIN(created_at) ASC', async () => {
    mockNeonSql.mockResolvedValueOnce([]);
    await listLearnersWithLiveNotes(6, 100);

    const templateStrings: string[] = mockNeonSql.mock.calls[0]![0] as string[];
    const sqlText = templateStrings.join('$?');

    expect(sqlText).toMatch(/GROUP BY learner_id/i);
    expect(sqlText).toMatch(/HAVING COUNT\(\*\)\s*>=\s*\$\?/i);
    expect(sqlText).toMatch(/ORDER BY MIN\(created_at\) ASC/i);
  });
});
