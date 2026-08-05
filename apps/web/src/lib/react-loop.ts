/**
 * Bounded native tool-calling loop (ReAct) for learner chat (ADR-0015, Phase A).
 *
 * This is a tool-augmentation PRE-PASS: the model plans which tools to call, we
 * execute them server-side, and we hand the accumulated observations back to the
 * normal answer generator (which keeps the quality gate, hygiene, locale and
 * streaming intact). The loop never writes the learner-facing answer itself.
 *
 * Bounds (60s Vercel ceiling + no endless nagging):
 *   - total tool calls per turn: `maxToolCalls` (default 4)
 *   - planner turns: `maxIterations` (default 3)
 * Degrades cleanly (returns `degraded:true`, empty observations) when no
 * tool-capable model is available or the planner fails — the caller then falls
 * back to the static-grounding path.
 */
import 'server-only';
import {
  llmCompleteWithTools,
  type LLMFailureInfo,
  type LLMToolCall,
  type LLMToolMessage,
} from '@/lib/llm-provider';
import type { AgentTool, ToolContext } from '@/lib/agent-tools';
import { logger } from '@/lib/logger';

export interface ReactLoopResult {
  /** Formatted tool observations to inject; '' when no tools were used. */
  observations: string;
  /** Concept ids touched by tools this turn (for grounding / citations). */
  groundingIds: string[];
  toolCallsMade: number;
  /** True when the loop could not run (no tool model / planner failure). */
  degraded: boolean;
}

const DEFAULT_MAX_TOOL_CALLS = 4;
const DEFAULT_MAX_ITERATIONS = 3;

function parseArgs(raw: string): Record<string, unknown> {
  try {
    const parsed = JSON.parse(raw || '{}');
    return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

const DEFAULT_BUDGET_MS = 18_000;
const DEFAULT_PER_CALL_TIMEOUT_MS = 8_000;
/** Stop starting new planner turns once less than this remains in the budget. */
const MIN_TURN_BUDGET_MS = 1_500;

export async function runReactLoop(opts: {
  system: string;
  memory: Array<{ role: 'user' | 'assistant'; content: string }>;
  userMessage: string;
  tools: AgentTool[];
  ctx: ToolContext;
  maxToolCalls?: number;
  maxIterations?: number;
  /** Overall wall-clock budget for the whole loop (default 18s). */
  budgetMs?: number;
  /** Per planner-call timeout ceiling (default 8s), clamped to remaining budget. */
  perCallTimeoutMs?: number;
  failureSink?: { current: LLMFailureInfo | null };
}): Promise<ReactLoopResult> {
  const empty: ReactLoopResult = {
    observations: '',
    groundingIds: [],
    toolCallsMade: 0,
    degraded: true,
  };
  if (opts.tools.length === 0) return empty;

  const maxToolCalls = opts.maxToolCalls ?? DEFAULT_MAX_TOOL_CALLS;
  const maxIterations = opts.maxIterations ?? DEFAULT_MAX_ITERATIONS;
  const budgetMs = opts.budgetMs ?? DEFAULT_BUDGET_MS;
  const perCallTimeoutMs = opts.perCallTimeoutMs ?? DEFAULT_PER_CALL_TIMEOUT_MS;
  const deadline = Date.now() + budgetMs;
  const toolSpecs = opts.tools.map((t) => t.spec);
  const byName = new Map(opts.tools.map((t) => [t.spec.function.name, t]));

  const messages: LLMToolMessage[] = [
    ...opts.memory.map((m) => ({ role: m.role, content: m.content })),
    { role: 'user' as const, content: opts.userMessage },
  ];

  const observations: string[] = [];
  const groundingIds = new Set<string>();
  let toolCallsMade = 0;
  let anyPlannerSuccess = false;

  for (let iter = 0; iter < maxIterations; iter++) {
    const remaining = maxToolCalls - toolCallsMade;
    if (remaining <= 0) break;
    // Never let planner turns eat into the answer generator's slice of the 60s
    // route budget: stop starting turns once the shared deadline is close.
    const timeLeft = deadline - Date.now();
    if (timeLeft < MIN_TURN_BUDGET_MS) break;

    const result = await llmCompleteWithTools({
      system: opts.system,
      messages,
      tools: toolSpecs,
      toolChoice: 'auto',
      maxTokens: 512,
      temperature: 0.2,
      timeoutMs: Math.min(perCallTimeoutMs, timeLeft),
      failureSink: opts.failureSink,
    });

    // First planner turn failing → degrade. A later turn failing → keep what we
    // already gathered (don't discard successful observations).
    if (!result) {
      if (!anyPlannerSuccess) return empty;
      break;
    }
    anyPlannerSuccess = true;

    const calls = result.toolCalls.slice(0, remaining);
    if (calls.length === 0) break; // model has what it needs; no more tools

    // Record the assistant tool-call turn so the tool results have a parent.
    messages.push({ role: 'assistant', content: result.content ?? '', tool_calls: calls });

    for (const call of calls) {
      const tool = byName.get(call.function.name);
      toolCallsMade++;
      let observation: string;
      if (!tool) {
        observation = `Unknown tool "${call.function.name}".`;
      } else {
        try {
          const res = await tool.handler(parseArgs(call.function.arguments), opts.ctx);
          observation = res.observation;
          for (const id of res.groundingIds ?? []) groundingIds.add(id);
        } catch (err) {
          logger.warn('react: tool handler threw', {
            tool: call.function.name,
            err: String(err),
          });
          observation = 'Tool failed.';
        }
      }
      observations.push(`### ${call.function.name}\n${observation}`);
      messages.push({
        role: 'tool',
        content: observation,
        tool_call_id: call.id,
        name: call.function.name,
      });
    }
  }

  if (observations.length === 0) {
    // A planner turn that deliberately chose no tools is NOT degraded (the model
    // answered directly); never running a turn (budget exhausted, no tool model)
    // is degraded so the caller falls back to static grounding.
    return {
      observations: '',
      groundingIds: [...groundingIds],
      toolCallsMade,
      degraded: !anyPlannerSuccess,
    };
  }

  return {
    observations: observations.join('\n\n'),
    groundingIds: [...groundingIds],
    toolCallsMade,
    degraded: false,
  };
}

export type { LLMToolCall };
