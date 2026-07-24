/**
 * Unit tests for the Tier-2 LLM classifier in concept-resolver.ts.
 *
 * The llm-provider module is mocked entirely — no network calls are made.
 * Covers: tier passthrough, guard skips, valid classifier hits, unknown-id
 * dropping, malformed JSON, and error / timeout paths.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

// Must be declared before any imports that transitively load llm-provider.
vi.mock('@/lib/llm-provider', () => ({
  llmComplete: vi.fn(),
  getLLMConfig: vi.fn(() => ({
    configured: true,
    cheapModels: ['llama-3.1-8b-instant'],
    primaryModels: ['llama-3.1-8b-instant'],
    baseUrl: 'https://api.groq.com/openai/v1',
    apiKey: 'test-key',
    providerLabel: 'groq',
  })),
  // Re-export any other symbols concept-resolver doesn't use, but keep the
  // mock complete so TypeScript callers in the module don't blow up.
  llmStream: vi.fn(),
  llmConfigured: vi.fn(() => true),
  resolveChatModelChain: vi.fn(() => ['llama-3.1-8b-instant']),
}));

import { llmComplete } from '@/lib/llm-provider';
import { resolveConceptsWithClassifier } from '../concept-resolver';

const mockLlmComplete = vi.mocked(llmComplete);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** A physics-topic message long enough to pass the length guard. */
const PHYSICS_MSG = 'why does the ball slow down when thrown upward?';

/** A math-topic message that bypasses tiers 0–1 but is a real question. */
const MATH_PARAPHRASE_MSG = 'how do you find the rate of change of a function at a point?';

// ---------------------------------------------------------------------------
// Tier passthrough (no LLM call when exact/alias hits)
// ---------------------------------------------------------------------------

describe('tier passthrough', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns exact tier and does NOT call LLM when exact match hits', async () => {
    const result = await resolveConceptsWithClassifier('explain Logarithms', []);
    expect(result.tier).toBe('exact');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });

  it('returns alias tier and does NOT call LLM when alias match hits', async () => {
    // "כלל השרשרת" resolves to derivatives_chain_rule via alias table
    const result = await resolveConceptsWithClassifier('איך משתמשים בכלל השרשרת?', []);
    expect(result.tier).toBe('alias');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// Guard: skip LLM for trivial / non-subject messages
// ---------------------------------------------------------------------------

describe('trivial-message guards', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('skips LLM for messages shorter than 12 chars', async () => {
    const result = await resolveConceptsWithClassifier('hi', []);
    expect(result.tier).toBe('none');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });

  it('skips LLM for EN greeting openers', async () => {
    const result = await resolveConceptsWithClassifier('hello, can you help me?', []);
    expect(result.tier).toBe('none');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });

  it('skips LLM for HE greeting opener "שלום"', async () => {
    const result = await resolveConceptsWithClassifier('שלום, אני רוצה לדעת', []);
    expect(result.tier).toBe('none');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });

  it('skips LLM for exam-date meta "מתי המבחן"', async () => {
    const result = await resolveConceptsWithClassifier('מתי המבחן הבא?', []);
    expect(result.tier).toBe('none');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });

  it('skips LLM for single-word yes/no reply', async () => {
    const result = await resolveConceptsWithClassifier('כן', []);
    expect(result.tier).toBe('none');
    expect(mockLlmComplete).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// Classifier: valid response mapped to concepts
// ---------------------------------------------------------------------------

describe('classifier hit', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns classifier tier with concepts when LLM returns valid ids', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["kinematics_1d"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('classifier');
    expect(result.concepts.map((c) => c.id)).toContain('kinematics_1d');
    expect(mockLlmComplete).toHaveBeenCalledOnce();
  });

  it('caps results at 3 even when LLM returns more ids', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["kinematics_1d", "projectile_motion", "forces_newtons_laws", "energy_conservation"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('classifier');
    expect(result.concepts.length).toBeLessThanOrEqual(3);
  });

  it('passes the subject filter correctly (physics message with physics subject)', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["kinematics_1d"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.concepts.every((c) => c.subject === 'physics')).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Classifier: invalid / unknown ids are dropped
// ---------------------------------------------------------------------------

describe('invalid id handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('drops ids that are not in the KG', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["kinematics_1d", "totally_fake_concept_xyz", "another_unknown_concept"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('classifier');
    expect(result.concepts.map((c) => c.id)).toEqual(['kinematics_1d']);
  });

  it('returns none when all returned ids are unknown', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["fake_concept_1", "fake_concept_2"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });

  it('drops ids whose subject does not match the filter', async () => {
    // kinematics_1d is physics, but subject=['math'] — should be dropped
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": ["kinematics_1d"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(MATH_PARAPHRASE_MSG, ['math']);
    // kinematics_1d is physics → filtered out → tier none
    expect(result.concepts.map((c) => c.id)).not.toContain('kinematics_1d');
    expect(result.tier).toBe('none');
  });

  it('returns none when ids field is empty array', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"ids": []}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// Classifier: error paths → tier 'none', never throws
// ---------------------------------------------------------------------------

describe('error / failure paths', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns none when LLM returns malformed JSON', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: 'not valid json {{{',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });

  it('returns none when LLM returns JSON without ids field', async () => {
    mockLlmComplete.mockResolvedValueOnce({
      content: '{"concepts": ["kinematics_1d"]}',
      model: 'llama-3.1-8b-instant',
    });

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('none');
  });

  it('returns none when llmComplete returns null', async () => {
    mockLlmComplete.mockResolvedValueOnce(null);

    const result = await resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });

  it('returns none when llmComplete throws (e.g. network error)', async () => {
    mockLlmComplete.mockRejectedValueOnce(new Error('network error'));

    await expect(
      resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']),
    ).resolves.toMatchObject({ tier: 'none', concepts: [] });
  });

  it('returns none (never throws) when Promise.race timeout fires', async () => {
    // Simulate a hung completion that never resolves within the race window
    mockLlmComplete.mockImplementationOnce(
      () => new Promise<never>(() => { /* intentionally never resolves */ }),
    );

    // The outer fence timeout fires at ~2000ms; use fake timers to avoid real wait
    vi.useFakeTimers();
    const pending = resolveConceptsWithClassifier(PHYSICS_MSG, ['physics']);
    // Advance time past the CLASSIFIER_TIMEOUT_MS (2000ms)
    vi.advanceTimersByTime(3000);
    const result = await pending;
    vi.useRealTimers();

    expect(result.tier).toBe('none');
    expect(result.concepts).toHaveLength(0);
  });
});
