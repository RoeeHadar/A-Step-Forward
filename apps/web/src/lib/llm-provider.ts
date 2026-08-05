/**
 * Unified OpenAI-compatible LLM provider for the Vercel web runtime.
 *
 * Supports Groq, Ollama, vLLM, Together, Fireworks, OpenRouter, etc. via:
 *   LLM_BASE_URL + LLM_API_KEY + LLM_PRIMARY_MODEL (+ optional LLM_CHEAP_MODEL)
 *
 * Backward compatible with GROQ_API_KEY / GROQ_BASE_URL.
 */
import 'server-only';
import { logger } from '@/lib/logger';

export type LLMFailureKind =
  | 'not_configured'
  | 'auth_failure'
  | 'rate_limited'
  | 'timeout'
  | 'context_too_large'
  | 'provider_error'
  | 'empty_response'
  | 'network_error'
  | 'stream_interrupted'
  | 'unknown';

export interface LLMFailureInfo {
  kind: LLMFailureKind;
  status?: number;
  provider?: string;
  model?: string;
}

export type LLMModelTier = 'primary' | 'cheap' | 'all';

export interface LLMProviderConfig {
  configured: boolean;
  baseUrl: string;
  apiKey: string;
  primaryModels: string[];
  cheapModels: string[];
  providerLabel: string;
}

/**
 * A concrete chat provider (base URL + key + the models it serves). The primary
 * comes from LLM_/GROQ_ env; optional secondaries (e.g. NVIDIA NIM) are appended
 * as quality fallbacks. The chat model chain spans providers; each model is
 * routed to the provider that lists it.
 */
export interface ChatProvider {
  label: string;
  baseUrl: string;
  apiKey: string;
  models: string[];
}

export interface LLMChatMessage {
  role: 'system' | 'user' | 'assistant' | string;
  content: string;
}

export interface LLMCompletionOptions {
  /** Prepended as the first system message when set. */
  system?: string;
  messages: LLMChatMessage[];
  maxTokens?: number;
  temperature?: number;
  /** Nucleus sampling. Omitted from the request body when undefined. */
  topP?: number;
  jsonMode?: boolean;
  timeoutMs?: number;
  modelTier?: LLMModelTier;
  /** Override the model chain entirely. */
  models?: string[];
  /** Updated when an attempt fails (keeps the most specific failure). */
  failureSink?: { current: LLMFailureInfo | null };
  /** Last stream finish_reason when known (e.g. stop | length). */
  finishSink?: { current: string | null };
}

export interface LLMCompletionResult {
  content: string;
  model: string;
}

const DEFAULT_GROQ_BASE = 'https://api.groq.com/openai/v1';
/**
 * Quality-first learner chat default (ADR-0015).
 * Cheap 8B remains available for classifiers / background via `resolveModelChain('cheap')`.
 */
const DEFAULT_PRIMARY = 'llama-3.3-70b-versatile';
const DEFAULT_CHEAP = 'llama-3.1-8b-instant';
/** Extra quality models when primary fails (auth/rate/empty). */
const DEFAULT_EXTRA_PRIMARY = [
  'openai/gpt-oss-120b',
  'qwen/qwen3.6-27b',
  'llama-3.1-8b-instant',
];

function trimSlash(url: string): string {
  return url.replace(/\/+$/, '');
}

/** Strip accidental surrounding quotes from env values. */
function unquoteEnv(raw: string | undefined): string {
  const v = (raw ?? '').trim();
  if (
    (v.startsWith('"') && v.endsWith('"')) ||
    (v.startsWith("'") && v.endsWith("'"))
  ) {
    return v.slice(1, -1).trim();
  }
  return v;
}

function parseModelList(raw: string | undefined, fallback: string[]): string[] {
  if (!raw?.trim()) return fallback;
  const parts = unquoteEnv(raw)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.length ? parts : fallback;
}

function detectProviderLabel(baseUrl: string): string {
  const lower = baseUrl.toLowerCase();
  if (lower.includes('groq.com')) return 'groq';
  if (lower.includes('11434') || lower.includes('ollama')) return 'ollama';
  if (lower.includes('openrouter')) return 'openrouter';
  if (lower.includes('together')) return 'together';
  if (lower.includes('fireworks')) return 'fireworks';
  if (lower.includes('localhost') || lower.includes('127.0.0.1')) return 'local';
  return 'openai-compatible';
}

/** Resolve runtime LLM configuration from env (cached per process). */
let cachedConfig: LLMProviderConfig | null = null;
let cachedProviders: ChatProvider[] | null = null;

export function getLLMConfig(): LLMProviderConfig {
  if (cachedConfig) return cachedConfig;

  const baseUrl = trimSlash(
    unquoteEnv(process.env.LLM_BASE_URL) ||
      unquoteEnv(process.env.GROQ_BASE_URL) ||
      DEFAULT_GROQ_BASE,
  );

  const apiKey =
    unquoteEnv(process.env.LLM_API_KEY) ||
    unquoteEnv(process.env.GROQ_API_KEY) ||
    (detectProviderLabel(baseUrl) === 'ollama' ? 'ollama' : '');

  const primaryModels = parseModelList(process.env.LLM_PRIMARY_MODEL, [DEFAULT_PRIMARY]);
  const cheapModels = parseModelList(process.env.LLM_CHEAP_MODEL, [DEFAULT_CHEAP]);
  const fallbackModels = parseModelList(process.env.LLM_FALLBACK_MODELS, DEFAULT_EXTRA_PRIMARY);

  const allPrimary = [...new Set([...primaryModels, ...fallbackModels])];
  const configured = Boolean(apiKey) || detectProviderLabel(baseUrl) === 'ollama';

  cachedConfig = {
    configured,
    baseUrl,
    apiKey: apiKey || 'ollama',
    primaryModels: allPrimary,
    cheapModels,
    providerLabel: process.env.LLM_PROVIDER?.trim() || detectProviderLabel(baseUrl),
  };
  return cachedConfig;
}

/** Clear config cache (tests). */
export function resetLLMConfigCache(): void {
  cachedConfig = null;
  cachedProviders = null;
}

export function llmConfigured(): boolean {
  return getLLMConfig().configured;
}

/**
 * Ordered chat providers: primary (Groq / LLM_*) first, then optional
 * secondaries (NVIDIA NIM) as quality fallbacks. Cached per process.
 */
export function getChatProviders(): ChatProvider[] {
  if (cachedProviders) return cachedProviders;
  const primary = getLLMConfig();
  const providers: ChatProvider[] = [
    {
      label: primary.providerLabel,
      baseUrl: primary.baseUrl,
      apiKey: primary.apiKey,
      models: [...new Set([...primary.primaryModels, ...primary.cheapModels])],
    },
  ];

  const nvidiaKey = unquoteEnv(process.env.NVIDIA_API_KEY);
  const nvidiaModels = parseModelList(process.env.NVIDIA_FALLBACK_MODELS, []);
  if (nvidiaKey && nvidiaModels.length) {
    providers.push({
      label: 'nvidia',
      baseUrl: trimSlash(
        unquoteEnv(process.env.NVIDIA_BASE_URL) || 'https://integrate.api.nvidia.com/v1',
      ),
      apiKey: nvidiaKey,
      models: nvidiaModels,
    });
  }

  cachedProviders = providers;
  return providers;
}

/** Resolve which provider serves a model; defaults to the primary provider. */
export function resolveProviderForModel(model: string): ChatProvider {
  const providers = getChatProviders();
  for (const p of providers) {
    if (p.models.includes(model)) return p;
  }
  return providers[0]!;
}

/**
 * Reasoning models (DeepSeek-R1, QwQ, o1/o3, *-thinking) misbehave at low
 * temperature (repetition/incoherence). Vendors recommend ~0.6 / top_p 0.95.
 */
export function isReasoningModel(model: string): boolean {
  return /deepseek-?r1|deepseek.*reason|qwq|-thinking|(?:^|\/)o1|(?:^|\/)o3/i.test(model);
}

/**
 * Per-model sampling body, applying the reasoning-model clamp. Exported for
 * tests; callers should not need it directly.
 */
export function resolveSamplingBody(
  model: string,
  opts: LLMCompletionOptions,
): Record<string, number> {
  if (isReasoningModel(model)) {
    return { temperature: 0.6, top_p: 0.95 };
  }
  const out: Record<string, number> = { temperature: opts.temperature ?? 0.4 };
  if (opts.topP != null) out.top_p = opts.topP;
  return out;
}

export function resolveModelChain(tier: LLMModelTier = 'primary'): string[] {
  const cfg = getLLMConfig();
  if (tier === 'cheap') return [...cfg.cheapModels, ...cfg.primaryModels];
  if (tier === 'all') return [...new Set([...cfg.primaryModels, ...cfg.cheapModels])];
  return [...cfg.primaryModels, ...cfg.cheapModels];
}

/**
 * Learner-facing chat model chain (ADR-0015).
 *
 * Default: quality primary + fallbacks (`resolveModelChain('primary')`).
 * Escape hatch for free-tier emergencies:
 *   `CHAT_MODEL_POLICY=cheap` → single cheap model only (legacy behavior).
 */
export function resolveChatModelChain(): string[] {
  const policy = (process.env.CHAT_MODEL_POLICY ?? 'quality').trim().toLowerCase();
  if (policy === 'cheap' || policy === 'volume') {
    const cfg = getLLMConfig();
    const model = cfg.cheapModels[0] ?? cfg.primaryModels[0] ?? DEFAULT_CHEAP;
    return [model];
  }
  const primaryChain = resolveModelChain('primary');
  const secondary = getChatProviders()
    .slice(1)
    .flatMap((p) => p.models);
  return [...new Set([...primaryChain, ...secondary])];
}

/** Classifier / background tasks — keep on the cheap tier. */
export function resolveClassifierModelChain(): string[] {
  return resolveModelChain('cheap');
}

const MAX_FETCH_RETRIES = 2;

const FAILURE_PRIORITY: Record<LLMFailureKind, number> = {
  auth_failure: 100,
  not_configured: 90,
  context_too_large: 80,
  rate_limited: 70,
  timeout: 60,
  network_error: 50,
  provider_error: 40,
  stream_interrupted: 35,
  empty_response: 30,
  unknown: 0,
};

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Per-process token bucket. Protects rate-limited providers (NVIDIA NIM free
 * tier is ~40 RPM) from being overrun. Serverless instances are independent, so
 * this is an in-instance throttle layered on top of 429 backoff — not a global
 * quota. Per-user abuse limiting is enforced separately (Neon-backed).
 */
class TokenBucket {
  private tokens: number;
  private last: number;
  constructor(
    private readonly capacity: number,
    private readonly refillPerSec: number,
  ) {
    this.tokens = capacity;
    this.last = Date.now();
  }

  async acquire(maxWaitMs = 5_000): Promise<void> {
    const deadline = Date.now() + maxWaitMs;
    for (;;) {
      const now = Date.now();
      this.tokens = Math.min(
        this.capacity,
        this.tokens + ((now - this.last) / 1000) * this.refillPerSec,
      );
      this.last = now;
      if (this.tokens >= 1) {
        this.tokens -= 1;
        return;
      }
      if (now >= deadline) return; // fail-open; 429 backoff is the backstop
      const waitMs = Math.ceil(((1 - this.tokens) / this.refillPerSec) * 1000);
      await sleep(Math.min(waitMs, deadline - now));
    }
  }
}

/**
 * Small burst (5) + ~30 tokens/min refill keeps worst-case first-minute
 * throughput (~35) safely under NVIDIA NIM's ~40 RPM free-tier ceiling, while
 * still absorbing short bursts. 429 backoff is the backstop above this.
 */
const providerBuckets: Record<string, TokenBucket> = {
  nvidia: new TokenBucket(5, 30 / 60),
};

export function classifyHttpStatus(status: number, provider?: string, model?: string): LLMFailureInfo {
  if (status === 401 || status === 403) {
    return { kind: 'auth_failure', status, provider, model };
  }
  if (status === 429) {
    return { kind: 'rate_limited', status, provider, model };
  }
  if (status === 413) {
    return { kind: 'context_too_large', status, provider, model };
  }
  if (status >= 500 || status >= 400) {
    return { kind: 'provider_error', status, provider, model };
  }
  return { kind: 'unknown', status, provider, model };
}

export function classifyFetchError(err: unknown, provider?: string, model?: string): LLMFailureInfo {
  const msg = String(err);
  if (/abort/i.test(msg) || (err instanceof Error && err.name === 'AbortError')) {
    return { kind: 'timeout', provider, model };
  }
  if (/ENOTFOUND|ECONNREFUSED|ECONNRESET|ETIMEDOUT|network|fetch failed/i.test(msg)) {
    return { kind: 'network_error', provider, model };
  }
  return { kind: 'unknown', provider, model };
}

function recordFailure(
  sink: LLMCompletionOptions['failureSink'],
  next: LLMFailureInfo,
): void {
  if (!sink) return;
  const prev = sink.current;
  if (!prev || FAILURE_PRIORITY[next.kind] >= FAILURE_PRIORITY[prev.kind]) {
    sink.current = next;
  }
}

interface FetchProvider {
  label: string;
  baseUrl: string;
  apiKey: string;
}

async function fetchCompletions(
  provider: FetchProvider,
  body: Record<string, unknown>,
  timeoutMs: number,
): Promise<Response> {
  const bucket = providerBuckets[provider.label];
  let lastError: unknown;
  for (let attempt = 0; attempt <= MAX_FETCH_RETRIES; attempt++) {
    if (bucket) await bucket.acquire();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const resp = await fetch(completionsUrl(provider.baseUrl), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${provider.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (resp.status === 429 && attempt < MAX_FETCH_RETRIES) {
        const retryAfterSec = Number(resp.headers.get('retry-after') ?? 1);
        const waitMs = Math.min(Math.max(retryAfterSec, 1), 8) * 1000;
        logger.warn('llm: rate limited, retrying', {
          attempt: attempt + 1,
          waitMs,
          model: body.model,
          provider: provider.label,
        });
        await sleep(waitMs);
        continue;
      }

      if (!resp.ok) {
        const errBody = await resp.text().catch(() => '');
        logger.warn('llm: request non-ok', {
          status: resp.status,
          model: body.model,
          provider: provider.label,
          body: errBody.slice(0, 300),
        });
      }
      return resp;
    } catch (err) {
      clearTimeout(timeoutId);
      lastError = err;
      if (attempt < MAX_FETCH_RETRIES) {
        await sleep(500 * (attempt + 1));
        continue;
      }
      logger.warn('llm: fetch failed after retries', {
        model: body.model,
        err: String(err),
      });
      throw err;
    }
  }
  throw lastError ?? new Error('llm: fetch exhausted retries');
}

function buildMessages(opts: LLMCompletionOptions): LLMChatMessage[] {
  const out: LLMChatMessage[] = [];
  if (opts.system?.trim()) {
    out.push({ role: 'system', content: opts.system.trim() });
  }
  for (const m of opts.messages) {
    if (m.content?.trim()) out.push({ role: m.role, content: m.content });
  }
  return out;
}

function completionsUrl(baseUrl: string): string {
  return `${trimSlash(baseUrl)}/chat/completions`;
}

/**
 * Non-streaming chat completion. Tries models in order; returns null if all fail.
 */
export async function llmComplete(
  opts: LLMCompletionOptions,
): Promise<LLMCompletionResult | null> {
  const cfg = getLLMConfig();
  if (!cfg.configured) {
    logger.warn('llm: not configured — set LLM_API_KEY or LLM_BASE_URL (Ollama)');
    return null;
  }

  const models = opts.models ?? resolveModelChain(opts.modelTier ?? 'primary');
  const messages = buildMessages(opts);
  const timeoutMs = opts.timeoutMs ?? 45_000;

  for (const model of models) {
    const provider = resolveProviderForModel(model);
    try {
      const body: Record<string, unknown> = {
        model,
        messages,
        max_tokens: opts.maxTokens ?? 2048,
        ...resolveSamplingBody(model, opts),
      };
      if (opts.jsonMode) {
        body.response_format = { type: 'json_object' };
      }

      const resp = await fetchCompletions(provider, body, timeoutMs);

      if (!resp.ok) {
        recordFailure(
          opts.failureSink,
          classifyHttpStatus(resp.status, provider.label, model),
        );
        // Auth failure on one provider must not block a different provider's
        // models later in the chain — skip to the next model instead of aborting.
        continue;
      }

      const json = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const content = json.choices?.[0]?.message?.content;
      if (content?.trim()) {
        return { content, model };
      }
      recordFailure(opts.failureSink, {
        kind: 'empty_response',
        provider: provider.label,
        model,
      });
    } catch (err) {
      recordFailure(
        opts.failureSink,
        classifyFetchError(err, provider.label, model),
      );
      logger.warn('llm: completion attempt failed', { model, err: String(err) });
    }
  }
  return null;
}

/**
 * Streaming chat completion (SSE). Yields text tokens; tries models in order.
 */
export async function* llmStream(
  opts: LLMCompletionOptions,
): AsyncGenerator<string> {
  const cfg = getLLMConfig();
  if (!cfg.configured) {
    logger.warn('llm: stream skipped — not configured');
    return;
  }

  const models = opts.models ?? resolveModelChain(opts.modelTier ?? 'primary');
  const messages = buildMessages(opts);
  const timeoutMs = opts.timeoutMs ?? 45_000;

  for (const model of models) {
    const provider = resolveProviderForModel(model);
    let emitted = false;
    try {
      const resp = await fetchCompletions(
        provider,
        {
          model,
          messages,
          max_tokens: opts.maxTokens ?? 1024,
          ...resolveSamplingBody(model, opts),
          stream: true,
        },
        timeoutMs,
      );

      if (!resp.ok || !resp.body) {
        recordFailure(
          opts.failureSink,
          classifyHttpStatus(resp.status, provider.label, model),
        );
        // Skip to the next model/provider on failure (incl. auth) so a bad
        // primary key still lets NVIDIA fallbacks run.
        continue;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6).trim();
          if (data === '[DONE]') break;
          try {
            const parsed = JSON.parse(data) as {
              choices?: Array<{
                delta?: { content?: string };
                finish_reason?: string | null;
              }>;
            };
            const choice = parsed.choices?.[0];
            const reason = choice?.finish_reason;
            if (reason && opts.finishSink) {
              opts.finishSink.current = reason;
            }
            const token = choice?.delta?.content;
            if (token) {
              emitted = true;
              yield token;
            }
          } catch {
            // ignore malformed SSE chunks
          }
        }
      }
      if (emitted) return;
      recordFailure(opts.failureSink, {
        kind: 'empty_response',
        provider: provider.label,
        model,
      });
    } catch (err) {
      recordFailure(
        opts.failureSink,
        classifyFetchError(err, provider.label, model),
      );
      logger.warn('llm: stream attempt failed', { model, err: String(err) });
    }
  }
}

// ---------------------------------------------------------------------------
// Native tool-calling (ReAct loop primitive)
// ---------------------------------------------------------------------------

/** OpenAI-style function tool advertised to the model. */
export interface LLMTool {
  type: 'function';
  function: {
    name: string;
    description: string;
    /** JSON Schema for the arguments object. */
    parameters: Record<string, unknown>;
  };
}

/** A tool call the model emitted (arguments is a raw JSON string). */
export interface LLMToolCall {
  id: string;
  type: 'function';
  function: { name: string; arguments: string };
}

/**
 * Message shape for the tool loop. Extends the plain chat message with the
 * OpenAI tool fields: an assistant turn may carry `tool_calls`, and a `tool`
 * turn carries the matching `tool_call_id` + result `content`.
 */
export interface LLMToolMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: LLMToolCall[];
  tool_call_id?: string;
  name?: string;
}

export interface LLMToolCompletionOptions {
  system?: string;
  messages: LLMToolMessage[];
  tools: LLMTool[];
  /** 'auto' (default) lets the model decide; 'none' forces a text answer. */
  toolChoice?: 'auto' | 'none' | 'required';
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  timeoutMs?: number;
  models?: string[];
  failureSink?: { current: LLMFailureInfo | null };
}

export interface LLMToolCompletionResult {
  content: string;
  toolCalls: LLMToolCall[];
  model: string;
  finishReason?: string;
}

/**
 * Models we trust to honor OpenAI-style `tools` / `tool_calls`. Groq's 70B and
 * gpt-oss/qwen3 lines support function calling reliably; the 8B instant model is
 * flaky with tools, and NVIDIA NIM models vary — both are excluded so the loop
 * only ever runs on a capable model and otherwise degrades to the prompt path.
 */
export function isToolCapableModel(model: string): boolean {
  return /llama-3\.3-70b|gpt-oss|qwen3|llama-4|mixtral-8x/i.test(model);
}

/** Chat model chain filtered to tool-capable models (may be empty). */
export function resolveToolModelChain(): string[] {
  return resolveChatModelChain().filter(isToolCapableModel);
}

/** True when at least one tool-capable model is available in the chat chain. */
export function toolCallingAvailable(): boolean {
  return resolveToolModelChain().length > 0;
}

function buildToolMessages(opts: LLMToolCompletionOptions): LLMToolMessage[] {
  const out: LLMToolMessage[] = [];
  if (opts.system?.trim()) {
    out.push({ role: 'system', content: opts.system.trim() });
  }
  for (const m of opts.messages) {
    // Keep assistant turns that carry tool_calls even when content is empty,
    // and always keep tool-result turns (their content is the observation).
    const hasToolCalls = Array.isArray(m.tool_calls) && m.tool_calls.length > 0;
    if (!m.content?.trim() && !hasToolCalls && m.role !== 'tool') continue;
    const msg: LLMToolMessage = { role: m.role, content: m.content ?? '' };
    if (hasToolCalls) msg.tool_calls = m.tool_calls;
    if (m.role === 'tool') {
      msg.tool_call_id = m.tool_call_id;
      if (m.name) msg.name = m.name;
    }
    out.push(msg);
  }
  return out;
}

/**
 * One non-streamed tool-calling turn. Returns the assistant message — which is
 * EITHER a text answer (`content`, empty `toolCalls`) OR a set of `toolCalls`
 * the caller must execute and feed back. Returns null when every model fails
 * (e.g. the provider rejects the `tools` param), signalling the caller to
 * degrade to the plain completion path.
 */
export async function llmCompleteWithTools(
  opts: LLMToolCompletionOptions,
): Promise<LLMToolCompletionResult | null> {
  const cfg = getLLMConfig();
  if (!cfg.configured) {
    logger.warn('llm: tool completion skipped — not configured');
    return null;
  }

  const models = (opts.models ?? resolveToolModelChain()).filter(isToolCapableModel);
  if (models.length === 0) return null;

  const messages = buildToolMessages(opts);
  const timeoutMs = opts.timeoutMs ?? 45_000;

  for (const model of models) {
    const provider = resolveProviderForModel(model);
    try {
      const body: Record<string, unknown> = {
        model,
        messages,
        max_tokens: opts.maxTokens ?? 1024,
        ...resolveSamplingBody(model, opts),
        tools: opts.tools,
        tool_choice: opts.toolChoice ?? 'auto',
      };

      const resp = await fetchCompletions(provider, body, timeoutMs);
      if (!resp.ok) {
        recordFailure(
          opts.failureSink,
          classifyHttpStatus(resp.status, provider.label, model),
        );
        continue;
      }

      const json = (await resp.json()) as {
        choices?: Array<{
          message?: {
            content?: string | null;
            tool_calls?: LLMToolCall[] | null;
          };
          finish_reason?: string | null;
        }>;
      };
      const choice = json.choices?.[0];
      const msg = choice?.message;
      const toolCalls = (msg?.tool_calls ?? []).filter(
        (t) => t?.function?.name,
      );
      const content = msg?.content ?? '';
      if (toolCalls.length > 0 || content.trim()) {
        return {
          content,
          toolCalls,
          model,
          finishReason: choice?.finish_reason ?? undefined,
        };
      }
      recordFailure(opts.failureSink, {
        kind: 'empty_response',
        provider: provider.label,
        model,
      });
    } catch (err) {
      recordFailure(opts.failureSink, classifyFetchError(err, provider.label, model));
      logger.warn('llm: tool completion attempt failed', { model, err: String(err) });
    }
  }
  return null;
}

/** Parse JSON object from an LLM completion (jsonMode). */
export async function llmCompleteJson<T extends Record<string, unknown>>(
  opts: LLMCompletionOptions,
): Promise<{ json: T; model: string } | null> {
  const result = await llmComplete({ ...opts, jsonMode: true });
  if (!result) return null;
  try {
    return { json: JSON.parse(result.content) as T, model: result.model };
  } catch {
    return null;
  }
}
