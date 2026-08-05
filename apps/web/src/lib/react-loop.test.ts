import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { AgentTool, ToolContext } from '@/lib/agent-tools';
import type { LLMToolCompletionResult } from '@/lib/llm-provider';

const { completeWithTools } = vi.hoisted(() => ({ completeWithTools: vi.fn() }));

vi.mock('@/lib/llm-provider', () => ({
  llmCompleteWithTools: (...args: unknown[]) => completeWithTools(...args),
}));

import { runReactLoop } from './react-loop';

const ctx: ToolContext = { userId: 'u1', agent: 'tutor', locale: 'he' };

function textTurn(content = ''): LLMToolCompletionResult {
  return { content, toolCalls: [], model: 'llama-3.3-70b-versatile' };
}

function toolTurn(name: string, args: Record<string, unknown>, id = 'c1'): LLMToolCompletionResult {
  return {
    content: '',
    toolCalls: [{ id, type: 'function', function: { name, arguments: JSON.stringify(args) } }],
    model: 'llama-3.3-70b-versatile',
  };
}

function makeTool(name: string, impl: AgentTool['handler']): AgentTool {
  return {
    spec: {
      type: 'function',
      function: { name, description: `${name} tool`, parameters: { type: 'object', properties: {} } },
    },
    handler: impl,
  };
}

const base = {
  system: 'planner',
  memory: [] as Array<{ role: 'user' | 'assistant'; content: string }>,
  userMessage: 'מה זה גבול?',
  ctx,
};

beforeEach(() => completeWithTools.mockReset());
afterEach(() => vi.clearAllMocks());

describe('runReactLoop', () => {
  it('degrades with no tools', async () => {
    const res = await runReactLoop({ ...base, tools: [] });
    expect(res.degraded).toBe(true);
    expect(res.toolCallsMade).toBe(0);
    expect(completeWithTools).not.toHaveBeenCalled();
  });

  it('degrades when the first planner turn returns null (no tool-capable model)', async () => {
    completeWithTools.mockResolvedValueOnce(null);
    const tool = makeTool('retrieve', async () => ({ observation: 'x' }));
    const res = await runReactLoop({ ...base, tools: [tool] });
    expect(res.degraded).toBe(true);
    expect(res.observations).toBe('');
  });

  it('returns no observations when the model calls no tools', async () => {
    completeWithTools.mockResolvedValueOnce(textTurn('I can answer directly'));
    const tool = makeTool('retrieve', async () => ({ observation: 'x' }));
    const res = await runReactLoop({ ...base, tools: [tool] });
    expect(res.degraded).toBe(false);
    expect(res.observations).toBe('');
    expect(res.toolCallsMade).toBe(0);
  });

  it('executes a tool call and injects the observation + grounding', async () => {
    completeWithTools
      .mockResolvedValueOnce(toolTurn('retrieve', { query: 'גבול' }))
      .mockResolvedValueOnce(textTurn('done'));
    const handler = vi.fn(async () => ({
      observation: 'passage about limits',
      groundingIds: ['limit_of_function'],
    }));
    const tool = makeTool('retrieve', handler);
    const res = await runReactLoop({ ...base, tools: [tool] });
    expect(handler).toHaveBeenCalledTimes(1);
    expect(res.degraded).toBe(false);
    expect(res.toolCallsMade).toBe(1);
    expect(res.observations).toContain('passage about limits');
    expect(res.observations).toContain('### retrieve');
    expect(res.groundingIds).toContain('limit_of_function');
  });

  it('passes parsed arguments to the handler', async () => {
    completeWithTools
      .mockResolvedValueOnce(toolTurn('get_lesson', { concept_id: 'derivative' }))
      .mockResolvedValueOnce(textTurn());
    const handler = vi.fn(async () => ({ observation: 'lesson' }));
    await runReactLoop({ ...base, tools: [makeTool('get_lesson', handler)] });
    expect(handler).toHaveBeenCalledWith({ concept_id: 'derivative' }, ctx);
  });

  it('reports an unknown tool without throwing', async () => {
    completeWithTools
      .mockResolvedValueOnce(toolTurn('nope', {}))
      .mockResolvedValueOnce(textTurn());
    const res = await runReactLoop({ ...base, tools: [makeTool('retrieve', async () => ({ observation: 'x' }))] });
    expect(res.observations).toContain('Unknown tool');
    expect(res.degraded).toBe(false);
  });

  it('survives a throwing handler', async () => {
    completeWithTools
      .mockResolvedValueOnce(toolTurn('retrieve', {}))
      .mockResolvedValueOnce(textTurn());
    const tool = makeTool('retrieve', async () => {
      throw new Error('boom');
    });
    const res = await runReactLoop({ ...base, tools: [tool] });
    expect(res.observations).toContain('Tool failed');
    expect(res.degraded).toBe(false);
  });

  it('does not start a planner turn when the time budget is exhausted', async () => {
    const tool = makeTool('retrieve', async () => ({ observation: 'x' }));
    const res = await runReactLoop({ ...base, tools: [tool], budgetMs: 0 });
    expect(completeWithTools).not.toHaveBeenCalled();
    expect(res.degraded).toBe(true);
  });

  it('clamps the per-call timeout to the remaining budget', async () => {
    completeWithTools.mockResolvedValueOnce(textTurn());
    const tool = makeTool('retrieve', async () => ({ observation: 'x' }));
    await runReactLoop({
      ...base,
      tools: [tool],
      budgetMs: 3_000,
      perCallTimeoutMs: 8_000,
    });
    const passed = completeWithTools.mock.calls[0]?.[0] as { timeoutMs: number };
    expect(passed.timeoutMs).toBeLessThanOrEqual(3_000);
    expect(passed.timeoutMs).toBeGreaterThan(0);
  });

  it('respects the tool-call budget across iterations', async () => {
    // Always ask for one tool; loop must stop at maxToolCalls.
    completeWithTools.mockResolvedValue(toolTurn('retrieve', { query: 'q' }));
    const handler = vi.fn(async () => ({ observation: 'x' }));
    const res = await runReactLoop({
      ...base,
      tools: [makeTool('retrieve', handler)],
      maxToolCalls: 2,
      maxIterations: 5,
    });
    expect(res.toolCallsMade).toBeLessThanOrEqual(2);
    expect(handler.mock.calls.length).toBeLessThanOrEqual(2);
  });
});
