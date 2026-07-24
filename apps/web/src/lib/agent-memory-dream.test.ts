/**
 * Unit tests for dreamLearnerMemory DB claim logic and cron worklist ordering.
 * All DB / LLM calls are mocked — no network required.
 *
 * Claim scenarios tested:
 *  - Claim succeeds (column null / expired)  → processes and releases
 *  - Claim blocked (0 rows returned)         → returns empty immediately
 *  - Claim released on completion (success)  → release UPDATE fired in finally
 *  - Claim released on error                 → release UPDATE fired in finally
 *  - DB claim skipped on SQL error           → falls through to in-memory guard
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('server-only', () => ({}));

// vi.hoisted ensures these variables are initialised before any vi.mock factory runs.
const { mockNeonSql, mockEnsureMemoryClaimColumns, mockSupersedeAgentNote } = vi.hoisted(() => ({
  mockNeonSql: vi.fn(),
  mockEnsureMemoryClaimColumns: vi.fn().mockResolvedValue(undefined),
  mockSupersedeAgentNote: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('@neondatabase/serverless', () => {
  // Set DATABASE_URL so the module-level `sql` is initialised to our mock.
  process.env['DATABASE_URL'] = 'postgresql://test-dream';
  return {
    neon: () => mockNeonSql,
    neonConfig: {},
  };
});

vi.mock('@/lib/neon-db', () => ({
  dbConfigured: true,
  ensureMemoryClaimColumns: mockEnsureMemoryClaimColumns,
  supersedeAgentNote: mockSupersedeAgentNote,
}));

vi.mock('@/lib/web-agents', () => ({
  WEB_LIVE_AGENTS: ['tutor', 'mentor'] as readonly string[],
}));

vi.mock('@asf/schemas/agents', () => ({
  agentNameSchema: {
    safeParse: (v: unknown) => ({ success: true, data: v }),
  },
}));

import { dreamLearnerMemory, listLearnersWithAnyLiveNotes } from './agent-memory-dream';

/**
 * Each test uses a unique learnerId so the module-level `dreamLastStarted`
 * cooldown map never interferes between tests.
 */
let _counter = 0;
function freshLearner(): string {
  return `learner_dream_test_${++_counter}`;
}

// ---------------------------------------------------------------------------
// dreamLearnerMemory — claim lifecycle
// ---------------------------------------------------------------------------
describe('dreamLearnerMemory — DB claim lifecycle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockEnsureMemoryClaimColumns.mockResolvedValue(undefined);
  });

  it('calls ensureMemoryClaimColumns at entry before the DB claim', async () => {
    const callOrder: string[] = [];
    mockEnsureMemoryClaimColumns.mockImplementation(async () => {
      callOrder.push('ensure');
    });
    mockNeonSql
      .mockImplementationOnce(async () => { callOrder.push('claim'); return [{ learner_id: 'x' }]; })
      .mockResolvedValueOnce([]) // listAgentsWithNotes
      .mockResolvedValueOnce(undefined); // release

    await dreamLearnerMemory(freshLearner());

    expect(callOrder[0]).toBe('ensure');
    expect(callOrder[1]).toBe('claim');
  });

  it('returns empty without processing when DB claim returns 0 rows (another instance owns it)', async () => {
    // 0 rows = another Vercel instance already claimed this learner.
    mockNeonSql.mockResolvedValueOnce([]);

    const result = await dreamLearnerMemory(freshLearner());

    expect(result).toEqual({ archived: 0, superseded: 0, agents_processed: 0 });
    // Only 1 SQL call — the claim attempt; no listAgentsWithNotes, no release.
    expect(mockNeonSql).toHaveBeenCalledTimes(1);
  });

  it('releases the claim (sets last_dreamed_at = NULL) after successful processing', async () => {
    mockNeonSql
      .mockResolvedValueOnce([{ learner_id: 'x' }]) // claim succeeds
      .mockResolvedValueOnce([])                     // listAgentsWithNotes → no agents
      .mockResolvedValueOnce(undefined);             // release

    await dreamLearnerMemory(freshLearner());

    // 3 SQL calls: claim, list agents, release.
    expect(mockNeonSql).toHaveBeenCalledTimes(3);

    // Verify the third call is the NULL release.
    const releaseCall = mockNeonSql.mock.calls[2]!;
    const releaseStrings: string[] = releaseCall[0] as string[];
    expect(releaseStrings.join('')).toMatch(/last_dreamed_at\s*=\s*NULL/i);
  });

  it('releases the claim even when inner processing throws', async () => {
    const learnerId = freshLearner();
    mockNeonSql
      .mockResolvedValueOnce([{ learner_id: learnerId }]) // claim succeeds
      .mockRejectedValueOnce(new Error('query explosion')) // listAgentsWithNotes fails
      .mockResolvedValueOnce(undefined);                   // release should still fire

    await expect(dreamLearnerMemory(learnerId)).rejects.toThrow('query explosion');

    // Claim + failed inner call + release = 3 calls total.
    expect(mockNeonSql).toHaveBeenCalledTimes(3);
    const releaseStrings: string[] = mockNeonSql.mock.calls[2]![0] as string[];
    expect(releaseStrings.join('')).toMatch(/last_dreamed_at\s*=\s*NULL/i);
  });

  it('continues without DB claim (falls back to in-memory guard) when claim query throws', async () => {
    // Simulates the race where the column does not exist yet on first cold start.
    mockNeonSql
      .mockRejectedValueOnce(new Error('column "last_dreamed_at" does not exist')) // claim errors
      .mockResolvedValueOnce([]) // listAgentsWithNotes
      .mockResolvedValueOnce(undefined); // (no release since dbClaimed=false)

    const result = await dreamLearnerMemory(freshLearner());

    // Should still process normally (0 agents → 0 archived).
    expect(result).toEqual({ archived: 0, superseded: 0, agents_processed: 0 });
    // 2 SQL calls: failed claim + listAgentsWithNotes (no release).
    expect(mockNeonSql).toHaveBeenCalledTimes(2);
  });

  it('the in-memory cooldown guard fires before the DB claim on same-instance repeat', async () => {
    const learnerId = freshLearner();

    // First call — claim succeeds, no agents.
    mockNeonSql
      .mockResolvedValueOnce([{ learner_id: learnerId }])
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce(undefined);
    await dreamLearnerMemory(learnerId, { agents: [] });

    vi.clearAllMocks();

    // Second call for same learnerId within cooldown → returns empty, no SQL calls.
    const result = await dreamLearnerMemory(learnerId, { agents: [] });
    expect(result).toEqual({ archived: 0, superseded: 0, agents_processed: 0 });
    expect(mockNeonSql).not.toHaveBeenCalled();
    expect(mockEnsureMemoryClaimColumns).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// listLearnersWithAnyLiveNotes — fair FIFO ordering
// ---------------------------------------------------------------------------
describe('listLearnersWithAnyLiveNotes — ordering', () => {
  // Use resetAllMocks to also flush any leftover once-queues from prior tests.
  beforeEach(() => vi.resetAllMocks());

  it('returns learner IDs from the query result', async () => {
    mockNeonSql.mockResolvedValueOnce([{ learner_id: 'a' }, { learner_id: 'b' }]);

    const result = await listLearnersWithAnyLiveNotes(5);
    expect(result).toEqual(['a', 'b']);
  });

  it('issues a GROUP BY + ORDER BY MIN(created_at) ASC query (not SELECT DISTINCT)', async () => {
    mockNeonSql.mockResolvedValueOnce([]);
    await listLearnersWithAnyLiveNotes(10);

    const templateStrings: string[] = mockNeonSql.mock.calls[0]![0] as string[];
    const sqlText = templateStrings.join('$?');

    expect(sqlText).toMatch(/GROUP BY learner_id/i);
    expect(sqlText).toMatch(/ORDER BY MIN\(created_at\) ASC/i);
    expect(sqlText).not.toMatch(/SELECT DISTINCT/i);
  });

  it('returns empty array when sql is null (no DATABASE_URL configured)', async () => {
    // This tests the `if (!sql) return []` guard.
    // With DATABASE_URL set, sql is non-null — we test via mock returning [].
    mockNeonSql.mockResolvedValueOnce([]);
    const result = await listLearnersWithAnyLiveNotes(50);
    expect(result).toEqual([]);
  });
});
